import pytest
from unittest.mock import patch, MagicMock

from cli.commands import safety_cmd
from cli.commands.safety_cmd import handle, handle_detect_toxic, handle_detect_review_bombing, handle_detect_spam, handle_detect_scam, handle_detect_sentiment_crisis, handle_detect_trend_alerts


def test_safety_handle_detect_toxic_calls_handler():
    args = [
        "detect_toxic",
        "--threshold", "0.9",
        "--platform", "reddit",
        "--since", "2024-01-01"
    ]
    with patch.object(safety_cmd, "handle_detect_toxic") as mock_detect_toxic:
        safety_cmd.handle(args)
        mock_detect_toxic.assert_called_once()
        called_args = mock_detect_toxic.call_args[0][0]
        assert called_args.threshold == 0.9
        assert called_args.platform == ["reddit"]
        assert called_args.since == "2024-01-01"

def test_safety_handle_detect_spam_calls_handler():
    args = [
        "detect_spam",
        "--auto_flag"
    ]
    with patch.object(safety_cmd, "handle_detect_spam") as mock_detect_spam:
        safety_cmd.handle(args)
        mock_detect_spam.assert_called_once()
        called_args = mock_detect_spam.call_args[0][0]
        assert called_args.auto_flag is True

def test_safety_handle_detect_scam_calls_handler():
    args = [
        "detect_scam",
        "--scam_patterns_file", "scam.txt",
        "--alert_high_risk"
    ]
    with patch.object(safety_cmd, "handle_detect_scam") as mock_detect_scam:
        safety_cmd.handle(args)
        mock_detect_scam.assert_called_once()
        called_args = mock_detect_scam.call_args[0][0]
        assert called_args.scam_patterns_file == "scam.txt"
        assert called_args.alert_high_risk is True

def test_safety_handle_detect_sentiment_crisis_calls_handler():
    args = [
        "detect_sentiment_crisis",
        "--timeframe", "48h",
        "--minimum_posts", "100",
        "--threshold", "0.7"
    ]
    with patch.object(safety_cmd, "handle_detect_sentiment_crisis") as mock_handler:
        safety_cmd.handle(args)
        mock_handler.assert_called_once()
        called_args = mock_handler.call_args[0][0]
        assert called_args.timeframe == "48h"
        assert called_args.minimum_posts == 100
        assert called_args.threshold == 0.7

def test_safety_handle_detect_trend_alerts_calls_handler():
    args = [
        "detect_trend_alerts",
        "--sentiment_drop", "0.5",
        "--volume_spike", "3.0",
        "--timeframe", "7d",
        "--alert"
    ]
    with patch.object(safety_cmd, "handle_detect_trend_alerts") as mock_handler:
        safety_cmd.handle(args)
        mock_handler.assert_called_once()
        called_args = mock_handler.call_args[0][0]
        assert called_args.sentiment_drop == 0.5
        assert called_args.volume_spike == 3.0
        assert called_args.timeframe == "7d"
        assert called_args.alert is True

def test_safety_handle_detect_review_bombing_calls_handler():
    args = [
        "detect_review_bombing",
        "--ratio_threshold", "3.0",
        "--volume_threshold", "2.0",
        "--minimum_posts", "80",
        "--timeframe", "12h",
        "--platform", "steam", "epic"
    ]
    with patch.object(safety_cmd, "handle_detect_review_bombing") as mock_handler:
        safety_cmd.handle(args)
        mock_handler.assert_called_once()
        called_args = mock_handler.call_args[0][0]
        assert called_args.ratio_threshold == 3.0
        assert called_args.volume_threshold == 2.0
        assert called_args.minimum_posts == 80
        assert called_args.timeframe == "12h"
        assert called_args.platform == ["steam", "epic"]

def test_safety_handle_invalid_subcommand(capsys):
    args = ["not_a_real_subcommand"]
    safety_cmd.handle(args)
    captured = capsys.readouterr()
    assert "[ArgParse Error]" in captured.out

