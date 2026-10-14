"""Models facade - Abstrae acceso a DB y entidades."""

from typing import Optional, List
from datetime import datetime
import uuid


class FacadePoema:
    """Modelo simplificado de Poema para uso en frontend/API."""
    
    def __init__(self, id: int, titulo: str, autor: Optional[str] = None, 
                  texto: str = "", ruta_audio: Optional[str] = None,
                  voz: str = "", velocidad: float = 1.0, 
                  estado: str = "pending", creado_en: datetime = None):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.texto = texto
        self.ruta_audio = ruta_audio
        self.voz = voz
        self.velocidad = velocidad
        self.estado = estado
        self.creado_en = creado_en or datetime.utcnow()
    
    def to_dict(self):
        """Convertir a dict para JSON responses."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "texto": self.texto,
            "ruta_audio": self.ruta_audio,
            "voz": self.voz,
            "velocidad": self.velocidad,
            "estado": self.estado,
            "creado_en": self.creado_en.isoformat() if hasattr(self.creado_en, 'isoformat') else str(self.creado_en)
        }

    @classmethod
    def from_db_obj(cls, poem):
        """Crear FacadePoema desde modelo SQLAlchemy."""
        return cls(
            id=poem.id,
            titulo=poem.titulo,
            autor=poem.autor,
            texto=poem.texto,
            ruta_audio=poem.ruta_audio,
            voz=poem.voz,
            velocidad=poem.velocidad,
            estado=poem.estado,
            creado_en=poem.creado_en
        )

    @classmethod
    def create(cls, titulo: str, autor: Optional[str] = None, texto: str = "", 
               voz: str = "", velocidad: float = 1.0):
        """Crear nuevo poema con ID auto-incremental."""
        return cls(
            id=0,  # Se asignará en DB
            titulo=titulo,
            autor=autor,
            texto=texto,
            ruta_audio=None,
            voz=voz,
            velocidad=velocidad,
            estado="pending"
        )

    def to_api_dict(self):
        """Dict optimizado para API responses."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor or "",
            "texto": self.texto[:500] + "..." if len(self.texto) > 500 else self.texto,
            "ruta_audio": self.ruta_audio,
            "voz": self.voz,
            "velocidad": f"{self.velocidad:.1f}x",
            "estado": self.estado,
            "creado_en": self.creado_en.isoformat() if hasattr(self.creado_en, 'isoformat') else str(self.creado_en)
        }
