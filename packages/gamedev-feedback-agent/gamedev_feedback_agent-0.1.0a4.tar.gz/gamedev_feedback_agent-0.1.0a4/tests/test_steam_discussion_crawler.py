from crawlers.steam_discussion_crawler import SteamDiscussionCrawler
import pytest
from playwright.sync_api import sync_playwright
from unittest.mock import MagicMock, patch
import tempfile
from pathlib import Path
from cli.commands.database_cmd import bulk_insert_from_file


# 1. test initialization of SteamDiscussionCrawler
def test_steam_discussion_crawler_initialization():
    crawler = SteamDiscussionCrawler(app_id="123", max_threads=1, max_comments=0, sort_mode="newest")
    assert crawler.platform == "steam"
    assert crawler.app_id == "123"
    assert crawler.max_threads == 1
    assert crawler.max_comments == 0
    assert crawler.sort_mode == "newest"


# 2. test initialization of SteamDiscussionCrawler with default parameters
def test_steam_discussion_crawler_default_initialization():
    crawler = SteamDiscussionCrawler(app_id="0")
    assert crawler.platform == "steam"
    assert crawler.app_id == "0"
    assert crawler.max_threads == 10
    assert crawler.max_comments == 10
    assert crawler.sort_mode == "mostrecent"


# 3. Test the SteamDiscussionCrawler class to ensure it correctly initializes with given parameters.
@patch("crawlers.steam_discussion_crawler.sync_playwright")
def test_steam_discussion_playwright_handling(mock_sync_playwright):
    mock_page = MagicMock()
    mock_page.content.return_value = "<html><div class='forum_topic'><a class='forum_topic_overlay' href='https://example.com/thread/1'></a><div class='forum_topic_name'>Test Title</div><div class='forum_topic_reply_count'>5</div></div></html>"

    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_context.new_page.return_value = mock_page
    mock_browser.new_context.return_value = mock_context

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

    crawler = SteamDiscussionCrawler(app_id="123", max_threads=1, max_comments=0)
    results = list(crawler.fetch_data())

    assert len(results) == 1
    assert results[0]["type"] == "steam_discussion_thread"
    assert "Test Title" in results[0]["content"]
    
    
# 4. test the SteamDiscussionCrawler class to ensure it correctly handles empty pages gracefully.
@patch("crawlers.steam_discussion_crawler.sync_playwright")
def test_network_timeout_recovery(mock_sync_playwright, capsys):
    mock_page = MagicMock()
    mock_page.content.return_value = "Some page"
    mock_page.goto.side_effect = TimeoutError("Timeout reached")
    
    mock_context = MagicMock()
    mock_context.new_page.return_value = mock_page
    mock_browser = MagicMock()
    mock_browser.new_context.return_value = mock_context
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

    crawler = SteamDiscussionCrawler(app_id="999", max_threads=1)
    results = list(crawler.fetch_data())

    captured = capsys.readouterr()
    assert "Timeout" in captured.out or "timeout" in captured.out.lower()
    assert results == []  # nothing should be yielded
    
