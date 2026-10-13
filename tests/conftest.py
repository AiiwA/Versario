"""
Conjunto de fixtures para pytest - Versario Test Suite
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# --- MOCK SETUP (must happen before any app import) ---
class MockPiperTextToSpeech:
    """Mock que solo lista voces, no genera audio."""
    def __init__(self, model_path):
        self.model_dir = model_path
        
    def list_voices(self):
        return [{"name": "es_ES-davefx-medium", "language": "en-US", "quality": "4", "gender": None}]
    
    def synthesize(self, texto, voice_id, speed):
        raise NotImplementedError("No genera audio - usa fake_tts fixture")


def reset_app_modules():
    """Resetea todos los módulos de app para reiniciar con mocks."""
    modules_to_clean = [k for k in sys.modules.keys() if k.startswith('app') or 'piper' in k]
    for mod_name in modules_to_clean:
        del sys.modules[mod_name]


# Configuramos el mock DEPENDIENDO del test que se ejecute
def pytest_collection_modifyitems(items):
    """Modifica cada item para asignar el fixture correcto."""
    pass  # No hacemos nada aquí, fixtures son per-test automáticamente


@pytest.fixture(scope="function")
def audio_dir():
    """Carpeta temporal para archivos de audio."""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture(scope="function")
def db_tempo_with_tables():
    """Base de datos SQLite temporal con tablas reales."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker, declarative_base
    from app.models import Poema
    
    temp_db = Path(tempfile.mktemp(suffix=".db"))
    
    engine_test = create_engine(
        f"sqlite:///{temp_db}", 
        connect_args={"check_same_thread": False}
    )
    
    BaseTest = declarative_base()
    # Crear tabla poemas (y otras si son necesarias)
    Poema.__table__.create(engine_test, checkfirst=True)
    
    SessionTest = sessionmaker(bind=engine_test)
    
    def get_session():
        return SessionTest()
    
    yield get_session
    
    if temp_db.exists():
        temp_db.unlink()
    
    engine_test.dispose()


@pytest.fixture(scope="function") 
def client(db_tempo_with_tables):
    """Client de FastAPI con DB temporal."""
    # IMPORTANTE: setup_piper_mock SE DEBE HACER ANTES de importar app.main
    
    reset_app_modules()  # Limpieza previa
    
    import types
    piper_provider_mock = types.ModuleType('app.tts.piper_provider')
    
    class MockPiperReal:
        def __init__(self, model_path):
            self.model_dir = model_path
            
        def list_voices(self):
            return [{"name": "es_ES-davefx-medium", "language": "en-US", "quality": "4", "gender": None}]
    
    piper_provider_mock.PiperTextToSpeech = MockPiperReal
    sys.modules['app.tts.piper_provider'] = piper_provider_mock
    
    piper_tts_mock = types.ModuleType('piper_tts')
    piper_tts_mock.OnnxTTS = None
    sys.modules['piper_tts'] = piper_tts_mock
    
    from app.database import get_db as original_get_db
    from app.main import app
    
    app.dependency_overrides[original_get_db] = db_tempo_with_tables
    
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
        
        # Limpieza final
        for mod_name in ['app.tts.piper_provider', 'piper_tts', 'app.main']:
            if mod_name in sys.modules:
                del sys.modules[mod_name]


@pytest.fixture(scope="function")
def fake_tts(audio_dir):
    """FakeTTSProvider que genera WAVs de silencio."""
    class FakePiperTextToSpeech:
        def __init__(self, model_path="./tts_models"):
            self.model_dir = model_path
            
        def list_voices(self):
            return [{"name": "es_ES-davefx-medium", "language": "en-US", "quality": "4", "gender": None}]
        
        def synthesize(self, texto, voice_id, speed):
            import wave
            import random
            
            wav_path = Path(audio_dir) / f"fake_{len(texto)}_chars.wav"
            duration_seconds = max(0.5, len(texto) * 0.03)
            
            sample_rate = 44100
            num_frames = int(duration_seconds * sample_rate)
            
            with wave.open(str(wav_path), 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                for _ in range(num_frames):
                    sample = random.randint(-32768, 32767)
                    wav_file.writeframes(bytes([sample & 0xFF, (sample >> 8) & 0xFF]))
            
            mp3_path = wav_path.with_suffix('.mp3')
            
            cmd = ["ffmpeg", "-y", "-i", str(wav_path), 
                   "-ar", "24000", "-acodec", "mp3", str(mp3_path)]
            
            import subprocess
            subprocess.run(cmd, capture_output=True, check=True)
            
            return f"/audio/{wav_path.name}"

    return FakePiperTextToSpeech()


@pytest.fixture(scope="function")
def voice_exists(tmp_path):
    """Crea un archivo .onnx falso para simular voz disponible."""
    model_file = tmp_path / "es_ES-davefx-medium.onnx"
    model_file.write_bytes(b"fake onnx data")
    return model_file

