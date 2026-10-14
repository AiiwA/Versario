import React, { useState, useEffect } from 'react';
import { Poema, CreatePoemaDTO } from './types/poema';
import {
  getStoredPoems,
  savePoem,
  updatePoemStatus,
  deletePoem,
  getPoemById,
} from './services/storageService';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { PoemForm } from './components/PoemForm';
import { PoemList } from './components/PoemList';
import { PoemDetail } from './components/PoemDetail';
import { ErrorModal } from './components/ErrorModal';

export const App: React.FC = () => {
  const [poems, setPoems] = useState<Poema[]>([]);
  const [selectedPoemId, setSelectedPoemId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const stored = getStoredPoems();
    setPoems(stored);
  }, []);

  const handleCreatePoem = (dto: CreatePoemaDTO) => {
    setIsSubmitting(true);
    try {
      const newPoem = savePoem(dto);
      setPoems(getStoredPoems());
      setSelectedPoemId(newPoem.id);
    } catch {
      setErrorMessage('Error al crear el poema en almacenamiento local.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectPoem = (poem: Poema) => {
    setSelectedPoemId(poem.id);
  };

  const handleUpdatePoem = (id: number, estado: Poema['estado'], extra?: Partial<Poema>) => {
    updatePoemStatus(id, estado, extra);
    setPoems(getStoredPoems());
  };

  const handleDeletePoem = (id: number) => {
    deletePoem(id);
    const updated = getStoredPoems();
    setPoems(updated);
    if (selectedPoemId === id) {
      setSelectedPoemId(null);
    }
  };

  const selectedPoem = selectedPoemId !== null ? getPoemById(selectedPoemId) : null;

  return (
    <div className="container">
      <Header
        showBack={selectedPoemId !== null}
        onGoHome={() => setSelectedPoemId(null)}
      />

      <main className="app-main">
        {selectedPoem ? (
          <PoemDetail
            poema={selectedPoem}
            onBack={() => setSelectedPoemId(null)}
            onUpdatePoem={handleUpdatePoem}
            onDeletePoem={handleDeletePoem}
            onError={(msg) => setErrorMessage(msg)}
          />
        ) : (
          <>
            <PoemForm
              onSubmit={handleCreatePoem}
              isSubmitting={isSubmitting}
              onError={(msg) => setErrorMessage(msg)}
            />
            <PoemList
              poems={poems}
              onSelectPoem={handleSelectPoem}
              onDeletePoem={handleDeletePoem}
            />
          </>
        )}
      </main>

      <Footer />

      <ErrorModal
        isOpen={errorMessage !== null}
        message={errorMessage || ''}
        onClose={() => setErrorMessage(null)}
      />
    </div>
  );
};

export default App;
