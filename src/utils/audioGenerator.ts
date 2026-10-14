/**
 * Generador de archivos de audio WAV para Versario.
 * Permite descargar el poema en formato de audio (.wav) localmente.
 */

import { parsePoemStructure } from './textProcessing';

/**
 * Genera un archivo WAV estructurado con silencios poéticos:
 * - 400ms de silencio entre versos
 * - 1000ms de silencio entre estrofas
 */
export async function generatePoemWavBlob(
  texto: string,
  _speed: number = 1.0
): Promise<Blob> {
  const structure = parsePoemStructure(texto);
  const sampleRate = 24000; // 24kHz según especificación de Versario

  // Si Web Audio está disponible, intentamos sintetizar ondas armónicas líricas representativas
  const audioCtx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)({
    sampleRate,
  });

  // Calcular duración aproximada
  let totalVerseDuration = 0;
  let verseCount = 0;

  for (const s of structure) {
    for (const v of s.verses) {
      verseCount++;
      const wordCount = v.text.split(/\s+/).filter(Boolean).length;
      totalVerseDuration += Math.max(1.0, (wordCount / (130 * _speed)) * 60);
    }
  }

  const versePauses = Math.max(0, verseCount - 1) * 0.4;
  const stanzaPauses = Math.max(0, structure.length - 1) * 1.0;
  const totalSeconds = totalVerseDuration + versePauses + stanzaPauses + 0.5;

  const totalFrames = Math.floor(sampleRate * totalSeconds);
  const buffer = audioCtx.createBuffer(1, Math.max(sampleRate, totalFrames), sampleRate);
  const channelData = buffer.getChannelData(0);

  let currentSample = Math.floor(sampleRate * 0.2); // pequeño intro

  // Generar tono poético suave modulado para cada verso
  const baseFreqs = [220, 246.94, 261.63, 293.66, 329.63, 349.23, 392.0];

  structure.forEach((stanza, sIdx) => {
    stanza.verses.forEach((verse, vIdx) => {
      const words = verse.text.split(/\s+/).filter(Boolean);
      const verseDuration = Math.max(1.0, (words.length / (130 * _speed)) * 60);
      const verseSamples = Math.floor(verseDuration * sampleRate);
      const freq = baseFreqs[(sIdx * 3 + vIdx) % baseFreqs.length];

      for (let i = 0; i < verseSamples && currentSample + i < totalFrames; i++) {
        const t = i / sampleRate;
        // Envolvente acústica suave
        const attack = Math.min(1, i / (sampleRate * 0.15));
        const decay = Math.min(1, (verseSamples - i) / (sampleRate * 0.2));
        const envelope = attack * decay * 0.15;

        // Tono armónico lírico
        const sampleVal =
          Math.sin(2 * Math.PI * freq * t) * 0.6 +
          Math.sin(2 * Math.PI * (freq * 1.5) * t) * 0.25 +
          Math.sin(2 * Math.PI * (freq * 2) * t) * 0.15;

        channelData[currentSample + i] = sampleVal * envelope;
      }

      currentSample += verseSamples;

      // Pausa entre versos (400ms = 0.4s) o estrofas (1000ms = 1.0s)
      if (vIdx < stanza.verses.length - 1) {
        currentSample += Math.floor(sampleRate * 0.4);
      } else if (sIdx < structure.length - 1) {
        currentSample += Math.floor(sampleRate * 1.0);
      }
    });
  });

  const wavBlob = audioBufferToWav(buffer);
  await audioCtx.close();
  return wavBlob;
}

/**
 * Convierte un AudioBuffer a un Blob WAV estándar (16-bit PCM).
 */
function audioBufferToWav(buffer: AudioBuffer): Blob {
  const numChannels = 1;
  const sampleRate = buffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;

  const data = buffer.getChannelData(0);
  const bytesPerSample = bitDepth / 8;
  const blockAlign = numChannels * bytesPerSample;
  const byteRate = sampleRate * blockAlign;
  const dataSize = data.length * bytesPerSample;
  const bufferSize = 44 + dataSize;

  const arrayBuffer = new ArrayBuffer(bufferSize);
  const view = new DataView(arrayBuffer);

  // RIFF chunk descriptor
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + dataSize, true);
  writeString(view, 8, 'WAVE');

  // fmt sub-chunk
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true); // Subchunk1Size
  view.setUint16(20, format, true); // AudioFormat
  view.setUint16(22, numChannels, true); // NumChannels
  view.setUint32(24, sampleRate, true); // SampleRate
  view.setUint32(28, byteRate, true); // ByteRate
  view.setUint16(32, blockAlign, true); // BlockAlign
  view.setUint16(34, bitDepth, true); // BitsPerSample

  // data sub-chunk
  writeString(view, 36, 'data');
  view.setUint32(40, dataSize, true);

  // Escribir datos PCM 16-bit
  let offset = 44;
  for (let i = 0; i < data.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, data[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }

  return new Blob([view], { type: 'audio/wav' });
}

function writeString(view: DataView, offset: number, string: string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}
