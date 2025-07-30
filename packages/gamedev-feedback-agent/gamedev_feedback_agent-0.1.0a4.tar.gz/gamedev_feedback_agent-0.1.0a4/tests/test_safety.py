from intelligence.safety import load_keywords_json, load_keywords_txt, detect_toxic, check_if_toxic, detect_spam, check_if_spam, detect_scam, check_if_scam, \
    detect_sentiment_crisis, detect_trend_alerts, detect_review_bombing
    
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path


# ---------- load_keywords_txt ----------
@patch("intelligence.safety.os.path.exists", return_value=True)
@patch("intelligence.safety.get_context", return_value={"workspace": Path(".")})
def test_load_keywords_txt_success(mock_ctx, mock_exists):
    # Simulate file contents
    m = mock_open(read_data="toxic\nword\n\n\nextra\n")
    with patch("builtins.open", m):
        result = load_keywords_txt("dummy.txt")
        assert result == {"toxic", "word", "extra"}
        
@patch("intelligence.safety.os.path.exists", return_value=True)
@patch("intelligence.safety.get_context", return_value={"workspace": Path(".")})
def test_load_keywords_txt_failed(mock_ctx, mock_exists, capsys):
    # simulate open raising an IOError
    m = mock_open()
    m.side_effect = IOError("File not found")
    with patch("builtins.open", m):
        load_keywords_txt("dummy.txt")
    assert "[Error] Failed to load toxic keywords" in capsys.readouterr().out

@patch("intelligence.safety.os.path.exists", return_value=False)
def test_load_keywords_txt_missing(mock_exists, capsys):
    result = load_keywords_txt("dummy.txt")
    assert result == set()
    assert "[Error] Toxic keywords file not found" in capsys.readouterr().out

# ---------- load_keywords_json ----------
@patch("intelligence.safety.os.path.exists", return_value=True)
@patch("intelligence.safety.get_context", return_value={"workspace": Path(".")})
def test_load_keywords_json_success(mock_ctx, mock_exists):
    fake_json = {"regex_patterns": {"r1": ".*foo.*"}}
    m = mock_open(read_data='{"regex_patterns": {"r1": ".*foo.*"}}')
    with patch("builtins.open", m):
        import json
        result = load_keywords_json("dummy.json")
        assert isinstance(result, dict)
        assert "regex_patterns" in result

@patch("intelligence.safety.os.path.exists", return_value=False)
def test_load_keywords_json_missing(mock_exists, capsys):
    result = load_keywords_json("dummy.json")
    assert result == {}
    assert "[Error] Toxic keywords JSON file not found" in capsys.readouterr().out
    
@patch("intelligence.safety.os.path.exists", return_value=True)
@patch("intelligence.safety.get_context", return_value={"workspace": Path(".")})
def test_load_keywords_json_failed(mock_ctx, mock_exists, capsys):
    # simulate open raising an IOError
    m = mock_open()
    m.side_effect = IOError("File not found")
    with patch("builtins.open", m):
        load_keywords_json("dummy.json")
    assert "[Error] Failed to load keywords JSON" in capsys.readouterr().out

