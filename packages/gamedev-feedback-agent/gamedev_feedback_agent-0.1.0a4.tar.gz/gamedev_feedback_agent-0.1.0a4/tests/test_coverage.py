from intelligence.coverage import get_coverage_summary
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from database.db_models import Post, Analysis, Embedding, Platform

# Mock config
class DummyConfig:
    DEFAULT_LANGUAGE = "en"
    EMBEDDING_PROVIDER = "openai"
    
class DummyConfig2:
    DEFAULT_LANGUAGE = "en"
    EMBEDDING_PROVIDER = "ollama"

@patch("intelligence.coverage.IntelligenceConfig", DummyConfig)
def test_get_coverage_summary_empty():
    session = MagicMock()
    session.query().all.return_value = []
    result = get_coverage_summary(session)
    assert result["total_post_count"] == 0
    assert result["missing_posts"] == []
    assert result["missing_language_detection"] == []
    assert result["missing_translation"] == []
    assert result["missing_sentiment"] == []
    assert result["missing_priority"] == []
    assert result["missing_1536_embedding"] == "no embeddings in 1536 dimension"
    assert result["missing_768_embedding"] == "no embeddings in 768 dimension"

@patch("intelligence.coverage.IntelligenceConfig", DummyConfig)
def test_get_coverage_summary_all_covered():
    # Setup posts
    post = MagicMock()
    post.post_id = 1
    post.language = "en"
    post.translated_content = "content"
    post.timestamp = datetime.now()
    session = MagicMock()
    session.query().all.return_value = [post]
    # Analysis coverage
    session.query().filter().all.side_effect = [
        [MagicMock(post_id=1)],  # sentiment
        [MagicMock(post_id=1)],  # priority
        [MagicMock(post_id=1, embedding=[0]*1536)],  # embeddings
    ]
    result = get_coverage_summary(session)
    assert result["total_post_count"] == 1
    assert result["missing_posts"] == []
    assert result["missing_language_detection"] == []
    assert result["missing_translation"] == []
    assert result["missing_sentiment"] == []
    assert result["missing_priority"] == []
    assert result["missing_1536_embedding"] == []
    assert result["missing_768_embedding"] == "no embeddings in 768 dimension"

@patch("intelligence.coverage.IntelligenceConfig", DummyConfig)
def test_get_coverage_summary_missing_language_and_translation():
    post = MagicMock()
    post.post_id = 2
    post.language = None
    post.translated_content = None
    post.timestamp = datetime.now()
    session = MagicMock()
    session.query().all.return_value = [post]
    session.query().filter().all.side_effect = [
        [],  # sentiment
        [],  # priority
        [],  # embeddings
    ]
    result = get_coverage_summary(session)
    assert result["missing_language_detection"] == [2]
    assert result["missing_translation"] == [2]
    assert 2 in result["missing_posts"]

@patch("intelligence.coverage.IntelligenceConfig", DummyConfig)
def test_get_coverage_summary_missing_translation():
    post = MagicMock()
    post.post_id = 3
    post.language = "fr"
    post.translated_content = None
    post.timestamp = datetime.now()
    session = MagicMock()
    session.query().all.return_value = [post]
    session.query().filter().all.side_effect = [
        [],  # sentiment
        [],  # priority
        [],  # embeddings
    ]
    result = get_coverage_summary(session)
    assert result["missing_translation"] == [3]
    assert 3 in result["missing_posts"]

@patch("intelligence.coverage.IntelligenceConfig", DummyConfig)
def test_get_coverage_summary_platform_filter():
    session = MagicMock()
    post = MagicMock()
    post.post_id = 4
    post.language = "en"
    post.translated_content = "content"
    post.timestamp = datetime.now()
    # Simulate platform filter
    session.query().all.return_value = [post]
    session.query().filter().all.side_effect = [
        [MagicMock(post_id=4)],  # sentiment
        [MagicMock(post_id=4)],  # priority
        [MagicMock(post_id=4, embedding=[0]*1536)],  # embeddings
        [MagicMock(post_id=4)], 
        [MagicMock(post_id=4)], 
    ]
    session.query().filter().filter().all.return_value = [post]
    session.query().filter().filter().filter().all.return_value = [post]
    session.query().filter().filter().filter().filter().all.return_value = [post]
    result = get_coverage_summary(session, platforms=["reddit"])
    assert result["total_post_count"] == 1

@patch("intelligence.coverage.IntelligenceConfig", DummyConfig)
def test_get_coverage_summary_date_filter():
    session = MagicMock()
    post = MagicMock()
    post.post_id = 5
    post.language = "en"
    post.translated_content = "content"
    post.timestamp = datetime.now() - timedelta(days=2)
    session.query().all.return_value = [post]
    session.query(Post).filter().all.return_value = [post]
    session.query().filter().filter().all.return_value = [post]
    session.query().filter().filter().filter().all.return_value = [post]
    session.query().filter().all.side_effect = [
        [MagicMock(post_id=5)],  # sentiment
        [MagicMock(post_id=5)],  # priority
        [MagicMock(post_id=5, embedding=[0]*1536)],  # embeddings
    ]
    since = datetime.now() - timedelta(days=3)
    until = datetime.now()
    result = get_coverage_summary(session, since=since, until=until)
    assert result["total_post_count"] == 1
    
    
def test_get_coverage_summary_with_different_embedding_provider():
    session = MagicMock()
    post = MagicMock()
    post.post_id = 6
    post.language = "en"
    post.translated_content = "content"
    post.timestamp = datetime.now()
    session.query().all.return_value = [post]
    session.query().filter().all.return_value = [post]
    session.query().filter().filter().all.return_value = [post]
    session.query().filter().filter().filter().all.return_value = [post]
    session.query().filter().all.side_effect = [
        [MagicMock(post_id=6)],  # sentiment
        [MagicMock(post_id=6)],  # priority
        [MagicMock(post_id=6, embedding=[0]*768)],  # embeddings
    ]
    result = get_coverage_summary(session)
    assert result["total_post_count"] == 1
    assert result["missing_posts"] == []
    assert result["missing_language_detection"] == []
    assert result["missing_translation"] == []
    assert result["missing_sentiment"] == []
    assert result["missing_priority"] == []
    assert result["missing_1536_embedding"] == "no embeddings in 1536 dimension"
    assert result["missing_768_embedding"] == []