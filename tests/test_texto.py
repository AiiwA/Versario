"""
Test suite for text processing functions in app/tasks.py

Tests separation of verses and stanzas in poetry.
"""
import pytest
from app.tasks import normalize_text_poem, split_into_verses


class TestNormalizeTextPoem:
    """Tests for normalize_text_poem function."""
    
    def test_empty_string_returns_empty(self):
        """Empty string should return empty string."""
        assert normalize_text_poem("") == ""
    
    def test_whitespace_only_returns_empty(self):
        """Whitespace only should return empty string."""
        assert normalize_text_poem("   \n\t\n  ") == ""
    
    def test_removes_extra_spaces_in_lines(self):
        """Multiple spaces in lines should be normalized to single space."""
        text = "Hola    mundo\n\nAdiós"
        result = normalize_text_poem(text)
        assert "  " not in result  # No double spaces
    
    def test_preserves_double_newlines_for_stanzas(self):
        """Double newlines mark stanza separation and should be preserved."""
        text = "Primer verso\n\nSegundo verso"
        result = normalize_text_poem(text)
        assert "\n\n" in result
    
    def test_trims_leading_trailing_whitespace(self):
        """Leading and trailing whitespace should be removed."""
        text = "  \nHola mundo\n  \n  "
        result = normalize_text_poem(text)
        assert result.startswith("Hola")
        assert not result.endswith(" ")
    
    def test_preserves_punctuation_accentos(self):
        """Punctuation and accents should be preserved exactly."""
        text = "¡Ay! ¿Cómo?"
        result = normalize_text_poem(text)
        assert result == "¡Ay! ¿Cómo?"


class TestSplitIntoVerses:
    """Tests for split_into_verses function."""
    
    def test_single_stanza_multiple_lines(self):
        """Single stanza with multiple lines should return all as verses."""
        texto = "Hola mundo\n\nEsta es una segunda línea"
        result = split_into_verses(texto)
        assert len(result) == 2
        assert result[0] == "Hola mundo"
        assert result[1] == "Esta es una segunda línea"
    
    def test_two_stanzas_multiple_lines(self):
        """Two stanzas should have correct separation."""
        texto = "Primer verso\n\nSegundo verso\n\nTercer verso"
        result = split_into_verses(texto)
        # Should be 3 verses: ["Primer verso", "Segundo verso", "Tercer verso"]
        assert len(result) == 3
        assert result[0] == "Primer verso"
        assert result[1] == "Segundo verso"
        assert result[2] == "Tercer verso"
    
    def test_multiple_consecutive_newlines_count_as_one_stanza_change(self):
        """Multiple blank lines should count as single stanza separator."""
        texto = "Verso 1\n\n\n\nVerso 2"
        result = split_into_verses(texto)
        assert len(result) == 2
        assert result[0] == "Verso 1"
        assert result[1] == "Verso 2"
    
    def test_empty_text_returns_empty_list(self):
        """Empty or whitespace-only text returns empty list."""
        assert split_into_verses("") == []
        assert split_into_verses("   \n\n  ") == []
    
    def test_preserves_punctuation_accentos(self):
        """Punctuation and accents must remain unchanged."""
        texto = "¡Ay!\n\n¿Cómo?"
        result = split_into_verses(texto)
        assert len(result) == 2
        assert result[0] == "¡Ay!"
        assert result[1] == "¿Cómo?"
    
    def test_windows_line_endings_handled(self):
        """Windows line endings (\\r\\n) should be handled same as \\n."""
        texto = "Hola mundo\r\n\r\nAdiós"
        result = split_into_verses(texto)
        assert len(result) == 2
        assert result[0] == "Hola mundo"
        assert result[1] == "Adiós"
    
    def test_empty_lines_in_stanza_ignored(self):
        """Empty lines within a stanza are ignored, only non-empty count."""
        texto = "Linea uno\n\n   \nLinea tres"
        result = split_into_verses(texto)
        assert len(result) == 2  # Empty line in middle is skipped
        assert result[0] == "Linea uno"
        assert result[1] == "Linea tres"
