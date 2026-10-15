import React, { useEffect } from 'react';

interface ErrorModalProps {
  isOpen: boolean;
  message: string;
  onClose: () => void;
}

export const ErrorModal: React.FC<ErrorModalProps> = ({ isOpen, message, onClose }) => {
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="rise w-full max-w-md rounded-3xl border border-line bg-panel p-8"
        onClick={(e) => e.stopPropagation()}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="error-title"
      >
        <h3 id="error-title" className="font-serif text-2xl text-danger">Algo salió mal</h3>
        <p className="mt-3 whitespace-pre-line text-muted">{message}</p>
        <button onClick={onClose} className="btn btn-primary mt-6" autoFocus>Cerrar</button>
      </div>
    </div>
  );
};
