/**
 * Funciones de procesamiento de texto para poemas de Versario.
 * Basado en la lógica original de app/tasks.py y tests/test_texto.py.
 */

/**
 * Normaliza el texto del poema para síntesis.
 * Normaliza saltos de línea múltiples a doble salto (\n\n) y limpia espacios.
 */
export function normalizeTextPoem(texto: string): string {
  if (!texto) {
    return '';
  }

  // Normalizar retornos de carro Windows (\r\n -> \n)
  const cleanNewlines = texto.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

  // Separar por bloques de dobles saltos o múltiples saltos
  const stanzas = cleanNewlines
    .split(/\n\s*\n+/)
    .map((stanza) => stanza.trim())
    .filter((stanza) => stanza.length > 0);

  return stanzas.join('\n\n').trim();
}

/**
 * Separa un poema en versos individuales (líneas no vacías).
 */
export function splitIntoVerses(texto: string): string[] {
  if (!texto || !texto.trim()) {
    return [];
  }

  const cleanNewlines = texto.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  const stanzas = cleanNewlines
    .split(/\n\s*\n+/)
    .map((stanza) => stanza.trim())
    .filter((stanza) => stanza.length > 0);

  const verses: string[] = [];
  for (const stanza of stanzas) {
    for (const line of stanza.split('\n')) {
      const trimmed = line.trim();
      if (trimmed.length > 0) {
        verses.push(trimmed);
      }
    }
  }

  return verses;
}

export interface StanzaStructure {
  stanzaIndex: number;
  verses: {
    verseIndex: number;
    globalIndex: number;
    text: string;
  }[];
}

/**
 * Agrupa versos por estrofas con índices para resaltado en tiempo real.
 */
export function parsePoemStructure(texto: string): StanzaStructure[] {
  if (!texto || !texto.trim()) {
    return [];
  }

  const cleanNewlines = texto.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  const rawStanzas = cleanNewlines
    .split(/\n\s*\n+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);

  let globalCounter = 0;
  const result: StanzaStructure[] = [];

  rawStanzas.forEach((stanzaText, sIdx) => {
    const rawLines = stanzaText.split('\n');
    const verses: StanzaStructure['verses'] = [];

    rawLines.forEach((line, vIdx) => {
      const trimmed = line.trim();
      if (trimmed.length > 0) {
        verses.push({
          verseIndex: vIdx,
          globalIndex: globalCounter++,
          text: trimmed,
        });
      }
    });

    if (verses.length > 0) {
      result.push({
        stanzaIndex: sIdx,
        verses,
      });
    }
  });

  return result;
}

/**
 * Estima la duración total aproximada en segundos del audio.
 * Regla de pausas: 400ms entre versos, 1000ms entre estrofas.
 */
export function estimateDuration(texto: string, speed = 1.0): number {
  const structure = parsePoemStructure(texto);
  if (structure.length === 0) return 0;

  let totalWords = 0;
  let verseCount = 0;

  for (const stanza of structure) {
    for (const verse of stanza.verses) {
      totalWords += verse.text.split(/\s+/).filter(Boolean).length;
      verseCount++;
    }
  }

  // Estimado: ~130 palabras por minuto a velocidad 1.0
  const speechSeconds = (totalWords / (130 * speed)) * 60;
  const versePauses = Math.max(0, verseCount - 1) * 0.4;
  const stanzaPauses = Math.max(0, structure.length - 1) * 1.0;

  return Math.ceil(speechSeconds + versePauses + stanzaPauses);
}
