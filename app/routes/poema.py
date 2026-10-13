"""Rutas API Versario."""
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import text
import uuid
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
    id: str
    titulo: str  
    autor: str | None
    texto: str
    ruta_audio: str | None
    voz: str
    velocidad: float
    estado: str
    creado_en: str


@router.post("/", response_model=PoemaResponse, status_code=201)
async def crear_poema(request: CreatePoemaRequest, db: Session = Depends(get_db)):
    try:
        if len(request.texto) > 10000:
            raise HTTPException(status_code=400, detail="Texto máximo 10,000 caracteres")
        
        poem_id = f"{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4]}"
        
        db.add(Poema(
            id=poem_id,
            titulo=request.titulo,
            autor=request.autor or "",
            texto=request.texto,
            voz=request.voz or "es_ES-davefx-medium",
            velocidad=float(request.velocidad) if hasattr(request, 'velocidad') else request.velocidad,
            estado="pending"
        ))
        db.commit()
        
        poem = db.query(Poema).filter(Poema.id == poem_id).first()
        return PoemaResponse(**poem.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[PoemaResponse])
async def listar_poemas(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    return [PoemaResponse(**p.__dict__) for p in db.query(Poema).offset(offset).limit(limit).all()]


@router.get("/{poema_id}", response_model=PoemaResponse)
async def obtener_poema(poema_id: str, db: Session = Depends(get_db)):
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    if not poem:
        raise HTTPException(status_code=404, detail="Poema no encontrado")
    return PoemaResponse(**poem.__dict__)


@router.delete("/{poema_id}", status_code=204)
async def eliminar_poema(poema_id: str, db: Session = Depends(get_db)):
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    if not poem:
        raise HTTPException(status_code=404, detail="Poema no encontrado")
    
    if poem.ruta_audio and os.path.exists(str(poem.ruta_audio)):
        try:
            os.unlink(str(poem.ruta_audio))
        except Exception as e:
            pass
    
    db.delete(poema)
    db.commit()


@router.get("/{poema_id}/audio", response_class=str)
async def obtener_audio(poema_id: str, db: Session = Depends(get_db)):
    from fastapi.responses import FileResponse
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    if not poem or not poem.ruta_audio or not os.path.exists(str(poem.ruta_audio)):
        raise HTTPException(status_code=404, detail="Audio no disponible")
    return FileResponse(str(poem.ruta_audio), media_type="audio/mpeg")
