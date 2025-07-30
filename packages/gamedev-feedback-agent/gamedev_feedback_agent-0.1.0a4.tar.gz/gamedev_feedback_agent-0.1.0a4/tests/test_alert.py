from unittest.mock import patch, mock_open, MagicMock
import pytest
from pathlib import Path

from intelligence.alert import load_alert_config, change_alert_config, dry_run_test, check_alerts, get_alert_history, get_alert_summary


@patch("intelligence.alert.get_context", return_value={"workspace": Path("/workdir")})
@patch("intelligence.alert.open", new_callable=mock_open, read_data='{"key": "val"}')
def test_load_alert_config_success(mock_file, mock_ctx):
    result = load_alert_config("alert.json")
    assert isinstance(result, dict)
    assert result["key"] == "val"
    # Check joined path
    mock_file.assert_called_with(Path("/workdir") / "alert.json", "r")

@patch("intelligence.alert.get_context", return_value={"workspace": Path("/workdir")})
@patch("intelligence.alert.open", new_callable=mock_open)
def test_load_alert_config_abs_path(mock_file, mock_ctx):
    # Provide an absolute path; should not join
    result = load_alert_config("/abs/alert.json")
    # open called directly with absolute path
    mock_file.assert_called_with("/abs/alert.json", "r")

@patch("intelligence.alert.get_context", return_value={"workspace": Path("/workdir")})
@patch("intelligence.alert.open", side_effect=FileNotFoundError)
def test_load_alert_config_file_not_found(mock_file, mock_ctx):
    result = load_alert_config("notfound.json")
    assert result is None

@patch("intelligence.alert.get_context", return_value={"workspace": Path("/workdir")})
@patch("intelligence.alert.open", new_callable=mock_open, read_data="not a json")
def test_load_alert_config_invalid_json(mock_file, mock_ctx):
    result = load_alert_config("bad.json")
    assert result is None
    
    
    
    
# --- SUCCESS PATH ---
@patch("intelligence.alert.get_context", return_value={"workspace": Path("/my/workspace")})
@patch("intelligence.alert.load_alert_config", return_value={"a": 1, "b": 2})
@patch("intelligence.alert.open", new_callable=mock_open)
def test_change_alert_config_success(mock_file, mock_load, mock_ctx, capsys):
    from intelligence.alert import change_alert_config
    ok = change_alert_config("config.json", a=2)
    assert ok is True
    handle = mock_file()
    handle.write.assert_called()  # json.dump writes
    assert "[Info] Alert configuration updated successfully." in capsys.readouterr().out

# --- NO CHANGES ---
@patch("intelligence.alert.get_context", return_value={"workspace": Path("/my/workspace")})
@patch("intelligence.alert.load_alert_config", return_value={"a": 1, "b": 2})
@patch("intelligence.alert.open", new_callable=mock_open)
def test_change_alert_config_no_changes(mock_file, mock_load, mock_ctx, capsys):
    from intelligence.alert import change_alert_config
    ok = change_alert_config("config.json", a=1)
    assert ok is True
    handle = mock_file()
    handle.write.assert_not_called()
    assert "[Info] No changes made to the alert configuration." in capsys.readouterr().out

# --- WARNING FOR MISSING KEY ---
@patch("intelligence.alert.get_context", return_value={"workspace": Path("/my/workspace")})
@patch("intelligence.alert.load_alert_config", return_value={"a": 1})
@patch("intelligence.alert.open", new_callable=mock_open)
def test_change_alert_config_warn_missing_key(mock_file, mock_load, mock_ctx, capsys):
    from intelligence.alert import change_alert_config
    ok = change_alert_config("config.json", z=999)
    assert ok is True
    assert "[Warning] Key 'z' not found in alert configuration." in capsys.readouterr().out

