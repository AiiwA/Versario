"""
Test suite for audio processing functions in app/tasks.py

Tests merging fragments with correct pauses.
"""
import pytest
from pathlib import Path


class TestAudioFunctionsExist:
    """Test that required functions exist and are callable."""
    
    def test_merge_audio_fragments_exists(self):
        """merge_audio_fragments function should be defined."""
        from app.tasks import merge_audio_fragments
        assert callable(merge_audio_fragments)
    
    def test_normalize_text_exists(self):
        """normalize_text_poem function should be defined."""
        from app.tasks import normalize_text_poem
        assert callable(normalize_text_poem)
    
    def test_split_into_verses_exists(self):
        """split_into_verses function should be defined."""
        from app.tasks import split_into_verses
        assert callable(split_into_verses)


class TestMP3Conversion:
    """Test MP3 conversion with ffmpeg."""
    
    def test_ffmpeg_successfully_creates_mp3(self, tmp_path):
        """When ffmpeg works, should create valid MP3 file."""
        from app.tasks import merge_audio_fragments
        
        input_wav = tmp_path / "input.wav"
        
        # Create minimal WAV file (1 second mono 44.1kHz)
        import wave
        with wave.open(str(input_wav), 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            for _ in range(44100):
                wav_file.writeframes(b'\x00\x00')
        
        output_mp3 = str(tmp_path / "output.mp3")
        result = merge_audio_fragments([str(input_wav)], output_mp3)
        
        assert Path(result).exists(), f"MP3 file does not exist: {result}"


def test_merge_audio_fragments_with_single_fragment(audio_dir):
    """Test merge with single fragment converts to MP3."""
    from app.tasks import merge_audio_fragments
    import wave
    
    wav_path = Path(audio_dir) / "test_single.wav"
    
    # Create a valid WAV file (1 second of silence)
    with wave.open(str(wav_path), 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        for _ in range(44100):
            wav_file.writeframes(b'\x00\x00')
    
    try:
        # Output path is required now
        output_path = str(audio_dir / "output.mp3")
        result = merge_audio_fragments([str(wav_path)], output_path)
        
        # Result should be a string (path) and file should exist
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert Path(result).exists(), f"MP3 file does not exist: {result}"
    finally:
        if wav_path.exists():
            wav_path.unlink(missing_ok=True)
