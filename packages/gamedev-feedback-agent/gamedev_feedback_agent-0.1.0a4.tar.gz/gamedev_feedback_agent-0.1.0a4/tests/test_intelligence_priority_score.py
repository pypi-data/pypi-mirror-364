from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from intelligence.priority_score import get_priority_score
from intelligence.priority_score import get_sentiment_score_from_data, get_sentiment_score
from intelligence.priority_score import get_engagement_score
from intelligence.priority_score import get_critical_keywords_score_from_content, get_critical_keywords_score
import pytest
from intelligence.priority_score import get_recency_score_from_timestamp, get_recency_score
from intelligence.priority_score import get_author_score, get_author_post_stats

def test_get_priority_score_mocked():
    # Create dummy Post, Analysis, and Platform mock
    dummy_post = MagicMock()
    dummy_post.post_id = 1
    dummy_post.platform_id = 1
    dummy_post.author_id = 1
    dummy_post.timestamp = datetime.now(timezone.utc) - timedelta(hours=2)
    dummy_post.upvotes = 15
    dummy_post.replies = 10
    dummy_post.post_type = "reddit_post"
    dummy_post.content = "This game is unplayable! Total bugfest."
    dummy_post.translated_content = None
    dummy_post.post_metadata = {}

    dummy_analysis = MagicMock()
    dummy_analysis.post_id = 1
    dummy_analysis.sentiment_label = "negative"
    dummy_analysis.sentiment_score = 0.8
    dummy_analysis.priority_score = None

    # Patch get_session and close_session
    with patch("intelligence.priority_score.get_session") as mock_get_session, \
         patch("intelligence.priority_score.close_session") as mock_close_session, \
         patch("intelligence.priority_score.write_priority_score") as mock_write_priority_score:

        mock_session = MagicMock()
        mock_session.query().filter().first.side_effect = [dummy_post, dummy_analysis, ("reddit",)]
        mock_session.query().filter().one.return_value = (12, 3.5)
        mock_get_session.return_value = mock_session

        score = get_priority_score(1)

    # Total score and breakdown: should match fixed logic
    total, sentiment, engagement, keywords, recency, author = score

    # Assertions
    assert isinstance(score, list)
    assert len(score) == 6
    assert total == sum(score[1:])  # Total is sum of components
    assert sentiment > 0
    assert engagement > 0
    assert keywords > 0
    assert recency > 0
    assert author > 0



def test_get_sentiment_score_error():
    mock_analysis = MagicMock()
    mock_analysis.sentiment_score = -1
    with pytest.raises(Exception):
        get_sentiment_score(mock_analysis)


def test_sentiment_score():
    with patch("intelligence.priority_score.project_to_01_range") as mock_project:
        # Test negative sentiment, high confidence
        mock_project.return_value = 0.85
        score = get_sentiment_score_from_data("negative", 0.95)
        assert score == 25

        # Test neutral sentiment, medium confidence
        mock_project.return_value = 0.5
        score = get_sentiment_score_from_data("neutral", 0.5)
        assert score == 5

        # Test positive sentiment, low confidence
        mock_project.return_value = 0.15
        score = get_sentiment_score_from_data("positive", 0.2)
        assert score == 30
        
        mock_project.return_value = 0.3
        score = get_sentiment_score_from_data("negative", 0.3)
        assert score == 20
        
        mock_project.return_value = 0.7
        score = get_sentiment_score_from_data("positive", 0.7)
        assert score == 10

        # Test out-of-range value
        mock_project.return_value = -0.1
        score = get_sentiment_score_from_data("positive", 0.9)
        assert score == 0
        

def test_engagement_score():
    # Create dummy Post mock for different platforms and scenarios
    dummy_post = MagicMock()
    dummy_post.upvotes = 0
    dummy_post.replies = 0
    dummy_post.post_type = ""
    dummy_post.post_metadata = {}


    # Reddit: high engagement
    dummy_post.upvotes = 55
    dummy_post.replies = 10
    dummy_post.post_type = "reddit_post"
    assert get_engagement_score("reddit", dummy_post) == 25

    # Reddit: medium engagement
    dummy_post.upvotes = 12
    dummy_post.replies = 2
    assert get_engagement_score("reddit", dummy_post) == 15

    # Reddit: low engagement
    dummy_post.upvotes = 2
    dummy_post.replies = 1
    assert get_engagement_score("reddit", dummy_post) == 5

    # Steam review: high engagement
    dummy_post.upvotes = 120
    dummy_post.post_type = "steam_review"
    assert get_engagement_score("steam", dummy_post) == 25

    # Steam review: medium engagement
    dummy_post.upvotes = 25
    assert get_engagement_score("steam", dummy_post) == 15

    # Steam review: low engagement
    dummy_post.upvotes = 5
    assert get_engagement_score("steam", dummy_post) == 5

    # Steam discussion thread: high engagement
    dummy_post.upvotes = 150
    dummy_post.post_type = "steam_discussion_thread"
    assert get_engagement_score("steam", dummy_post) == 25
    
    dummy_post.upvotes = 30
    dummy_post.post_type = "steam_discussion_thread"
    assert get_engagement_score("steam", dummy_post) == 15
    
    dummy_post.upvotes = 2
    dummy_post.post_type = "steam_discussion_thread"
    assert get_engagement_score("steam", dummy_post) == 5
    
    

    # Steam discussion comment: always 0
    dummy_post.post_type = "steam_discussion_comment"
    assert get_engagement_score("steam", dummy_post) == 0

    # Discord: high engagement (replies)
    dummy_post.replies = 15
    dummy_post.post_metadata = {}
    dummy_post.post_type = "discord_message"
    assert get_engagement_score("discord", dummy_post) == 25

    # Discord: high engagement (pinned)
    dummy_post.replies = 2
    dummy_post.post_metadata = {"pinned": True}
    assert get_engagement_score("discord", dummy_post) == 25

    # Discord: high engagement (mentions)
    dummy_post.post_metadata = {"mentions": ["a", "b", "c", "d"]}
    assert get_engagement_score("discord", dummy_post) == 25

    # Discord: medium engagement (replies)
    dummy_post.replies = 6
    dummy_post.post_metadata = {"mentions": []}
    assert get_engagement_score("discord", dummy_post) == 15

    # Discord: medium engagement (mentions)
    dummy_post.replies = 2
    dummy_post.post_metadata = {"mentions": ["a", "b"]}
    assert get_engagement_score("discord", dummy_post) == 15

    # Discord: low engagement
    dummy_post.replies = 1
    dummy_post.post_metadata = {"mentions": []}
    assert get_engagement_score("discord", dummy_post) == 5

    # Unsupported platform
    try:
        get_engagement_score("unknown", dummy_post)
        assert False, "Should raise ValueError for unsupported platform"
    except ValueError:
        pass
    
    
    