# --- LOAD FAILURE ---
@patch("intelligence.alert.get_context", return_value={"workspace": Path("/my/workspace")})
@patch("intelligence.alert.load_alert_config", return_value=None)
@patch("intelligence.alert.open", new_callable=mock_open)
def test_change_alert_config_load_fail(mock_file, mock_load, mock_ctx, capsys):
    from intelligence.alert import change_alert_config
    ok = change_alert_config("config.json", a=2)
    assert ok is False
    assert "[Error] Failed to load alert configuration." in capsys.readouterr().out

# --- WRITE FAILURE ---
@patch("intelligence.alert.get_context", return_value={"workspace": Path("/my/workspace")})
@patch("intelligence.alert.load_alert_config", return_value={"a": 1, "b": 2})
@patch("intelligence.alert.open", side_effect=OSError("disk full"))
def test_change_alert_config_write_fail(mock_file, mock_load, mock_ctx, capsys):
    from intelligence.alert import change_alert_config
    ok = change_alert_config("config.json", a=2)
    assert ok is False
    out = capsys.readouterr().out
    assert "[Error] Failed to update alert configuration: disk full" in out
    
    
    
    
@patch("intelligence.alert.load_alert_config", return_value={
    "toxic_threshold": 0.8,
    "sentiment_crisis_threshold": 0.8,
    "sentiment_crisis_minimum_posts": 2,
    "sentiment_crisis_timeframe": "1d",
    "sentiment_alert_drop": 0.3,
    "sentiment_alert_volume_spike_threshold": 2.0,
    "sentiment_alert_timeframe": "1d",
    "review_bombing_negative_ratio_threshold": 2.5,
    "review_bombing_volume_spike_threshold": 1.5,
    "review_bombing_minimum_posts": 2,
    "review_bombing_timeframe": "1d",
})
@patch("intelligence.alert.get_session")
@patch("intelligence.alert.detect_toxic", return_value=[(MagicMock(content="toxic content"), "badword")])
@patch("intelligence.alert.detect_spam", return_value=[(MagicMock(post_id=123), "regex")])
@patch("intelligence.alert.detect_scam", return_value=[(MagicMock(post_id=222), 5, "scam reason")])
@patch("intelligence.alert.detect_sentiment_crisis", return_value=[MagicMock()])
@patch("intelligence.alert.detect_trend_alerts", return_value={"posts": [MagicMock()], "alerts": [("sentiment drop", "desc")]})
@patch("intelligence.alert.detect_review_bombing", return_value=[MagicMock()])
def test_dry_run_test_success(
    mock_detect_review_bombing, mock_detect_trend_alerts, mock_detect_sentiment_crisis,
    mock_detect_scam, mock_detect_spam, mock_detect_toxic, mock_get_session, mock_load_config, capsys
):
    dry_run_test()
    out = capsys.readouterr().out
    assert "[Info] Running dry run test..." in out
    assert "[Alert] Toxic Post Detected: toxic content | Reason: badword" in out
    assert "[Alert] Spam Post Detected: 123 | Reason: regex" in out
    assert "[Alert] Scam Post Detected: 222 | Score: 5 | Reason: scam reason" in out
    assert "Sentiment Crisis Detected:" in out
    assert "[Alert] Sentiment Trend Alerts Detected:" in out
    assert "sentiment drop: desc" in out
    assert "[Alert] Review Bombing Detected:" in out

@patch("intelligence.alert.load_alert_config", return_value=None)
def test_dry_run_test_config_fail(mock_load_config, capsys):
    dry_run_test()
    out = capsys.readouterr().out
    assert "[Error] Failed to load alert configuration." in out