# ---------- detect_toxic ----------
@patch("intelligence.safety.load_keywords_txt", return_value={"badword"})
def test_detect_toxic_basic(mock_load_keywords):
    session = MagicMock()
    # Mock posts with analysis
    post = MagicMock(content="something badword here", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    session.query().join().filter().all.return_value = [(post, analysis)]
    result = detect_toxic(session, sentiment_threshold=0.8)
    assert len(result) == 1
    assert result[0][1] == "toxic_keyword"
    
    
@patch("intelligence.safety.check_if_toxic", return_value=(True, "toxic_keyword"))
@patch("intelligence.safety.load_keywords_txt", return_value={"badword"})
def test_detect_toxic_with_platform(mock_load_keywords, mock_check_if_toxic):
    session = MagicMock()
    # Mock Platform query
    platform_obj = MagicMock(platform_id=42)
    session.query().filter().all.return_value = [platform_obj]
    # Mock posts with analysis
    post = MagicMock(content="something badword here", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    # posts_analysis_query.filter().all() should return posts/analysis
    session.query().join().filter().filter().all.return_value = [(post, analysis)]
    result = detect_toxic(session, sentiment_threshold=0.8, platform=["platform"])
    assert len(result) == 1
    assert result[0][1] == "toxic_keyword"
    
def test_detect_toxic_no_platform_found():
    session = MagicMock()
    # Mock Platform query to return empty
    session.query().filter().all.return_value = []
    # Mock posts with analysis
    post = MagicMock(content="something badword here", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    session.query().join().filter().all.return_value = [(post, analysis)]
    result = detect_toxic(session, sentiment_threshold=0.8, platform=["platform"])
    assert len(result) == 0
    

@patch("intelligence.safety.load_keywords_txt", return_value={"badword"})
def test_detect_toxic_since(mock_load_keywords):
    session = MagicMock()
    # Mock posts with analysis
    post = MagicMock(content="something badword here", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    session.query().join().filter().filter().all.return_value = [(post, analysis)]
    result = detect_toxic(session, sentiment_threshold=0.8, since="2023-01-01")
    assert len(result) == 1
    assert result[0][1] == "toxic_keyword"
    
@patch("intelligence.safety.load_keywords_txt", return_value={"badword"})
def test_detect_toxic_since_datetime_convert_error(mock_load_keywords, capsys):
    session = MagicMock()
    # Mock posts with analysis
    post = MagicMock(content="something badword here", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    session.query().join().filter().filter().all.return_value = [(post, analysis)]
    detect_toxic(session, sentiment_threshold=0.8, since="invalid-date")
    assert "[Error] Invalid date format for 'since'" in capsys.readouterr().out
    
@patch("intelligence.safety.load_keywords_txt", return_value={"badword"})
def test_detect_toxic_until(mock_load_keywords):
    session = MagicMock()
    # Mock posts with analysis
    post = MagicMock(content="something badword here", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    session.query().join().filter().filter().all.return_value = [(post, analysis)]
    result = detect_toxic(session, sentiment_threshold=0.8, until="2023-01-01")
    assert len(result) == 1
    assert result[0][1] == "toxic_keyword"
    
@patch("intelligence.safety.load_keywords_txt", return_value={"badword"})
def test_detect_toxic_until_datetime_convert_error(mock_load_keywords, capsys):
    session = MagicMock()
    # Mock posts with analysis
    post = MagicMock(content="something badword here", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    session.query().join().filter().filter().all.return_value = [(post, analysis)]
    detect_toxic(session, sentiment_threshold=0.8, until="invalid-date")
    assert "[Error] Invalid date format for 'until'" in capsys.readouterr().out
    
def test_check_if_toxic_basic():
    post = MagicMock(content="badword", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    assert check_if_toxic(post, analysis, {"badword"}, 0.8) == (True, "toxic_keyword")
    
def test_check_if_toxic_not_negative():
    post = MagicMock(content="good content", translated_content=None)
    analysis = MagicMock(sentiment_label="positive", sentiment_score=0.1)
    assert check_if_toxic(post, analysis, {"badword"}, 0.8) == (False, "sentiment_label_not_negative")
    
def test_check_if_toxic_no_keywords():
    post = MagicMock(content="good content", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    assert check_if_toxic(post, analysis, set(), 0.8) == (False, "not_toxic")


# ---------- detect_spam ----------
@patch("intelligence.safety.load_keywords_json", return_value={"foo": ["bad"], "regex_patterns": {"r1": "bad"}})
def test_detect_spam_basic(mock_load_keywords_json):
    session = MagicMock()
    spam_tag = MagicMock(tag_id=1)
    session.query().filter().first.return_value = spam_tag
    # Mock posts
    post = MagicMock(content="this is bad", translated_content=None, post_id=123)
    session.query().all.return_value = [post]
    result = detect_spam(session)
    assert len(result) == 1
    assert result[0][1] == "foo" or result[0][1] == "r1"
    
def test_detect_spam_regex_patterns_compile_error():
    # Test that regex patterns compile errors are handled
    with patch("intelligence.safety.load_keywords_json", return_value={"regex_patterns": {"r1": "[invalid["}}):
        session = MagicMock()
        post = MagicMock(content="this is bad", translated_content=None, post_id=123)
        session.query().all.return_value = [post]
        result = detect_spam(session)
        assert len(result) == 0  # No posts should be detected due to regex error
        
@patch("intelligence.safety.load_keywords_json", return_value={"foo": ["bad"], "regex_patterns": {"r1": "bad"}})
def test_detect_spam_tag_not_found(mock_load_keywords_json):
    session = MagicMock()
    session.query().filter().first.return_value = None
    result = detect_spam(session)
    assert result == []
    
@patch("intelligence.safety.load_keywords_json", return_value={"foo": ["bad"], "regex_patterns": {"r1": "bad"}})
def test_detect_spam_autotag(mock_load_keywords_json):
    session = MagicMock()
    post = MagicMock(content="this is bad", translated_content=None, post_id=123)
    session.query().all.return_value = [post]
    # Mock PostTag and session.add/commit for auto_flag
    with patch("intelligence.safety.PostTag") as MockPostTag:
        session.add = MagicMock()
        session.commit = MagicMock()
        result = detect_spam(session, auto_flag=True)
        assert len(result) == 1
        assert result[0][1] == "foo"
        # Check PostTag was created and session.add/commit called
        MockPostTag.assert_called_once_with(post_id=123, tag_id=session.query().filter().first().tag_id)
        session.add.assert_called()
        session.commit.assert_called()
        
def test_check_if_spam_regex_pattern_match():
    post = MagicMock(content="Special OFFER2024 now!", translated_content=None)
    spam_keywords = {}
    spam_patterns = {"offer_pattern": r"offer\d+"}
    assert check_if_spam(post, spam_keywords, spam_patterns) == (True, "offer_pattern")

def test_check_if_spam_regex_pattern_no_match():
    post = MagicMock(content="No spam here", translated_content=None)
    spam_keywords = {}
    spam_patterns = {"digits": r"\d{5,}"}
    assert check_if_spam(post, spam_keywords, spam_patterns) == (False, "not_spam")

def test_check_if_spam_multiple_regex_patterns_first_match():
    post = MagicMock(content="Buy now! CODE999", translated_content=None)
    spam_keywords = {}
    spam_patterns = {
        "code_pattern": r"code\d+",
        "buy_pattern": r"buy now"
    }
    # Should match "code_pattern" first due to dict order
    result = check_if_spam(post, spam_keywords, spam_patterns)
    assert result[0] is True
    assert result[1] in spam_patterns

def test_check_if_spam_regex_pattern_with_translated_content():
    post = MagicMock(content="irrelevant", translated_content="SPAM2023 detected")
    spam_keywords = {}
    spam_patterns = {"spam_pattern": r"spam\d+"}
    assert check_if_spam(post, spam_keywords, spam_patterns) == (True, "spam_pattern")

# ---------- detect_scam ----------
@patch("intelligence.safety.load_keywords_json", return_value={
    "regex_patterns": {"scam": "scammy"},
    "suspicious_domains": ["scam.com"],
    "keywords": {"high": ["urgent"], "low": ["deal"]}
})
def test_detect_scam_basic(mock_load_keywords_json):
    session = MagicMock()
    post = MagicMock(content="urgent! scammy offer at scam.com", post_id=55)
    session.query().all.return_value = [post]
    result = detect_scam(session)
    assert len(result) == 1
    assert isinstance(result[0][1], int)  # scam_score
    
def test_detect_scam_regex_pattern_compile_error():
    # Test that regex patterns compile errors are handled
    with patch("intelligence.safety.load_keywords_json", return_value={"regex_patterns": {"scam": "[invalid["}}):
        session = MagicMock()
        post = MagicMock(content="urgent! scammy offer at scam.com", post_id=55)
        session.query().all.return_value = [post]
        result = detect_scam(session)
        assert len(result) == 0
        
def test_detect_scam_alert_high_risk():
    session = MagicMock()
    post = MagicMock(content="urgent! scammy offer at scam.com", post_id=55)
    # Patch Alert and session.add/commit to avoid side effects
    with patch("intelligence.safety.Alert") as MockAlert:
        session.add = MagicMock()
        session.commit = MagicMock()
        # Patch load_keywords_json to provide high-risk patterns
        with patch("intelligence.safety.load_keywords_json", return_value={
            "regex_patterns": {"scam": "scammy"},
            "suspicious_domains": ["scam.com"],
            "keywords": {"high": ["urgent"], "low": ["deal"]}
        }):
            session.query().all.return_value = [post]
            result = detect_scam(session, alert_high_risk=True)
            assert len(result) == 1
            assert result[0][1] >= 5  # scam score should be high risk
            # Check alert was created and session.add/commit called
            MockAlert.assert_called_once()
            session.add.assert_called()
            session.commit.assert_called()
            
            
def test_check_if_scam_all_path():
    # Covers all keyword levels, patterns, and suspicious domains
    post = MagicMock(content="Critical scam! urgent deal scam.com suspicious")
    scam_keywords = {
        "critical": ["critical scam"],
        "high": ["urgent"],
        "medium": ["deal"],
        "low": ["suspicious"],
        "info": ["info"]
    }
    scam_patterns = {"pat": r"scam!"}
    suspicious_domain = ["scam.com"]

    score, reasons = check_if_scam(post, scam_keywords, scam_patterns, suspicious_domain)
    # Should match only the highest level (critical), plus pattern and domain
    assert score == 6  # 4 (critical) + 1 (pattern) + 1 (domain)
    assert "critical_scam_keyword" in reasons
    assert "scam_pattern_detected" in reasons
    assert "suspicious_domain_detected" in reasons
    
    # check other levels
    post2 = MagicMock(content="urgent deal")
    score2, reasons2 = check_if_scam(post2, scam_keywords, scam_patterns, suspicious_domain)
    assert score2 == 3 
    assert "high_scam_keyword" in reasons2
    
    post2.content = "deal"
    score3, reasons3 = check_if_scam(post2, scam_keywords, scam_patterns, suspicious_domain)
    assert score3 == 2  # only medium level matched
    assert "medium_scam_keyword" in reasons3
    
    post2.content = "suspicious"
    score4, reasons4 = check_if_scam(post2, scam_keywords, scam_patterns, suspicious_domain)
    assert score4 == 1  # only low level matched
    assert "low_scam_keyword" in reasons4

# ---------- detect_sentiment_crisis ----------
def test_detect_sentiment_crisis_minimum_posts():
    session = MagicMock()
    post = MagicMock(timestamp=1)
    analysis = MagicMock(sentiment_score=0.85, sentiment_label="negative")
    # Only one post returned, but minimum_posts=2 required
    session.query().join().filter().all.return_value = [(post, analysis)]
    result = detect_sentiment_crisis(session, threshold=0.8, minimum_posts=2)
    assert result == []
    
def test_detect_sentiment_crisis_no_threshold_specified():
    session = MagicMock()
    post = MagicMock(timestamp=1)
    analysis = MagicMock(sentiment_score=0.85, sentiment_label="negative")
    # No threshold specified, should return empty
    session.query().join().filter().all.return_value = [(post, analysis)]
    result = detect_sentiment_crisis(session, minimum_posts=2)
    assert result == []
    
def test_detect_sentiment_crisis_with_timeframe():
    session = MagicMock()
    post1 = MagicMock(timestamp=2)
    # Patch for possible multiple .filter() chains
    session.query().join().filter().all.return_value = [post1]
    session.query().join().filter().filter().all.return_value = [post1]
    session.query().join().filter().filter().filter().all.return_value = [post1]
    result = detect_sentiment_crisis(session, threshold=0.8, minimum_posts=1, timeframe="1d")
    result2 = detect_sentiment_crisis(session, threshold=0.8, minimum_posts=1, timeframe="1h")
    assert len(result) == 1
    assert len(result2) == 1
    assert result[0] == post1
    assert result2[0] == post1
    
def test_detect_sentiment_crisis_timeframe_invalid():
    session = MagicMock()
    post1 = MagicMock(timestamp=2)
    # Patch for possible multiple .filter() chains
    session.query().join().filter().all.return_value = [post1]
    session.query().join().filter().filter().all.return_value = [post1]
    session.query().join().filter().filter().filter().all.return_value = [post1]
    result = detect_sentiment_crisis(session, threshold=0.8, minimum_posts=1, timeframe="invalid-timeframe")
    assert len(result) == 1
    

# ---------- detect_trend_alerts ----------
@patch("intelligence.safety.project_to_01_range", side_effect=lambda label, score: score)
def test_detect_trend_alerts_drop(mock_project_to_01_range):
    session = MagicMock()
    # Current posts (lower sentiment), previous (higher sentiment)
    post1, a1 = MagicMock(post_id=1), MagicMock(sentiment_score=0.2, sentiment_label="negative")
    post2, a2 = MagicMock(post_id=2), MagicMock(sentiment_score=0.9, sentiment_label="positive")
    session.query().join().filter().all.side_effect = [
        [(post1, a1)],  # current
        [(post2, a2)],  # previous
    ]
    result = detect_trend_alerts(session, sentiment_drop=0.2, volume_spike=1, timeframe="1d")
    assert isinstance(result, dict)
    assert any("sentiment drop" in alert[0] for alert in result["alerts"])
    
@patch("intelligence.safety.project_to_01_range", side_effect=lambda label, score: score)
def test_detect_trend_alerts_drop_no_sentiment_drop_no_volume_spike(mock_project_to_01_range):
    session = MagicMock()
    # Current posts (lower sentiment), previous (higher sentiment)
    post1, a1 = MagicMock(post_id=1), MagicMock(sentiment_score=0.2, sentiment_label="negative")
    post2, a2 = MagicMock(post_id=2), MagicMock(sentiment_score=0.9, sentiment_label="positive")
    session.query().join().filter().all.side_effect = [
        [(post1, a1)],  # current
        [(post2, a2)],  # previous
    ]
    result = detect_trend_alerts(session)
    assert isinstance(result, dict)
    assert any("sentiment drop" in alert[0] for alert in result["alerts"])
    
@patch("intelligence.safety.project_to_01_range", side_effect=lambda label, score: score)
def test_detect_trend_alerts_no_posts_found(mock_project_to_01_range):
    session = MagicMock()
    # No posts returned
    session.query().join().filter().all.return_value = []
    result = detect_trend_alerts(session, sentiment_drop=0.2, volume_spike=1, timeframe="1d")
    assert isinstance(result, dict)
    assert result["alerts"] == []

# ---------- detect_review_bombing ----------
def test_detect_review_bombing_no_bombing():
    session = MagicMock()
    post, analysis = MagicMock(post_id=10), MagicMock(sentiment_label="negative")
    # current and previous posts (not enough ratio to trigger bombing)
    session.query().join().filter().all.side_effect = [
        [(post, analysis)],  # current
        [(post, analysis)],  # previous
    ]
    result, posts = detect_review_bombing(session, negative_ratio_threshold=100, minimum_posts=1, timeframe="1h")
    assert result is False
    assert posts == []
    
def test_detect_review_bombing_less_parameters():
    session = MagicMock()
    post, analysis = MagicMock(post_id=10), MagicMock(sentiment_label="negative")
    # current and previous posts (not enough ratio to trigger bombing)
    session.query().join().all.side_effect = [
        [(post, analysis)],  # current
        [(post, analysis)],  # previous
    ]
    result, posts = detect_review_bombing(session)
    assert result is False
    assert posts == []

def test_detect_review_bombing_with_timeframe():
    session = MagicMock()
    post, analysis = MagicMock(post_id=10), MagicMock(sentiment_label="negative")
    # current and previous posts (enough ratio to trigger bombing)
    session.query().join().filter().all.side_effect = [
        [(post, analysis)],  # current
        [(post, analysis)],  # previous
        [(post, analysis)],  # current
        [(post, analysis)], 
    ]
    result, posts = detect_review_bombing(session, negative_ratio_threshold=1.0, minimum_posts=1, timeframe="1h")
    assert result is True
    assert len(posts) == 1  # only current negative posts should be included
    result2, posts2 = detect_review_bombing(session, negative_ratio_threshold=1.0, minimum_posts=1, timeframe="1d")
    assert result2 is True
    assert len(posts2) == 1  # only current negative posts should be included
    
def test_detect_review_bombing_with_platform():
    session = MagicMock()
    post, analysis = MagicMock(post_id=10, platform_id=42), MagicMock(sentiment_label="negative")
    # Mock platform lookup to return a platform_id
    platform_obj = MagicMock(platform_id=42)
    session.query().filter().all.return_value = [platform_obj]
    # Mock current and previous posts
    session.query().join().filter().filter().all.side_effect = [
        [(post, analysis)],  # current
        [(post, analysis)],  # previous
    ]
    result, posts = detect_review_bombing(
        session,
        negative_ratio_threshold=1.0,
        minimum_posts=1,
        timeframe="1h",
        platform=["TestPlatform"]
    )
    assert result is True
    assert len(posts) == 1
    assert posts[0].post_id == 10
    
def test_detect_review_bombing_not_enough_posts():
    session = MagicMock()
    post, analysis = MagicMock(post_id=10), MagicMock(sentiment_label="negative")
    # Only one post returned, but minimum_posts=2 required
    session.query().join().filter().all.return_value = [(post, analysis)]
    result, posts = detect_review_bombing(session, negative_ratio_threshold=1.0, minimum_posts=2)
    assert result is False
    assert posts == []
    
def test_detect_review_bombing_not_volume_spike():
    session = MagicMock()
    post, analysis = MagicMock(post_id=10), MagicMock(sentiment_label="negative")
    # Current posts (lower sentiment), previous (higher sentiment)
    session.query().join().filter().all.side_effect = [
        [(post, analysis)],  # current
        [(post, analysis)],  # previous
    ]
    result, posts = detect_review_bombing(session, negative_ratio_threshold=1.0, minimum_posts=1, volume_spike_threshold=10)
    assert result is False
    assert posts == []


# --------- check_if_toxic, check_if_spam, check_if_scam (unitary) ---------
def test_check_if_toxic_basic():
    post = MagicMock(content="badword", translated_content=None)
    analysis = MagicMock(sentiment_label="negative", sentiment_score=0.9)
    assert check_if_toxic(post, analysis, {"badword"}, 0.8) == (True, "toxic_keyword")

def test_check_if_spam_basic():
    post = MagicMock(content="buy now", translated_content=None)
    spam_keywords = {"ads": ["buy now"]}
    spam_patterns = {}
    assert check_if_spam(post, spam_keywords, spam_patterns) == (True, "ads")

def test_check_if_scam_basic():
    post = MagicMock(content="urgent offer scam.com")
    scam_keywords = {"high": ["urgent"], "low": []}
    scam_patterns = {}
    suspicious_domain = ["scam.com"]
    score, reasons = check_if_scam(post, scam_keywords, scam_patterns, suspicious_domain)
    assert score > 0
    assert any("high_scam_keyword" in r or "suspicious_domain_detected" in r for r in reasons)
