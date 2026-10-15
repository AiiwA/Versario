import React from 'react';
import { ArrowLeft } from 'lucide-react';

interface HeaderProps {
  onGoHome?: () => void;
  showBack?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onGoHome, showBack }) => (
  <header className="rise mb-12 md:mb-16">
    <div className="flex h-10 items-center justify-between">
      <span className="text-sm font-semibold tracking-[0.2em] text-amber uppercase">Versario</span>
      {showBack && onGoHome && (
        <button onClick={onGoHome} className="btn btn-ghost !py-2 text-sm" title="Volver al inicio">
          <ArrowLeft size={16} aria-hidden /> Volver
        </button>
      )}
    </div>
    <h1 className="mt-8 max-w-4xl font-serif text-4xl leading-[1.1] text-balance md:text-6xl">
      Tus poemas, dichos en voz alta, con sus silencios.
    </h1>
    <p className="mt-5 max-w-2xl text-lg text-muted">
      Escribe o pega un poema y escúchalo con pausas naturales entre versos y estrofas.
    </p>
  </header>
);
