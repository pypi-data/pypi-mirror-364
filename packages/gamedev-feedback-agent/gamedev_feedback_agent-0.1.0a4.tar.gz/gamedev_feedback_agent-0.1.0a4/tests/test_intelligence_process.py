import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from intelligence import process
from intelligence.language import LANGUAGE_MAPPING


def test_process_post_all_steps():
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "This is a test post."
    mock_post.language = None
    mock_post.language_confidence = None
    mock_post.translated_content = None
    mock_post.platform_id = 1

    # Patch all intelligence functions and db queries
    with patch("intelligence.process.detect_language", return_value=("en", 0.99)), \
         patch("intelligence.process.translate_text", return_value="This is a test post."), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]), \
         patch("intelligence.process.get_text_embedding", return_value=("test-model", [0.1, 0.2, 0.3])), \
         patch("intelligence.intelligence_config.IntelligenceConfig.DEFAULT_LANGUAGE", "en"), \
         patch("intelligence.process.Analysis", autospec=True) as MockAnalysis, \
         patch("intelligence.process.Embedding", autospec=True) as MockEmbedding, \
         patch("intelligence.process.Platform", autospec=True) as MockPlatform:

        # Mock session.query().filter().first() for Analysis and Embedding
        mock_analysis_instance = MockAnalysis.return_value
        mock_analysis_instance.sentiment_label = None
        mock_analysis_instance.priority_score = None
        mock_embedding_instance = MockEmbedding.return_value
        mock_embedding_instance.embedding = None

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            None,  # Analysis
            None   # Embedding
        ]
        mock_session.query.return_value.filter.return_value.scalar.return_value = "TestPlatform"

        # Run process_post
        process.process_post(
            mock_session,
            mock_post,
            lang_detection=True,
            translation=True,
            sentiment_analysis=True,
            priority_score=True,
            embedding_generation=True,
            explain=True,
            rewrite=True
        )

        # Check that commit was called
        assert mock_session.commit.called

def test_process_post_no_post_id(capsys):
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = None

    process.process_post(mock_session, mock_post)
    captured = capsys.readouterr()
    assert "[Process Error] No post_id provided." in captured.out

def test_process_post_no_steps_selected():
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1

    with pytest.raises(Exception):
        process.process_post(
            mock_session,
            mock_post,
            lang_detection=False,
            translation=False,
            sentiment_analysis=False,
            priority_score=False,
            embedding_generation=False
        )
        
        
def test_lang_detect_query_fail():
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "This is a test post."

    with patch("intelligence.process.detect_language", side_effect=Exception()):
        with pytest.raises(Exception):
            process.process_post(mock_session, mock_post, lang_detection=True)
            
            
def test_lang_detect_already_detected():
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "This is a test post."
    mock_post.translated_content = None
    mock_post.language = "en"
    mock_post.language_confidence = 0.99

    
    with patch("intelligence.process.translate_text", return_value="This is a test post."), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]), \
         patch("intelligence.process.get_text_embedding", return_value=("test-model", [0.1, 0.2, 0.3])), \
         patch("intelligence.process.detect_language") as mock_detect_language:
        process.process_post(mock_session, mock_post, lang_detection=True, rewrite=False)
        mock_detect_language.assert_not_called()  # Should not call detect_language if already detected
        
        

def test_translation_text_part(capsys):
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "Bonjour le monde"
    mock_post.language = "fr"
    mock_post.translated_content = None
    
    mock_post2 = MagicMock()
    mock_post2.post_id = 2
    mock_post2.content = "no known language"
    mock_post2.language = "no"
    mock_post2.translated_content = "something"

    with patch("intelligence.process.translate_text", return_value="Hello world") as mock_translate_text, \
         patch("intelligence.process.detect_language", return_value=("fr", 0.99)), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]), \
         patch("intelligence.process.get_text_embedding", return_value=("test-model", [0.1, 0.2, 0.3])), \
         patch("intelligence.intelligence_config.IntelligenceConfig.DEFAULT_LANGUAGE", "en"), \
         patch("intelligence.process.LANGUAGE_MAPPING", {"en": "en", "fr": "fr"}):
        process.process_post(
            mock_session,
            mock_post,
            translation=True,
            explain=True,
            rewrite=True
        )
        mock_translate_text.assert_called_once_with("Bonjour le monde", "en")
        assert mock_post.translated_content == "Hello world"
        assert mock_session.commit.called
        
    with patch("intelligence.process.translate_text", return_value="Hello world") as mock_translate_text, \
         patch("intelligence.process.IntelligenceConfig") as mock_intelligence_config, \
         patch("intelligence.process.detect_language", return_value=("en", 0.99)), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]), \
         patch("intelligence.process.get_text_embedding", return_value=("test-model", [0.1, 0.2, 0.3])):
            mock_intelligence_config.DEFAULT_LANGUAGE.return_value = "xx"
             
            process.process_post(
                mock_session,
                mock_post2,
                translation=True,
                explain=False,
                rewrite=True
            )
            out = capsys.readouterr().out

            
            process.process_post(
                mock_session,
                mock_post2,
                translation=True,
                explain=True,
                rewrite=False
            )
            out = capsys.readouterr().out
            assert "already has translated" in out
            
            
