"""Rutas API Versario."""
import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Poema

router = APIRouter()


class CreatePoemaRequest(BaseModel):
    titulo: str
    autor: str | None = None
    texto: str
    voz: str
    velocidad: float = 1.0


class PoemaResponse(BaseModel):
    id: int
    titulo: str  
    autor: str | None
    texto: str
    ruta_audio: str | None
    voz: str
    velocidad: float
    estado: str
    creado_en: datetime
    
    class Config:
        orm_mode = True  # Usar attrs del modelo ORM


@router.post("/", response_model=PoemaResponse, status_code=201)
async def crear_poema(request: CreatePoemaRequest, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    if not request.titulo or len(request.titulo.strip()) == 0:
        raise HTTPException(status_code=422, detail="Título no puede estar vacío")
    
    if len(request.texto) > 10000:
        raise HTTPException(status_code=400, detail="Texto máximo 10,000 caracteres")
    
    velocity = request.velocidad
    if not (0.8 <= velocity <= 1.2):
        raise HTTPException(status_code=422, detail="Velocidad debe estar entre 0.8 y 1.2")
    
    nuevo_poema = Poema(
        titulo=request.titulo,
        autor=request.autor or "",
        texto=request.texto,
        voz=request.voz or "es_ES-davefx-medium",
        velocidad=velocity,
        estado="pendiente"
    )
    
    db.add(nuevo_poema)
    db.commit()
    db.refresh(nuevo_poema)
    
    from app.tasks import generate_audio_for_poem
    
    if background_tasks is None:
        background_tasks = BackgroundTasks()
    
    ruta_relativa = f"/audio/poema_{nuevo_poema.id}.mp3"
    
    background_tasks.add_task(
        generate_audio_for_poem,
        nuevo_poema.id,
        request.texto,
        request.voz or "es_ES-davefx-medium",
        velocity,
        db_path="poemas.db"
    )
    
    nuevo_poema.estado = "generando"
    db.commit()
    
    return nuevo_poema


@router.get("/", response_model=list[PoemaResponse])
async def listar_poemas(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    poems = db.query(Poema).order_by(Poema.creado_en.desc()).offset(offset).limit(limit).all()
    return poems


@router.get("/{poema_id}", response_model=PoemaResponse)
async def obtener_poema(poema_id: int, db: Session = Depends(get_db)):
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    if not poem:
        raise HTTPException(status_code=404, detail="Poema no encontrado")
    return poem


@router.delete("/{poema_id}", status_code=204)
async def eliminar_poema(poema_id: int, db: Session = Depends(get_db)):
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    if not poem:
        raise HTTPException(status_code=404, detail="Poema no encontrado")
    
    if poem.ruta_audio and os.path.exists(poem.ruta_audio):
        try:
            os.unlink(poem.ruta_audio)
        except Exception as e:
            pass
    
    db.delete(poem)
    db.commit()


@router.get("/{poema_id}/audio", response_class=FileResponse)
async def obtener_audio(poema_id: int, db: Session = Depends(get_db)):
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    
    if not poem or not poem.ruta_audio or not os.path.exists(poem.ruta_audio):
        raise HTTPException(status_code=404, detail="Audio no disponible")
    
    return FileResponse(
        poem.ruta_audio, 
        media_type="audio/mpeg"
    )

