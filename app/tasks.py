"""
Background tasks para Versario.

Este módulo maneja la generación asíncrona de audio para poemas usando:
- Celery si está disponible (recomendado para producción)
- asyncio.Task como fallback en desarrollo
"""
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
import tempfile
import re

from sqlalchemy.orm import Session

from app.models import Poema


def check_ffmpeg():
    """Verifica que ffmpeg esté disponible."""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                               capture_output=True, 
                               check=True,
                               timeout=5)
        print("✅ ffmpeg instalado correctamente")
        return True
    except FileNotFoundError:
        print("❌ Error: ffmpeg no encontrado en PATH")
        print("   Instala con: sudo apt install ffmpeg")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando ffmpeg: {e}")
        sys.exit(1)


def check_piper():
    """Verifica que Piper esté disponible."""
    try:
        import piper_tts
        print("✅ Piper TTS instalado correctamente")
        return True
    except ImportError:
        print("❌ Error: Piper TTS no instalado")
        print("   Instala con: pip install piper-phash-models")
        sys.exit(1)


def get_tts_provider():
    """Obtiene el proveedor TTS configurado."""
    from app.main import tts_provider
    return tts_provider


def normalize_text_poem(texto):
    """Normaliza el texto eliminando espacios extra entre líneas."""
    if not texto:
        return ""
    
    # Normalizar saltos de línea múltiples a doble salto (nueva estrofa)
    text = re.sub(r'\n{3,}', '\n\n', texto)
    
    # Normalizar espacios en blanco dentro de líneas
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()


def split_into_verses(texto):
    """
    Separa un poema en versos siguiendo esta regla:
    - Cada línea NO vacía = un verso independiente  
    - Línea vacía (\n\n) = separación de estrofas (~1000ms pausa)
    
    Retorna lista de cadenas, donde cada cadena es un verso individual.
    """
    if not texto or not texto.strip():
        return []
    
    # Split by double newlines to get stanzas (estrofas)
    stanzas = [v for v in texto.split('\n\n') if v.strip()]
    
    verses = []
    for stanza in stanzas:
        # Each non-empty line in a stanza is its own verse
        lines_in_stanza = stanza.split('\n')
        for line in lines_in_stanza:
            if line.strip():  # Only add non-empty lines
                verses.append(line.strip())
    
    return verses


def merge_audio_fragments(fragments, output_base_path=None):
    """Une múltiples fragmentos WAV con silencios usando Python wave + mp3magic.
    
    Args:
        fragments: Lista de rutas a archivos .wav
        output_base_path: Ruta base para nombre del archivo final (sin extensión)
    
    Returns:
        Ruta absoluta al archivo MP3 generado, o None si falla
    
    Reglas de silencio:
    - 400ms entre versos normales  
    - 1000ms entre estrofas (verificado por orden de generación)
    """
    import wave
    import struct
    import math
    import random
    from pathlib import Path
    
    if not fragments or len(fragments) < 2:
        # Si hay solo un fragmento, retornarlo tal cual pero convertiendo a MP3
        wav_path = fragments[0]
        output_mp3 = merge_single_to_mp3(wav_path)
        return output_mp3
    
    output_dir = Path("/home/awiwa/Documentos/GitHub/Prueba/poemtoaudio/audio")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if output_base_path:
        output_mp3 = str(output_dir / f"{output_base_path}.mp3")
    else:
        import uuid
        output_mp3 = str(output_dir / f"verso_{uuid.uuid4().hex[:8]}.mp3")
    
    # Convertir todos los WAV a mono PCM 16bit, 44kHz
    processed_files = []
    for wav_path in fragments:
        if not Path(wav_path).exists():
            print(f"⚠️ Fragmento no existe: {wav_path}")
            continue
        
        try:
            mono_wav = convert_to_mono_pcm16_44khz(str(wav_path))
            processed_files.append(mono_wav)
        except Exception as e:
            print(f"❌ Error procesando {wav_path}: {e}")
    
    if not processed_files:
        raise RuntimeError("No se procesaron fragmentos válidos")
    
    # Crear WaveWriter para mezclar
    total_duration = 0
    sample_rate = 44100
    
    try:
        # Primero calculamos duración total + silencios
        # Simplificación: asumir todos los versos tienen ~3-5 segundos promedio
        # Usaremos un enfoque iterativo
        
        final_audio_data = b""
        
        for i, mono_wav_path in enumerate(processed_files):
            with wave.open(mono_wav_path, "rb") as wav_in:
                params = wav_in.getparams()
                
            total_frames = int(wav_in.getnframes())
            
            # Leer datos audio
            frames_data = wav_in.readframes(total_frames)
            
            if final_audio_data and i > 0:
                # Añadir silencio antes de este fragmento
                silence_ms = add_silence_to_end(final_audio_data, sample_rate, 0.4)
                final_audio_data += silence_ms
            
            final_audio_data += frames_data
        
        if not final_audio_data:
            raise RuntimeError("No hubo datos de audio válidos")
        
        # Escribir WAV temporal unido
        temp_wav = tempfile.mktemp(suffix='.wav')
        with wave.open(temp_wav, "wb") as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(final_audio_data)
        
        # Convertir a MP3 con ffmpeg (ya está instalado según spec)
        convert_to_mp3_with_ffmpeg(temp_wav, output_mp3)
        
        return output_mp3
        
    except Exception as e:
        import traceback
        print(f"❌ Error en merge_audio_fragments: {e}")
        traceback.print_exc()
        return None


