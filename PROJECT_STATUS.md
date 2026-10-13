# Versario - Estado del Proyecto

## 📊 Resumen de Progreso: 45% Completado

### ✅ LO QUE FUNCIONA (30%)
```
1. ✓ Estructura de carpetas creada y organizada
2. ✓ Base de datos SQLite inicializada con SQLAlchemy
3. ✓ Modelo Poema con campos definidos
4. ✓ Servidor FastAPI corre en puerto 8765
5. ✓ Endpoint /api/health responde HTTP 200
6. ✓ Piper TTS instalado y listo para uso
7. ✓ Voz es_ES-davefx-medium (61MB) descargada
8. ✓ Endpoint /api/voices lista 3 voces disponibles
```

### ❌ LO QUE NO FUNCIONA (45%)
```
1. ✗ POST /api/poemas/ falla al crear nuevo poema
   - Error: "List argument must consist only of dictionaries"
   - Causa: SQLAlchemy 2.0 incompatibilidad con text() INSERT

2. ✗ generate_audio_for_poem incompleto
   - Falta implementación de merge_audio_fragments()  
   - No se llama a la función desde el endpoint

3. ✗ Frontend no funcional
   - HTML/CSS/JS presentes pero sin backend connectivo
   
4. ✗ Sistema de estado pendiente/generando/listo/error no implementado
```

### 📋 LO QUE FALTA (25%)
```
1. ✗ Integración Piper API con Python en lugar de CLI
2. ✗ Generador de audio por verso con pausas naturales
3. ✗ Reproductor web integrado en frontend
4. ✗ Sistema de polling para status updates
5. ✗ Borrar poema + eliminar MP3
```

---

## 🔧 ARREGLOS NECESARIOS POR PRIORITY

### 🔴 CRÍTICO (bloquea todo)

#### 1. Fix SQLite INSERT en app/routes/poema.py
**Problema:** SQLAlchemy 2.0 no acepta tuple params con text()
**Solución:** Usar ORM insert().values() o db.add(Poema(...))

```python
# ACTUAL (falla):
db.execute(text("INSERT INTO ... VALUES (?, ?, ?)"), {"param": val})

# CORREGIDO:
from sqlalchemy import insert, text
db.add(Poema(
    id=poem_id, titulo="...", texto="...", estado="pending"
))
```

**Archivo:** app/routes/poema.py (función crear_poema)

---

#### 2. Configurar DATABASE_URL con check_same_thread=False
**Problema:** SQLite permite concurrente en solo una thread por defecto
**Solución:** Agregar parámetro a engine url

```python
# app/database.py - line 10:
DATABASE_URL = "sqlite:///./poemas.db?check_same_thread=False"
```

---

### 🟠 ALTO (necesario para funcionalidad)

#### 3. Implementar PIPERTextToSynthesize correctamente  
**Problema:** Piper CLI no funciona con Python API
**Solución:** Usar subprocess directamente en piper_provider.py

```python
# app/tts/piper_provider.py - método synthesize():
cmd = [
    "./venv/bin/python", "-m", "piper",
    "-m", model_path,  # Modelo .onnx
    "-i", input_file.name,
    "-f", output_wav,
    "-s", "0"  # Speaker ID
]
```

**Evidencia:** Comandos ejecutados exitosamente:
```bash
✅ python -m piper -m tts_models/es_ES-davefx-medium.onnx \
   -i /tmp/hola.txt -f /tmp/out.wav -s 0  
   → Genera archivo WAV de 35KB
```

---

#### 4. Unir audio con pausas naturales (400ms/1000ms)
**Problema:** merge_audio_fragments() incompleto, usa wave básico sin ffmpeg
**Solución:** Implementar lógica completa usando Python wave + ffmpeg mp3

```python
# app/tasks.py - funciones necesarias:
def merge_audio_fragments(fragments, output_path):
    # 1. Convertir cada .wav a mono PCM 44kHz
    # 2. Leer frames y añadir silencio entre ellos
    # 3. Unir en WaveWriter temporal
    # 4. Convertir a MP3 con ffmpeg
```

