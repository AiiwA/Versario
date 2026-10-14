"""
Modelos SQLAlchemy para Versario.
Define la entidad Poema con sus campos y relaciones.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Poema(Base):
    """
    Modelo para un poema guardado en la base de datos.
    
    Campos:
    - id: identificador único autoincremental
    - titulo: título del poema (obligatorio)
    - autor: nombre del autor (opcional)
    - texto: contenido completo del poema (obligatorio)
    - ruta_audio: ruta al archivo MP3 generado
    - voz: ID de la voz TTS usada
    - velocidad: factor de velocidad (0.8x a 1.2x)
    - estado: pendiente/generando/listo/error
    - creado_en: timestamp de creación
    """
    __tablename__ = "poemas"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    autor = Column(String(200), nullable=True)  # Opcional
    texto = Column(Text, nullable=False)
    
    # Referencia al archivo de audio generado (ruta relativa)
    ruta_audio = Column(String(500), nullable=True)
    
    # Configuración del audio
    voz = Column(String(100), nullable=False)  # ID o nombre de la voz TTS
    velocidad = Column(Float, default=1.0)  # Factor de velocidad (0.8 - 1.2)
    
    # Estado de la generación
    estado = Column(String(20), default="pendiente", nullable=False)  # pendiente | generando | listo | error
    
    # Timestamps
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convierte el poema a diccionario para JSON responses."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "texto": self.texto,
            "ruta_audio": self.ruta_audio,
            "voz": self.voz,
            "velocidad": self.velocidad,
            "estado": self.estado,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None
        }

    def __repr__(self):
        return f"<Poema(id={self.id}, titulo='{self.titulo[:30]}...', estado='{self.estado}')>"
