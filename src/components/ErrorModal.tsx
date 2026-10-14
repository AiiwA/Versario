import React from 'react';

interface ErrorModalProps {
  isOpen: boolean;
  message: string;
  onClose: () => void;
}

export const ErrorModal: React.FC<ErrorModalProps> = ({
  isOpen,
  message,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <h3>Error</h3>
        <p style={{ whiteSpace: 'pre-line', color: '#555', margin: '12px 0' }}>
          {message}
        </p>
        <button onClick={onClose}>Cerrar</button>
      </div>
    </div>
  );
};