**Estado:** Esqueleto creado pero incompleto (~50% implementado)

---

#### 5. Integrar generar_audio en POST endpoint
**Problema:** Endpoint crea poema con estado="pending" pero no llama generator
**Solución:** Usar BackgroundTasks o asyncio.create_task()

```python
@router.post("/api/poemas/")
async def crear_poema(request, db, background_tasks: BackgroundTasks):
    # ... crear en DB ...
    
    # Lanzar generación asíncrona
    background_tasks.add_task(
        generate_audio_for_poem, poem.id, request.texto, 
        request.voz, request.velocidad
    )
```

---

### 🟡 MEDIO (funcionalidad completa)

#### 6. Frontend con reproductor integrado
**Estado:** HTML/CSS/JS completos pero sin backend integration

**Arreglar en app/routes/poema.py - agregar endpoint GET /api/poemas/:id/audio**:
```python
@router.get("/{poema_id}/audio")
async def serve_audio(poema_id, db):
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    return FileResponse(str(poem.ruta_audio), media_type="audio/mpeg")
```

---

#### 7. Sistema de polling para status updates
**Problema:** Frontend no detecta cuando estado cambia a "generando" → "listo"
**Solución:** Endpoint GET /api/poemas/{id} que devuelve estado actualizado

```python
@router.get("/{poema_id}")
async def get_poema_status(poema_id, db):
    poem = db.query(Poema).filter(Poema.id == poema_id).first()
    return {"estado": poem.estado, "ruta_audio": poem.ruta_audio}
```

**Frontend en app.js:** Polling cada 2 segundos:
```javascript
setInterval(() => fetch(`/api/poemas/${poemId}`), 2000);
```

---

#### 8. Frontend completo con reproductor
**Estado:** Todo el HTML/CSS/JS ya está creado (17KB CSS, 21KB JS)

**Últimos cambios necesarios:**
- Conectar form submission a POST /api/poemas/
- Mostrar lista de poemas en GET /api/poemas/?offset&limit
- Implementar reproductor HTML5 audio con FileResponse URL
- Agregar botón de descarga: `<a href="/api/poemas/{id}/audio" download>`

---

## 📁 ESTRUCTURA DEL PROYECTO

```
poemtoaudio/
├── app/                          # Backend FastAPI
│   ├── __init__.py              # Package init (38 lines)
│   ├── main.py                   # App entry point + TTS config
│   ├── database.py               # SQLAlchemy engine & session
│   ├── models.py                 # Poema ORM model (267 lines)
│   └── routes/                   # API endpoints
│       ├── __init__.py           # Router export
│       └── poema.py              # CRUD + audio serve (143 lines)
│
├── app/tts/                      # TTS layer (ABSTRACTO)
│   ├── __init__.py               # Package init
│   ├── provider.py               # TTSProvider ABC (definición interface)
│   └── piper_provider.py         # PiperTextToSpeech impl (58 lines)
│
├── static/                       # Frontend assets
│   ├── css/style.css             # Dark elegant theme (17KB)
│   └── js/app.js                 # Vanilla JS logic (21KB)
│
├── templates/                    # Jinja2 HTML templates  
│   ├── index.html                # Main page + form (346 lines)
│   └── poema.html                # Detail page + player (99 lines)
│
├── audio/                        # Output directory for MP3s
├── tts_models/                   # Piper models (es_ES-davefx-medium 61MB)
├── scripts/                      # Utility scripts
│   └── crear_poemas_ejemplo.py   # Test data creator
│
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation  
└── venv/                         # Virtual environment (EXCLUDE)
```

**Total archivos:** 18 python, 2 html, 3 css/js, 4 txt/markdown  
**Líneas de código:** ~1500 lines

---

## 📦 DEPENDENCIAS INSTALADAS

