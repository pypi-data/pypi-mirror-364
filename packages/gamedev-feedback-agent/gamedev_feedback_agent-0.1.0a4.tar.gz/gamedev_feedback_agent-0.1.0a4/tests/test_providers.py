import pytest
from intelligence.providers.base_provider import TranslationProvider, SentimentProvider, EmbeddingProvider
from intelligence.providers.openai_provider import OpenAITranslationProvider, OpenAISentimentProvider, OpenAIEmbeddingProvider
from intelligence.providers.ollama_provider import OllamaTranslationProvider, OllamaSentimentProvider, OllamaEmbeddingProvider

from unittest.mock import MagicMock, patch, AsyncMock, ANY

class DummyTranslationProvider(TranslationProvider):
    def translate(self, text: str, target_lang: str = "English") -> str:
        return f"{text} in {target_lang}"

class DummySentimentProvider(SentimentProvider):
    def analyze_sentiment(self, text: str) -> tuple[str, float]:
        return ("positive", 0.9)
    def batch_analyze_sentiment(self, texts: list[str]) -> list[tuple[str, float]]:
        return [self.analyze_sentiment(t) for t in texts]

class DummyEmbeddingProvider(EmbeddingProvider):
    def create_embedding(self, text: str, model: str) -> tuple[str, list[float]]:
        return (model, [1.0, 2.0, 3.0])
    def batch_create_embeddings(self, texts: list[str], model: str) -> tuple[str, list[list[float]]]:
        return (model, [[1.0, 2.0, 3.0] for _ in texts])

def test_translation_provider():
    provider = DummyTranslationProvider()
    result = provider.translate("Hello", "French")
    assert result == "Hello in French"

def test_sentiment_provider():
    provider = DummySentimentProvider()
    sentiment, score = provider.analyze_sentiment("Great job!")
    assert sentiment == "positive"
    assert score == 0.9

def test_batch_sentiment_provider():
    provider = DummySentimentProvider()
    results = provider.batch_analyze_sentiment(["Good", "Bad"])
    assert results == [("positive", 0.9), ("positive", 0.9)]

def test_embedding_provider():
    provider = DummyEmbeddingProvider()
    model, embedding = provider.create_embedding("Test", "model1")
    assert model == "model1"
    assert embedding == [1.0, 2.0, 3.0]

def test_batch_embedding_provider():
    provider = DummyEmbeddingProvider()
    model, embeddings = provider.batch_create_embeddings(["A", "B"], "model2")
    assert model == "model2"
    assert embeddings == [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
    

# mock openai provider
# test translate
@patch('intelligence.providers.openai_provider.OpenAITranslationProvider.get_client')
def test_openai_translation_provider(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_message = MagicMock()
    mock_message.content = "Hello in French"

    mock_choices = MagicMock()
    mock_choices.message = mock_message
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choices]
    mock_client.chat.completions.create.return_value = mock_completion

    provider = OpenAITranslationProvider()
    result = provider.translate("Hello", "French")
    assert result == "Hello in French"
    
def test_openai_translation_provider_no_key():
    with patch('intelligence.intelligence_config.IntelligenceConfig.OPENAI_API_KEY', ''):
        provider = OpenAITranslationProvider()
        with pytest.raises(ValueError, match="OpenAI API key is not set"):
            provider.get_client()
        
def test_openai_translation_provider_error():
    with patch('intelligence.providers.openai_provider.OpenAITranslationProvider.get_client') as mock_get_client:
        mock_get_client.side_effect = ValueError("OpenAI API key is not set")
        provider = OpenAITranslationProvider()
        result = provider.translate("Hello", "French")
        assert result == "Hello"
        
def test_openai_translation_provider_unexpected_error():
    with patch('intelligence.providers.openai_provider.OpenAITranslationProvider.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Unexpected error")
        
        provider = OpenAITranslationProvider()
        result = provider.translate("Hello", "French")
        assert result == "Hello"
        
def test_openai_sentiment_provider():
    with patch('intelligence.providers.openai_provider.OpenAI') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="positive | 0.95"))]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAISentimentProvider()
        sentiment, score = provider.analyze_sentiment("Great job!")
        assert sentiment == "positive"
        assert score == 0.95
        
        
