# Versario - Generador de Audio para Poemas 🎶

Convierte tus poemas en audio narrado con Inteligencia Artificial usando **Piper TTS** (local, gratuito, sin API calls).

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv3-green.svg)](LICENSE)

---

## ✨ Características

- 📝 **Sube poemas** con título, autor y texto completo
- 🎙️ **Audio natural en español** usando TTS local de Piper
- ⏱️ **Pausas inteligentes**: 400ms entre versos, 1000ms entre estrofas
- 📥 **Descarga MP3** de alta calidad  
- 🎚️ **Control de velocidad**: 0.8x a 1.2x
- 🔄 **Generación asíncrona**: no bloquea la página

---

## 🚀 Instalación Rápida

```bash
# 1. Clonar repo
cd poemtoaudio

# 2. Python 3.11+ requerido
python3 --version  # ≥ 3.11

# 3. Entorno virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependencias
pip install --upgrade pip
pip install fastapi uvicorn[standard] sqlalchemy aiosqlite \
           pydub piper-phash-models python-dateutil jinja2

# 5. Descargar modelo Piper español (61MB)
mkdir -p tts_models/es_ES-davefx-medium
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/tts_spanish-esm_24khz_24hz_fastspeech2_onnx/model.onnx \
   -O tts_models/es_ES-davefx-medium/model.onnx

# 6. Instalar ffmpeg (si falta)
sudo apt install ffmpeg

# 7. ¡Listo! Arrancar servidor
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Abre http://localhost:8000 en tu navegador 🎉

---

## 📁 Estructura del Proyecto

```
poemtoaudio/
├── app/                        # Backend FastAPI
│   ├── main.py                 # Entry point + TTS config
│   ├── models.py               # ORM Poema model
│   ├── database.py             # SQLite engine & session
│   └── routes/poema.py         # API endpoints
│
├── app/tts/                    # TTS providers (ABC + Piper)
│   ├── provider.py             # TTSProvider abstract class
│   └── piper_provider.py       # PiperTextToSpeech impl
│
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Main page + form
│   └── poema.html              # Detail + audio player
│
├── static/                     # CSS, JS (vanilla)
├── audio/                      # Output MP3s
├── tts_models/                 # Piper models (~61MB)
```

---

## 🎛️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/poemas/` | Create new poem |
| GET | `/api/poemas/` | List poems (paginable) |
| GET | `/api/poemas/{id}` | Get poem details |
| DELETE | `/api/poemas/{id}` | Delete poem + audio |
| GET | `/api/poemas/{id}/audio` | Serve MP3 stream |

**Ejemplo crear poema:**
```bash
curl -X POST http://localhost:8000/api/poemas/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Mi Primer Poema",
    "autor": "Tu Nombre",
    "texto": "Hola mundo\n\nEsta es una segunda estrofa vacía",
    "voz": "es_ES-davefx-medium",
    "velocidad": 1.0
  }'
```

---

## 🎤 Modelos TTS Disponibles

| Model | Gender | Language | Size |
|-------|--------|----------|------|
| es_ES-davefx-medium | Unisex | Español (España) | ~61MB |
| en_US-lessac-medium | Female/Male | Inglés (US) | ~50MB |
| Más voces en: https://huggingface.co/rhasspy/piper-voices/tree/main |

**Instalar modelo:**
```bash
# Desde Hugging Face CLI (recomendado)
pip install huggingface-hub
huggingface-cli download rhasspy/piper-voices \
  es/es_ES/davefx/tts_spanish-esm_24khz_24hz_fastspeech2_onnx \
  --local-dir tts_models

# O descarga directa:
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/tts_spanish-esm_24khz_24hz_fastspeech2_onnx/model.onnx \
   -O tts_models/es_ES-davefx-medium/model.onnx
```

---

## 🔧 Configuración Avanzada

### Variables de entorno

```bash
# Ruta alternativa a modelos (si no es ./tts_models)
export PIPER_MODELS_DIR="/home/user/piper_models"
export PIPER_VOICE="es_ES-davefx-medium"
```

### Cambiar velocidad de generación
```python
# En app/routes/poema.py crear_poema():
velocidad = float(request.velocidad)  # 0.8 - 1.2x
db.add(Poema(..., velocidad=velocidad))
```

---

## 🐛 Troubleshooting

**Error: "ffmpeg no encontrado"**
```bash
sudo apt install ffmpeg
```

**Error: "Voz no encontrada"**
- Verifica que `tts_models/es_ES-davefx-medium/model.onnx` exista (61MB)
- Lista voces disponibles: http://localhost:8000/api/voices

**Error: SQLAlchemy INSERT failure**
- Usa ORM `db.add(Poema(...))` no `text()` con params en Python 3.14+
- Revisa app/routes/poema.py linea ~50

---

## 📄 Licencia

GPLv3 - Libre para uso educativo y personal

---

**Versión:** 1.0  
**Última actualización:** Octubre 2026  
**Estado:** Alpha (funcional, necesita polish)
