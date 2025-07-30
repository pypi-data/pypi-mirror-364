from cli.commands.alert_cmd import handle, handle_check, handle_configure, handle_dry_run_test, handle_history, handle_mark_reviewed, handle_show_config, handle_summary

from unittest.mock import patch, mock_open, MagicMock
import pytest
from pathlib import Path


@patch("cli.commands.alert_cmd.handle_configure")
@patch("cli.commands.alert_cmd.handle_show_config")
@patch("cli.commands.alert_cmd.handle_dry_run_test")
@patch("cli.commands.alert_cmd.handle_check")
@patch("cli.commands.alert_cmd.handle_history")
@patch("cli.commands.alert_cmd.handle_summary")
@patch("cli.commands.alert_cmd.handle_mark_reviewed")
def test_handle_all_subcommands(
    mock_mark, mock_summary, mock_history, mock_check, mock_dry_run, mock_show, mock_conf, capsys
):
    # configure
    handle(["configure", "--toxic_threshold", "0.7"])
    mock_conf.assert_called_once()
    # show_config
    handle(["show_config"])
    mock_show.assert_called_once()
    # dry_run_test
    handle(["dry_run_test"])
    mock_dry_run.assert_called_once()
    # check
    handle(["check", "--live"])
    mock_check.assert_called_once()
    # history
    handle(["history", "--since", "2023-01-01"])
    mock_history.assert_called_once()
    # summary
    handle(["summary", "--show_recent"])
    mock_summary.assert_called_once()
    # mark_reviewed
    handle(["mark_reviewed", "1", "2"])
    mock_mark.assert_called_once()
    # All handlers should be called once
    assert mock_conf.call_count == 1
    assert mock_show.call_count == 1
    assert mock_dry_run.call_count == 1
    assert mock_check.call_count == 1
    assert mock_history.call_count == 1
    assert mock_summary.call_count == 1
    assert mock_mark.call_count == 1

def test_handle_no_args(capsys):
    handle([])
    out = capsys.readouterr().out
    assert "Usage: alert <command> [options]" in out

def test_handle_bad_subcommand(capsys):
    handle(["doesnotexist"])
    out = capsys.readouterr().out
    assert "[ArgParse Error]" in out or "[Error] Unknown subcommand:" in out

@patch("cli.commands.alert_cmd.handle_configure", side_effect=Exception("fail!"))
def test_handle_handler_raises(mock_conf, capsys):
    handle(["configure", "--toxic_threshold", "0.7"])
    out = capsys.readouterr().out
    assert "[Alert Error] An unexpected error occurred: fail!" in out

def test_handle_argparse_error(monkeypatch, capsys):
    class DummyParser:
        def parse_args(self, _):
            raise SystemExit()
        def add_subparsers(self, **kwargs):
            return self
        def add_parser(self, *args, **kwargs):
            return self
        def add_argument(self, *args, **kwargs):
            return None
    monkeypatch.setattr("cli.commands.alert_cmd.argparse.ArgumentParser", lambda *a, **k: DummyParser())
    handle(["configure"])
    out = capsys.readouterr().out
    assert "[ArgParse Error]" in out
    
    



@patch("cli.commands.alert_cmd.change_alert_config", return_value=True)
def test_handle_configure_single_field(mock_change, capsys):
    args = MagicMock()
    args.toxic_threshold = 0.5
    args.sentiment_crisis_threshold = None
    args.sentiment_crisis_minimum_posts = None
    args.sentiment_crisis_timeframe = None
    args.sentiment_alert_drop = None
    args.sentiment_alert_volume_spike_threshold = None
    args.sentiment_alert_timeframe = None
    args.review_bombing_negative_ratio_threshold = None
    args.review_bombing_volume_spike_threshold = None
    args.review_bombing_minimum_posts = None
    args.review_bombing_timeframe = None

    handle_configure(args)
    out = capsys.readouterr().out
    assert "Configuring alert settings..." in out
    assert "Alert configuration updated successfully." in out
    mock_change.assert_called_once_with(toxic_threshold=0.5)

