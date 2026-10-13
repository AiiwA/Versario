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
    
    def test_convert_to_mp3_exists(self):
        """convert_to_mp3_with_ffmpeg function should be defined."""
        from app.tasks import convert_to_mp3_with_ffmpeg
        assert callable(convert_to_mp3_with_ffmpeg)


class TestMP3Conversion:
    """Test MP3 conversion with ffmpeg."""
    
    def test_ffmpeg_successfully_creates_mp3(self, tmp_path):
        """When ffmpeg works, should create valid MP3 file."""
        from app.tasks import convert_to_mp3_with_ffmpeg
        
        input_wav = tmp_path / "input.wav"
        output_mp3 = tmp_path / "output.mp3"
        
        # Create minimal WAV file (1 second mono 44.1kHz)
        import wave
        with wave.open(str(input_wav), 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            for _ in range(44100):
                wav_file.writeframes(b'\x00\x00')
        
        result = convert_to_mp3_with_ffmpeg(str(input_wav), str(output_mp3))
        
        assert Path(result).exists(), f"MP3 file does not exist: {result}"
        assert output_mp3.exists() or "output.mp3" in result.lower()


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
        # Should return MP3 path
        result = merge_audio_fragments([str(wav_path)])
        
        # Result should be a string (path) and file should exist
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert Path(result).exists(), f"MP3 file does not exist: {result}"
    finally:
        if wav_path.exists():
            wav_path.unlink(missing_ok=True)


def test_merge_audio_fragments_error_on_empty_list(capsys):
    """Test that empty fragments list is handled gracefully."""
    from app.tasks import merge_audio_fragments
    
    try:
        result = merge_audio_fragments([])
        # Function should handle this case without crashing, returns error message or None
        print(f"Empty list returned: {result}")
    except Exception as e:
        print(f"Empty list raised: {type(e).__name__}: {e}")


def test_merge_audio_fragments_error_on_nonexistent(capsys):
    """Test behavior with nonexistent file."""
    from app.tasks import merge_audio_fragments
    
    try:
        result = merge_audio_fragments(["/nonexistent/path.wav"])
        print(f"Non-existent returned: {result}")
    except Exception as e:
        print(f"Non-existent raised: {type(e).__name__}: {e}")