def test_openai_sentiment_provider_error():
    with patch('intelligence.providers.openai_provider.OpenAI') as mock_get_client:
        mock_get_client.side_effect = ValueError("OpenAI API key is not set")
        provider = OpenAISentimentProvider()
        sentiment, score = provider.analyze_sentiment("Great job!")
        assert sentiment == "unknown"
        assert score == -1.0

def test_openai_sentiment_provider_unexpected_error():
    with patch('intelligence.providers.openai_provider.OpenAI') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Unexpected error")
        
        provider = OpenAISentimentProvider()
        sentiment, score = provider.analyze_sentiment("Great job!")
        assert sentiment == "unknown"
        assert score == -1.0
        
def test_openai_sentiment_provider_batch():
    with patch('intelligence.providers.openai_provider.OpenAI') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="1 : positive | 0.95\n2 : positive | 0.95"))]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAISentimentProvider()
        results = provider.batch_analyze_sentiment(["Great job!", "Bad job!"])
        assert results == [(1, "positive", 0.95), (2, "positive", 0.95)]
        
def test_openai_sentiment_provider_length_mismatch():
    with patch('intelligence.providers.openai_provider.OpenAI') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="1 : positive | 0.95"))]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAISentimentProvider()
        results = provider.batch_analyze_sentiment(["Great job!", "Bad job!"])
        assert results == [(1, "positive", 0.95), (-1, "mismatch", -1.0)]
        
def test_openai_embedding_provider():
    with patch('intelligence.providers.openai_provider.OpenAI') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[1.0, 2.0, 3.0])]
        mock_client.embeddings.create.return_value = mock_response
        
        provider = OpenAIEmbeddingProvider()
        model, embedding = provider.create_embedding("Test")
        assert "openai" in model
        assert embedding == [1.0, 2.0, 3.0]
        
