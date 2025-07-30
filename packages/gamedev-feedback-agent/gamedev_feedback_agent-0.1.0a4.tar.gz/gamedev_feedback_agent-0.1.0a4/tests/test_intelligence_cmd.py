import pytest
from unittest.mock import patch
from argparse import Namespace
from unittest.mock import MagicMock

from cli.commands.intelligence_cmd import handle, handle_show_coverage, handle_process_uncovered

def test_handle_show_coverage(capsys):
    with patch("cli.commands.intelligence_cmd.handle_show_coverage") as mock_show_coverage, \
            patch("cli.commands.intelligence_cmd.handle_process_uncovered") as mock_process_uncovered:
        handle(["show_coverage"])
        mock_show_coverage.assert_called_once()
        captured = capsys.readouterr()
        assert "Executing intelligence command with subcommand: show_coverage" in captured.out
        
        handle(["process_uncovered"])
        mock_process_uncovered.assert_called_once()
        captured = capsys.readouterr()
        assert "Executing intelligence command with subcommand: process_uncovered" in captured.out

def test_handle_invalid_subcommand(capsys):
    handle(["invalid_subcommand"])
    captured = capsys.readouterr()
    assert "[ArgParse Error]" in captured.out
    
    
def test_handle_unexpected_error(capsys):
    with patch("cli.commands.intelligence_cmd.get_session", side_effect=Exception("Unexpected error")):
        handle(["show_coverage"])
        captured = capsys.readouterr()
        assert "[Intelligence Error] An unexpected error occurred: Unexpected error" in captured.out
        
        
        
def test_handle_show_coverage_prints_summary(monkeypatch, capsys):
    class DummyArgs:
        platforms = ["pc"]
        since = "2024-01-01"
        until = "2024-06-01"
        detailed = False
    
    class DummyArgs2:
        platforms = ["pc"]
        since = "2024-01-01"
        until = "2024-06-01"
        detailed = True

    dummy_summary = {"files_covered": 10, "files_uncovered": ["a.py", "b.py"]}

    def fake_get_session():
        return "dummy_session"

    def fake_get_coverage_summary(session, platforms, since, until):
        assert session == "dummy_session"
        assert platforms == ["pc"]
        assert since == "2024-01-01"
        assert until == "2024-06-01"
        return dummy_summary

    def fake_close_session():
        pass

    monkeypatch.setattr("cli.commands.intelligence_cmd.get_session", fake_get_session)
    monkeypatch.setattr("cli.commands.intelligence_cmd.get_coverage_summary", fake_get_coverage_summary)
    monkeypatch.setattr("cli.commands.intelligence_cmd.close_session", fake_close_session)

    handle_show_coverage(DummyArgs())
    captured = capsys.readouterr()
    assert "Coverage Summary:" in captured.out
    assert "files_covered: 10" in captured.out
    assert "files_uncovered: 2" in captured.out
    
    
    handle_show_coverage(DummyArgs2())
    captured = capsys.readouterr()
    assert "Detailed Coverage Summary:" in captured.out
    assert "Coverage Summary:" in captured.out
    assert "files_covered: 10" in captured.out
    assert "files_uncovered: 2" in captured.out
    

def test_handle_show_coverage_handles_exception(capsys):
    with patch("cli.commands.intelligence_cmd.get_coverage_summary", side_effect=Exception("Unexpected error")):
        args = Namespace(
            platforms=None,
            since=None,
            until=None,
            detailed=False
        )
        handle_show_coverage(args)
        captured = capsys.readouterr()
        assert "[Intelligence Error] An unexpected error occurred: Unexpected error" in captured.out
        
        
        
@patch("cli.commands.intelligence_cmd.close_session")
@patch("cli.commands.intelligence_cmd.process_post")
@patch("cli.commands.intelligence_cmd.get_session")
@patch("cli.commands.intelligence_cmd.get_coverage_summary")
def test_handle_process_uncovered_basic(
    mock_get_coverage_summary,
    mock_get_session,
    mock_process_post,
    mock_close_session,
    capsys
):
    # Arrange: mock session and posts
    session = MagicMock()
    mock_get_session.return_value = session

    # Setup a coverage summary with missing posts
    mock_get_coverage_summary.return_value = {
        "total_post_count": 2,
        "missing_posts": [1, 2],
    }

    # Mock .query(Post).filter().first() to return a mock post for id=1, None for id=2
    mock_post = MagicMock()
    session.query().filter().first.side_effect = [mock_post, None]

    # Build args Namespace as argparse would
    args = Namespace(
        platforms=None,
        since=None,
        until=None,
        lang_detection=False,
        translation=False,
        sentiment=False,
        priority=False,
        embedding=False
    )

    # Act
    handle_process_uncovered(args)
    captured = capsys.readouterr()

    # Assert
    # Should process post 1 and skip post 2 (not found)
    assert "Processing post ID: 1" in captured.out
    assert "Post with ID 2 not found." in captured.out

    # process_post should have been called only for post 1, with all steps enabled
    mock_process_post.assert_called_once_with(
        session,
        mock_post,
        lang_detection=True,
        translation=True,
        sentiment_analysis=True,
        priority_score=True,
        embedding_generation=True
    )

    # close_session should be called
    mock_close_session.assert_called_once()

@patch("cli.commands.intelligence_cmd.close_session")
@patch("cli.commands.intelligence_cmd.get_session")
@patch("cli.commands.intelligence_cmd.get_coverage_summary")
def test_handle_process_uncovered_no_posts(
    mock_get_coverage_summary,
    mock_get_session,
    mock_close_session,
    capsys
):
    # Arrange: mock session
    session = MagicMock()
    mock_get_session.return_value = session
    mock_get_coverage_summary.return_value = {
        "total_post_count": 0,
        "missing_posts": [],
    }
    args = Namespace(
        platforms=None, since=None, until=None,
        lang_detection=False, translation=False,
        sentiment=False, priority=False, embedding=False
    )

    # Act
    handle_process_uncovered(args)
    captured = capsys.readouterr()

    # Assert
    assert "No posts found for the given filters." in captured.out
    mock_close_session.assert_called_once()

@patch("cli.commands.intelligence_cmd.close_session")
@patch("cli.commands.intelligence_cmd.get_session")
@patch("cli.commands.intelligence_cmd.get_coverage_summary", side_effect=Exception("Unexpected error"))
def test_handle_process_uncovered_exception(
    mock_get_coverage_summary,
    mock_get_session,
    mock_close_session,
    capsys
):
    session = MagicMock()
    mock_get_session.return_value = session
    args = Namespace(
        platforms=None, since=None, until=None,
        lang_detection=False, translation=False,
        sentiment=False, priority=False, embedding=False
    )

    # Act
    handle_process_uncovered(args)
    captured = capsys.readouterr()

    # Assert
    assert "[Intelligence Error] An unexpected error occurred while processing uncovered posts: Unexpected error" in captured.out
    mock_close_session.assert_called_once()