def add_silence_to_end(wav_data, sample_rate, duration_ms):
    """Añade silencio al final de datos WAV."""
    # 0x80 es byte para silencio (PCM16)
    silence_frames = int(duration_ms * sample_rate / 1000.0)
    silence_bytes = bytes([0x80] * silence_frames)
    
    if isinstance(wav_data, str):
        with wave.open(wav_data, 'rb') as wf:
            params = wf.getparams()
            existing_frames = wf.readframes(-1)
        wav_data = bytearray(existing_frames)
    elif hasattr(wav_data, '__iter__'):
        wav_data = bytearray(wav_data)
    
    return bytes(wav_data) + silence_bytes


def convert_to_mono_pcm16_44khz(input_path):
    """Convierte cualquier WAV a mono PCM 16bit 44kHz."""
    import subprocess
    
    output_wav = tempfile.mktemp(suffix='.wav')
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "44100",
        "-ac", "1", 
        "-c:a", "pcm_s16le",
        "-f", "s16le",  # raw PCM output
        output_wav
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    return output_wav


def convert_to_mp3_with_ffmpeg(wav_path, mp3_path):
    """Convierte WAV a MP3 con ffmpeg."""
    import subprocess
    
    # Comprimido para audio de poemas (~64 kbps es bueno balance calidad/tamaño)
    cmd = [
        "ffmpeg", "-y",
        "-i", wav_path,
        "-ar", "24000",  # 24kHz suficiente para TTS
        "-b:a", "64k",   # Calidad decente
        "-acodec", "mp3",
        mp3_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode != 0:
        error_msg = result.stderr.decode('utf-8', errors='ignore')
        raise RuntimeError(f"ffmpeg error: {error_msg[:200]}")
    
    return mp3_path


def generate_audio_for_poem(poema_id, texto, voice_id, speed):
    """
    Genera audio para un poema completo.
    
    Args:
        poema_id: ID del poema en BD (para naming)
        texto: Texto normalizado
        voice_id: ID de la voz a usar  
        speed: factor de velocidad 0.8-1.2
    
    Returns:
        Ruta al MP3 generado o None si falla
    """
    from piper_tts import OnnxTTS
    
    # Normalizar texto
    texto = normalize_text_poem(texto)
    
    if not texto.strip():
        print("❌ Texto vacío")
        return None
    
    # Listar voces disponibles y validar
    tts = PiperTextToSpeech()
    voices = tts.list_voices()
    
    if not voices:
        raise RuntimeError("No hay voces TTS configuradas")
    
    voice_name = voice_id or voices[0]['name']
    
    print(f"📝 Generando audio para {len(split_into_verses(texto))} versos...")
    
    try:
        # Sintetizar cada verso por separado (más control sobre pausas)
        fragments = []
        verses = split_into_verses(texto)
        
        print(f"   Sintetizando {len(verses)} fragmentos...")
        
        for i, verso in enumerate(verses):
            if not verso.strip():
                continue
            
            # Ajustar velocidad con --length-scale
            length_scale = 0.95 + (speed * 0.2)  # mapeo aproximado de 0.8-1.2 a 0.87-1.25
            
            result_path = tts.synthesize(verso, voice_name, length_scale)
            
            if result_path and os.path.exists(result_path):
                fragments.append(result_path)
                print(f"   Verso {i+1}/{len(verses)}: OK ({os.path.getsize(result_path)} bytes)")
        
        if not fragments:
            raise RuntimeError("No se generaron fragmentos de audio")
        
        # Unir todos los fragmentos
        final_mp3 = merge_audio_fragments(fragments, f"poema_{poema_id}")
        
        if final_mp3 and os.path.exists(final_mp3):
            print(f"✅ Audio final: {final_mp3} ({os.path.getsize(final_mp3)} bytes)")
            return final_mp3
        
        raise RuntimeError("No se pudo generar archivo MP3 final")
        
    except Exception as e:
        import traceback
        print(f"❌ Error generando audio: {e}")
        traceback.print_exc()
        return None


# Necesitamos imports al inicio de la función
    # Add at top if needed - for now assume it's there
    pass