def test_openai_embedding_provider_batch():
    with patch('intelligence.providers.openai_provider.OpenAI') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[1.0, 2.0, 3.0], index=1) for _ in range(3)]
        mock_client.embeddings.create.return_value = mock_response
        
        provider = OpenAIEmbeddingProvider()
        model, embeddings = provider.batch_create_embeddings(["A", "B", "C"])
        assert "openai" in model
        assert embeddings == [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
        

def test_ollama_translation_provider():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        # OllamaTranslationProvider expects res.text to be a JSON string with a "response" key
        mock_response.text = '{"response": "Hello in French"}\n'
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        provider = OllamaTranslationProvider()
        result = provider.translate("Hello", "French")
        assert result == "Hello in French"
        
def test_ollama_translation_provider_error():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        provider = OllamaTranslationProvider()
        result = provider.translate("Hello", "French")
        assert result == "Hello"
        
def test_ollama_sentiment_provider():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        # OllamaSentimentProvider expects res.json()["response"] to be a string with sentiment and score
        mock_response.json.return_value = {"response": "positive | 0.95"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        provider = OllamaSentimentProvider()
        sentiment, score = provider.analyze_sentiment("Great job!")
        assert sentiment == "positive"
        assert score == 0.95

def test_ollama_sentiment_provider_error():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        provider = OllamaSentimentProvider()
        sentiment, score = provider.analyze_sentiment("Great job!")
        assert sentiment == "unknown"
        assert score == -1.0
        
def test_ollama_sentiment_provider_unexpected_response():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "unexpected format"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        provider = OllamaSentimentProvider()
        sentiment, score = provider.analyze_sentiment("Great job!")
        assert sentiment == "unknown"
        assert score == -1.0
        
def test_ollama_sentiment_provider_batch():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        # Mocking a response for batch sentiment analysis
        mock_response.json.return_value = {"response": "1 : positive | 0.95\n2 : negative | 0.85"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        provider = OllamaSentimentProvider()
        results = provider.batch_analyze_sentiment(["Great job!", "Bad job!"])
        assert results == [(1, "positive", 0.95), (2, "negative", 0.85)]
        
def test_ollama_sentiment_provider_batch_bad_response():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        # Mocking a response for batch sentiment analysis with unexpected format
        mock_response.json.return_value = {"response": "1 : positive | 0.95\n2 : mismatch"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        provider = OllamaSentimentProvider()
        results = provider.batch_analyze_sentiment(["Great job!", "Bad job!"])
        assert results == [(1, "positive", 0.95), (-1, "mismatch", -1.0)]

        mock_response.json.return_value = {"response": "no the vertical bar symbol found"}
        results = provider.batch_analyze_sentiment(["Great job!", "Bad job!"])
        assert results == [(-1, "unknown", -1.0), (-1, "unknown", -1.0)]


def test_ollama_extract_sentiment_from_response():
    provider = OllamaSentimentProvider()
    response = "positive | 0.95"
    label, score = provider.extract_sentiment_from_response(response)
    assert label == "positive"
    assert score == 0.95
    
    response2 = "sentiment: negative | 0.85"
    label, score = provider.extract_sentiment_from_response(response2)
    assert label == "negative"
    assert score == 0.85
    
    response3 = "sentiment: neutral | 0.75"
    label, score = provider.extract_sentiment_from_response(response3)
    assert label == "neutral"
    assert score == 0.75
    
    response4 = "sentiment | positive | 0.90"
    label, score = provider.extract_sentiment_from_response(response4)
    assert label == "positive"
    assert score == 0.90
    
    response5 = "noexistinglabel | 0.50"
    label, score = provider.extract_sentiment_from_response(response5)
    assert label == "unknown"
    assert score == 0.0
    
    response6 = "positive | 1.95 # score out of range"
    label, score = provider.extract_sentiment_from_response(response6)
    assert label == "positive"
    assert score == 0.0

def test_ollama_embedding_provider(capsys):
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        # OllamaEmbeddingProvider expects res.json() to return a dict with "embedding" as a list
        mock_response.json.return_value = {"embedding": [1.0, 2.0, 3.0]}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        provider = OllamaEmbeddingProvider()
        provider.OLLAMA_EMBEDDING_LENGTH = 3  # Ensure length matches for test
        model, embedding = provider.create_embedding("Test")
        assert "ollama" in model
        assert embedding == [1.0, 2.0, 3.0]
        
        provider.OLLAMA_EMBEDDING_LENGTH = 2
        provider.create_embedding("Test")
        out, err = capsys.readouterr()
        assert "Embedding length mismatch" in out
        
        
        
        
def test_ollama_embedding_provider_error():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        provider = OllamaEmbeddingProvider()
        model, embedding = provider.create_embedding("Test")
        assert "unknown" in model
        assert embedding == []
        

def test_ollama_embedding_provider_batch():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_response = MagicMock()
        # Mocking a response for batch embedding analysis
        mock_response.json.return_value = {"embedding": [1.0, 2.0, 3.0]}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        provider = OllamaEmbeddingProvider()
        provider.OLLAMA_EMBEDDING_LENGTH = 3  # Ensure length matches for test
        model, embeddings = provider.batch_create_embeddings(["A", "B", "C"])
        assert "ollama" in model
        assert embeddings == [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
        

        
        
        
def test_ollama_exceptions():
    with patch('intelligence.providers.ollama_provider.requests.post') as mock_post:
        mock_post.side_effect = Exception("Network error")
        
        provider = OllamaTranslationProvider()
        result = provider.translate("Hello", "French")
        assert result == "Hello"
        
        provider = OllamaSentimentProvider()
        sentiment, score = provider.analyze_sentiment("Great job!")
        assert sentiment == "unknown"
        assert score == 0.0
        
        provider = OllamaEmbeddingProvider()
        model, embedding = provider.create_embedding("Test")
        assert "unknown" in model
        assert embedding == []