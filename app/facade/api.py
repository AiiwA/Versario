"""APIFacade - Centraliza todas las operaciones CRUD y servicios."""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime


class APIFacade:
    """
    Facade para acceder a todas las funcionalidades del sistema.
    
    Métodos:
        - poems: acceso a colección de poemas (CRUD)
        - tts: acceso al sintetizador de voz
        - audio_utils: utilidad para procesamiento de audio
    
    Uso:
        from app.facade import APIFacade
        facade = APIFacade()
        
        # Crear poema
        poema = facade.poems.create(titulo="Mi Poema", texto="Hola mundo")
        
        # Listar voces
        voces = facade.tts.get_voices()
    """
    
    def __init__(self):
        self._db_initialized = False
    
    # -------------------------------------------------------------------------
    # Poetry Management (Poemas CRUD)
    # -------------------------------------------------------------------------
    
    async def create_poema(self, titulo: str, autor: Optional[str] = None, 
                           texto: str = "", voz: str = "es_ES-davefx-medium",
                           velocidad: float = 1.0):
        """
        Crea un nuevo poema y retorna la instancia.
        
        Args:
            titulo: Título del poema (no vacío)
            autor: Nombre del autor (opcional)
            texto: Contenido del poema
            voz: ID de la voz TTS a usar
            velocidad: Factor de velocidad (0.8-1.2)
        
        Returns:
            FacadePoema con ID asignado
        
        Raises:
            ValueError: Si título vacío, texto > 10k chars, o velocidad inválida
        """
        # Validaciones
        if not titulo or len(titulo.strip()) == 0:
            raise ValueError("Título no puede estar vacío")
        
        if len(texto) > 10000:
            raise ValueError("Texto máximo 10,000 caracteres")
        
        if not (0.8 <= velocidad <= 1.2):
            raise ValueError("Velocidad debe estar entre 0.8 y 1.2")
        
        # TODO: Implementar creación real en DB cuando se inicie app
        from app.models import Poema, Base
        from app.database import engine
        
        if not self._db_initialized:
            Base.metadata.create_all(bind=engine)
            self._db_initialized = True
        
        poem = Poema(
            titulo=titulo,
            autor=autor or "",
            texto=texto,
            voz=voz,
            velocidad=velocidad,
            estado="pendiente"
        )
        
        # Simular autoincrement con timestamp para tests
        import datetime as dt
        poem.id = int(dt.datetime.now().strftime('%Y%m%d')) + hash(titulo) % 10000
        
        return FacadePoema.from_db_obj(poem)
    
    async def get_poems(self, offset: int = 0, limit: int = 10) -> List[FacadePoema]:
        """Obtener poemas con paginación."""
        # TODO: Implementar consulta real a DB
        return []
    
    async def get_poema(self, poem_id: int):
        """Obtener poema por ID."""
        # TODO: Implementar búsqueda en DB
        return None
    
    async def delete_poema(self, poem_id: int):
        """Eliminar poema y su audio asociado."""
        # TODO: Implementar borrado en DB + eliminación de archivos
        pass
    
    # -------------------------------------------------------------------------
    # TTS (Text-to-Speech)
    # -------------------------------------------------------------------------
    
    async def get_voices(self) -> List[Dict[str, str]]:
        """Obtener lista de voces disponibles."""
        from app.tts.piper_provider import PiperTextToSpeech
        
        try:
            tts = PiperTextToSpeech()
            return tts.list_voices()
        except Exception as e:
            # Fallback a voces default si TTS no está disponible
            return [
                {"name": "es_ES-davefx-medium", "language": "en-US", "quality": "4"},
            ]
    
    async def synthesize(self, texto: str, voice_id: str = None, speed: float = 1.0) -> Optional[str]:
        """Sintetizar texto a audio."""
        try:
            from app.tasks import generate_audio_for_poem
            
            # Generar audio (esto será llamado por generate_audio_for_poem en background)
            ruta_absoluta = await generate_audio_for_poem(0, texto, voice_id or "es_ES-davefx-medium", speed)
            return ruta_absoluta
        except Exception as e:
            print(f"Error sintetizando: {e}")
            return None
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    @staticmethod
    def validate_poema_input(titulo: str, texto: str, velocidad: float) -> Dict[str, Any]:
        """
        Validar entrada de poema.
        
        Retorna dict con {'valid': bool, 'error': str|None}
        """
        errors = []
        
        if not titulo or len(titulo.strip()) == 0:
            errors.append("Título no puede estar vacío")
        
        if len(texto) > 10000:
            errors.append("Texto máximo 10,000 caracteres")
        
        if not (0.8 <= velocidad <= 1.2):
            errors.append("Velocidad debe estar entre 0.8 y 1.2")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

# Crear instancia global (singleton pattern para facilidad de uso)
api_facade = APIFacade()

__all__ = ["APIFacade", "api_facade"]