def test_translation_text_fail(capsys):
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "Bonjour le monde"
    mock_post.language = "fr"
    mock_post.language_confidence = 0.99
    mock_post.translated_content = None

    with patch("intelligence.process.translate_text", side_effect=Exception("Translation failed")), \
         patch("intelligence.process.detect_language", return_value=("en", 0.99)), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]), \
         patch("intelligence.process.get_text_embedding", return_value=("test-model", [0.1, 0.2, 0.3])):
             
            with pytest.raises(Exception):
                process.process_post(
                    mock_session,
                    mock_post,
                    translation=True,
                    explain=True,
                    rewrite=False
                )
                captured = capsys.readouterr()
                assert "[Process Error] Failed to translate post 1" in captured.out
                assert not mock_session.commit.called
            
            

def test_analysis_precheck_fail(capsys):
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "Test content"

    # Simulate exception when querying Analysis
    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.side_effect = Exception("DB error")

    with patch("intelligence.process.Analysis"), \
         patch("intelligence.process.detect_language", return_value=("en", 0.99)), \
         patch("intelligence.process.translate_text", return_value="This is a test post."), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]), \
         patch("intelligence.process.get_text_embedding", return_value=("test-model", [0.1, 0.2, 0.3])):
        with pytest.raises(Exception) as excinfo:
            process.process_post(
                mock_session,
                mock_post,
                sentiment_analysis=True
            )
        captured = capsys.readouterr()
        assert "[Process Error] Failed to query analysis for post 1" in captured.out
        assert "DB error" in str(excinfo.value)


def test_sentiment_analysis_fail(capsys):
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "Test content"

    with patch("intelligence.process.get_text_sentiment", side_effect=Exception("Sentiment error")), \
         patch("intelligence.process.Analysis"), \
         patch("intelligence.process.detect_language", return_value=("en", 0.99)), \
         patch("intelligence.process.translate_text", return_value="Test content"), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]), \
         patch("intelligence.process.get_text_embedding", return_value=("test-model", [0.1, 0.2, 0.3])):
        with pytest.raises(Exception) as excinfo:
            process.process_post(
                mock_session,
                mock_post,
                sentiment_analysis=True,
                explain=True
            )
        captured = capsys.readouterr()
        assert "[Process Error] Failed to analyze sentiment for post 1" in captured.out
        assert "Sentiment error" in str(excinfo.value)
        assert mock_session.rollback.called
        




def test_priority_score_fail(capsys):
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "Test content"

    with patch("intelligence.process.get_priority_score_from_post_analysis", side_effect=Exception("Priority score error")), \
         patch("intelligence.process.Analysis"), \
         patch("intelligence.process.detect_language", return_value=("en", 0.99)), \
         patch("intelligence.process.translate_text", return_value="Test content"), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_text_embedding", return_value=("test-model", [0.1, 0.2, 0.3])):
        with pytest.raises(Exception) as excinfo:
            process.process_post(
                mock_session,
                mock_post,
                priority_score=True,
                explain=True
            )
        captured = capsys.readouterr()
        assert "[Process Error] Failed to calculate priority score for post 1" in captured.out
        assert "Priority score error" in str(excinfo.value)
        assert mock_session.rollback.called
        
        
        
        
def test_embedding_generation_fail(capsys):
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "Test content"

    with patch("intelligence.process.get_text_embedding", side_effect=Exception("Embedding error")), \
         patch("intelligence.process.Analysis"), \
         patch("intelligence.process.detect_language", return_value=("en", 0.99)), \
         patch("intelligence.process.translate_text", return_value="Test content"), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]):
        with pytest.raises(Exception) as excinfo:
            process.process_post(
                mock_session,
                mock_post,
                embedding_generation=True,
                explain=True
            )
        captured = capsys.readouterr()
        assert "[Process Error] Failed to generate embedding for post 1" in captured.out
        assert "Embedding error" in str(excinfo.value)
        assert mock_session.rollback.called
        
        
def test_embedding_generation_no_embedding(capsys):
    mock_session = MagicMock()
    mock_post = MagicMock()
    mock_post.post_id = 1
    mock_post.content = "Test content"

    with patch("intelligence.process.get_text_embedding", return_value=(None, None)), \
         patch("intelligence.process.Analysis"), \
         patch("intelligence.process.detect_language", return_value=("en", 0.99)), \
         patch("intelligence.process.translate_text", return_value="Test content"), \
         patch("intelligence.process.get_text_sentiment", return_value=("positive", 0.95)), \
         patch("intelligence.process.get_priority_score_from_post_analysis", return_value=[0.8, 0.9, 0.7, 0.6, 0.5, 0.4]):
        with pytest.raises(Exception) as excinfo:
            process.process_post(
                mock_session,
                mock_post,
                embedding_generation=True,
                explain=True
            )
        captured = capsys.readouterr()
        assert "[Process Error] Failed to generate embedding for post 1" in captured.out
        assert "Failed to generate embedding for post 1." in str(excinfo.value)
        assert mock_session.rollback.called
