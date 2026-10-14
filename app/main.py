"""Versario - Punto de entrada de la aplicación FastAPI."""
import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Absolute imports from project root (for uvicorn run)
from app.database import get_db, init_database
from app.routes.poema import router as poema_router

app = FastAPI(
    title="Versario",
    description="Generador de audio para poemas con TTS en español usando Piper",
    version="1.0.0"
)

# Montar carpeta de estáticos (si existe)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


def get_poema_db(db: Session = Depends(get_db)):
    """Dependencia para obtener sesión DB con modelo Poema."""
    return db


@app.get("/api/health", tags=["Status"])
async def health_check():
    """Verifica que el servidor está respondiendo."""
    return {"status": "ok", "service": "versario"}


@app.get("/api/voices", tags=["TTS"])
async def list_available_voices(db: Session = Depends(get_poema_db)):
    """Lista todas las voces disponibles en el sistema TTS."""
    from app.tts.piper_provider import PiperTextToSpeech
    
    try:
        tts = PiperTextToSpeech()
        voices = tts.list_voices()
        return voices
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error listando voces: {e}")


@app.get("/", response_class=None)
async def root(request: Request):
    """Renderiza la página principal."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/poema/{poema_id}")
async def poema_detail(request: Request, poema_id: int, db = Depends(get_poema_db)):
    """Renderiza el detalle de un poema con reproductor."""
    from app.models import Poema
    
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    
    if not poem:
        raise HTTPException(status_code=404, detail="Poema no encontrado")
    
    return templates.TemplateResponse("poema.html", {
        "request": request,
        "poema": poem.to_dict() if hasattr(poem, 'to_dict') else poem.__dict__
    })


# Incluir rutas API
from app.routes import poema_router
app.include_router(poema_router, prefix="/api/poemas", tags=["Poemas"])

