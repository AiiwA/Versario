import React, { useState, useEffect } from 'react';
import { CreatePoemaDTO, VoiceOption } from '../types/poema';
import { SAMPLE_POEMS } from '../utils/samplePoems';
import { getAvailableVoices } from '../services/speechService';

const MAX_TEXT_LENGTH = 10000;

interface PoemFormProps {
  onSubmit: (data: CreatePoemaDTO) => void;
  isSubmitting?: boolean;
  onError: (msg: string) => void;
}

export const PoemForm: React.FC<PoemFormProps> = ({
  onSubmit,
  isSubmitting = false,
  onError,
}) => {
  const [titulo, setTitulo] = useState('');
  const [autor, setAutor] = useState('');
  const [texto, setTexto] = useState('');
  const [velocidad, setVelocidad] = useState<number>(1.0);
  const [voz, setVoz] = useState('es_ES-davefx-medium');
  const [voices, setVoices] = useState<VoiceOption[]>([]);

  useEffect(() => {
    getAvailableVoices().then((loaded) => {
      setVoices(loaded);
      if (loaded.length > 0 && !loaded.some((v) => v.id === voz)) {
        setVoz(loaded[0].id);
      }
    });
  }, []);

  const getSpeedLabel = (spd: number) => {
    if (spd < 0.95) return 'pausado';
    if (spd > 1.05) return 'rápido';
    return 'normal';
  };

  const handleSelectSample = (sampleIdx: number) => {
    const s = SAMPLE_POEMS[sampleIdx];
    if (s) {
      setTitulo(s.titulo);
      setAutor(s.autor);
      setTexto(s.texto);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const errors: string[] = [];
    if (!titulo.trim()) {
      errors.push('Título no puede estar vacío');
    }
    if (texto.length > MAX_TEXT_LENGTH) {
      errors.push(`Texto máximo ${MAX_TEXT_LENGTH} caracteres`);
    }
    if (velocidad < 0.8 || velocidad > 1.2) {
      errors.push('Velocidad debe estar entre 0.8 y 1.2');
    }

    if (errors.length > 0) {
      onError(`Errores:\n${errors.join('\n')}`);
      return;
    }

    onSubmit({
      titulo: titulo.trim(),
      autor: autor.trim() || undefined,
      texto: texto.trim(),
      voz,
      velocidad,
    });
  };

  const charCount = texto.length;
  const isNearLimit = charCount > MAX_TEXT_LENGTH * 0.8;

  return (
    <section className="poem-form">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
        <h2>Nuevo Poema</h2>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.85em', color: 'var(--secondary-color)', fontWeight: 600 }}>
            Ejemplos:
          </span>
          {SAMPLE_POEMS.map((sp, idx) => (
            <button
              key={idx}
              type="button"
              className="btn-secondary"
              onClick={() => handleSelectSample(idx)}
              title={sp.descripcion}
            >
              {sp.titulo}
            </button>
          ))}
        </div>
      </div>

      <form id="poemForm" className="poem-form__form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="titulo">Título:</label>
          <input
            type="text"
            id="titulo"
            name="titulo"
            required
            placeholder="Ej: Mi Primer Poema"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="autor">Autor (opcional):</label>
          <input
            type="text"
            id="autor"
            name="autor"
            placeholder="Tu nombre"
            value={autor}
            onChange={(e) => setAutor(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="texto">Texto del poema:</label>
          <textarea
            id="texto"
            name="texto"
            rows={7}
            required
            placeholder={'Escribe tu poema aquí...\n\nRecuerda: Usa doble salto de línea para separar estrofas.\nCada línea no vacía será un verso separado.'}
            maxLength={MAX_TEXT_LENGTH}
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
          />
          <small
            id="textoCounter"
            className="form-counter"
            style={{ color: isNearLimit ? '#f44336' : 'var(--secondary-color)' }}
          >
            {charCount}/{MAX_TEXT_LENGTH} caracteres
          </small>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div className="form-group">
            <label htmlFor="velocidad">
              Velocidad: <span style={{ fontWeight: 400 }}>({velocidad.toFixed(1)}x)</span>
            </label>
            <input
              type="number"
              id="velocidad"
              name="velocidad"
              min="0.8"
              max="1.2"
              step="0.1"
              required
              value={velocidad}
              onChange={(e) => setVelocidad(parseFloat(e.target.value) || 1.0)}
            />
            <small style={{ color: 'var(--secondary-color)', display: 'block', marginTop: '4px' }}>
              Nivel: {getSpeedLabel(velocidad)}
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="voz">Voz:</label>
            <select
              id="voz"
              name="voz"
              required
              value={voz}
              onChange={(e) => setVoz(e.target.value)}
            >
              {voices.length > 0 ? (
                voices.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} - {v.language} {v.quality ? `(${v.quality})` : ''}
                  </option>
                ))
              ) : (
                <option value="es_ES-davefx-medium">Voz predeterminada (Piper)</option>
              )}
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="btn-primary"
          style={{ width: '100%', marginTop: '10px' }}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creando Poema...' : '🎵 Crear Poema'}
        </button>
      </form>
    </section>
  );
};