@patch("intelligence.alert.load_alert_config", return_value={
    "toxic_threshold": 0.8,
    "sentiment_crisis_threshold": 0.8,
    "sentiment_crisis_minimum_posts": 2,
    "sentiment_crisis_timeframe": "1d",
    "sentiment_alert_drop": 0.3,
    "sentiment_alert_volume_spike_threshold": 2.0,
    "sentiment_alert_timeframe": "1d",
    "review_bombing_negative_ratio_threshold": 2.5,
    "review_bombing_volume_spike_threshold": 1.5,
    "review_bombing_minimum_posts": 2,
    "review_bombing_timeframe": "1d",
})
@patch("intelligence.alert.get_session")
@patch("intelligence.alert.detect_toxic", return_value=[])
@patch("intelligence.alert.detect_spam", return_value=[])
@patch("intelligence.alert.detect_scam", return_value=[])
@patch("intelligence.alert.detect_sentiment_crisis", return_value=[])
@patch("intelligence.alert.detect_trend_alerts", return_value={})
@patch("intelligence.alert.detect_review_bombing", return_value=[])
def test_dry_run_test_no_alerts(
    mock_detect_review_bombing, mock_detect_trend_alerts, mock_detect_sentiment_crisis,
    mock_detect_scam, mock_detect_spam, mock_detect_toxic, mock_get_session, mock_load_config, capsys
):
    dry_run_test()
    out = capsys.readouterr().out
    assert "[Info] No toxic posts detected." in out
    assert "[Info] No spam posts detected." in out
    assert "[Info] No scam posts detected." in out
    assert "No sentiment crisis detected with the given criteria." in out
    assert "[Info] No sentiment trend alerts detected." in out
    assert "[Info] No review bombing detected." in out






def test_check_alerts_basic():
    session = MagicMock()
    alert = MagicMock()
    platform = MagicMock()
    platform.name = "Steam"
    session.query().join().join().order_by().all.return_value = [(alert, platform)]
    result = check_alerts(session)
    assert result == [(alert, "Steam")]

def test_check_alerts_live_filter():
    session = MagicMock()
    alert = MagicMock()
    platform = MagicMock()
    platform.name = "Epic"
    session.query().join().join().filter().order_by().all.return_value = [(alert, platform)]
    result = check_alerts(session, live=True)
    assert result == [(alert, "Epic")]

def test_check_alerts_platform_filter_found(monkeypatch, capsys):
    session = MagicMock()
    alert = MagicMock()
    platform_obj = MagicMock()
    platform_obj.name = "GOG"
    session.query().filter().first.side_effect = [(99,), (88,)]  # two platform lookups
    session.query().join().join().filter().order_by().all.return_value = [(alert, platform_obj)]
    result = check_alerts(session, platform=["GOG", "FakePlatform"])
    assert result == [(alert, "GOG")]

def test_check_alerts_platform_filter_missing(monkeypatch, capsys):
    session = MagicMock()
    alert = MagicMock()
    platform_obj = MagicMock()
    platform_obj.name = "XBox"
    session.query().filter().first.side_effect = [None, (42,)]
    session.query().join().join().filter().order_by().all.return_value = [(alert, platform_obj)]
    result = check_alerts(session, platform=["Missing", "XBox"])
    assert result == [(alert, "XBox")]
    out = capsys.readouterr().out
    assert "[Warning] Platform 'Missing' not found. Skipping it." in out

def test_check_alerts_empty_result():
    session = MagicMock()
    session.query().join().join().order_by().all.return_value = []
    result = check_alerts(session)
    assert result == []





def test_get_alert_history_all():
    session = MagicMock()
    alerts = [MagicMock()]
    session.query().all.return_value = alerts
    result = get_alert_history(session)
    assert result == alerts

def test_get_alert_history_since_until():
    session = MagicMock()
    query = session.query.return_value
    # Each .filter() returns the query so chaining works
    query.filter.return_value = query
    alerts = [MagicMock()]
    query.all.return_value = alerts
    result = get_alert_history(session, since="2024-07-20T10:00:00", until="2024-07-21T10:00:00")
    assert result == alerts
    # Optionally, check that filter was called for both dates:
    assert query.filter.call_count >= 2

def test_get_alert_history_severity_critical():
    session = MagicMock()
    query = session.query.return_value
    query.filter.return_value = query
    alerts = [MagicMock()]
    query.all.return_value = alerts
    result = get_alert_history(session, severity="critical")
    assert result == alerts

