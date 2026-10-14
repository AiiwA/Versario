import React from 'react';

interface HeaderProps {
  onGoHome?: () => void;
  showBack?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onGoHome, showBack }) => {
  return (
    <header className="app-header">
      {showBack && onGoHome && (
        <button
          onClick={onGoHome}
          className="back-link text-white hover:text-white"
          style={{
            position: 'absolute',
            left: '20px',
            top: '20px',
            color: 'white',
            background: 'rgba(255, 255, 255, 0.2)',
            padding: '6px 14px',
            borderRadius: '6px',
          }}
          title="Volver al inicio"
        >
          ← Volver
        </button>
      )}
      <h1>🎵 Versario</h1>
      <p>Convierte tus poemas en audio con síntesis de voz</p>
    </header>
  );
};
