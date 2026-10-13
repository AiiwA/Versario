"""
Abstracción TTSProvider para Versario.

Define la interfaz que todos los proveedores de síntesis de voz deben implementar.
Esto permite cambiar fácilmente entre Piper, OpenAI TTS o ElevenLabs sin modificar
el resto de la aplicación.

Para usar otro proveedor:
1. Implementar esta clase heredando de TTSProvider
2. Asignarla en app/main.py a tts_provider
3. Asegurar que los métodos list_voices() y synthesize() funcionen correctamente
"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict


class TTSProvider(ABC):
    """
    Proveedor abstracto de síntesis de texto a voz (TTS).
    
    Todos los proveedores deben implementar:
    - synthesize(texto: str, voz: str, velocidad: float) -> str: ruta al archivo WAV generado
    - list_voices() -> List[Dict]: lista de voces disponibles con su información
    """
    
    def __init__(self):
        self.model_dir = os.getenv("PIPER_MODELS_DIR", "./tts_models/piper")
        
    @abstractmethod
    def synthesize(self, texto: str, voz_id: str, velocidad: float) -> str:
        """
        Sintetiza el texto de voz y retorna la ruta al archivo WAV generado.
        
        Args:
            texto: Texto a sintetizar (ya procesado con pausas insertadas)
            voz_id: Identificador de la voz (ej: "es_ES_bahnc", "alloy")
            velocidad: Factor de velocidad (0.8x - 1.2x)
        
        Returns:
            Ruta absoluta al archivo WAV generado, o None en caso de error
            
        Raises:
            RuntimeError: Si el proveedor no está disponible o hay un error crítico
        """
        pass
    
    @abstractmethod
    def list_voices(self) -> List[Dict]:
        """
        Retorna lista de voces disponibles para este proveedor.
        
        Returns:
            Lista de diccionarios con keys: "name", "language", "gender" (opcional), "description"
            
        Ejemplo:
        [
            {"name": "es_ES_bahnc", "language": "es-ES", "gender": "female", "quality": "4"},
            {"name": "es_ES_damek", "language": "es-ES", "gender": "male", "quality": "4"}
        ]
        """
        pass
    
    def validate_text(self, texto: str) -> bool:
        """Valida que el texto tenga contenido."""
        return isinstance(texto, str) and len(texto.strip()) > 0
    
    def sanitize_text(self, texto: str) -> str:
        """Limpia y normaliza el texto para síntesis de voz."""
        # Conservar espacios pero eliminar saltos de línea extraños
        import re
        # Normalizar múltiples espacios en blanco a uno simple
        texto = re.sub(r'\s+', ' ', texto)
        return texto.strip()
