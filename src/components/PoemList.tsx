import React from 'react';
import { Poema } from '../types/poema';

interface PoemListProps {
  poems: Poema[];
  onSelectPoem: (poem: Poema) => void;
  onDeletePoem: (id: number) => void;
}

export const PoemList: React.FC<PoemListProps> = ({
  poems,
  onSelectPoem,
  onDeletePoem,
}) => {
  if (poems.length === 0) {
    return null;
  }

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '';
    }
  };

  return (
    <section style={{ marginTop: '36px', borderTop: '2px solid #f0f0f0', paddingTop: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ color: 'var(--secondary-color)', fontSize: '1.25rem' }}>
          Poemas Guardados ({poems.length})
        </h3>
      </div>

      <div style={{ display: 'grid', gap: '12px' }}>
        {poems.map((poem) => (
          <div
            key={poem.id}
            style={{
              padding: '16px 20px',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              backgroundColor: '#fbfcfd',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
              transition: 'all 0.2s',
            }}
          >
            <div
              style={{ cursor: 'pointer', flex: 1 }}
              onClick={() => onSelectPoem(poem)}
              title="Abrir reproductor y texto"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <strong style={{ fontSize: '1.05rem', color: '#1e293b' }}>
                  {poem.titulo}
                </strong>
                <span className={`status-badge status-${poem.estado}`}>
                  {poem.estado}
                </span>
              </div>
              <div style={{ fontSize: '0.88rem', color: 'var(--secondary-color)', marginTop: '4px' }}>
                {poem.autor ? `Por ${poem.autor}` : 'Anónimo'} • {formatDate(poem.creado_en)} • Voz: {poem.voz} ({poem.velocidad}x)
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button
                type="button"
                className="btn-primary"
                style={{ padding: '8px 14px', fontSize: '0.9rem' }}
                onClick={() => onSelectPoem(poem)}
                title="Reproducir poema"
              >
                ▶ Escuchar
              </button>
              <button
                type="button"
                className="btn-secondary"
                style={{
                  padding: '8px 12px',
                  color: 'var(--error-color)',
                  borderColor: '#ffcdd2',
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm(`¿Eliminar el poema "${poem.titulo}"?`)) {
                    onDeletePoem(poem.id);
                  }
                }}
                title="Eliminar poema"
              >
                🗑
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
