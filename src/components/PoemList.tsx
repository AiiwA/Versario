import React from 'react';
import { Play, Trash2 } from 'lucide-react';
import { Poema } from '../types/poema';

interface PoemListProps {
  poems: Poema[];
  onSelectPoem: (poem: Poema) => void;
  onDeletePoem: (id: number) => void;
}

const formatDate = (iso: string) => {
  const d = new Date(iso);
  return isNaN(d.getTime())
    ? ''
    : d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' });
};

export const PoemList: React.FC<PoemListProps> = ({ poems, onSelectPoem, onDeletePoem }) => {
  if (poems.length === 0) return null;

  return (
    <section className="mt-24 md:mt-32">
      <h3 className="font-serif text-3xl">
        Tu biblioteca <span className="text-muted">({poems.length})</span>
      </h3>

      <ul className="mt-8 grid grid-flow-dense gap-4 sm:grid-cols-2">
        {poems.map((poem, i) => (
          <li
            key={poem.id}
            className={`rise group relative flex flex-col justify-between overflow-hidden rounded-3xl border border-line bg-panel p-6 transition-colors duration-500 hover:border-amber/60 ${
              // el primero ocupa todo el ancho; si el total es impar, el último también, sin huecos
              i === 0 || (i === poems.length - 1 && poems.length % 2 === 0) ? 'sm:col-span-2' : ''
            }`}
            style={{ animationDelay: `${Math.min(i, 8) * 60}ms` }}
          >
            <button
              type="button"
              onClick={() => onSelectPoem(poem)}
              className="text-left after:absolute after:inset-0 after:content-['']"
              aria-label={`Abrir ${poem.titulo}`}
            >
              <span className="block font-serif text-2xl transition-transform duration-500 group-hover:translate-x-1">
                {poem.titulo}
              </span>
              <span className="mt-2 block text-sm text-muted">
                {poem.autor || 'Anónimo'} · {formatDate(poem.creado_en)}
              </span>
            </button>

            <div className="mt-6 flex items-center justify-between">
              <span className="inline-flex items-center gap-2 text-sm font-medium text-amber">
                <Play size={14} aria-hidden /> {poem.velocidad}x · {poem.estado}
              </span>
              <button
                type="button"
                className="relative z-10 rounded-full p-2 text-muted transition-colors hover:bg-white/5 hover:text-danger"
                onClick={() => {
                  if (confirm(`¿Eliminar el poema "${poem.titulo}"?`)) onDeletePoem(poem.id);
                }}
                aria-label={`Eliminar ${poem.titulo}`}
              >
                <Trash2 size={18} aria-hidden />
              </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
};
