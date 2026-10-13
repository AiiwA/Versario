# Versario - Guía de Instalación Completa

## Requisitos Previos

- **Sistema**: Linux (Ubuntu/Debian recomendado)
- **Python**: 3.11 o superior
- **Herramientas**: `git`, `curl`

## Paso 1: Clonar y Navegar al Directorio

```bash
cd poemtoaudio
```

## Paso 2: Verificar Dependencias del Sistema

```bash
# Instalar ffmpeg (OBLIGATORIO para convertir audio)
sudo apt update && sudo apt install -y ffmpeg

# Crear directorio para modelos Piper
mkdir -p tts_models/piper/tts-spanish-esm

# Crear entorno de trabajo (opcional pero recomendado)
mkdir -p /opt/vsrio
cd /opt/vsrio
```

## Paso 3: Verificar Python y pip

```bash
python3 --version  # Debe ser 3.11+
pip3 --version     # Verificar que pip funciona
```

## Paso 4: Activar Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar
source venv/bin/activate

# Instalar upgrade de pip
pip install --upgrade pip
```

## Paso 5: Instalar Dependencias Python

```bash
cd /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio
pip install -r requirements.txt
```

## Paso 6: Descargar Voz Piper (OBLIGATORIO)

### Opción A: Desde Hugging Face CLI (Recomendado)

```bash
# Si ya tienes huggingface-hub instalado
pip install huggingface-hub

# Descargar modelo en español - Voz femenina (Bahnc)
huggingface-cli download rhasspy/piper-voices \
  es/es_ES/bahnc/tts_spanish-esm_24khz_24hz_fastspeech2_onnx \
  --local-dir tts_models/piper

# Descargar modelo - Voz masculina (Damek)
huggingface-cli download rhasspy/piper-voices \
  es/es_ES/damek/tts_spanish-esm_24khz_24hz_fastspeech2_onnx \
  --local-dir tts_models/piper
```

### Opción B: Descargar Manualmente desde Hugging Face

```bash
# Voz femenina (Bahnc) - clara y expresiva
cd tts_models/piper/tts-spanish-esm/bahnc
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/bahnc/tts_spanish-esm_24khz_24hz_fastspeech2_onnx/bahnc.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/bahnc/tts_spanish-esm_24khz_24hz_fastspeech2_onnx/vocabulary.json
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/bahnc/tts_spanish-esm_24khz_24hz_fastspeech2_onnx/tokenizer.pt

# Voz masculina (Damek) - profunda y autoritaria
cd tts_models/piper/tts-spanish-esm/damek
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/damek/tts_spanish-esm_24khz_24hz_fastspeech2_onnx/damek.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/damek/tts_spanish-esm_24khz_24hz_fastspeech2_onnx/vocabulary.json
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/damek/tts_spanish-esm_24khz_24hz_fastspeech2_onnx/tokenizer.pt

# Retornar al directorio principal
cd ..
```

## Paso 7: Verificar Instalación

```bash
# Verificar que ffmpeg funciona
ffmpeg -version | head -1

# Crear la base de datos
python3 -c "from app.database import init_database; print('Base de datos inicializada')"

# Listar voces disponibles
cd /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
curl http://localhost:8001/api/voices

# Detener servidor (Ctrl+C)
```

## Paso 8: Ejecutar el Servidor

### Modo Desarrollo (con hot-reload)

```bash
cd /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio

# Activar entorno virtual si usas uno
source venv/bin/activate

# Ejecutar con uvicorn (incluye reloaded automático)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Modo Producción (sin reload, más rápido)

```bash
cd /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio

# Opción A: uvicorn standalone
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Opción B: gunicorn (requiere instalar)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

## Paso 9: Acceder a la Aplicación

Abre tu navegador y navega a:

**http://localhost:8000**

## Comandos de Utilidad

### Crear Poemas Ejemplo (si existen modelos)

```bash
cd /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio
python3 scripts/crear_poemas_ejemplo.py
```

### Ver Estado del Servidor

```bash
curl http://localhost:8000/api/health
```

### Ver Poemas en BD

```bash
sqlite3 /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio/poemas.db "SELECT id, titulo, estado FROM poemas;"
```

## Solución de Problemas

### Error: "ffmpeg no encontrado"

```bash
sudo apt install ffmpeg
```

### Error: "Piper not installed"

```bash
pip install piper-tts
```

### Error: "Voz no encontrada"

Verifica que los modelos están en `tts_models/piper/` y revisa el output de `/api/voices`.

### Error: "No hay voz configurada"

Crea un archivo `.env`:

```bash
mkdir -p ~/.copilot/session-state/fe946f4d-8b27-49de-99be-c31268ae7ca2/env && touch .env
echo "PIPER_MODELS_DIR=/home/awiwa/Documentos/GitHub/Prueba/poemtoaudio/tts_models/piper" >> .env
```

## Estructura de Archivos de Audio

Los archivos MP3 generados se guardan en `/tmp/` con un nombre único (UUID) y duración máxima de 1 hora.

Para persistencia permanente, configura una ruta alternativa en `tasks.py`.

---

**¡Listo!** Tu servidor Versario está corriendo. Abre http://localhost:8000
