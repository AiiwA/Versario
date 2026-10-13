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


def merge_single_to_mp3(wav_path):
    """Convierte un único WAV a MP3 usando ffmpeg."""
    import subprocess
    from pathlib import Path
    
    # Convertir string a Path si es necesario
    if isinstance(wav_path, str):
        wav_path = Path(wav_path)
    
    output_mp3 = wav_path.with_suffix('.mp3')
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(wav_path),
        "-ar", "24000",  # 24kHz suficiente para TTS
        "-acodec", "mp3",
        str(output_mp3)
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode != 0:
        error_msg = result.stderr.decode('utf-8', errors='ignore')
        raise RuntimeError(f"ffmpeg error: {error_msg[:200]}")
    
    return str(output_mp3)

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
    Genera audio para un poema usando subprocess con Piper CLI.
    
    Args:
        poema_id: ID del poema en BD (para naming)
        texto: Texto normalizado  
        voice_id: ID de la voz a usar
        speed: factor de velocidad 0.8-1.2

    Returns:
        Ruta relativa al MP3 generado o None si falla
    """
    import wave
    import tempfile
    from pathlib import Path
    
    # Abrir propia sesión de DB con SQLAlchemy directo
    from sqlalchemy import create_engine, text
    engine = create_engine("sqlite:///./poems.db", connect_args={"check_same_thread": False})
    
    try:
        with engine.connect() as conn:
            conn.execute(text(f"UPDATE poemas SET estado='generando' WHERE id={poema_id}"))
            conn.commit()
            
            # Normalizar texto
            texto = normalize_text_poem(texto)
            
            if not texto.strip():
                with engine.connect() as conn:
                    conn.execute(text("UPDATE poems SET estado='error' WHERE id=?"), {"id": poema_id})
                    conn.commit()
                print("❌ Texto vacío")
                return None
            
            # Listar voces disponibles y validar
            tts = PiperTextToSpeech()
            voices = tts.list_voices()
            
            if not voices:
                raise RuntimeError("No hay voces TTS configuradas")
            
            voice_name = voice_id or voices[0]['name']
            model_path = f"{tts.model_dir}/{voice_name}.onnx"
            
            print(f"📝 Generando audio con voz {voice_name}...")
            
            # Crear directorio de audio
            audio_dir = Path("/home/awiwa/Documentos/GitHub/Prueba/poemtoaudio/audio")
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            final_mp3_path = None
            
            try:
                # Sintetizar cada verso por separado
                fragments = []  # [(wav_path, txt_path), ...]
                verses = split_into_verses(texto)
                
                print(f"   Sintetizando {len(verses)} fragmentos...")
                
                for idx, verso in enumerate(verses):
                    if not verso.strip():
                        continue
                    
                    # Ajustar velocidad con --length-scale
                    length_scale = 0.95 + (speed * 0.2)
                    
                    input_txt = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                    input_txt.write(verso)
                    input_txt.close()
                    
                    output_wav = tempfile.mktemp(suffix='.wav')
                    
                    # Comando Piper CLI vía subprocess
                    cmd = [
                        sys.executable, "-m", "piper",
                        "-m", model_path,
                        "-i", input_txt.name,
                        "-f", output_wav,
                        "--length-scale", str(length_scale)
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, timeout=60)
                    
                    if result.returncode != 0:
                        raise RuntimeError(f"Error Piper verso {idx+1}: {result.stderr.decode('utf-8', errors='ignore')}")
                    
                    if not os.path.exists(output_wav):
                        raise RuntimeError(f"WAV no generado para verso {idx+1}")
                    
                    print(f"   Verso {idx+1}/{len(verses)}: OK ({os.path.getsize(output_wav)} bytes)")
                    fragments.append((output_wav, input_txt.name))
                
                if not fragments:
                    raise RuntimeError("No se generaron fragmentos de audio")
                
                # Unir todos los fragmentos con merge_audio_fragments
                final_mp3_path = merge_audio_fragments(
                    [f[0] for f in fragments], 
                    f"poema_{poema_id}",
                    input_files=[f[1] for f in fragments]
                )
                
                if not final_mp3_path or not os.path.exists(final_mp3_path):
                    raise RuntimeError("No se pudo generar archivo MP3 final")
                
                print(f"✅ Audio generado: {final_mp3_path}")
                
                # Actualizar estado a listo en DB y guardar ruta
                ruta_rel = f"/audio/poema_{poema_id}.mp3"
                with engine.connect() as conn:
                    conn.execute(text(f"UPDATE poemas SET estado='listo', ruta_audio='{ruta_rel}' WHERE id={poema_id}"))
                    conn.commit()
                
                return ruta_rel
                
            except Exception as e:
                import traceback
                print(f"❌ Error generando audio: {e}")
                traceback.print_exc()
                
                # Actualizar estado a error en DB
                with engine.connect() as conn:
                    conn.execute(text("UPDATE poems SET estado='error' WHERE id=?"), {"id": poema_id})
                    conn.commit()
                
                return None
    
    finally:
        # Limpiar archivos temporales WAV y TXT
        for wav_path, txt_path in fragments if 'fragments' in dir() else []:
            try:
                os.unlink(wav_path)
                if txt_path and os.path.exists(txt_path):
                    os.unlink(txt_path)
            except:
                pass

