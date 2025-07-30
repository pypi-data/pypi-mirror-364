from intelligence.report import generate_brief_report, get_cross_platform_data, get_priority_alert, get_sentiment_trend

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from database.db_models import Platform, Post, Analysis, Alert, PostTag



@patch("intelligence.report.project_to_01_range", side_effect=lambda label, score: score)
def test_generate_brief_report_full(mock_proj):
    session = MagicMock()
    plat = MagicMock(platform_id=1, name="Steam")
    session.query().all.side_effect = [[plat]]
    post = MagicMock(post_type="news", language="en", platform_id=1)
    analysis = MagicMock(sentiment_label="positive", sentiment_score=0.9, priority_score=88)
    alert = MagicMock(alert_type="toxic", reviewed=False, alert_severity=5)
    post_tag = MagicMock()
    # This side_effect needs to be as long as the number of .filter().all() calls
    session.query().filter().all.side_effect = [
        [post],     # posts
    ]
    session.query().join().filter().all.side_effect = [
        [analysis], 
        [alert],    # alerts
    ]
    session.query().join().join().filter().all.side_effect = [
        [(post_tag, "VIP")] # tags
    ]
        
    report = generate_brief_report(session, since=datetime(2024, 7, 1))
    assert report["post_count"] == 1
    assert report["analysis_count"] == 1
    assert report["alert_count"] == 1
    assert report["tag_counts"]["VIP"] == 1

@patch("intelligence.report.project_to_01_range", side_effect=lambda _, score: score)
def test_generate_brief_report_with_platform(mock_proj):
    session = MagicMock()
    plat = MagicMock(platform_id=1, name="PS5")
    post = MagicMock(post_type="news", language="jp", platform_id=1)
    analysis = MagicMock()
    analysis.sentiment_label = "neutral"
    analysis.sentiment_score = 0.5
    analysis.priority_score = 90
    alert = MagicMock(alert_type="spam", reviewed=True, alert_severity=3)
    post_tag = MagicMock()

    # We'll count calls and hand out the right value at the right time
    all_returns = [
        [plat],                        # platforms = session.query(Platform).all()
        [post],                        # posts = session.query(Post).filter...all()
        [analysis],                    # analyses = session.query(Analysis).join(Post).filter...all()
        [alert],                       # alerts = session.query(Alert).join(Post).filter...all()
        [(post_tag, "VIP")]            # tags = session.query(PostTag, Tag.name).join(Tag)...all()
    ]
    def all_side_effect(*_, **__):
        return all_returns.pop(0)
    
    # Patch EVERY .all() (no matter the chain)
    session.query().all.side_effect = all_side_effect
    session.query().filter().all.side_effect = all_side_effect
    session.query().filter().filter().all.side_effect = all_side_effect
    session.query().join().filter().all.side_effect = all_side_effect
    session.query().join().filter().filter().all.side_effect = all_side_effect
    session.query().join().join().filter().filter().all.side_effect = all_side_effect

    report = generate_brief_report(session, since=datetime(2024, 7, 1), platform=["PS5"])
    assert report["post_count"] == 1
    assert report["analysis_count"] == 1
    assert report["alert_count"] == 1
    # assert report["tag_counts"]["VIP"] == 1
    # assert report["post_platforms"]["PS5"] == 1




def test_generate_brief_report_no_data():
    session = MagicMock()
    # All queries return empty lists
    session.query().all.return_value = []
    session.query().filter().all.return_value = []
    session.query().join().filter().all.return_value = []
    report = generate_brief_report(session, since=datetime(2024, 7, 1))
    assert report["post_count"] == 0
    assert report["analysis_count"] == 0
    assert report["alert_count"] == 0
    assert sum(report["alert_severity"].values()) == 0
    assert sum(report["priority_summary"].values()) == 0
    assert report["tag_counts"] == {}

def test_generate_brief_report_missing_since():
    session = MagicMock()
    with pytest.raises(ValueError):
        generate_brief_report(session, since=None)