def test_safety_handle_unexpected_exception(monkeypatch, capsys):
    def raise_exception(*a, **kw):
        raise RuntimeError("unexpected!")
    monkeypatch.setattr("cli.commands.safety_cmd.argparse.ArgumentParser.parse_args", lambda self, args: raise_exception())
    safety_cmd.handle(["detect_toxic"])
    captured = capsys.readouterr()
    assert "[Error] An unexpected error occurred: unexpected!" in captured.out
        
def test_safety_handle_no_args(capsys):
    safety_cmd.handle([])
    captured = capsys.readouterr()
    assert "[Error] No subcommand provided for safety command." in captured.out
    
    
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_toxic")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_toxic_good(
    mock_get_session, mock_detect_toxic, mock_Alert, mock_close_session, capsys
):
    # Arrange
    session = MagicMock()
    mock_get_session.return_value = session

    post = MagicMock(post_id=123)
    mock_detect_toxic.return_value = [(post, "toxic_keyword")]
    args = MagicMock()
    args.threshold = 0.8
    args.platform = None
    args.since = None
    args.until = None
    args.toxic_keywords_file = None

    # Act
    handle_detect_toxic(args)
    captured = capsys.readouterr()

    # Assert
    assert "Toxic Post Detected: 123 | Reason: toxic_keyword" in captured.out
    session.add.assert_called_once()
    session.commit.assert_called_once()
    mock_close_session.assert_called_once()
    
    
def test_handle_toxic_exceptions(capsys):
    with patch("cli.commands.safety_cmd.detect_toxic", side_effect=RuntimeError("Test error")):
        args = MagicMock()
        args.threshold = 0.8
        args.platform = None
        args.since = None
        args.until = None
        args.toxic_keywords_file = None

        handle_detect_toxic(args)

        captured = capsys.readouterr()
        assert "[Error] Failed to detect toxic posts: Test error" in captured.out
        
def test_handle_toxic_no_posts(capsys):
    with patch("cli.commands.safety_cmd.detect_toxic", return_value=[]):
        args = MagicMock()
        args.threshold = 0.8
        args.platform = None
        args.since = None
        args.until = None
        args.toxic_keywords_file = None

        handle_detect_toxic(args)

        captured = capsys.readouterr()
        assert "No toxic posts detected with the given criteria." in captured.out
        
def test_handle_toxic_commit_error(capsys):
    session = MagicMock()
    with patch("cli.commands.safety_cmd.get_session", return_value=session), \
         patch("cli.commands.safety_cmd.detect_toxic", return_value=[(MagicMock(post_id=123), "toxic_keyword")]), \
         patch("cli.commands.safety_cmd.close_session") as mock_close_session:
        
        session.commit.side_effect = RuntimeError("Commit failed")
        
        args = MagicMock()
        args.threshold = 0.8
        args.platform = None
        args.since = None
        args.until = None
        args.toxic_keywords_file = None

        handle_detect_toxic(args)

        captured = capsys.readouterr()
        assert "[Error] Failed to add alert for toxic posts" in captured.out
        mock_close_session.assert_called_once()
        

@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_spam")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_spam_good(
    mock_get_session, mock_detect_spam, mock_Alert, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session

    post = MagicMock(post_id=123)
    mock_detect_spam.return_value = [(post, "regex")]
    args = MagicMock()
    args.spam_patterns_file = "dummy.json"
    args.auto_flag = False

    handle_detect_spam(args)
    captured = capsys.readouterr()
    assert "Spam Post Detected: 123 | Reason: regex" in captured.out
    session.add.assert_called_once()
    session.commit.assert_called_once()
    mock_close_session.assert_called_once()

# --- NO SPAM ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_spam")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_spam_none(mock_get_session, mock_detect_spam, mock_close_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    mock_detect_spam.return_value = []
    args = MagicMock()
    args.spam_patterns_file = "dummy.json"
    args.auto_flag = False

    handle_detect_spam(args)
    captured = capsys.readouterr()
    assert "No spam posts detected with the given criteria." in captured.out
    session.add.assert_not_called()
    session.commit.assert_not_called()
    mock_close_session.assert_called_once()

