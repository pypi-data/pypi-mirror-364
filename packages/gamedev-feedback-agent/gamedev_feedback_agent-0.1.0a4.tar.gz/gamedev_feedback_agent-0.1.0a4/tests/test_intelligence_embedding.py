import pytest
from unittest.mock import patch, MagicMock
from intelligence import embedding

def test_get_embedding_provider():
    with patch('intelligence.embedding.IntelligenceConfig.EMBEDDING_PROVIDER', 'openai'):
        provider = embedding.get_embedding_provider()
        assert provider.__class__.__name__ == "OpenAIEmbeddingProvider"

    with patch('intelligence.embedding.IntelligenceConfig.EMBEDDING_PROVIDER', 'ollama'):
        provider = embedding.get_embedding_provider()
        assert provider.__class__.__name__ == "OllamaEmbeddingProvider"

    with patch('intelligence.embedding.IntelligenceConfig.EMBEDDING_PROVIDER', 'unknown'):
        with pytest.raises(ValueError):
            embedding.get_embedding_provider()
            
def test_get_fallback_embedding_provider_list():
    fallback_list = embedding.get_fallback_embedding_provider_list()
    assert isinstance(fallback_list, list)
    assert len(fallback_list) > 0
    assert "openai" in fallback_list or "ollama" in fallback_list

def test_get_embedding_provider_by_name():
    provider = embedding.get_embedding_provider_by_name("openai")
    assert provider.__class__.__name__ == "OpenAIEmbeddingProvider"

    provider = embedding.get_embedding_provider_by_name("ollama")
    assert provider.__class__.__name__ == "OllamaEmbeddingProvider"

    with pytest.raises(ValueError):
        embedding.get_embedding_provider_by_name("unknown")
        


def test_get_text_embedding():
    with patch('intelligence.embedding.get_embedding_provider') as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider

        mock_provider.create_embedding.return_value = [0.1, 0.2, 0.3]

        result = embedding.get_text_embedding("This is a test.")
        assert result == [0.1, 0.2, 0.3]
        mock_get_provider.assert_called_once()
        mock_provider.create_embedding.assert_called_once_with("This is a test.")
        
        
def test_get_text_embedding_fallback():
    # Simulate main provider failure, fallback succeeds
    with patch('intelligence.embedding.get_embedding_provider') as mock_get_provider, \
         patch('intelligence.embedding.get_fallback_embedding_provider_list') as mock_fallback_list, \
         patch('intelligence.embedding.get_embedding_provider_by_name') as mock_by_name:

        # Main provider raises exception
        mock_get_provider.side_effect = Exception("Main provider failed")
        # Fallback list returns two providers
        mock_fallback_list.return_value = ["openai", "ollama"]
        # Fallback provider returns embedding for "ollama"
        mock_by_name.side_effect = [
            Exception("OpenAI failed"),  # First fallback fails
            MagicMock(create_embedding=MagicMock(return_value=[0.4, 0.5, 0.6]))  # Second fallback succeeds
        ]

        result = embedding.get_text_embedding("Fallback test")
        assert result == []
        assert mock_get_provider.call_count == 1
        assert mock_fallback_list.call_count == 1
        assert mock_by_name.call_count == 1
        
        result = embedding.get_text_embedding("Fallback test")
        assert result == [0.4, 0.5, 0.6]
        assert mock_by_name.call_count == 2  # Called twice, once for each fallback provider


def test_batch_get_text_embeddings():
    with patch('intelligence.embedding.get_embedding_provider') as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        mock_provider.batch_create_embeddings.return_value = ("openai", [[0.1, 0.2], [0.3, 0.4]])

        result = embedding.batch_get_text_embeddings(["text1", "text2"])
        assert result == ("openai", [[0.1, 0.2], [0.3, 0.4]])
        mock_get_provider.assert_called_once()
        mock_provider.batch_create_embeddings.assert_called_once_with(["text1", "text2"])

    # Simulate main provider failure, fallback succeeds
    with patch('intelligence.embedding.get_embedding_provider') as mock_get_provider, \
            patch('intelligence.embedding.get_fallback_embedding_provider_list') as mock_fallback_list, \
            patch('intelligence.embedding.get_embedding_provider_by_name') as mock_by_name:

        mock_get_provider.side_effect = Exception("Main provider failed")
        mock_fallback_list.return_value = ["openai", "ollama"]
        mock_by_name.side_effect = [
            Exception("OpenAI failed"),
            MagicMock(batch_create_embeddings=MagicMock(return_value=("ollama", [[0.5, 0.6], [0.7, 0.8]])))
        ]

        result = embedding.batch_get_text_embeddings(["text3", "text4"])
        assert result == ("unknown", [])
        assert mock_get_provider.call_count == 1
        assert mock_fallback_list.call_count == 1
        assert mock_by_name.call_count == 1
        
        result = embedding.batch_get_text_embeddings(["text3", "text4"])
        assert result == ("ollama", [[0.5, 0.6], [0.7, 0.8]])
        assert mock_by_name.call_count == 2  # Called twice, once for each fallback
