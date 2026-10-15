import { VoiceOption } from '../types/poema';
import { parsePoemStructure } from '../utils/textProcessing';

// Voces Piper originales como referencia y compatibilidad
export const DEFAULT_PIPER_VOICES: VoiceOption[] = [
  {
    id: 'es_ES-davefx-medium',
    name: 'es_ES-davefx-medium',
    language: 'Español (España)',
    quality: 'media (calidad 4)',
    gender: 'Masculina',
    description: 'Voz predeterminada (Piper davefx)',
  },
  {
    id: 'es_ES-carolina-medium',
    name: 'es_ES-carolina-medium',
    language: 'Español (España)',
    quality: 'alta (calidad 4)',
    gender: 'Femenina',
    description: 'Voz lírica femenina (Piper carolina)',
  },
  {
    id: 'es_ES-diego-medium',
    name: 'es_ES-diego-medium',
    language: 'Español (España)',
    quality: 'alta (calidad 4)',
    gender: 'Masculina',
    description: 'Voz pausada masculina (Piper diego)',
  },
];

/**
 * Obtiene lista combinada de voces del sistema y de Piper.
 */
export function getAvailableVoices(): Promise<VoiceOption[]> {
  return new Promise((resolve) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      resolve(DEFAULT_PIPER_VOICES);
      return;
    }

    const checkVoices = () => {
      const browserVoices = window.speechSynthesis.getVoices();
      const combined: VoiceOption[] = [...DEFAULT_PIPER_VOICES];

      // Añadir voces del navegador en español o compatibles
      browserVoices.forEach((v) => {
        const isSpanish = v.lang.startsWith('es') || v.lang.includes('Spanish');
        if (isSpanish && !combined.some((c) => c.id === v.voiceURI)) {
          combined.push({
            id: v.voiceURI,
            name: `${v.name} (${v.lang})`,
            language: v.lang,
            quality: 'Sistema',
            gender: v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('mujer') ? 'Femenina' : 'Masculina',
            description: v.name,
          });
        }
      });

      resolve(combined);
    };

    const initial = window.speechSynthesis.getVoices();
    if (initial.length > 0) {
      checkVoices();
    } else {
      window.speechSynthesis.onvoiceschanged = () => {
        checkVoices();
      };
      // Fallback timeout
      setTimeout(() => checkVoices(), 400);
    }
  });
}

export interface PlaybackCallbacks {
  onVerseChange?: (globalVerseIndex: number | null) => void;
  onEnd?: () => void;
  onError?: (err: Error) => void;
}

export class PoemSpeaker {
  // Cada lectura nueva incrementa runId; los bucles viejos se detectan y terminan solos.
  private runId = 0;
  private isPaused = false;
  private pauseResolver: (() => void) | null = null;

  private pickVoice(voiceId: string): SpeechSynthesisVoice | undefined {
    const available = window.speechSynthesis.getVoices();
    return (
      available.find((v) => v.voiceURI === voiceId || v.name === voiceId) ||
      available.find((v) => v.lang.startsWith('es')) ||
      available[0]
    );
  }

  async speakPoem(
    texto: string,
    voiceId: string,
    speed: number,
    callbacks: PlaybackCallbacks
  ): Promise<void> {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      callbacks.onError?.(new Error('La síntesis de voz no está soportada en este navegador.'));
      return;
    }

    this.stop();
    const myRun = this.runId;
    const alive = () => this.runId === myRun;

    const voice = this.pickVoice(voiceId);
    const structure = parsePoemStructure(texto);

    try {
      for (let sIdx = 0; sIdx < structure.length && alive(); sIdx++) {
        const stanza = structure[sIdx];

        for (let vIdx = 0; vIdx < stanza.verses.length && alive(); vIdx++) {
          const verse = stanza.verses[vIdx];

          await this.checkPause(alive);
          if (!alive()) break;

          callbacks.onVerseChange?.(verse.globalIndex);
          await this.speakVerse(verse.text, voice, speed, alive);
          if (!alive()) break;

          // 400 ms entre versos, 1000 ms entre estrofas
          const isLastVerse = vIdx === stanza.verses.length - 1;
          const isLastStanza = sIdx === structure.length - 1;
          if (!isLastVerse) await this.sleep(400, alive);
          else if (!isLastStanza) await this.sleep(1000, alive);
        }
      }

      if (alive()) {
        callbacks.onVerseChange?.(null);
        callbacks.onEnd?.();
      }
    } catch (err) {
      if (alive()) {
        callbacks.onVerseChange?.(null);
        callbacks.onError?.(err instanceof Error ? err : new Error(String(err)));
      }
    }
  }

  /** Lee un solo verso, cancelando cualquier lectura en curso. */
  async speakSingle(text: string, voiceId: string, speed: number): Promise<void> {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    this.stop();
    const myRun = this.runId;
    await this.speakVerse(text, this.pickVoice(voiceId), speed, () => this.runId === myRun).catch(() => {});
  }

  private speakVerse(
    text: string,
    voice: SpeechSynthesisVoice | undefined,
    speed: number,
    alive: () => boolean
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!alive()) return resolve();

      const utterance = new SpeechSynthesisUtterance(text);
      if (voice) utterance.voice = voice;
      utterance.lang = voice?.lang || 'es-ES';
      utterance.rate = Math.max(0.5, Math.min(2.0, speed));
      utterance.onend = () => resolve();
      utterance.onerror = (e) => {
        if (!alive() || e.error === 'interrupted' || e.error === 'canceled') resolve();
        else reject(new Error(`Error de síntesis: ${e.error}`));
      };

      window.speechSynthesis.speak(utterance);
    });
  }

  pause() {
    this.isPaused = true;
    window.speechSynthesis.pause();
  }

  resume() {
    this.isPaused = false;
    window.speechSynthesis.resume();
    this.pauseResolver?.();
    this.pauseResolver = null;
  }

  stop() {
    this.runId++;
    this.isPaused = false;
    this.pauseResolver?.();
    this.pauseResolver = null;
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }

  private async checkPause(alive: () => boolean) {
    while (this.isPaused && alive()) {
      await new Promise<void>((resolve) => {
        this.pauseResolver = resolve;
      });
    }
  }

  // La pausa también congela los silencios poéticos, no solo la voz.
  private async sleep(ms: number, alive: () => boolean) {
    let remaining = ms;
    while (remaining > 0 && alive()) {
      await this.checkPause(alive);
      const step = Math.min(50, remaining);
      await new Promise((r) => setTimeout(r, step));
      remaining -= step;
    }
  }
}