@patch("intelligence.report.project_to_01_range", side_effect=lambda label, score: score)
def test_get_sentiment_trend_daily(mock_proj):
    session = MagicMock()
    # Platforms
    plat = MagicMock(platform_id=1, name="Steam")
    session.query().all.return_value = [plat]
    # Analyses, sorted by Post.timestamp
    analysis1 = MagicMock()
    analysis1.sentiment_label = "positive"
    analysis1.sentiment_score = 0.8
    analysis2 = MagicMock()
    analysis2.sentiment_label = "neutral"
    analysis2.sentiment_score = 0.5
    d1 = datetime(2024, 7, 18, 12)
    d2 = datetime(2024, 7, 18, 17)
    # Query chain returns iterable of tuples (Analysis, Post.timestamp)
    session.query().join().filter().order_by.return_value = [
        (analysis1, d1),
        (analysis2, d2)
    ]
    since = datetime(2024, 7, 18)
    trend = get_sentiment_trend(session, since=since, daily=True)
    assert isinstance(trend, list)
    assert trend[0]["positive"] == 1
    assert trend[0]["neutral"] == 1
    assert trend[0]["total"] == 2
    assert trend[0]["average_score"] == (0.8 + 0.5) / 2

@patch("intelligence.report.project_to_01_range", side_effect=lambda label, score: score)
def test_get_sentiment_trend_weekly(mock_proj):
    session = MagicMock()
    # Platforms
    plat = MagicMock(platform_id=1, name="Epic")
    session.query().all.return_value = [plat]
    analysis1 = MagicMock()
    analysis1.sentiment_label = "negative"
    analysis1.sentiment_score = 0.2
    # Same week
    d1 = datetime(2024, 7, 15)  # Monday
    d2 = datetime(2024, 7, 19)  # Friday
    session.query().join().filter().order_by.return_value = [
        (analysis1, d1),
        (analysis1, d2)
    ]
    since = datetime(2024, 7, 15)
    trend = get_sentiment_trend(session, since=since, weekly=True)
    assert isinstance(trend, list)
    assert "to" in trend[0]["date"]
    assert trend[0]["negative"] == 2
    assert trend[0]["average_score"] == 0.2

def test_get_sentiment_trend_missing_since():
    session = MagicMock()
    with pytest.raises(ValueError):
        get_sentiment_trend(session, since=None)

def test_get_sentiment_trend_both_daily_weekly():
    session = MagicMock()
    with pytest.raises(ValueError):
        get_sentiment_trend(session, since=datetime.now(), daily=True, weekly=True)













def test_get_priority_alert_no_explain():
    session = MagicMock()
    alert = MagicMock()
    alert.alert_id = 1
    alert.post_id = 2
    analysis = MagicMock()
    analysis.priority_score = 95
    # Simulate query result as iterable
    session.query().join().filter.return_value = [(alert, analysis)]
    results = get_priority_alert(session, threshold=90)
    assert len(results) == 1
    assert results[0]["alert_id"] == 1
    assert results[0]["post_id"] == 2
    assert results[0]["priority_score"] == 95
    assert "explanation" not in results[0]

def test_get_priority_alert_with_explain_note():
    session = MagicMock()
    alert = MagicMock()
    alert.alert_id = 10
    alert.post_id = 20
    alert.note = "good reason"
    analysis = MagicMock()
    analysis.priority_score = 100
    session.query().join().filter.return_value = [(alert, analysis)]
    results = get_priority_alert(session, threshold=80, explain=True)
    assert len(results) == 1
    assert results[0]["alert_id"] == 10
    assert results[0]["explanation"] == "good reason"

def test_get_priority_alert_with_explain_no_note():
    session = MagicMock()
    alert = MagicMock()
    alert.alert_id = 11
    alert.post_id = 21
    alert.note = None
    analysis = MagicMock()
    analysis.priority_score = 88
    session.query().join().filter.return_value = [(alert, analysis)]
    results = get_priority_alert(session, threshold=80, explain=True)
    assert results[0]["explanation"] == "No explanation provided"

def test_get_priority_alert_empty():
    session = MagicMock()
    session.query().join().filter.return_value = []
    results = get_priority_alert(session, threshold=80)
    assert results == []








@pytest.fixture
def now():
    return datetime.now()

@pytest.fixture
def sample_platforms():
    return [
        Platform(platform_id=1, name="Reddit"),
        Platform(platform_id=2, name="Steam")
    ]

@pytest.fixture
def sample_posts(now):
    return [
        Post(post_id=10, platform_id=1, timestamp=now - timedelta(hours=3)),
        Post(post_id=20, platform_id=2, timestamp=now - timedelta(hours=2)),
        Post(post_id=21, platform_id=2, timestamp=now - timedelta(hours=1)),
    ]

