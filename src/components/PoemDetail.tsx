import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Play, Pause, Square, Download, Trash2, Mic, Gauge, Loader2 } from 'lucide-react';
import { Poema } from '../types/poema';
import { parsePoemStructure } from '../utils/textProcessing';
import { PoemSpeaker } from '../services/speechService';
import { generatePoemWavBlob } from '../utils/audioGenerator';

interface PoemDetailProps {
  poema: Poema;
  onBack: () => void;
  onUpdatePoem: (id: number, estado: Poema['estado'], extra?: Partial<Poema>) => void;
  onDeletePoem: (id: number) => void;
  onError: (msg: string) => void;
}

export const PoemDetail: React.FC<PoemDetailProps> = ({ poema, onBack, onUpdatePoem, onDeletePoem, onError }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [activeVerseIndex, setActiveVerseIndex] = useState<number | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const speakerRef = useRef<PoemSpeaker | null>(null);
  const structure = useMemo(() => parsePoemStructure(poema.texto), [poema.texto]);
  const preparing = poema.estado === 'generando' || poema.estado === 'pendiente';

  // Preparación simulada: pasa a 'listo' una sola vez (sin efectos dentro de setState).
  useEffect(() => {
    if (!preparing) return;
    const t = setTimeout(() => onUpdatePoem(poema.id, 'listo', { ruta_audio: `/audio/poema_${poema.id}.mp3` }), 1200);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preparing, poema.id]);

  useEffect(() => () => speakerRef.current?.stop(), []);

  const getSpeaker = () => (speakerRef.current ??= new PoemSpeaker());

  const resetPlayback = () => {
    setIsPlaying(false);
    setIsPaused(false);
    setActiveVerseIndex(null);
  };

  const handlePlay = async () => {
    const speaker = getSpeaker();
    if (isPaused) {
      speaker.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }
    setIsPlaying(true);
    await speaker.speakPoem(poema.texto, poema.voz, poema.velocidad, {
      onVerseChange: setActiveVerseIndex,
      onEnd: resetPlayback,
      onError: (err) => {
        resetPlayback();
        onError(`Error al reproducir audio: ${err.message}`);
      },
    });
  };

  const handlePause = () => {
    speakerRef.current?.pause();
    setIsPaused(true);
    setIsPlaying(false);
  };

  const handleStop = () => {
    speakerRef.current?.stop();
    resetPlayback();
  };

  const handleVerseClick = async (text: string, globalIndex: number) => {
    resetPlayback();
    setActiveVerseIndex(globalIndex);
    await getSpeaker().speakSingle(text, poema.voz, poema.velocidad);
    setActiveVerseIndex((cur) => (cur === globalIndex ? null : cur));
  };

  const handleDownload = async () => {
    try {
      setIsDownloading(true);
      const wavBlob = await generatePoemWavBlob(poema.texto, poema.velocidad);
      const url = URL.createObjectURL(wavBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `poema_${poema.id}_${poema.titulo.toLowerCase().replace(/[^a-z0-9]+/g, '_')}.wav`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 2000);
    } catch (err) {
      onError(`Error al generar la descarga: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <article className="rise">
      <h2 className="max-w-4xl font-serif text-4xl leading-tight text-balance md:text-6xl">{poema.titulo}</h2>
      <p className="mt-4 text-lg text-muted">por {poema.autor || 'Anónimo'}</p>

      {preparing ? (
        <div className="mt-16 flex items-center gap-4 text-muted" role="status">
          <Loader2 className="animate-spin text-amber" aria-hidden />
          Preparando "{poema.titulo}"…
        </div>
      ) : (
        <>
          <section className="mt-12 flex flex-wrap items-center gap-3 rounded-3xl border border-line bg-panel p-4 md:p-5" aria-label="Reproductor">
            {isPlaying ? (
              <button type="button" className="btn btn-primary" onClick={handlePause}>
                <Pause size={18} aria-hidden /> Pausar
              </button>
            ) : (
              <button type="button" className="btn btn-primary" onClick={handlePlay}>
                <Play size={18} aria-hidden /> {isPaused ? 'Reanudar' : 'Reproducir'}
              </button>
            )}
            {(isPlaying || isPaused) && (
              <button type="button" className="btn btn-ghost" onClick={handleStop}>
                <Square size={16} aria-hidden /> Detener
              </button>
            )}

            <div className="flex flex-wrap items-center gap-x-5 gap-y-1 px-2 text-sm text-muted">
              <span className="inline-flex items-center gap-2"><Mic size={16} aria-hidden /> {poema.voz}</span>
              <span className="inline-flex items-center gap-2"><Gauge size={16} aria-hidden /> {poema.velocidad}x</span>
            </div>

            <button
              type="button"
              className="btn btn-ghost sm:ml-auto"
              onClick={handleDownload}
              disabled={isDownloading}
              title="Genera un WAV con la duración y los silencios del poema; la voz del navegador no se puede grabar"
            >
              <Download size={18} aria-hidden /> {isDownloading ? 'Preparando…' : 'Descargar guía WAV'}
            </button>
          </section>

          <section className="mt-12 max-w-3xl font-serif text-2xl leading-relaxed md:text-3xl md:leading-[1.6]" aria-live="off">
            {structure.map((stanza) => (
              <div key={stanza.stanzaIndex} className="mb-10">
                {stanza.verses.map((verse) => (
                  <button
                    type="button"
                    key={verse.globalIndex}
                    className={`verse block w-full text-left ${activeVerseIndex === verse.globalIndex ? 'active' : ''}`}
                    onClick={() => handleVerseClick(verse.text, verse.globalIndex)}
                    title="Escuchar este verso"
                  >
                    {verse.text}
                  </button>
                ))}
              </div>
            ))}
          </section>

          <div className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-line pt-6">
            <span className="text-sm text-muted">Toca cualquier verso para escucharlo solo.</span>
            <button
              type="button"
              className="btn btn-ghost !text-danger"
              onClick={() => {
                if (confirm(`¿Seguro que deseas eliminar el poema "${poema.titulo}"?`)) {
                  onDeletePoem(poema.id);
                  onBack();
                }
              }}
            >
              <Trash2 size={16} aria-hidden /> Eliminar poema
            </button>
          </div>
        </>
      )}
    </article>
  );
};
