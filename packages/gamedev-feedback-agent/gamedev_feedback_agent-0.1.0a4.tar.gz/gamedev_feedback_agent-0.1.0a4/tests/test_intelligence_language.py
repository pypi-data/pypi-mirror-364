import pytest
from intelligence import language
from unittest.mock import MagicMock, patch, AsyncMock, ANY
from langdetect.lang_detect_exception import LangDetectException
from intelligence.language import LANGUAGE_MAPPING

def test_detect_language():
    text = "Hello, how are you?"
    lang, confidence = language.detect_language(text)
    assert lang == "en"
    assert confidence > 0.5

def test_detect_language_unknown():
    text = "palsh efw xvpp er adegrg aa"
    lang, confidence = language.detect_language(text)
    assert lang != "en"
    assert confidence < 0.9

def test_detect_language_error_handling():
    # Passing None should return ("unknown", 0.0) instead of raising an exception
    lang, confidence = language.detect_language(None)
    assert lang == "unknown"
    assert confidence == 0.0

    lang, confidence = language.detect_language("This is a test.")
    assert lang == "en"
    assert confidence > 0.5
    
    with patch('intelligence.language.detect_langs') as mock_detect_langs:
        mock_detect_langs.side_effect = LangDetectException("error", 0.0)
        lang, confidence = language.detect_language("This will raise an exception")
        assert lang == "unknown"
        assert confidence == 0.0
        

def test_get_translation_provider():
    with patch('intelligence.language.IntelligenceConfig.TRANSLATION_PROVIDER', 'openai'):
        provider = language.get_translation_provider()
        assert provider.__class__.__name__ == "OpenAITranslationProvider"

    with patch('intelligence.language.IntelligenceConfig.TRANSLATION_PROVIDER', 'ollama'):
        provider = language.get_translation_provider()
        assert provider.__class__.__name__ == "OllamaTranslationProvider"

    with patch('intelligence.language.IntelligenceConfig.TRANSLATION_PROVIDER', 'unknown'):
        with pytest.raises(ValueError):
            language.get_translation_provider()
            
def test_get_fallback_translation_provider_list():
    fallback_list = language.get_fallback_translation_provider_list()
    assert isinstance(fallback_list, list)
    assert len(fallback_list) > 0
    assert "openai" in fallback_list or "ollama" in fallback_list
    
    
def test_get_translation_provider_by_name():
    provider = language.get_translation_provider_by_name("openai")
    assert provider.__class__.__name__ == "OpenAITranslationProvider"

    provider = language.get_translation_provider_by_name("ollama")
    assert provider.__class__.__name__ == "OllamaTranslationProvider"

    with pytest.raises(ValueError):
        language.get_translation_provider_by_name("unknown")
        
        

def test_translate_text():
    with patch('intelligence.language.get_translation_provider') as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider

        mock_provider.translate.return_value = "Hola, ¿cómo estás?"

        result = language.translate_text("Hello, how are you?", target_lang="es")
        assert result == "Hola, ¿cómo estás?"
        mock_get_provider.assert_called_once()
        mock_provider.translate.assert_called_once_with("Hello, how are you?", "es")


def test_translate_text_fallback():
    with patch('intelligence.language.get_translation_provider') as mock_get_provider \
        , patch('intelligence.language.get_fallback_translation_provider_list') as mock_get_fallback \
        , patch('intelligence.language.get_translation_provider_by_name') as mock_get_provider_by_name:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        mock_get_fallback.return_value = ["openai", "ollama"]
        mock_provider_by_name = MagicMock()
        mock_get_provider_by_name.side_effect = [mock_provider, mock_provider]

        mock_provider.translate.side_effect = Exception("Translation error")

        result = language.translate_text("Hello, how are you?", target_lang="es")
        assert result == "Hello, how are you?"
        mock_get_provider.assert_called_once()
        assert mock_provider.translate.call_count == 2
        

def test_translate_text_fallback_no_providers():
    with patch('intelligence.language.get_translation_provider') as mock_get_provider \
        , patch('intelligence.language.get_fallback_translation_provider_list') as mock_get_fallback \
        , patch('intelligence.language.get_translation_provider_by_name') as mock_get_provider_by_name:
        
        mock_get_provider.return_value = None
        mock_get_fallback.return_value = []


        result = language.translate_text("Hello, how are you?", target_lang="es")
        assert result == "Hello, how are you?"
        mock_get_provider.assert_called_once()
        

def test_translate_text_fallback_once():
    with patch('intelligence.language.get_translation_provider') as mock_get_provider \
        , patch('intelligence.language.get_fallback_translation_provider_list') as mock_get_fallback \
        , patch('intelligence.language.get_translation_provider_by_name') as mock_get_provider_by_name:
        
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        mock_get_fallback.return_value = ["openai", "ollama"]
        mock_get_provider_by_name.side_effect = [mock_provider, mock_provider]

        mock_provider.translate.side_effect = [Exception("Translation error"), "Hola, ¿cómo estás?"]

        result = language.translate_text("Hello, how are you?", target_lang="es")
        assert result == "Hola, ¿cómo estás?"
        assert mock_provider.translate.call_count == 2
        
        

def test_detect_post_language_all(capsys):
    with patch('intelligence.language.get_session') as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        mock_posts = [MagicMock(content="Hello, how are you?"),
                      MagicMock(content="Hola, ¿cómo estás?")]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_posts

        language.detect_post_language_all(show_stats=True)

        for post in mock_posts:
            assert post.language in LANGUAGE_MAPPING
            assert post.language_confidence > 0.0

        # query error
        mock_session.query.side_effect = Exception("Database error")
        language.detect_post_language_all(show_stats=True)
        captured = capsys.readouterr()
        assert "Error processing posts" in captured.out