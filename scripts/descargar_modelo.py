#!/usr/bin/env python3
"""
Script de utilidad para descargar/modelo Piper TTS.

Nota: Usa el modelo existente si ya está presente, o descarga desde
https://huggingface.co/rhasspy/piper-voices en lugar de piper-phash-models obsoleto.

Uso:
    python scripts/descargar_modelo.py
"""

import os
import sys
import urllib.request
from pathlib import Path

MODEL_DIR = "./tts_models"
MODELO_OBJETIVO = "es_ES-davefx-medium.onnx"
URL_MODELO = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    f"es_ES-davefx-{MODEL_OBJETIVO}"
)

# Tamaño aproximado esperado
EXPECTED_SIZE_MB = 61


def check_existing_model():
    """Verifica si modelo ya existe."""
    model_path = Path(MODEL_DIR) / MODEL_OBJETIVO
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ Modelo ya existe: {model_path}")
        print(f"   Tamaño: {size_mb:.1f}MB")
        
        # Verificar integridad básica (no está corrupto)
        if size_mb >= EXPECTED_SIZE_MB * 0.5:  # >50% del tamaño esperado
            return True
        
        print("⚠️ Modelo incompleto o corrupto, intentando descargar nuevamente...")
        return False
    
    return False


def download_model():
    """Descargar modelo desde Huggingface."""
    print(f"📥 Descargando modelo: {MODEL_OBJETIVO}")
    print(f"   URL: {URL_MODELO}")
    
    try:
        # Crear directorio si no existe
        Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)
        
        # Descargar con curl o urllib según disponibilidad de curl
        cmd = f"curl -L -o '{MODEL_OBJETIVO}' '{URL_MODELO}'"
        
        print("   Ejecutando descarga...")
        os.system(cmd)
        
        # Verificar éxito
        model_path = Path(MODEL_DIR) / MODEL_OBJETIVO
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"✅ Modelo descargado: {model_path}")
            print(f"   Tamaño: {size_mb:.1f}MB")
            
            # Limpiar archivos temporales si existen
            for p in Path(MODEL_DIR).glob("es_ES-davefx-medium.onnx.*"):
                if p != model_path:
                    try:
                        p.unlink()
                        print(f"   Limpieza temporal eliminada: {p}")
                    except: pass
            
            return True
        else:
            print(f"❌ Error: Archivo no creado en {model_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante descarga: {e}")
        sys.exit(1)


def main():
    """Función principal."""
    print("📦 Versario - Descargador de modelo Piper TTS")
    print("=" * 60)
    
    if check_existing_model():
        return 0
    
    # No existe o está incompleto, descargar
    success = download_model()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