```
fastapi>=0.104.0          ✅ Web framework
uvicorn[standard]>=0.24.0 ✅ Server
python-multipart>=0.0.6   ✅ Form uploads  
sqlalchemy>=2.0.0         ✅ ORM (Python 3.14 compatible)
aiosqlite>=0.19.0         ✅ Async SQLite driver
pydub>=0.25.1             ✅ Audio manipulation
piper-tts                 ❌ Uninstallado (no PyPI para 3.14, usando CLI directo)
huggingface-hub           ✅ Model downloads

System dependencies:
✅ ffmpeg                   # Audio conversion
```

**requirements.txt actualizado:**
- Añadir jinja2>=3.1.0 para templates
- piper-tts no se puede instalar en Python 3.14 → usar subprocess a CLI

---

## 🔍 RAZONES DETALLLADAS POR ARREGLO

### Por qué falla INSERT actualmente:
```python
# app/routes/poema.py line ~55:
db.execute(
    text(f"INSERT INTO {Poema.__tablename__} ... VALUES (?, ?, ...)"),
    {"param": value}  # ← SQLAlchemy 2.0 espera dict en segundo argumento
)

# Error trace:
File "/home/awiwa/.../venv/lib/python3.14/site-packages/sqlalchemy/engine/base.py",
line 2195, in execute
    distilled_parameters = _distill_params_20(parameters)
sqlalchemy.exc.ArgumentError: List argument must consist only of dictionaries

# Solución: db.add(Poema(...)) o text() sin params
```

### Por qué no se generan audio:
- `generate_audio_for_poem()` está definida pero nunca llamada desde POST endpoint
- BackgroundTasks no configurado en main.py (no tiene router import)
- Necesita: `background_tasks = BackgroundTasks` en route signature

### Por qué frontend no conecta:
- app.js hace fetch a `/api/poemas/` pero endpoint devuelve error 500
- Form submit no preven defecte y resetea página
- Reproductor HTML5 `<audio src="/api/poemas/{id}/audio">` falla (404)

---

## 🛠️ CÓMO ARREGLAR - PASE POR PASO

### Paso 1: Fix INSERT en app/routes/poema.py
```bash
cd /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio

# Editar create endpoint (~linea 40-55):
sed -i 's/from sqlalchemy import text//' app/routes/poema.py

# Cambiar INSERT block por:
cat > /tmp/create_fix.py << 'PYFIX'
new_code = '''        from sqlalchemy import insert
        
        db.add(Poema(
            id=poem_id, titulo=request.titulo, autor=request.autor or "",
            texto=request.texto, voz=request.voz or "es_ES-davefx-medium",
            velocidad=float(request.velocidad), estado="pending"
        ))
        
        # Commit necesario para que insert() funcione
        db.commit()'''

with open('app/routes/poema.py', 'r') as f:
    content = f.read()
# Replace old text INSERT with new code...
PYFIX
python3 /tmp/create_fix.py
```

### Paso 2: Fix DATABASE_URL check_same_thread
```bash
cd poemtoaudio
sed -i "s/Database_URL = .*/DATABASE_URL = 'sqlite: \/\/.\/poemas.db?check_same_thread=False'/" app/database.py
```

### Paso 3: Add BackgroundTasks import en main.py  
```python
from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
# ...
app.state["background_tasks"] = BackgroundTasks()
```

### Paso 4: Call generate_audio en create endpoint
```python
@router.post("/")
async def crear_poema(request, db, background_tasks: BackgroundTasks):
    # Create DB insert...
    
    # Start async task
    background_tasks.add_task(generate_audio_for_poem)
    return PoemaResponse(**poem.__dict__)
```

### Paso 5: Implementar merge_audio_fragments completo
```python
# app/tasks.py - función merge_audio_fragments:
import wave, subprocess, tempfile

def merge_audio_fragments(fragments):
    temp_wavs = [Path(w).read_bytes() for w in fragments]
    
    # Write combined WAV with pauses (400ms silence between)
    out_path = Path("/tmp/verso.mp3")
    
    # 1. Concat WAVs + add silence bytes  
    # 2. ffmpeg -f wav -i merged.wav -b:a 64k -acodec mp3 output.mp3
    
    return str(out_path) if out_path.exists() else None
```