# --- COMMIT FAILS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_spam")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_spam_commit_fails(
    mock_get_session, mock_detect_spam, mock_Alert, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    post = MagicMock(post_id=123)
    mock_detect_spam.return_value = [(post, "regex")]
    args = MagicMock()
    args.spam_patterns_file = "dummy.json"
    args.auto_flag = False

    session.commit.side_effect = Exception("commit error")
    handle_detect_spam(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to add spam alerts: commit error" in captured.out
    session.rollback.assert_called_once()
    mock_close_session.assert_called_once()

# --- DETECT_SPAM RAISES EXCEPTION ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_spam", side_effect=Exception("Detect fail"))
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_spam_detect_error(
    mock_get_session, mock_detect_spam, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.spam_patterns_file = "dummy.json"
    args.auto_flag = False

    handle_detect_spam(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to detect spam posts: Detect fail" in captured.out
    mock_close_session.assert_called_once()
    
    
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_scam")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_scam_good(
    mock_get_session, mock_detect_scam, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session

    post = MagicMock(post_id=555)
    mock_detect_scam.return_value = [(post, 6, "critical scam!")]
    args = MagicMock()
    args.scam_patterns_file = "dummy.json"
    args.alert_high_risk = True

    handle_detect_scam(args)
    captured = capsys.readouterr()
    assert "Scam Post Detected: 555 | Score: 6 | Reason: critical scam!" in captured.out
    mock_close_session.assert_called_once()

# --- NO SCAMS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_scam")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_scam_none(mock_get_session, mock_detect_scam, mock_close_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    mock_detect_scam.return_value = []
    args = MagicMock()
    args.scam_patterns_file = "dummy.json"
    args.alert_high_risk = True

    handle_detect_scam(args)
    captured = capsys.readouterr()
    assert "No scam posts detected with the given criteria." in captured.out
    mock_close_session.assert_called_once()

# --- EXCEPTION PATH ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_scam", side_effect=Exception("Something broke!"))
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_scam_exception(
    mock_get_session, mock_detect_scam, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.scam_patterns_file = "dummy.json"
    args.alert_high_risk = True
    handle_detect_scam(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to detect scam posts: Something broke!" in captured.out
    mock_close_session.assert_called_once()
    
    
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_sentiment_crisis")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_sentiment_crisis_good(
    mock_get_session, mock_detect_sentiment_crisis, mock_Alert, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    # Prepare posts with post_id
    post = MagicMock(post_id=101)
    mock_detect_sentiment_crisis.return_value = [post]
    args = MagicMock()
    args.timeframe = "1d"
    args.minimum_posts = 1
    args.threshold = 0.8

    from cli.commands.safety_cmd import handle_detect_sentiment_crisis
    handle_detect_sentiment_crisis(args)
    captured = capsys.readouterr()
    assert "Sentiment Crisis Detected in 1 posts:" in captured.out
    assert "Post IDs:" in captured.out
    assert "Adding alert for sentiment crisis based on post ID: 101" in captured.out
    session.add.assert_called_once()
    session.commit.assert_called_once()
    mock_close_session.assert_called_once()

# --- NO CRISIS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_sentiment_crisis")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_sentiment_crisis_none(
    mock_get_session, mock_detect_sentiment_crisis, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    mock_detect_sentiment_crisis.return_value = []
    args = MagicMock()
    args.timeframe = "1d"
    args.minimum_posts = 1
    args.threshold = 0.8

    from cli.commands.safety_cmd import handle_detect_sentiment_crisis
    handle_detect_sentiment_crisis(args)
    captured = capsys.readouterr()
    assert "No sentiment crisis detected with the given criteria." in captured.out
    session.add.assert_not_called()
    session.commit.assert_not_called()
    mock_close_session.assert_called_once()

# --- COMMIT FAILS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_sentiment_crisis")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_sentiment_crisis_commit_error(
    mock_get_session, mock_detect_sentiment_crisis, mock_Alert, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    post = MagicMock(post_id=202)
    mock_detect_sentiment_crisis.return_value = [post]
    args = MagicMock()
    args.timeframe = "1d"
    args.minimum_posts = 1
    args.threshold = 0.8

    session.commit.side_effect = Exception("commit error!")
    from cli.commands.safety_cmd import handle_detect_sentiment_crisis
    handle_detect_sentiment_crisis(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to add alert for sentiment crisis: commit error!" in captured.out
    session.rollback.assert_called_once()
    mock_close_session.assert_called_once()

# --- DETECTION FAILS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_sentiment_crisis", side_effect=Exception("detection failed"))
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_sentiment_crisis_detect_error(
    mock_get_session, mock_detect_sentiment_crisis, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.timeframe = "1d"
    args.minimum_posts = 1
    args.threshold = 0.8

    from cli.commands.safety_cmd import handle_detect_sentiment_crisis
    handle_detect_sentiment_crisis(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to detect sentiment crisis: detection failed" in captured.out
    mock_close_session.assert_called_once()
    
    
    
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_trend_alerts")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_trend_alerts_good(
    mock_get_session, mock_detect_trend_alerts, mock_Alert, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session

    post = MagicMock(post_id=77)
    alerts = [("sentiment drop", "Sentiment fell")]
    posts = [(post, MagicMock())]
    mock_detect_trend_alerts.return_value = {"alerts": alerts, "posts": posts}
    args = MagicMock()
    args.volume_spike = 2.0
    args.sentiment_drop = 0.3
    args.timeframe = "2d"
    args.alert = True

    from cli.commands.safety_cmd import handle_detect_trend_alerts
    handle_detect_trend_alerts(args)
    captured = capsys.readouterr()
    assert "Trend Alerts Detected:" in captured.out
    assert "Alerts:" in captured.out
    session.add.assert_called_once()
    session.commit.assert_called_once()
    mock_close_session.assert_called_once()

# --- GOOD PATH: Alerts found, alert not saved (args.alert False) ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_trend_alerts")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_trend_alerts_no_save(
    mock_get_session, mock_detect_trend_alerts, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session

    post = MagicMock(post_id=88)
    alerts = [("volume spike", "Lots of posts!")]
    posts = [(post, MagicMock())]
    mock_detect_trend_alerts.return_value = {"alerts": alerts, "posts": posts}
    args = MagicMock()
    args.volume_spike = 2.0
    args.sentiment_drop = 0.3
    args.timeframe = "2d"
    args.alert = False

    from cli.commands.safety_cmd import handle_detect_trend_alerts
    handle_detect_trend_alerts(args)
    captured = capsys.readouterr()
    assert "Trend Alerts Detected:" in captured.out
    session.add.assert_not_called()
    session.commit.assert_not_called()
    mock_close_session.assert_called_once()

# --- NO ALERTS FOUND (empty or missing) ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_trend_alerts")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_trend_alerts_none(
    mock_get_session, mock_detect_trend_alerts, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    # Case 1: detect_trend_alerts returns {}
    mock_detect_trend_alerts.return_value = {}
    args = MagicMock()
    args.volume_spike = 1.5
    args.sentiment_drop = 0.2
    args.timeframe = "1d"
    args.alert = True

    from cli.commands.safety_cmd import handle_detect_trend_alerts
    handle_detect_trend_alerts(args)
    captured = capsys.readouterr()
    assert "No trend alerts detected with the given criteria." in captured.out

    # Case 2: alerts list is empty
    mock_detect_trend_alerts.return_value = {"alerts": [], "posts": []}
    handle_detect_trend_alerts(args)
    captured = capsys.readouterr()
    assert "No posts found that triggered trend alerts." in captured.out

# --- COMMIT FAILS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_trend_alerts")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_trend_alerts_commit_error(
    mock_get_session, mock_detect_trend_alerts, mock_Alert, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session

    post = MagicMock(post_id=99)
    alerts = [("sentiment drop", "Sentiment fell")]
    posts = [(post, MagicMock())]
    mock_detect_trend_alerts.return_value = {"alerts": alerts, "posts": posts}
    args = MagicMock()
    args.volume_spike = 1.5
    args.sentiment_drop = 0.2
    args.timeframe = "1d"
    args.alert = True

    session.commit.side_effect = Exception("commit fail!")
    from cli.commands.safety_cmd import handle_detect_trend_alerts
    handle_detect_trend_alerts(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to add alert for trend: commit fail!" in captured.out
    session.rollback.assert_called_once()
    mock_close_session.assert_called_once()

# --- DETECTION FAILS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_trend_alerts", side_effect=Exception("trend fail"))
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_trend_alerts_detect_error(
    mock_get_session, mock_detect_trend_alerts, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.volume_spike = 1.5
    args.sentiment_drop = 0.2
    args.timeframe = "1d"
    args.alert = True

    from cli.commands.safety_cmd import handle_detect_trend_alerts
    handle_detect_trend_alerts(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to detect trend alerts: trend fail" in captured.out
    mock_close_session.assert_called_once()
    
    
    
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_review_bombing")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_review_bombing_good(
    mock_get_session, mock_detect_review_bombing, mock_Alert, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    post = MagicMock(post_id=808)
    mock_detect_review_bombing.return_value = (True, [post])
    args = MagicMock()
    args.ratio_threshold = 2.5
    args.volume_threshold = 1.5
    args.minimum_posts = 2
    args.timeframe = "6h"
    args.platform = ["steam"]

    from cli.commands.safety_cmd import handle_detect_review_bombing
    handle_detect_review_bombing(args)
    captured = capsys.readouterr()
    assert "Review Bombing Detected in 1 posts:" in captured.out
    session.add.assert_called_once()
    session.commit.assert_called_once()
    mock_close_session.assert_called_once()

# --- NO REVIEW BOMBING ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_review_bombing")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_review_bombing_none(
    mock_get_session, mock_detect_review_bombing, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    mock_detect_review_bombing.return_value = (False, [])
    args = MagicMock()
    args.ratio_threshold = 2.5
    args.volume_threshold = 1.5
    args.minimum_posts = 2
    args.timeframe = "6h"
    args.platform = ["steam"]

    from cli.commands.safety_cmd import handle_detect_review_bombing
    handle_detect_review_bombing(args)
    captured = capsys.readouterr()
    assert "No review bombing detected with the given criteria." in captured.out
    session.add.assert_not_called()
    session.commit.assert_not_called()
    mock_close_session.assert_called_once()

# --- COMMIT FAILS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.Alert")
@patch("cli.commands.safety_cmd.detect_review_bombing")
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_review_bombing_commit_fails(
    mock_get_session, mock_detect_review_bombing, mock_Alert, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    post = MagicMock(post_id=909)
    mock_detect_review_bombing.return_value = (True, [post])
    args = MagicMock()
    args.ratio_threshold = 2.5
    args.volume_threshold = 1.5
    args.minimum_posts = 2
    args.timeframe = "6h"
    args.platform = ["steam"]

    session.commit.side_effect = Exception("fail!")
    from cli.commands.safety_cmd import handle_detect_review_bombing
    handle_detect_review_bombing(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to add alert for review bombing: fail!" in captured.out
    session.rollback.assert_called_once()
    mock_close_session.assert_called_once()

# --- DETECTION FUNCTION FAILS ---
@patch("cli.commands.safety_cmd.close_session")
@patch("cli.commands.safety_cmd.detect_review_bombing", side_effect=Exception("detect fail"))
@patch("cli.commands.safety_cmd.get_session")
def test_handle_detect_review_bombing_detect_error(
    mock_get_session, mock_detect_review_bombing, mock_close_session, capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.ratio_threshold = 2.5
    args.volume_threshold = 1.5
    args.minimum_posts = 2
    args.timeframe = "6h"
    args.platform = ["steam"]

    from cli.commands.safety_cmd import handle_detect_review_bombing
    handle_detect_review_bombing(args)
    captured = capsys.readouterr()
    assert "[Error] Failed to detect review bombing: detect fail" in captured.out
    mock_close_session.assert_called_once()