@pytest.fixture
def sample_analyses():
    return [
        Analysis(sentiment_label="positive", sentiment_score=0.8, priority_score=0.6),  # Reddit
        Analysis(sentiment_label="negative", sentiment_score=0.3, priority_score=0.2),  # Steam
        Analysis(sentiment_label="neutral", sentiment_score=0.5, priority_score=0.3),   # Steam
    ]

@pytest.fixture
def sample_alerts(now):
    return [
        Alert(post_id=10, triggered_at=now - timedelta(hours=2))
    ]

@pytest.fixture
def mock_session(sample_platforms, sample_posts, sample_analyses, sample_alerts):
    """
    Mocks a SQLAlchemy session for all tests.
    Order of .all() calls:
      1. platforms
      2. posts for Reddit
      3. analyses for Reddit
      4. posts for Steam
      5. analyses for Steam
    """
    session = MagicMock()

    # Filter posts/analyses by platform for call order
    posts_reddit = [p for p in sample_posts if p.platform_id == 1]
    posts_steam = [p for p in sample_posts if p.platform_id == 2]
    analyses_reddit = [sample_analyses[0]]
    analyses_steam = sample_analyses[1:]

    session.query.return_value.all.side_effect = [
        sample_platforms,
        posts_reddit,    # Reddit posts
        analyses_reddit, # Reddit analyses
        posts_steam,     # Steam posts
        analyses_steam   # Steam analyses
    ]
    session.query.return_value.filter.return_value.count.side_effect = [1, 0]
    return session

# def test_get_cross_platform_data_basic(mock_session):
#     with patch("intelligence.report.project_to_01_range", side_effect=lambda l, s: s):
#         result = get_cross_platform_data(mock_session)

#     assert "Reddit" in result
#     reddit = result["Reddit"]
#     # assert reddit["post_count"] == 1
#     assert reddit["analysis_count"] == 1
#     assert reddit["positive %"] == 100
#     assert reddit["neutral %"] == 0
#     assert reddit["negative %"] == 0
#     assert reddit["average_sentiment_score"] == 0.8
#     assert reddit["average_priority_score"] == 0.6
#     assert reddit["alert_count"] == 1

#     assert "Steam" in result
#     steam = result["Steam"]
#     assert steam["post_count"] == 2
#     assert steam["analysis_count"] == 2
#     assert steam["positive %"] == 0
#     assert steam["neutral %"] == 50
#     assert steam["negative %"] == 50
#     assert abs(steam["average_sentiment_score"] - 0.4) < 1e-6
#     assert abs(steam["average_priority_score"] - 0.25) < 1e-6
#     assert steam["alert_count"] == 0

def test_get_cross_platform_data_platform_filter(mock_session):
    with patch("intelligence.report.project_to_01_range", side_effect=lambda l, s: s):
        result = get_cross_platform_data(mock_session, platform=["Reddit"])
    assert set(result.keys()) == {"Reddit"}
    reddit = result["Reddit"]
    # assert reddit["post_count"] == 1

def test_get_cross_platform_data_since_filter(sample_platforms, sample_posts, sample_analyses, sample_alerts, now):
    # Filtered: only Steam data (posts <2h old)
    since = now - timedelta(hours=2)
    posts_reddit = [p for p in sample_posts if p.platform_id == 1 and p.timestamp >= since]
    posts_steam = [p for p in sample_posts if p.platform_id == 2 and p.timestamp >= since]
    analyses_reddit = []
    analyses_steam = sample_analyses[1:]
    session = MagicMock()
    session.query.return_value.all.side_effect = [
        sample_platforms,
        posts_reddit,    # Reddit posts (should be empty)
        analyses_reddit, # Reddit analyses (should be empty)
        posts_steam,     # Steam posts (2)
        analyses_steam   # Steam analyses (2)
    ]
    session.query.return_value.filter.return_value.filter.return_value.all.side_effect = [
        posts_reddit,    # Reddit posts (should be empty)
        posts_steam,     # Steam posts (2)
    ]
    session.query.return_value.join.return_value.filter.return_value.filter.return_value.all.side_effect = [
        analyses_reddit, # Reddit analyses (should be empty)
        analyses_steam   # Steam analyses (2)
    ]
    session.query.return_value.filter.return_value.count.side_effect = [0, 0]
    with patch("intelligence.report.project_to_01_range", side_effect=lambda l, s: s):
        result = get_cross_platform_data(session, since=since)
    assert result["Reddit"]["post_count"] == 0
    assert result["Steam"]["post_count"] == 2