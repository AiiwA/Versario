"""Implementación de TTS usando el CLI de Piper."""

import os
import subprocess
import tempfile
from typing import List, Dict

from .provider import TTSProvider


class PiperTextToSpeech(TTSProvider):
    """Proveedor de síntesis de voz usando el CLI de piper."""
    
    # VOCES: keys must match <lang>_<name> format, e.g. "es_ES-davefx-medium" - basado en rhasspy/piper-voices
    VOCES = {
        "es_ES-davefx-medium": {"language": "en-US", "quality": 4, "gender": None},
        "es_ES-carolina-medium": {"language": "es-ES", "quality": 4, "gender": "female"},
        "es_ES-diego-medium": {"language": "es-ES", "quality": 4, "gender": "male"},
    }
    
    def __init__(self, model_path: str = None):
        self.model_dir = model_path or os.getenv("PIPER_MODELS_DIR", "./tts_models")
        
        if not os.path.exists(self.model_dir):
            raise RuntimeError(f"Directorio de modelos no existe: {self.model_dir}")
    
    def _find_model_for_voice(self, voice_id: str) -> tuple:
        """Encuentra modelo y config para una voz dada."""
        for voice_name, info in self.VOCES.items():
            model_path = os.path.join(self.model_dir, voice_name + ".onnx")
            
            # Verificar si existe el modelo .onnx
            if os.path.exists(model_path):
                return (model_path, voice_name, info)
        
        raise RuntimeError(f"No se encontró modelo para voz '{voice_id}'")
    
    def synthesize(self, texto: str, voice_id: str, speed: float) -> str:
        """Sintetiza texto usando CLI de Piper."""
        model_path, voice_name, info = self._find_model_for_voice(voice_id)
        
        if not os.path.exists(model_path):
            raise RuntimeError(f"Modelo no existe: {model_path}")
        
        # Buscar config.json asociado (normalmente junto al modelo)
        config_search = os.path.join(self.model_dir, voice_name + ".json")
        if not os.path.exists(config_search):
            # Intentar encontrar cualquier .json en el directorio de voces
            import glob
            configs = glob.glob(os.path.join(self.model_dir, f"{voice_name}.json"))
            config_path = configs[0] if configs else None
        else:
            config_path = config_search
        
        # Crear archivo temporal de entrada
        input_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
        input_file.write(texto)
        input_file.close()
        
        output_wav = os.path.join(tempfile.gettempdir(), f"piper_{voice_name}_{os.urandom(4).hex()}.wav")
        
        try:
            # Comando piper CLI
            cmd = [
                "./venv/bin/python", "-m", "piper",
                "-m", model_path,
                "-i", input_file.name,
                "-f", output_wav,
                "-s", "0" if info.get("gender") == "female" else "1"
            ]
            
            # Ajuste de velocidad con --length-scale (1.0 = normal, >1 más rápido)
            if speed > 1.0:
                cmd.extend(["--length-scale", str(1.0 + speed * 0.2)])
            elif speed < 1.0:
                cmd.extend(["--length-scale", str(1.0 + speed * -0.3)])
            
            result = subprocess.run(cmd, capture_output=True, check=True, timeout=60)
            
            if not os.path.exists(output_wav):
                raise RuntimeError("Piper no generó archivo de audio")
            
            # Convertir WAV a MP3 usando ffmpeg
            output_mp3 = output_wav.replace(".wav", ".mp3")
            self._convert_to_mp3(output_wav, output_mp3)
            
            return os.path.abspath(output_mp3)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error en Piper:\n{e.stderr.decode('utf-8', errors='ignore')}")
        finally:
            # Limpiar temporal
            try:
                os.unlink(input_file.name)
            except:
                pass
    
    def _convert_to_mp3(self, wav_path: str, mp3_path: str):
        """Convierte WAV a MP3 con ffmpeg."""
        command = [
            "ffmpeg", "-y",
            "-i", wav_path,
            "-ar", "24000",
            "-acodec", "mp3",
            mp3_path
        ]
        
        subprocess.run(command, capture_output=True, check=True, timeout=60)
    
    def list_voices(self) -> List[Dict]:
        """Retorna voces disponibles con modelos existentes."""
        voices = []
        for voice_name, info in self.VOCES.items():
            model_path = os.path.join(self.model_dir, voice_name + ".onnx")
            if os.path.exists(model_path):
                voices.append({
                    "name": voice_name,
                    "language": info["language"],
                    "quality": str(info["quality"]),
                    "gender": info.get("gender"),
                    "description": f"Voz {info['language']} (calidad-{info['quality']})"
                })
        return voices
