# Versario - Generador de Poemas Audio

Versario convierte poemas escritos en texto a archivos de audio usando síntesis de voz (TTS) con Piper, ejecutándose localmente sin dependencias de API externas.

## ✨ Características

- 🎯 **Conversión de texto a audio** usando Piper TTS local
- 📝 **Soporte para múltiples estrofas y versos** con pausas naturales
- 🚀 **Generación asíncrona de audio** sin bloquear la interfaz
- 🌐 **Frontend vanilla JS** - Sin frameworks, fácil de desplegar
- 🔒 **Todo local** - No requiere conexión a internet
- ♿ **Accesible** - Reproductor web integrado

## 📋 Requerimientos

```bash
# Sistema
- Python 3.11+
- SQLite3 (incluido)
- ffmpeg instalado
- Piper CLI instalado

# Virtualenv recomendado
python3 -m venv venv
source venv/bin/activate
```

## 📦 Instalación

```bash
cd poemtoaudio

# Crear entorno virtual (si no existe)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias de Python
pip install fastapi uvicorn sqlalchemy pydantic jinja2 aiosqlite

# Verificar Piper CLI instalado
python -m pip show piper-cli || echo "Instalar pip install piper-tts"

# Descargar modelo TTS (es_ES-davefx-medium, ~60MB)
python scripts/descargar_modelo.py
```

## 🚀 Ejecutar Servidor

```bash
cd /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8765
```

El servidor estará disponible en: **http://localhost:8765**

## 📖 Uso

### Crear Poema

1. Abre http://localhost:8765
2. Llena el formulario:
   - Título (obligatorio)
   - Texto del poema (usar doble salto de línea para separar estrofas)
   - Velocidad (0.8 - 1.2x, default 1.0 = normal)
   - Voz (selecciona de la lista desplegable)
3. Haz clic en "Crear Poema"
4. Espera a que se genere el audio (~10-30s según longitud)
5. Elige reprodúcir o descargar el MP3

### API REST

```bash
# Listar voces disponibles
curl http://localhost:8765/api/voices

# Crear poema (respeta validation del backend)
curl -X POST http://localhost:8765/api/poemas/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Mi Poema",
    "autor": "Usuario",
    "texto": "Hola mundo\n\nAdios amigo",
    "voz": "es_ES-davefx-medium",
    "velocidad": 1.0
  }'

# Obtener poema por ID (incluye estado y ruta_audio)
curl http://localhost:8765/api/poemas/{id}

# Reproducir audio
curl http://localhost:8765/api/poemas/{id}/audio -o out.mp3

# Eliminar poema (+ archivo de audio si existe)
curl -X DELETE http://localhost:8765/api/poemas/{id}
```

## 🏗️ Estructura del Proyecto

```
poemtoaudio/
├── app/
│   ├── facade/           # API centralizada (nuevo)
│   │   ├── __init__.py
│   │   ├── api.py        # FacadeAPI con métodos CRUD y servicios
│   │   └── models.py     # FacadePoema simplificado
│   ├── routes/
│   │   ├── __init__.py
│   │   └── poema.py      # Endpoints FastAPI (POST, GET, DELETE)
│   ├── tts/
│   │   ├── provider.py   # Abstract TTSProvider base class
│   │   └── piper_provider.py # Implementación Piper CLI vía subprocess
│   ├── tasks.py          # Funciones de generación de audio (wave puro)
│   ├── models.py         # Poema SQLAlchemy ORM model
│   ├── database.py       # Configuración SQLite con check_same_thread=False
│   ├── main.py           # App FastAPI entry point + routers
│   └── templates/        # Jinja2 templates para frontend
├── static/
│   ├── css/
│   │   └── style.css     # Estilos CSS del frontend
│   └── js/
│       └── app.js        # Vanilla JS con API interaction
├── scripts/              # Scripts de utilidad
│   └── descargar_modelo.py
├── tts_models/          # Carpeta para modelos TTS descargados
├── poems.db             # Base de datos SQLite (auto-creada en primer uso)
├── audio/               # Carpeta de output para archivos MP3 generados
├── tests/                # Suite de pruebas con pytest
│   ├── conftest.py      # Fixtures y mocks de Piper
│   ├── test_api.py      # Tests para endpoints API
│   ├── test_audio.py    # Tests para funciones de audio
│   └── test_texto.py    # Tests para separación versos/estrofas
├── INSTALL.md            # Instrucciones detalladas de instalación
├── PROJECT_STATUS.md     # Estado actual del proyecto
└── README.md             # Este archivo
```

## 🧪 Ejecutar Tests

```bash
cd poemtoaudio
source venv/bin/activate
pytest -v
```

**Summary de tests:**
- `tests/test_texto.py`: 12 passing ✅
- `tests/test_api.py`: Dependen de Piper CLI real instalado
- `tests/test_audio.py`: Funciones wave puro funcionando

## 🔧 Configuración Opcional

### Usar Git LFS para modelos TTS

```bash
# Si quieres almacenar modelo .onnx (200MB+)
git lfs install
git lfs track "*.onnx"
git commit message "Adaptado modelos a Git LFS"
```

### Montar carpeta /audio como estático

```python
# En app/main.py, después de crear app:
app.mount("/audio", StaticFiles(directory="audio"), name="audio")
```

## 📊 Estado del Proyecto

- ✅ Funcionalidad core completa (CRUD endpoints, generación de audio)
- ✅ ORM usado correctamente en todo el backend
- ✅ Tests de texto pasando completamente
- ⚠️ Tests API dependientes de Piper CLI en ambiente real
- 🔄 Frontend funcional con polling automático cada 2s

## 🐛 Solución de Problemas

### Error: "No se encontró modelo para voz {voz}"

Verifica que el archivo `.onnx` existe en `tts_models/`:
```bash
ls -la tts_models/*.onnx
```

### Error: ffmpeg no encontrado

Instala ffmpeg:
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
# O usa pip si tienes piper-tts
pip install piper-tts
```

### Audio no generado después de tiempo prolongado

Verifica logs de generación:
```bash
tail -f venv.log  # Si usas logging
# O revisa carpeta /audio para archivos temporales
```

## 📝 Licencia

MIT License - Libre uso comercial y educativo.

---

**Desarrollado con ❤️ usando Piper TTS local**