def test_get_alert_history_severity_high():
    session = MagicMock()
    query = session.query.return_value
    query.filter.return_value = query
    alerts = [MagicMock()]
    query.all.return_value = alerts
    result = get_alert_history(session, severity="high")
    assert result == alerts

def test_get_alert_history_severity_medium():
    session = MagicMock()
    query = session.query.return_value
    query.filter.return_value = query
    alerts = [MagicMock()]
    query.all.return_value = alerts
    result = get_alert_history(session, severity="medium")
    assert result == alerts

def test_get_alert_history_severity_low():
    session = MagicMock()
    query = session.query.return_value
    query.filter.return_value = query
    alerts = [MagicMock()]
    query.all.return_value = alerts
    result = get_alert_history(session, severity="low")
    assert result == alerts

def test_get_alert_history_severity_info():
    session = MagicMock()
    query = session.query.return_value
    query.filter.return_value = query
    alerts = [MagicMock()]
    query.all.return_value = alerts
    result = get_alert_history(session, severity="info")
    assert result == alerts

def test_get_alert_history_severity_unknown(capsys):
    session = MagicMock()
    query = session.query.return_value
    query.filter.return_value = query
    alerts = [MagicMock()]
    query.all.return_value = alerts
    result = get_alert_history(session, severity="weirdness")
    assert result == alerts
    out = capsys.readouterr().out
    assert "[Warning] Unknown severity 'weirdness'. No filtering applied." in out

def test_get_alert_history_no_results(capsys):
    session = MagicMock()
    session.query().all.return_value = []
    result = get_alert_history(session)
    assert result == []
    out = capsys.readouterr().out
    assert "[Info] No alerts found for the specified criteria." in out





def test_get_alert_summary_basic():
    session = MagicMock()
    alert1 = MagicMock(alert_severity=5, alert_type="spam")
    alert2 = MagicMock(alert_severity=4, alert_type="scam")
    alert3 = MagicMock(alert_severity=3, alert_type="toxic")
    alert4 = MagicMock(alert_severity=2, alert_type="trend")
    alert5 = MagicMock(alert_severity=1, alert_type="info")
    session.query().all.return_value = [alert1, alert2, alert3, alert4, alert5]
    summary = get_alert_summary(session)
    assert summary["total_alerts"] == 5
    assert summary["severity_counts"]["critical"] == 1
    assert summary["severity_counts"]["high_severity"] == 1
    assert summary["severity_counts"]["medium_severity"] == 1
    assert summary["severity_counts"]["low_severity"] == 1
    assert summary["severity_counts"]["info"] == 1
    assert "type_counts" not in summary

def test_get_alert_summary_empty():
    session = MagicMock()
    session.query().all.return_value = []
    summary = get_alert_summary(session)
    assert summary["total_alerts"] == 0
    for k in summary["severity_counts"]:
        assert summary["severity_counts"][k] == 0

def test_get_alert_summary_recent():
    session = MagicMock()
    query = session.query.return_value
    query.filter.return_value = query
    query.limit.return_value = query
    alert = MagicMock(alert_severity=5, alert_type="scam")
    query.all.return_value = [alert]
    summary = get_alert_summary(session, show_recent=True)
    assert summary["total_alerts"] == 1
    assert summary["severity_counts"]["critical"] == 1

def test_get_alert_summary_count_by_type():
    session = MagicMock()
    alert1 = MagicMock(alert_severity=5, alert_type="spam")
    alert2 = MagicMock(alert_severity=4, alert_type="scam")
    alert3 = MagicMock(alert_severity=4, alert_type="scam")
    session.query().all.return_value = [alert1, alert2, alert3]
    summary = get_alert_summary(session, count_by_type=True)
    assert summary["type_counts"] == {"spam": 1, "scam": 2}
    assert summary["severity_counts"]["critical"] == 1
    assert summary["severity_counts"]["high_severity"] == 2
