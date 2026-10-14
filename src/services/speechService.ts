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
  private isCancelled = false;
  private isPaused = false;
  private pauseResolver: (() => void) | null = null;

  async speakPoem(
    texto: string,
    voiceId: string,
    speed: number,
    callbacks: PlaybackCallbacks
  ): Promise<void> {
    this.isCancelled = false;
    this.isPaused = false;

    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      callbacks.onError?.(new Error('La síntesis de voz no está soportada en este navegador.'));
      return;
    }

    window.speechSynthesis.cancel();

    // Seleccionar voz del navegador si coincide
    const available = window.speechSynthesis.getVoices();
    let selectedVoice = available.find(
      (v) => v.voiceURI === voiceId || v.name === voiceId
    );

    if (!selectedVoice) {
      // Buscar primera voz en español
      selectedVoice = available.find((v) => v.lang.startsWith('es')) || available[0];
    }

    const structure = parsePoemStructure(texto);

    try {
      for (let sIdx = 0; sIdx < structure.length; sIdx++) {
        if (this.isCancelled) break;
        const stanza = structure[sIdx];

        for (let vIdx = 0; vIdx < stanza.verses.length; vIdx++) {
          if (this.isCancelled) break;
          const verse = stanza.verses[vIdx];

          await this.checkPause();
          if (this.isCancelled) break;

          callbacks.onVerseChange?.(verse.globalIndex);

          await this.speakVerse(verse.text, selectedVoice, speed);

          if (this.isCancelled) break;

          // Pausa entre versos: 400ms (regla de Versario)
          // Si es el último verso de la estrofa y hay más estrofas, pausa de 1000ms
          const isLastVerseInStanza = vIdx === stanza.verses.length - 1;
          const isLastStanza = sIdx === structure.length - 1;

          if (!isLastVerseInStanza) {
            await this.sleep(400);
          } else if (!isLastStanza) {
            // Pausa entre estrofas: 1000ms (regla de Versario)
            await this.sleep(1000);
          }
        }
      }

      callbacks.onVerseChange?.(null);
      if (!this.isCancelled) {
        callbacks.onEnd?.();
      }
    } catch (err) {
      callbacks.onVerseChange?.(null);
      callbacks.onError?.(err instanceof Error ? err : new Error(String(err)));
    }
  }

  private speakVerse(
    text: string,
    voice: SpeechSynthesisVoice | undefined,
    speed: number
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isCancelled) {
        resolve();
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      if (voice) {
        utterance.voice = voice;
      }
      utterance.lang = voice?.lang || 'es-ES';
      utterance.rate = Math.max(0.5, Math.min(2.0, speed));
      utterance.pitch = 1.0;

      utterance.onend = () => {
        resolve();
      };

      utterance.onerror = (e) => {
        if (this.isCancelled) {
          resolve();
        } else {
          // Algunos navegadores lanzan 'interrupted' al cancelar
          if (e.error === 'interrupted' || e.error === 'canceled') {
            resolve();
          } else {
            reject(new Error(`Error de síntesis: ${e.error}`));
          }
        }
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
    if (this.pauseResolver) {
      this.pauseResolver();
      this.pauseResolver = null;
    }
  }

  stop() {
    this.isCancelled = true;
    this.isPaused = false;
    if (this.pauseResolver) {
      this.pauseResolver();
      this.pauseResolver = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }

  private async checkPause() {
    while (this.isPaused && !this.isCancelled) {
      await new Promise<void>((resolve) => {
        this.pauseResolver = resolve;
      });
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => {
      const timer = setTimeout(resolve, ms);
      if (this.isCancelled) {
        clearTimeout(timer);
        resolve();
      }
    });
  }
}
