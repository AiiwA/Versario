import { Poema, CreatePoemaDTO } from '../types/poema';
import { SAMPLE_POEMS } from '../utils/samplePoems';

const STORAGE_KEY = 'versario_poemas_db';

const INITIAL_POEMS: Poema[] = [
  {
    id: 1,
    titulo: SAMPLE_POEMS[0].titulo,
    autor: SAMPLE_POEMS[0].autor,
    texto: SAMPLE_POEMS[0].texto,
    ruta_audio: '/audio/poema_1.mp3',
    voz: 'es_ES-davefx-medium',
    velocidad: 1.0,
    estado: 'listo',
    creado_en: new Date(Date.now() - 3600000 * 2).toISOString(),
  },
  {
    id: 2,
    titulo: SAMPLE_POEMS[1].titulo,
    autor: SAMPLE_POEMS[1].autor,
    texto: SAMPLE_POEMS[1].texto,
    ruta_audio: '/audio/poema_2.mp3',
    voz: 'es_ES-carolina-medium',
    velocidad: 1.0,
    estado: 'listo',
    creado_en: new Date(Date.now() - 3600000 * 24).toISOString(),
  },
  {
    id: 3,
    titulo: SAMPLE_POEMS[2].titulo,
    autor: SAMPLE_POEMS[2].autor,
    texto: SAMPLE_POEMS[2].texto,
    ruta_audio: '/audio/poema_3.mp3',
    voz: 'es_ES-diego-medium',
    velocidad: 0.9,
    estado: 'listo',
    creado_en: new Date(Date.now() - 3600000 * 48).toISOString(),
  },
];

export function getStoredPoems(): Poema[] {
  if (typeof window === 'undefined') return INITIAL_POEMS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_POEMS));
      return INITIAL_POEMS;
    }
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : INITIAL_POEMS;
  } catch {
    return INITIAL_POEMS;
  }
}

export function savePoem(dto: CreatePoemaDTO): Poema {
  const current = getStoredPoems();
  const nextId = current.length > 0 ? Math.max(...current.map((p) => p.id)) + 1 : 1;

  const newPoem: Poema = {
    id: nextId,
    titulo: dto.titulo.trim(),
    autor: dto.autor?.trim() || null,
    texto: dto.texto.trim(),
    voz: dto.voz || 'es_ES-davefx-medium',
    velocidad: dto.velocidad || 1.0,
    estado: 'generando',
    ruta_audio: `/audio/poema_${nextId}.mp3`,
    creado_en: new Date().toISOString(),
  };

  const updated = [newPoem, ...current];
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (e) {
    console.error('Error saving to localStorage:', e);
  }

  return newPoem;
}

export function updatePoemStatus(id: number, estado: Poema['estado'], extra?: Partial<Poema>): Poema | null {
  const current = getStoredPoems();
  const idx = current.findIndex((p) => p.id === id);
  if (idx === -1) return null;

  const updatedPoem = {
    ...current[idx],
    estado,
    ...extra,
  };

  current[idx] = updatedPoem;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
  } catch (e) {
    console.error('Error updating localStorage:', e);
  }

  return updatedPoem;
}

export function deletePoem(id: number): boolean {
  const current = getStoredPoems();
  const filtered = current.filter((p) => p.id !== id);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    return true;
  } catch (e) {
    console.error('Error deleting from localStorage:', e);
    return false;
  }
}

export function getPoemById(id: number): Poema | null {
  const current = getStoredPoems();
  return current.find((p) => p.id === id) || null;
}
