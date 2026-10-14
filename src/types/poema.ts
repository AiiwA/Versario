export type PoemaEstado = 'pendiente' | 'generando' | 'listo' | 'error';

export interface Poema {
  id: number;
  titulo: string;
  autor?: string | null;
  texto: string;
  ruta_audio?: string | null;
  audioBlobUrl?: string | null;
  voz: string;
  velocidad: number;
  estado: PoemaEstado;
  creado_en: string;
}

export interface CreatePoemaDTO {
  titulo: string;
  autor?: string;
  texto: string;
  voz: string;
  velocidad: number;
}

export interface VoiceOption {
  id: string;
  name: string;
  language: string;
  quality: string;
  gender?: string | null;
  description?: string;
}