def test_critical_word_from_content():
    # Critical keywords
    assert get_critical_keywords_score_from_content("This game has a crash and is broken!") == 20
    assert get_critical_keywords_score_from_content("Refund please, it's unplayable due to bug.") == 20

    # High priority keywords
    assert get_critical_keywords_score_from_content("Performance is and there is a.") == 15
    assert get_critical_keywords_score_from_content("Error and with hahaha.") == 15

    # Medium priority keywords
    assert get_critical_keywords_score_from_content("I have a suggestion for something.") == 10
    assert get_critical_keywords_score_from_content("here is a feedback.") == 10

    # Low priority keywords
    assert get_critical_keywords_score_from_content("Love this piece of work!") == 5
    assert get_critical_keywords_score_from_content("Amazing and pppp.") == 5

    # Multiple keywords, but max score capped at 20
    assert get_critical_keywords_score_from_content("Crash bug broken refund unplayable performance lag slow glitch error problem suggestion feature improvement feedback love amazing perfect brilliant masterpiece") == 20

    # No keywords
    assert get_critical_keywords_score_from_content("Nothing special here.") == 0
    
    # combine
    assert get_critical_keywords_score_from_content("brilliant feature") == 15
    

def test_critical_word():
    dummy_post = MagicMock()
    dummy_post.content = "This game has a crash and is broken!"
    dummy_post.translated_content = None
    dummy_post.post_metadata = {}

    assert get_critical_keywords_score(dummy_post) == 20
    
    none_post = MagicMock()
    none_post.content = None
    with pytest.raises(ValueError):
        get_critical_keywords_score(none_post)
        
    translated_post = MagicMock()
    translated_post.content = "Ce jeu a un crash et est cassé !"
    translated_post.translated_content = "This game has a crash and is broken!"
    
    assert get_critical_keywords_score(translated_post) == 20
    
    
    
    
def test_get_recency(capsys):
    now = datetime.now(timezone.utc)
    # Less than 1 hour old
    assert get_recency_score_from_timestamp(now - timedelta(hours=5)) == 15
    # 1-6 hours old
    assert get_recency_score_from_timestamp(now - timedelta(hours=13)) == 12
    # 6-24 hours old
    assert get_recency_score_from_timestamp(now - timedelta(hours=70)) == 8
    # 1-3 days old
    assert get_recency_score_from_timestamp(now - timedelta(days=6)) == 4
    # Older than 3 days
    assert get_recency_score_from_timestamp(now - timedelta(days=25)) == 2
    
    assert get_recency_score_from_timestamp(now - timedelta(days=35)) == 0

    # Invalid timestamp

    get_recency_score_from_timestamp(None)
    out = capsys.readouterr().out
    assert "Invalid timestamp" in out
    
    
    
def test_get_recency_invalid_formats(capsys):
    # None timestamp
    assert get_recency_score_from_timestamp(None) == 0
    out = capsys.readouterr().out
    assert "Invalid timestamp" in out

    # Invalid string format
    assert get_recency_score_from_timestamp("not-a-date") == 0
    out = capsys.readouterr().out
    assert "Invalid timestamp format" in out

    # Not a datetime object or string
    assert get_recency_score_from_timestamp(12345) == 0
    out = capsys.readouterr().out
    assert "Timestamp is not a datetime object" in out
    
    
    
def test_get_recency():
    with pytest.raises(ValueError):
        get_recency_score(None)
        
        

def test_get_author_score_no_post():
    # Test with no post
    with pytest.raises(ValueError):
        get_author_score(None)
        
        
def test_get_author_score_with_post():
    # Create dummy Post mock
    dummy_post = MagicMock()
    dummy_post.author_id = 1

    # Patch get_author_post_stats to return fixed values
    with patch("intelligence.priority_score.get_author_post_stats") as mock_get_stats:
        mock_get_stats.return_value = (110, 25)  # 12 posts, 3.5 average score

        score = get_author_score(dummy_post)

        assert score == 10
        
    with patch("intelligence.priority_score.get_author_post_stats") as mock_get_stats:
        mock_get_stats.return_value = (30, 7)  # 12 posts, 3.5 average score

        score = get_author_score(dummy_post)

        assert score == 6
        
    with patch("intelligence.priority_score.get_author_post_stats") as mock_get_stats:
        mock_get_stats.return_value = (6, 2)  # 12 posts, 3.5 average score

        score = get_author_score(dummy_post)

        assert score == 3
        
    with patch("intelligence.priority_score.get_author_post_stats") as mock_get_stats:
        mock_get_stats.return_value = (1, 0)  # 12 posts, 3.5 average score

        score = get_author_score(dummy_post)

        assert score == 1