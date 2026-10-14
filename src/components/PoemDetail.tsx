import React, { useState, useEffect, useRef } from 'react';
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

export const PoemDetail: React.FC<PoemDetailProps> = ({
  poema,
  onBack,
  onUpdatePoem,
  onDeletePoem,
  onError,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [activeVerseIndex, setActiveVerseIndex] = useState<number | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);

  const speakerRef = useRef<PoemSpeaker | null>(null);
  const structure = parsePoemStructure(poema.texto);

  // Simulación de pipeline de generación si el poema está en estado 'generando' o 'pendiente'
  useEffect(() => {
    if (poema.estado === 'generando' || poema.estado === 'pendiente') {
      const interval = setInterval(() => {
        setGenerationProgress((prev) => {
          if (prev >= 90) {
            clearInterval(interval);
            onUpdatePoem(poema.id, 'listo', {
              ruta_audio: `/audio/poema_${poema.id}.mp3`,
            });
            return 100;
          }
          return prev + 30;
        });
      }, 500);

      return () => clearInterval(interval);
    }
  }, [poema.estado, poema.id]);

  // Limpiar reproductor al desmontar
  useEffect(() => {
    return () => {
      if (speakerRef.current) {
        speakerRef.current.stop();
      }
    };
  }, []);

  const handlePlay = async () => {
    if (isPaused && speakerRef.current) {
      speakerRef.current.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }

    if (!speakerRef.current) {
      speakerRef.current = new PoemSpeaker();
    }

    setIsPlaying(true);
    setIsPaused(false);

    await speakerRef.current.speakPoem(
      poema.texto,
      poema.voz,
      poema.velocidad,
      {
        onVerseChange: (idx) => {
          setActiveVerseIndex(idx);
        },
        onEnd: () => {
          setIsPlaying(false);
          setIsPaused(false);
          setActiveVerseIndex(null);
        },
        onError: (err) => {
          setIsPlaying(false);
          setIsPaused(false);
          setActiveVerseIndex(null);
          onError(`Error al reproducir audio: ${err.message}`);
        },
      }
    );
  };

  const handlePause = () => {
    if (speakerRef.current) {
      speakerRef.current.pause();
      setIsPaused(true);
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    if (speakerRef.current) {
      speakerRef.current.stop();
      setIsPaused(false);
      setIsPlaying(false);
      setActiveVerseIndex(null);
    }
  };

  const handleDownload = async () => {
    try {
      setIsDownloading(true);
      const wavBlob = await generatePoemWavBlob(poema.texto, poema.velocidad);
      const url = URL.createObjectURL(wavBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `poema_${poema.id}_${poema.titulo.toLowerCase().replace(/[^a-z0-9]/g, '_')}.wav`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 2000);
    } catch (err) {
      onError(`Error al generar descarga de audio: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="poem-detail-container">
      <button onClick={onBack} className="back-link">
        ← Volver
      </button>

      <header style={{ marginBottom: '24px' }}>
        <h1 id="poemTitle" style={{ fontSize: '2rem', color: '#1e293b', marginBottom: '8px' }}>
          {poema.titulo}
        </h1>
        <p className="poem-author" style={{ color: 'var(--secondary-color)', fontSize: '1.1rem' }}>
          por {poema.autor || 'Anónimo'}
        </p>
        <p className="poem-status" style={{ marginTop: '8px', fontSize: '0.95rem' }}>
          Estado:{' '}
          <span id="poemStatus" className={`status-badge status-${poema.estado}`}>
            {poema.estado}
          </span>
        </p>
      </header>

      {poema.estado === 'generando' || poema.estado === 'pendiente' ? (
        <div id="loadingSpinner" className="loading-spinner">
          <div className="spinner"></div>
          <p style={{ fontWeight: 600, color: 'var(--secondary-color)' }}>
            Sintetizando audio para "{poema.titulo}"...
          </p>
          <div
            style={{
              width: '240px',
              height: '8px',
              backgroundColor: '#e2e8f0',
              borderRadius: '4px',
              margin: '16px auto 0',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${generationProgress}%`,
                height: '100%',
                backgroundColor: 'var(--primary-color)',
                transition: 'width 0.4s ease',
              }}
            ></div>
          </div>
          <small style={{ color: '#888', display: 'block', marginTop: '8px' }}>
            Uniendo fragmentos y aplicando pausas poéticas...
          </small>
        </div>
      ) : (
        <>
          {/* Reproductor de audio */}
          <section className="audio-player audio-player-card">
            <div className="audio-controls">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {!isPlaying ? (
                  <button
                    id="playBtn"
                    type="button"
                    className="btn-primary"
                    onClick={handlePlay}
                    style={{ padding: '10px 20px', minWidth: '120px' }}
                  >
                    ▶ {isPaused ? 'Reanudar' : 'Reproducir'}
                  </button>
                ) : (
                  <button
                    type="button"
                    className="btn-primary"
                    onClick={handlePause}
                    style={{ padding: '10px 20px', minWidth: '120px', backgroundColor: '#e65100' }}
                  >
                    ⏸ Pausar
                  </button>
                )}

                {(isPlaying || isPaused) && (
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={handleStop}
                    style={{ padding: '10px 16px' }}
                    title="Detener lectura"
                  >
                    ⏹ Detener
                  </button>
                )}
              </div>

              <div style={{ fontSize: '0.9rem', color: 'var(--secondary-color)', display: 'flex', gap: '14px', alignItems: 'center' }}>
                <span>🎙️ Voz: <strong>{poema.voz}</strong></span>
                <span>⚡ Velocidad: <strong>{poema.velocidad}x</strong></span>
              </div>

              <button
                type="button"
                className="download-btn"
                onClick={handleDownload}
                disabled={isDownloading}
                title="Descargar archivo de audio"
              >
                {isDownloading ? '⏳ Preparando...' : '⬇ Descargar Audio'}
              </button>
            </div>

            {isPlaying && (
              <div style={{ marginTop: '14px', fontSize: '0.88rem', color: '#0284c7', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px', margin: 0 }}></span>
                <span>Recitando con pausas poéticas naturales (400ms versos / 1000ms estrofas)...</span>
              </div>
            )}
          </section>

          {/* Contenido del poema */}
          <section id="poemContent" className="poem-content">
            <div
              style={{
                padding: '28px',
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
              }}
            >
              {structure.map((stanza) => (
                <div
                  key={stanza.stanzaIndex}
                  style={{
                    marginBottom: '24px',
                    fontFamily: 'Georgia, Cambria, serif',
                    fontSize: '1.18rem',
                    lineHeight: '1.9',
                  }}
                >
                  {stanza.verses.map((verse) => {
                    const isActive = activeVerseIndex === verse.globalIndex;
                    return (
                      <div
                        key={verse.verseIndex}
                        className={`poem-verse ${isActive ? 'active' : ''}`}
                        style={{
                          margin: '2px 0',
                          cursor: 'pointer',
                        }}
                        onClick={() => {
                          // Al hacer clic, hablar solo este verso
                          if (speakerRef.current) speakerRef.current.stop();
                          const utterance = new SpeechSynthesisUtterance(verse.text);
                          utterance.rate = poema.velocidad;
                          setActiveVerseIndex(verse.globalIndex);
                          utterance.onend = () => setActiveVerseIndex(null);
                          window.speechSynthesis.speak(utterance);
                        }}
                        title="Haz clic para escuchar este verso"
                      >
                        {verse.text}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </section>

          <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--secondary-color)' }}>
              Tip: Puedes pulsar en cualquier verso para escucharlo individualmente.
            </span>
            <button
              type="button"
              className="btn-secondary"
              style={{ color: 'var(--error-color)', borderColor: '#ffcdd2' }}
              onClick={() => {
                if (confirm(`¿Seguro que deseas eliminar el poema "${poema.titulo}"?`)) {
                  onDeletePoem(poema.id);
                  onBack();
                }
              }}
            >
              🗑 Eliminar Poema
            </button>
          </div>
        </>
      )}
    </div>
  );
};
