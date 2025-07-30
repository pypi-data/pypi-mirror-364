import pytest

from intelligence import sentiment
from unittest.mock import MagicMock, patch, AsyncMock, ANY
from intelligence.sentiment import analyze_post_sentiment


def test_get_sentiment_provider():
    with patch('intelligence.sentiment.IntelligenceConfig.SENTIMENT_PROVIDER', 'openai'):
        provider = sentiment.get_sentiment_provider()
        assert provider.__class__.__name__ == "OpenAISentimentProvider"

    with patch('intelligence.sentiment.IntelligenceConfig.SENTIMENT_PROVIDER', 'ollama'):
        provider = sentiment.get_sentiment_provider()
        assert provider.__class__.__name__ == "OllamaSentimentProvider"

    with patch('intelligence.sentiment.IntelligenceConfig.SENTIMENT_PROVIDER', 'unknown'):
        with pytest.raises(ValueError):
            sentiment.get_sentiment_provider()
            
def test_get_fallback_sentiment_provider_list():
    fallback_list = sentiment.get_fallback_sentiment_provider_list()
    assert isinstance(fallback_list, list)
    assert len(fallback_list) > 0
    assert "openai" in fallback_list or "ollama" in fallback_list
    
def test_get_sentiment_provider_by_name():
    provider = sentiment.get_sentiment_provider_by_name("openai")
    assert provider.__class__.__name__ == "OpenAISentimentProvider"

    provider = sentiment.get_sentiment_provider_by_name("ollama")
    assert provider.__class__.__name__ == "OllamaSentimentProvider"

    with pytest.raises(ValueError):
        sentiment.get_sentiment_provider_by_name("unknown")
        
    
def test_get_text_sentiment():
    with patch('intelligence.sentiment.get_sentiment_provider') as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider

        mock_provider.analyze_sentiment.return_value = ("positive", 0.95)

        result = sentiment.get_text_sentiment("This is a great day!")
        assert result == ("positive", 0.95)
        mock_get_provider.assert_called_once()
        mock_provider.analyze_sentiment.assert_called_once_with("This is a great day!")

def test_get_text_sentiment_fallback():
    with patch('intelligence.sentiment.get_sentiment_provider') as mock_get_provider, \
         patch('intelligence.sentiment.get_fallback_sentiment_provider_list', return_value=["openai", "ollama"]), \
         patch('intelligence.sentiment.get_sentiment_provider_by_name') as mock_get_by_name:

        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        mock_provider.analyze_sentiment.side_effect = Exception("Sentiment analysis error")

        # All fallback providers also raise exceptions
        mock_fallback_provider = MagicMock()
        mock_fallback_provider.analyze_sentiment.side_effect = Exception("Fallback error")
        mock_get_by_name.return_value = mock_fallback_provider

        result = sentiment.get_text_sentiment("This is a great day!")
        assert result == ("unknown", 0.0)
        mock_get_provider.assert_called_once()
        assert mock_get_by_name.call_count == 1
        
        
        
def test_get_text_sentiment_batch():
    with patch('intelligence.sentiment.get_sentiment_provider') as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider

        mock_provider.batch_analyze_sentiment.return_value = [
            (0, "positive", 0.95),
            (1, "negative", 0.85),
            (2, "neutral", 0.75)
        ]

        texts = ["This is great!", "This is bad.", "This is okay."]
        result = sentiment.batch_get_text_sentiment(texts)

        assert len(result) == 3
        assert result[0] == (0, "positive", 0.95)
        assert result[1] == (1, "negative", 0.85)
        assert result[2] == (2, "neutral", 0.75)

        mock_get_provider.assert_called_once()
        mock_provider.batch_analyze_sentiment.assert_called_once_with(texts)
        
        mock_provider.batch_analyze_sentiment.return_value = []
        result = sentiment.batch_get_text_sentiment(texts)
        assert result == []
        
        mock_provider.batch_analyze_sentiment.side_effect = Exception("Batch analysis error")
        result = sentiment.batch_get_text_sentiment(texts)
        assert result == []


@patch('intelligence.sentiment.get_session')
@patch('intelligence.sentiment.get_text_sentiment')
@patch('intelligence.sentiment.close_session')
def test_analyze_post_sentiment(mock_close_session, mock_get_text_sentiment, mock_get_session):
    # Setup mock session and models
    mock_session = MagicMock()
    mock_get_session.return_value = mock_session

    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "This is a test post."
    mock_analysis = MagicMock()
    mock_analysis.post_id = 1
    mock_analysis.sentiment_label = "positive"
    mock_analysis.sentiment_score = 0.9

    # Case 1: Post not found
    mock_session.query().filter().first.side_effect = [None]
    result = analyze_post_sentiment(1)
    assert result == ("unknown", 0.0)

    # Case 2: Analysis exists and force_write is False
    mock_session.query().filter().first.side_effect = [mock_post, mock_analysis]
    result = analyze_post_sentiment(1)
    assert result == ("positive", 0.9)

    # Case 3: Analysis exists and force_write is True
    mock_get_text_sentiment.return_value = ("neutral", 0.7)
    mock_session.query().filter().first.side_effect = [mock_post, mock_analysis]
    result = analyze_post_sentiment(1, force_write=True)
    assert result == ("neutral", 0.7)
    assert mock_analysis.sentiment_label == "neutral"
    assert mock_analysis.sentiment_score == 0.7
    mock_session.commit.assert_called()

    # Case 4: No analysis exists
    mock_session.query().filter().first.side_effect = [mock_post, None]
    mock_get_text_sentiment.return_value = ("negative", 0.2)
    result = analyze_post_sentiment(1)
    assert result == ("negative", 0.2)
    mock_session.add.assert_called()
    mock_session.commit.assert_called()

    # Case 5: Exception handling
    mock_session.query.side_effect = Exception("DB error")
    result = analyze_post_sentiment(1)
    assert result == ("unknown", 0.0)

    mock_close_session.assert_called()
    

def test_project_to_01_range():
    assert sentiment.project_to_01_range("neutral", 0) == 0.5
    assert sentiment.project_to_01_range("positive", 0) == 0.5
    assert sentiment.project_to_01_range("negative", 0) == 0.5

    assert sentiment.project_to_01_range("neutral", 100) == 0.5
    assert sentiment.project_to_01_range("positive", 100) == 50.5
    assert sentiment.project_to_01_range("negative", 100) == -49.5

    assert sentiment.project_to_01_range("neutral", -100) == 0.5
    assert sentiment.project_to_01_range("positive", -100) == -49.5
    assert sentiment.project_to_01_range("negative", -100) == 50.5