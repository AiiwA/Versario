import subprocess
"""
Background tasks para Versario - Generación de audio simple con wave puro.

Este módulo maneja la generación asíncrona de audio para poemas usando:
- Piper TTS vía subprocess (CLI local)  
- wave module nativo de Python para concatenar fragmentos WAV
"""
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session


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
        sys.exit(1)


def normalize_text_poem(texto):
    """Normaliza el texto del poema para síntesis."""
    if not texto:
        return ""
    
    # Normalizar saltos de línea múltiples a doble salto
    text = '\n\n'.join(v.strip() for v in str(texto).split('\n\n'))
    
    return text.strip()


def split_into_verses(texto):
    """Separa un poema en versos individuales."""
    if not texto or not texto.strip():
        return []
    
    stanzas = [v for v in str(texto).split('\n\n') if v.strip()]
    
    verses = []
    for stanza in stanzas:
        for line in stanza.split('\n'):
            if line.strip():
                verses.append(line.strip())
    
    return verses


def merge_audio_fragments(fragments, output_base_path=None):
    """Une múltiples fragmentos WAV con silencios usando wave puro.
    
    Args:
        fragments: Lista de rutas absolutas a archivos .wav (mono 44kHz)
        output_base_path: Ruta base para nombre del archivo final
    
    Reglas de silencio:
        - 400ms entre versos normales  
        - 1000ms entre estrofas
    """
    import wave
    import struct
    
    if not fragments or len(fragments) < 1:
        raise RuntimeError("Debe proporcionarse al menos un fragmento WAV válido")
    
    # Crear directorio de salida
    audio_dir = Path("/home/awiwa/Documentos/GitHub/Prueba/poemtoaudio/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    if output_base_path:
        output_mp3 = str(audio_dir / f"{output_base_path}.mp3")
    else:
        output_mp3 = None
    
    # Leer y concatenar todos los fragmentos WAV
    final_audio_data = b""
    sample_rate = 44100
    
    try:
        for i, wav_path in enumerate(fragments):
            if not Path(wav_path).exists():
                print(f"⚠️ Fragmento no existe: {wav_path}")
                continue
            
            with wave.open(str(wav_path), 'rb') as wav_in:
                # Leer parámetros (asumimos todos iguales)
                params = wav_in.getparams()
                
                frames_data = wav_in.readframes(int(wav_in.getnframes()))
                
                if i > 0:
                    # Añadir silencio antes del fragmento actual
                    silence_samples = int(400 * sample_rate / 1000)  # 400ms
                    silence_data = b'\x00\x00' * silence_samples  # PCM 16-bit silencio
                    final_audio_data += silence_data
                
                final_audio_data += frames_data
        
        if not output_mp3:
            return None
        
        # Escribir WAV temporal unido
        temp_wav = tempfile.mktemp(suffix='.wav')
        
        with wave.open(temp_wav, 'wb') as wav_out:
            wav_out.setnchannels(params.channels)
            wav_out.setsampwidth(params.sampwidth)
            wav_out.setframerate(params.framerate)
            wav_out.writeframes(final_audio_data)
        
        # Convertir a MP3 con ffmpeg
        convert_to_mp3_with_ffmpeg(temp_wav, output_mp3)
        
        return output_mp3
        
    except Exception as e:
        import traceback
        print(f"❌ Error al unir audios: {e}")
        traceback.print_exc()
        # Borrar temporal si hay error
        if os.path.exists(temp_wav):
            try:
                os.unlink(temp_wav)
            except: pass
        return None


def convert_to_mp3_with_ffmpeg(wav_path, mp3_path):
    """Convierte WAV a MP3 con ffmpeg."""
    import subprocess
    
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Archivo WAV no existe: {wav_path}")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", wav_path,
        "-ar", "24000",  # 24kHz suficiente para TTS
        "-b:a", "64k",   # Calidad decente
        mp3_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode != 0:
        error_msg = result.stderr.decode('utf-8', errors='ignore')
        raise RuntimeError(f"ffmpeg error: {error_msg[:200]}")
    
    return mp3_path


def generate_audio_for_poem(poema_id, texto, voice_id, speed, db_path="poemas.db"):
    """
    Genera audio para un poema completo usando subprocess con Piper CLI.
    
    Args:
        poema_id: ID del poema (para naming de archivo)
        texto: Texto normalizado  
        voice_id: ID de la voz a usar
        speed: factor de velocidad 0.8-1.2
        db_path: Ruta base para nombres de archivos

    Returns:
        Ruta relativa al MP3 generado o None si falla
    """
    from app.tts.piper_provider import PiperTextToSpeech
    
    # Normalizar texto
    texto = normalize_text_poem(texto)
    
    if not texto.strip():
        raise ValueError("Texto vacío para síntesis")
    
    # Validar velocidad
    if not (0.8 <= speed <= 1.2):
        raise ValueError(f"Velocidad {speed} fuera de rango [0.8, 1.2]")
    
    # Listar voces disponibles y validar
    tts = PiperTextToSpeech()
    voices = tts.list_voices()
    
    if not voices:
        raise RuntimeError("No hay voces TTS configuradas")
    
    voice_name = voice_id or voices[0]['name']
    
    print(f"📝 Generando audio con voz {voice_name} para poema {poema_id}...")
    
    try:
        # Sintetizar cada verso por separado
        fragments = []
        verses = split_into_verses(texto)
        
        print(f"   Sintetizando {len(verses)} fragmentos...")
        
        for idx, verso in enumerate(verses):
            if not verso.strip():
                continue
            
            # Crear archivo temporal de entrada
            input_txt = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', 
                                                    delete=False, encoding='utf-8')
            input_txt.write(verso)
            input_txt.close()
            
            # Obtener modelo para la voz
            model_path = tts._find_model_for_voice(voice_name)[0] if hasattr(tts, '_find_model_for_voice') else None
            
            if not model_path:
                raise RuntimeError(f"No se encontró modelo para voz {voice_name}")
            
            output_wav = tempfile.mktemp(suffix='.wav')
            
            try:
                # Comando Piper CLI vía subprocess  
                cmd = [
                    sys.executable, "-m", "piper",
                    "-m", model_path,
                    "-i", input_txt.name,
                    "-f", output_wav,
                    "--length-scale", "1.0"  # Simplificado a velocidad normal por ahora
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=120)
                
                if result.returncode != 0:
                    error_msg = result.stderr.decode('utf-8', errors='ignore')
                    raise RuntimeError(f"Error Piper verso {idx+1}")
                
                # Guardar en carpeta de audio
                audio_dir = Path("/home/awiwa/Documentos/GitHub/Prueba/poemtoaudio/audio")
                
                # Copiar el WAV generado al directorio del proyecto
                output_wav_copied = str(audio_dir / f"temp_{idx}.wav")
                import shutil
                if os.path.exists(output_wav):
                    shutil.copy2(output_wav, output_wav_copied)
                
                print(f"   Verso {idx+1}/{len(verses)}: OK")
                fragments.append(str(output_wav_copied))
                
            except Exception as e:
                raise
            
            finally:
                try:
                    os.unlink(input_txt.name)
                except: pass
        
        if not fragments:
            raise RuntimeError("No se generaron fragmentos de audio")
        
        # Unir todos los fragmentos
        final_mp3_path = merge_audio_fragments(
            fragments, 
            f"poema_{poema_id}"
        )
        
        if final_mp3_path and os.path.exists(final_mp3_path):
            print(f"✅ Audio generado: {final_mp3_path}")
            
            # Actualizar estado en DB usando SQLAlchemy
            from app.models import Poema
            
            with Session(db_path) as db:
                poem = db.get(Poema, poema_id)
                if poem:
                    poem.estado = "listo"
                    poem.ruta_audio = f"/audio/poema_{poema_id}.mp3"
                    db.commit()
            
            return f"/audio/poema_{poema_id}.mp3"
        
        raise RuntimeError("No se pudo generar archivo MP3 final")
        
    except Exception as e:
        import traceback
        print(f"❌ Error generando audio: {e}")
        traceback.print_exc()
        
        # Actualizar estado a error
        from app.models import Poema
        
        with Session(db_path) as db:
            poem = db.get(Poema, poema_id)
            if poem:
                poem.estado = "error"
                db.commit()
        
        return None

