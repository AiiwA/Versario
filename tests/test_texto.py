"""
Test suite para funciones de procesamiento de texto en app/tasks.py
"""
import pytest
from app.tasks import normalize_text_poem, split_into_verses


class TestNormalizeTextPoem:
    """Tests para normalize_text_poem"""
    
    def test_empty_string_returns_empty(self):
        assert normalize_text_poem("") == ""
    
    def test_whitespace_only_returns_empty(self):
        assert normalize_text_poem("   \n\t\n  ") == ""
    
    def test_preserves_double_newlines_for_stanzas(self):
        text = "Primer verso\n\nSegundo verso"
        result = normalize_text_poem(text)
        assert "\n\n" in result
    
    def test_trims_leading_trailing_whitespace(self):
        text = "  \nHola mundo\n  \n  "
        result = normalize_text_poem(text)
        # Debe empezar con "Hola" y terminar sin espacio
        assert result.startswith("Hola")
    
    def test_preserves_punctuation_accentos(self):
        text = "¡Ay! ¿Cómo?"
        result = normalize_text_poem(text)
        assert result == "¡Ay! ¿Cómo?"


class TestSplitIntoVerses:
    """Tests para split_into_verses"""
    
    def test_single_stanza_multiple_lines(self):
        texto = "Hola mundo\n\nEsta es una segunda línea"
        result = split_into_verses(texto)
        assert len(result) == 2
    
    def test_two_stanzas_multiple_lines(self):
        texto = "Primer verso\n\nSegundo verso\n\nTercer verso"
        result = split_into_verses(texto)
        assert len(result) == 3
    
    def test_multiple_consecutive_newlines_count_as_one_stanza_change(self):
        texto = "Verso 1\n\n\n\nVerso 2"
        result = split_into_verses(texto)
        assert len(result) == 2
    
    def test_empty_text_returns_empty_list(self):
        assert split_into_verses("") == []
        assert split_into_verses("   \n\n  ") == []
    
    def test_preserves_punctuation_accentos(self):
        texto = "¡Ay!\n\n¿Cómo?"
        result = split_into_verses(texto)
        assert len(result) == 2
    
    def test_windows_line_endings_handled(self):
        texto = "Hola mundo\r\n\r\nAdiós"
        result = split_into_verses(texto)
        assert len(result) == 2
    
    def test_empty_lines_in_stanza_ignored(self):
        texto = "Linea uno\n\n   \nLinea tres"
        result = split_into_verses(texto)
        assert len(result) == 2
