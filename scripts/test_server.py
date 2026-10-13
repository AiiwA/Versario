"""
Script de prueba para verificar que Versario funciona correctamente.

Uso:
    python3 test_server.py
    
Esto testeará:
1. Que el servidor puede iniciar
2. Que la base de datos se inicializa
3. Que las voces están disponibles
4. Que los endpoints API responden
"""
import subprocess
import sys
import time
import requests
from urllib3.util.retry import Retry

def test_imports():
    """Test 1: Verificar que todos los módulos se pueden importar."""
    print("=" * 60)
    print("TEST 1: Importando módulos...")
    print("=" * 60)
    
    modules = [
        "poemtoaudio.app.main",
        "poemtoaudio.app.models", 
        "poemtoaudio.app.database",
        "poemtoaudio.app.tasks",
        "poemtoaudio.tts.provider",
        "poemtoaudio.tts.piper_provider"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            return False
    
    print("\n✅ Todos los módulos importados correctamente\n")
    return True

def test_app_startup():
    """Test 2: Verificar que FastAPI app se puede inicializar."""
    print("=" * 60)
    print("TEST 2: Inicializando aplicación FastAPI...")
    print("=" * 60)
    
    try:
        from poemtoaudio.app import main
        print(f"✅ Aplicación creada: {main.app.title}")
        print(f"   Versión: {main.app.version}")
        
        # Verificar endpoints registrados
        routes = [r.path for r in main.app.routes if hasattr(r, 'path')]
        api_routes = [r for r in routes if r.startswith('/api/')]
        print(f"   Endpoints API ({len(api_routes)}):")
        for route in api_routes:
            print(f"     • {route}")
        
        print("\n✅ Aplicación inicializada correctamente\n")
        return True
        
    except Exception as e:
        print(f"❌ Error al iniciar app: {e}\n")
        return False

def test_database():
    """Test 3: Verificar que base de datos se inicializa."""
    print("=" * 60)
    print("TEST 3: Base de datos SQLite...")
    print("=" * 60)
    
    try:
        from poemtoaudio.app.database import get_db, engine
        
        # Crear tablas
        print("   Inicializando tablas...")
        from poemtoaudio.app.models import Base
        Base.metadata.create_all(bind=engine)
        
        print(f"✅ Tablas creadas en: {engine.url}")
        print("\n✅ Base de datos lista\n")
        return True
        
    except Exception as e:
        print(f"❌ Error con base de datos: {e}\n")
        return False

def test_tts_provider():
    """Test 4: Verificar que TTS provider funciona."""
    print("=" * 60)
    print("TEST 4: Proveedor de voz TTS...")
    print("=" * 60)
    
    try:
        from poemtoaudio.tts.piper_provider import PiperTextToSpeech
        
        tts = PiperTextToSpeech()
        
        # Listar voces disponibles
        voices = tts.list_voices()
        print(f"   Voces encontradas: {len(voices)}")
        
        for voice in voices[:3]:  # Mostrar primeras 3
            print(f"     • {voice['name']} ({voice.get('gender', 'neutral')})")
        
        if len(voices) > 0:
            print("\n✅ TTS Provider configurado correctamente\n")
            return True
        else:
            print("\n⚠️  No se encontraron voces disponibles\n")
            return False
            
    except Exception as e:
        print(f"❌ Error con TTS: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_start_server():
    """Test 5: Iniciar servidor en segundo plano y testear endpoints."""
    print("=" * 60)
    print("TEST 5: Iniciando servidor y testeando endpoints...")
    print("=" * 60)
    
    try:
        # Cambiar al directorio del proyecto
        import os
        os.chdir('/home/awiwa/Documentos/GitHub/Prueba/poemtoaudio')
        
        # Iniciar servidor con uvicorn en background
        server = subprocess.Popen(
            ['uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8765'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env={**os.environ}  # Usar mismo entorno virtual
        )
        
        time.sleep(3)  # Esperar que se inicie
        
        try:
            # Testear endpoint de salud
            response = requests.get('http://127.0.0.1:8765/api/health', timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ /api/health responde con código {response.status_code}")
                print(f"   Status: {health_data.get('status', 'unknown')}")
                
                # Testear endpoint de voces
                voices_resp = requests.get('http://127.0.0.1:8765/api/voices', timeout=5)
                
                if voices_resp.status_code == 200:
                    voices = voices_resp.json()
                    print(f"✅ /api/voices responde con código {response.status_code}")
                    print(f"   Voces disponibles: {len(voices)}")
                else:
                    print(f"⚠️  /api/voices no responde (código {voices_resp.status_code})")
                
                print("\n✅ Servidor funcionando correctamente\n")
                return True
                
            else:
                print(f"❌ Server no respondió en el puerto 8765 (HTTP {response.status_code})\n")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error conectando al servidor: {e}\n")
            return False
            
    finally:
        # Detener servidor
        try:
            server.terminate()
            server.wait(timeout=5)
        except:
            pass

def main():
    print("\n" + "🧪 VERSIARIO - SCRIPT DE PRUEBAS COMPLETAS\n")
    
    tests = [
        ("Importar módulos", test_imports),
        ("Inicializar App", test_app_startup),
        ("Base de datos", test_database),
        ("Proveedor TTS", test_tts_provider),
        ("Servidor live", test_start_server),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results[name] = passed
        except Exception as e:
            print(f"\n❌ Test {name} falló con excepción: {e}\n")
            results[name] = False
        
        print("\n" + "-" * 60)
    
    # Resumen
    print("\n" + "📊 RESULTADO FINAL\n" + "=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        icon = "✅ PASÓ" if status else "❌ FALLÓ"
        print(f"   • {icon} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! Tu servidor está listo.\n")
        return 0
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa el output arriba.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