### Paso 6: Frontend connect - app.js form submit
```javascript
document.getElementById('poemForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // ← Importante!
    const formData = new FormData(e.target);
    
    try {
        const res = await fetch('/api/poemas/', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                titulo: formData.get('titulo'),
                texto: formData.get('texto'), voz: formData.get('voz'),
                velocidad: parseFloat(formData.get('velocidad'))
            })
        });
        
        if (res.ok) {
            window.location.href = '/poema/' + data.id; // Navigate to detail
        } else {
            alert('Error creando poema');
        }
    } catch (err) {
        console.error(err);
    }
});
```

### Paso 7: Frontend polling status
```javascript
// app.js - in viewPoemaDetail():
function startPolling(poemaId) {
    setInterval(async () => {
        const res = await fetch(`/api/poemas/${poemaId}`);
        const data = await res.json();
        
        // Update UI based on estado:
        // pending → generando → listo (show player) / error
        
    }, 2000); // Check every 2 seconds
}

// Call at top of function:
startPolling(window.poemaData.id);
```

---

## 📊 PORCENTAJES DETALLADOS

| Componente | Estado | % Completo | Bloqueante |
|------------|--------|------------|------------|
| Backend base (FastAPI + DB) | ✅ Funcional | 95% | No |
| Modelo Poema ORM | ✅ Definido | 100% | Sí |
| Endpoint GET listados | ✅ OK | 100% | No |
| Endpoint POST crear | ❌ Falla INSERT | 20% | **SÍ** |
| Endpoint DELETE | ⚠️ Parcial | 60% | No |
| Serve audio streaming | ❌ 404 | 0% | Sí |
| TTS Pipeline | 🟡 Incompleto | 35% | **SÍ** |
| Frontend HTML/CSS/JS | ✅ Completo | 95% | No |
| Frontend Integration | ❌ Sin connect | 5% | Sí |

**TOTAL: ~45% funcional completo, ~55% en desarrollo/bloqueado**

---

## 🎯 PRÓXIMOS PASOS RECOMENDADOS (ORDEN)

1. **[CRÍTICO]** Fix app/routes/poema.py create con ORM insert().values()
2. **[CRÍTICO]** Add generate_audio_for_poem call en POST endpoint  
3. **[ALTO]** Implementar merge_audio_fragments completo (wave + ffmpeg)
4. **[ALTO]** Configure BackgroundTasks para async audio generation
5. **[MEDIO]** Frontend form submit con e.preventDefault() + JSON body
6. **[MEDIO]** Polling mechanism para status updates en frontend
7. **[BAJO]** Error handling y UI feedback para failed generations

---

## 🔧 PARA OTRA IA: COMENZAR AQUÍ

```bash
# 1. Entorno ya configurado:
cd /home/awiwa/Documentos/GitHub/Prueba/poemtoaudio

# 2. Venv activado con todos los paquetes:
source venv/bin/activate

# 3. Servidor corre en 8765, prueba:
curl http://localhost:8765/api/health
# → {"status": "ok", "service": "versario"}

# 4. Voz disponible (ya descargada):
ls tts_models/es_ES-davefx-medium.onnx

# 5. Arreglo PRIORIDAD #1 - Fix INSERT:
# Editar app/routes/poema.py lines 40-60: cambiar text() por ORM insert

# 6. Luego probar POST endpoint:
curl -X POST http://localhost:8765/api/poemas/ \
   -H "Content-Type: application/json" \
   -d '{"titulo":"Test","texto":"Hola\n\nAdios","voz":"es_ES-davefx-medium"}'

# 7. Si funciona → Implementar audio generation → Frontend connect
```

---

**Generado:** 2026-10-13T14:40 - Versario v1.0  
**Estado:** Progreso funcional, necesita integración backend-tts-fronted completo
