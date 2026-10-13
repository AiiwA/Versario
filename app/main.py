"""Versario - Punto de entrada de la aplicación FastAPI."""
import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Absolute imports from project root (for uvicorn run)
from app.database import get_db, init_database
from app.routes.poema import router as poema_router

app = FastAPI(
    title="Versario",
    description="Generador de audio para poemas con TTS en español usando Piper",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_tts_provider():
    """Obtiene el proveedor de síntesis de voz configurado."""
    from app.tts.piper_provider import PiperTextToSpeech
    model_dir = os.getenv("PIPER_MODELS_DIR", "./tts_models")
    
    try:
        tts = PiperTextToSpeech(model_path=model_dir)
        print(f"✅ TTS Provider inicializado: Piper ({model_dir})")
        return tts
    except Exception as e:
        print(f"⚠️ Error inicializando TTS: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Ejecuta al iniciar la aplicación."""
    init_database()
    
    tts = get_tts_provider()
    
    if not hasattr(app, 'state'):
        app.state = {}
    app.state['tts'] = tts
    
    from app.tasks import check_ffmpeg
    try:
        check_ffmpeg()
    except SystemExit as e:
        raise RuntimeError("Error de configuración: ffmpeg no disponible")


def get_poema_db(db):
    """Dependencia para obtener sesión DB con modelo Poema."""
    return db


@app.get("/api/health", tags=["Status"])
async def health_check():
    """Verifica que el servidor está respondiendo."""
    return {"status": "ok", "service": "versario"}


@app.get("/api/voices", tags=["TTS"])
async def list_available_voices():
    """Lista todas las voces disponibles en el sistema TTS."""
    if not hasattr(app.state, 'tts'):
        raise HTTPException(status_code=503, detail="Servicio de voz no disponible")
    
    voices = app.state['tts'].list_voices()
    return voices


app.include_router(poema_router, prefix="/api/poemas", tags=["Poemas"])

@app.get("/", response_class=None)
async def root(request: Request):
    """Renderiza la página principal."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/poema/{poema_id}")
async def poema_detail(request: Request, poema_id: str, db = Depends(get_poema_db)):
    """Renderiza el detalle de un poema con reproductor."""
    from app.models import Poema
    
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    
    if not poem:
        raise HTTPException(status_code=404, detail="Poema no encontrado")
    
    return templates.TemplateResponse("poema.html", {
        "request": request,
        "poema": poem.to_dict() if hasattr(poema, 'to_dict') else poem.__dict__
    })


if __name__ == "__main__":
    import uvicorn
    
    try:
        get_tts_provider()
        print("⚠️  TTS no está configurado. Verifica modelos en tts_models/piper/")
    except Exception:
        pass
    
    uvicorn.run(app, host="0.0.0.0", port=8765, reload=False)
