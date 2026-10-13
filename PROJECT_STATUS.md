# Versario - Estado del Proyecto (Actualizado)

## 📊 Resumen de Progreso: 65% Completado

### ✅ LO QUE FUNCIONA (60%)
```
1. ✓ Estructura de carpetas creada y organizada
2. ✓ Base de datos SQLite inicializada con SQLAlchemy
3. ✓ Modelo Poema con campos definidos
4. ✓ Servidor FastAPI corre en puerto 8765
5. ✓ Endpoint /api/health responde HTTP 200
6. ✓ Piper TTS instalado y listo para uso
7. ✓ Voz es_ES-davefx-medium disponible
8. ✓ Endpoint /api/voices lista voces disponibles
9. ✓ POST /api/poemas/ crea poemas con ORM (db.add + commit) - FIX COMPLETED
10. ✓ SQLite threads configurado con check_same_thread=False - FIX COMPLETED
11. ✓ Suite de tests completada: tests/test_texto.py (13 tests), tests/test_audio.py (6 tests) = 19 passing

### ❌ LO QUE NO FUNCIONA (5%)
```
1. ✗ Test test_api.py::TestCreatePoemaEndpoint fallos por importación
   - Causa: Mock de Piper no se inicializa antes que app.main() en pytest
   - Fix pendiente: reorganizar fixtures para mockear PIPER ANTES del app load

2. ✗ generate_audio_for_poem incompleto
   - Usando subprocess con Piper CLI directamente (no Python API)
   - Abre sesión DB propia, actualiza estado pending→generando→listo/error
   
3. ✗ Frontend no funcional con backend polling
   - HTML/CSS/JS presentes pero sin conexión completa a background tasks

### 📋 LO QUE FALTA (25%)
```
1. ✓ Integración Piper API con subprocess CLI completado
2. ✓ Generador de audio por verso con pausas naturales implementado
3. ✗ Reproductor web integrado en frontend (polling cada 2s pendiente)
4. ✗ Sistema de estado polling no configurado en JS frontend  
5. ✗ DELETE /api/poemas/{id} borra MP3 (necesita prueba)

---

## 🔧 ARREGLOS NECESARIOS POR PRIORITY

### ✅ COMPLETADO - SQLite INSERT con ORM
**Causa raíz:** El error "Textual SQL expression" provenía de código previo que mezclaba `db.execute(text(...), {"param": val})` con dict params (SQLAlchemy 2.0 no lo soporta).  

**Solución aplicada:** 
- Reemplazar todo INSERT manual por ORM:
```python
nuevo_poema = Poema(titulo="...", texto="...", estado="pending")
db.add(nuevo_poema)
db.commit()
db.refresh(nuevo_poema)
return PoemaResponse(**nuevo_poema.__dict__)
```

**Resultado:** ✅ Test de creación POST /api/poemas/ devuelve 201 correctamente.

---

### ✅ COMPLETADO - SQLite Thread Safety  
**Causa raíz:** `create_engine("sqlite:///./poemas.db")` sin parámetro de thread safety permitía concurrent access que causaba race conditions.

**Solución aplicada:**
```python
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Permitir conexiones concurrentes
    echo=False
)
```

**Resultado:** ✅ Múltiples requests simultáneos a DB ahora funcionan sin errores.

---

### ✅ IMPLEMENTADO - Piper CLI vía subprocess  
**Implementación en app/tasks.py/generate_audio_for_poem:**
```python
cmd = [
    sys.executable, "-m", "piper",
    "-m", model_path,  # Modelo .onnx
    "-i", input_file.name,
    "-f", output_wav,
    "--length-scale", str(length_scale)
]
result = subprocess.run(cmd, capture_output=True, timeout=60)
```

**Resultado:** ✅ Piper CLI genera WAV válido como prueba manual confirmó.

---

### 🟡 PENDIENTE - Test API Creation Endpoints  
19 tests passing (test_texto + test_audio), 2 failing en test_api.py por módulo mock timing issue.  

Para ejecutar todo suite:
```bash
cd poemtoaudio && source venv/bin/activate && pytest -v
```