@patch("cli.commands.alert_cmd.change_alert_config", return_value=True)
def test_handle_configure_multiple_fields(mock_change, capsys):
    args = MagicMock()
    args.toxic_threshold = 0.7
    args.sentiment_crisis_threshold = 0.8
    args.sentiment_crisis_minimum_posts = 12
    args.sentiment_crisis_timeframe = "12h"
    args.sentiment_alert_drop = 0.3
    args.sentiment_alert_volume_spike_threshold = 2.2
    args.sentiment_alert_timeframe = "48h"
    args.review_bombing_negative_ratio_threshold = 2.1
    args.review_bombing_volume_spike_threshold = 1.8
    args.review_bombing_minimum_posts = 22
    args.review_bombing_timeframe = "3d"

    handle_configure(args)
    out = capsys.readouterr().out
    assert "Configuring alert settings..." in out
    assert "Alert configuration updated successfully." in out
    mock_change.assert_called_once_with(
        toxic_threshold=0.7,
        sentiment_crisis_threshold=0.8,
        sentiment_crisis_minimum_posts=12,
        sentiment_crisis_timeframe="12h",
        sentiment_alert_drop=0.3,
        sentiment_alert_volume_spike_threshold=2.2,
        sentiment_alert_timeframe="48h",
        review_bombing_negative_ratio_threshold=2.1,
        review_bombing_volume_spike_threshold=1.8,
        review_bombing_minimum_posts=22,
        review_bombing_timeframe="3d",
    )

@patch("cli.commands.alert_cmd.change_alert_config", return_value=True)
def test_handle_configure_none_fields(mock_change, capsys):
    args = MagicMock()
    # All fields None
    args.toxic_threshold = None
    args.sentiment_crisis_threshold = None
    args.sentiment_crisis_minimum_posts = None
    args.sentiment_crisis_timeframe = None
    args.sentiment_alert_drop = None
    args.sentiment_alert_volume_spike_threshold = None
    args.sentiment_alert_timeframe = None
    args.review_bombing_negative_ratio_threshold = None
    args.review_bombing_volume_spike_threshold = None
    args.review_bombing_minimum_posts = None
    args.review_bombing_timeframe = None

    handle_configure(args)
    out = capsys.readouterr().out
    assert "Configuring alert settings..." in out
    assert "Alert configuration updated successfully." in out
    mock_change.assert_called_once_with()

@patch("cli.commands.alert_cmd.change_alert_config", return_value=False)
def test_handle_configure_error_single_field(mock_change, capsys):
    args = MagicMock()
    args.toxic_threshold = 0.9
    args.sentiment_crisis_threshold = None
    args.sentiment_crisis_minimum_posts = None
    args.sentiment_crisis_timeframe = None
    args.sentiment_alert_drop = None
    args.sentiment_alert_volume_spike_threshold = None
    args.sentiment_alert_timeframe = None
    args.review_bombing_negative_ratio_threshold = None
    args.review_bombing_volume_spike_threshold = None
    args.review_bombing_minimum_posts = None
    args.review_bombing_timeframe = None

    handle_configure(args)
    out = capsys.readouterr().out
    assert "Configuring alert settings..." in out
    assert "[Error] Failed to update alert configuration." in out
    mock_change.assert_called_once_with(toxic_threshold=0.9)

@patch("cli.commands.alert_cmd.change_alert_config", return_value=False)
def test_handle_configure_error_no_fields(mock_change, capsys):
    args = MagicMock()
    # All fields None
    args.toxic_threshold = None
    args.sentiment_crisis_threshold = None
    args.sentiment_crisis_minimum_posts = None
    args.sentiment_crisis_timeframe = None
    args.sentiment_alert_drop = None
    args.sentiment_alert_volume_spike_threshold = None
    args.sentiment_alert_timeframe = None
    args.review_bombing_negative_ratio_threshold = None
    args.review_bombing_volume_spike_threshold = None
    args.review_bombing_minimum_posts = None
    args.review_bombing_timeframe = None

    handle_configure(args)
    out = capsys.readouterr().out
    assert "Configuring alert settings..." in out
    assert "[Error] Failed to update alert configuration." in out
    mock_change.assert_called_once_with()





