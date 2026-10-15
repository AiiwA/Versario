import React, { useState, useEffect } from 'react';
import { Feather } from 'lucide-react';
import { CreatePoemaDTO, VoiceOption } from '../types/poema';
import { SAMPLE_POEMS } from '../utils/samplePoems';
import { getAvailableVoices } from '../services/speechService';

const MAX_TEXT_LENGTH = 10000;

interface PoemFormProps {
  onSubmit: (data: CreatePoemaDTO) => void;
  isSubmitting?: boolean;
  onError: (msg: string) => void;
}

const label = 'mb-2 block text-sm font-medium text-muted';

export const PoemForm: React.FC<PoemFormProps> = ({ onSubmit, isSubmitting = false, onError }) => {
  const [titulo, setTitulo] = useState('');
  const [autor, setAutor] = useState('');
  const [texto, setTexto] = useState('');
  const [velocidad, setVelocidad] = useState<number>(1.0);
  const [voz, setVoz] = useState('es_ES-davefx-medium');
  const [voices, setVoices] = useState<VoiceOption[]>([]);

  useEffect(() => {
    getAvailableVoices().then((loaded) => {
      setVoices(loaded);
      setVoz((current) => (loaded.some((v) => v.id === current) ? current : loaded[0]?.id ?? current));
    });
  }, []);

  const handleSelectSample = (idx: number) => {
    const s = SAMPLE_POEMS[idx];
    if (s) {
      setTitulo(s.titulo);
      setAutor(s.autor);
      setTexto(s.texto);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const errors: string[] = [];
    if (!titulo.trim()) errors.push('El título no puede estar vacío');
    if (!texto.trim()) errors.push('El poema no puede estar vacío');
    if (velocidad < 0.8 || velocidad > 1.2) errors.push('La velocidad debe estar entre 0.8 y 1.2');
    if (errors.length > 0) {
      onError(errors.join('\n'));
      return;
    }
    onSubmit({ titulo: titulo.trim(), autor: autor.trim() || undefined, texto: texto.trim(), voz, velocidad });
  };

  const nearLimit = texto.length > MAX_TEXT_LENGTH * 0.8;

  return (
    <section className="rise rounded-3xl border border-line bg-panel p-6 md:p-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <h2 className="font-serif text-3xl">Nuevo poema</h2>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted">Probar con:</span>
          {SAMPLE_POEMS.map((sp, idx) => (
            <button key={sp.titulo} type="button" className="btn btn-ghost !px-4 !py-1.5 text-sm" onClick={() => handleSelectSample(idx)} title={sp.descripcion}>
              {sp.titulo}
            </button>
          ))}
        </div>
      </div>

      <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <label className={label} htmlFor="titulo">Título</label>
            <input className="field" type="text" id="titulo" required placeholder="Mi primer poema" value={titulo} onChange={(e) => setTitulo(e.target.value)} />
          </div>
          <div>
            <label className={label} htmlFor="autor">Autor (opcional)</label>
            <input className="field" type="text" id="autor" placeholder="Tu nombre" value={autor} onChange={(e) => setAutor(e.target.value)} />
          </div>
        </div>

        <div>
          <label className={label} htmlFor="texto">Texto del poema</label>
          <textarea
            className="field min-h-48 resize-y font-serif text-lg leading-relaxed"
            id="texto"
            required
            placeholder={'Escribe aquí.\n\nUna línea en blanco separa las estrofas; cada línea es un verso.'}
            maxLength={MAX_TEXT_LENGTH}
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
          />
          <small className={`mt-2 block text-right text-sm ${nearLimit ? 'text-danger' : 'text-muted'}`}>
            {texto.length}/{MAX_TEXT_LENGTH}
          </small>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <label className={label} htmlFor="velocidad">
              Velocidad <span className="text-paper">{velocidad.toFixed(1)}x</span>
            </label>
            <input
              type="range" id="velocidad" min="0.8" max="1.2" step="0.1"
              className="h-11 w-full accent-amber"
              value={velocidad}
              onChange={(e) => setVelocidad(parseFloat(e.target.value))}
            />
          </div>
          <div>
            <label className={label} htmlFor="voz">Voz</label>
            <select className="field" id="voz" value={voz} onChange={(e) => setVoz(e.target.value)}>
              {voices.length > 0 ? (
                voices.map((v) => (
                  <option key={v.id} value={v.id}>{v.name} · {v.language}</option>
                ))
              ) : (
                <option value="es_ES-davefx-medium">Voz predeterminada</option>
              )}
            </select>
          </div>
        </div>

        <button type="submit" className="btn btn-primary w-full !py-4 text-lg" disabled={isSubmitting}>
          <Feather size={20} aria-hidden /> {isSubmitting ? 'Creando…' : 'Crear poema'}
        </button>
      </form>
    </section>
  );
};