@patch("cli.commands.alert_cmd.load_alert_config", return_value={"a": 1, "b": "foo"})
def test_handle_show_config_success(mock_load, capsys):
    handle_show_config()
    out = capsys.readouterr().out
    assert "Showing current alert configuration:" in out
    assert "  a: 1" in out
    assert "  b: foo" in out

@patch("cli.commands.alert_cmd.load_alert_config", return_value=None)
def test_handle_show_config_error(mock_load, capsys):
    handle_show_config()
    out = capsys.readouterr().out
    assert "[Error] Failed to load alert configuration." in out



@patch("cli.commands.alert_cmd.dry_run_test")
def test_handle_dry_run_test_success(mock_dry_run, capsys):
    handle_dry_run_test()
    out = capsys.readouterr().out
    assert "Running dry run test for alert configuration..." in out
    mock_dry_run.assert_called_once()

@patch("cli.commands.alert_cmd.dry_run_test", side_effect=Exception("fail"))
def test_handle_dry_run_test_error(mock_dry_run, capsys):
    handle_dry_run_test()
    out = capsys.readouterr().out
    assert "[Error] An unexpected error occurred during dry run test: fail" in out
    mock_dry_run.assert_called_once()





@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.check_alerts")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_check_found(mock_close, mock_check, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    alert = MagicMock()
    alert.alert_id = 1
    alert.alert_type = "toxic"
    alert.reviewed = False
    alert.alert_severity = 5
    mock_check.return_value = [(alert, "Steam")]
    args = MagicMock()
    args.live = True
    args.platform = ["Steam"]
    handle_check(args)
    out = capsys.readouterr().out
    assert "Alerts found:" in out
    assert "Alert ID" in out
    assert "1" in out
    assert "toxic" in out
    assert "Steam" in out
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.check_alerts")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_check_none(mock_close, mock_check, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    mock_check.return_value = []
    args = MagicMock()
    args.live = False
    args.platform = None
    handle_check(args)
    out = capsys.readouterr().out
    assert "No alerts found." in out
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.check_alerts", side_effect=Exception("fail"))
@patch("cli.commands.alert_cmd.close_session")
def test_handle_check_exception(mock_close, mock_check, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.live = False
    args.platform = None
    handle_check(args)
    out = capsys.readouterr().out
    assert "[Error] An unexpected error occurred while checking alerts: fail" in out
    mock_close.assert_called_once()
    
    
    
    
    
    
@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.get_alert_history")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_history_found(mock_close, mock_history, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    alert = MagicMock()
    alert.alert_id = 42
    alert.alert_type = "scam"
    alert.alert_severity = 5
    alert.triggered_at = MagicMock()
    alert.triggered_at.strftime.return_value = "2024-07-21 20:30:00"
    mock_history.return_value = [alert]
    args = MagicMock()
    args.since = "2024-07-01"
    args.until = "2024-07-22"
    args.severity = "critical"

    handle_history(args)
    out = capsys.readouterr().out
    assert "Alert History:" in out
    assert "42" in out
    assert "scam" in out
    assert "2024-07-21 20:30:00" in out
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.get_alert_history")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_history_none(mock_close, mock_history, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    mock_history.return_value = []
    args = MagicMock()
    args.since = None
    args.until = None
    args.severity = None

    handle_history(args)
    out = capsys.readouterr().out
    assert "No alert history found." in out
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.get_alert_history", side_effect=Exception("fail"))
@patch("cli.commands.alert_cmd.close_session")
def test_handle_history_exception(mock_close, mock_history, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.since = None
    args.until = None
    args.severity = None

    handle_history(args)
    out = capsys.readouterr().out
    assert "[Error] An unexpected error occurred while retrieving alert history: fail" in out
    mock_close.assert_called_once()







@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.get_alert_summary")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_summary_found(mock_close, mock_summary, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    summary_dict = {
        "total_alerts": 7,
        "severity_counts": {
            "critical": 1, "high_severity": 2, "medium_severity": 1, "low_severity": 2, "info": 1
        }
    }
    mock_summary.return_value = summary_dict
    args = MagicMock()
    args.show_recent = False
    args.count_by_type = False
    handle_summary(args)
    out = capsys.readouterr().out
    assert "Alert Summary:" in out
    assert "Total Alerts" in out
    assert "Critical Alerts: 1" in out
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.get_alert_summary")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_summary_found_type_counts(mock_close, mock_summary, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    summary_dict = {
        "total_alerts": 3,
        "severity_counts": {
            "critical": 0, "high_severity": 1, "medium_severity": 1, "low_severity": 1, "info": 0
        },
        "type_counts": {
            "scam": 1, "toxic": 2
        }
    }
    mock_summary.return_value = summary_dict
    args = MagicMock()
    args.show_recent = False
    args.count_by_type = True
    handle_summary(args)
    out = capsys.readouterr().out
    assert "Alert Counts by Type:" in out
    assert "scam: 1" in out
    assert "toxic: 2" in out
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.get_alert_summary")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_summary_none(mock_close, mock_summary, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    mock_summary.return_value = None
    args = MagicMock()
    args.show_recent = False
    args.count_by_type = False
    handle_summary(args)
    out = capsys.readouterr().out
    assert "No alert summary found." in out
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.get_alert_summary", side_effect=Exception("fail"))
@patch("cli.commands.alert_cmd.close_session")
def test_handle_summary_exception(mock_close, mock_summary, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.show_recent = False
    args.count_by_type = False
    handle_summary(args)
    out = capsys.readouterr().out
    assert "[Error] An unexpected error occurred while summarizing alerts: fail" in out
    mock_close.assert_called_once()





@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_mark_reviewed_good(mock_close, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    alert1 = MagicMock()
    alert2 = MagicMock()
    session.query().filter().all.return_value = [alert1, alert2]
    args = MagicMock()
    args.alert_ids = ["10", "11"]

    handle_mark_reviewed(args)
    out = capsys.readouterr().out
    assert "Marked 2 alerts as reviewed." in out
    assert alert1.reviewed is True
    assert alert2.reviewed is True
    assert session.add.call_count == 2
    session.commit.assert_called_once()
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_mark_reviewed_none(mock_close, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    session.query().filter().all.return_value = []
    args = MagicMock()
    args.alert_ids = ["123", "456"]

    handle_mark_reviewed(args)
    out = capsys.readouterr().out
    assert "No alerts found with the provided IDs." in out
    session.commit.assert_not_called()
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_mark_reviewed_commit_error(mock_close, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    alert = MagicMock()
    session.query().filter().all.return_value = [alert]
    session.commit.side_effect = Exception("db fail!")
    args = MagicMock()
    args.alert_ids = ["9"]

    handle_mark_reviewed(args)
    out = capsys.readouterr().out
    assert "[Error] An unexpected error occurred while committing changes: db fail!" in out
    session.rollback.assert_called_once()
    mock_close.assert_called_once()

@patch("cli.commands.alert_cmd.get_session")
@patch("cli.commands.alert_cmd.close_session")
def test_handle_mark_reviewed_outer_exception(mock_close, mock_get_session, capsys):
    session = MagicMock()
    mock_get_session.return_value = session
    args = MagicMock()
    args.alert_ids = ["not_an_int"]

    handle_mark_reviewed(args)
    out = capsys.readouterr().out
    assert "[Error] An unexpected error occurred while marking alerts as reviewed:" in out
    mock_close.assert_called_once()
