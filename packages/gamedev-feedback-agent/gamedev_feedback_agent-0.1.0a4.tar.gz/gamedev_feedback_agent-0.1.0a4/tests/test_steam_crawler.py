# steam crawler test
import pytest
import time
from unittest.mock import patch, MagicMock
from crawlers.steam_crawler import SteamCrawler
from crawlers.steam_discussion_crawler import SteamDiscussionCrawler
from datetime import datetime
import re

# 1. test steam discussion crawler initialization
def test_steam_discussion_crawler_initialization():
    crawler = SteamDiscussionCrawler(
        app_id =  123456,
        max_comments = 10,
        max_threads = 5,
        sort_mode = "new"
    )
    
    assert crawler.platform == "steam"
    assert crawler.app_id == 123456
    assert crawler.max_comments == 10
    assert crawler.max_threads == 5
    assert crawler.sort_mode == "new"


# 2. test steam crawler initialization
def test_steam_crawler_initialization():

    crawler = SteamCrawler(
        app_id=123456,
        app_name="Test Game",
        max_reviews=10,
        max_discussion_threads=5,
        max_discussion_comments=10,
        fetch_review=True,
        fetch_discussion=True,
        discussion_sort_mode="new",
        keywords=[],  # skip filtering
    )

    assert crawler.platform == "steam"
    assert crawler.app_id == 123456
    assert crawler.app_name == "Test_Game"
    assert crawler.max_reviews == 10
    assert crawler.max_discussion_threads == 5
    assert crawler.max_discussion_comments == 10
    assert crawler.fetch_review is True
    assert crawler.fetch_discussion is True
    assert crawler.discussion_sort_mode == "new"
    assert crawler.discussion_crawler is not None
    assert isinstance(crawler.discussion_crawler, SteamDiscussionCrawler)
    assert "data/steam_123456_Test_Game" in crawler.output_path
    assert bool(re.search(r"\d{8}_\d{6}", crawler.output_path)) == True
    assert crawler.discussion_crawler.app_id == 123456
    assert crawler.discussion_crawler.max_threads == 5
    assert crawler.discussion_crawler.max_comments == 10
    assert crawler.discussion_crawler.sort_mode == "new"
    assert "data/steam_123456_Test_Game_discussions" in crawler.discussion_crawler.output_path
    assert bool(re.search(r"\d{8}_\d{6}", crawler.discussion_crawler.output_path)) == True


# 3. test default values for optional parameters
def test_steam_crawler_default_values():
    crawler = SteamCrawler(
        app_id=123456,
        app_name="Test Game",
    )

    assert crawler.max_reviews == 30
    assert crawler.max_discussion_threads == 10
    assert crawler.max_discussion_comments == 10
    assert crawler.fetch_review is True
    assert crawler.fetch_discussion is False
    assert crawler.discussion_sort_mode == "new"
    assert crawler.discussion_crawler is None
    assert "data/steam_123456_Test_Game" in crawler.output_path
    assert bool(re.search(r"\d{8}_\d{6}", crawler.output_path)) == True
    assert crawler.app_id == 123456
    assert crawler.app_name == "Test_Game"
    assert crawler.keywords == []  # default is empty list for keywords
    
    
# 4. test steam discussion crawler default values
def test_steam_discussion_crawler_default_values():
    crawler = SteamDiscussionCrawler(
        app_id=123456,
    )
    assert crawler.platform == "steam"
    assert crawler.app_id == 123456
    assert crawler.max_comments == 10
    assert crawler.max_threads == 10
    assert crawler.sort_mode == "mostrecent"
    assert crawler.keywords == []  # default is empty list for keywords
    

# 5. test steam crawler initialization with only reviews
def test_steam_crawler_initialization_only_reviews():
    crawler = SteamCrawler(
        app_id=123456,
        app_name="Test Game",
        max_reviews=10,
        max_discussion_threads=5,
        max_discussion_comments=10,
        fetch_review=True,
        fetch_discussion=False,
        discussion_sort_mode="new",
        keywords=[],  # skip filtering
    )

    assert crawler.fetch_review is True
    assert crawler.fetch_discussion is False
    assert crawler.discussion_crawler is None
    assert "data/steam_123456_Test_Game" in crawler.output_path
    assert bool(re.search(r"\d{8}_\d{6}", crawler.output_path)) == True
    assert crawler.app_id == 123456
    assert crawler.app_name == "Test_Game"
    
    
# 6. test steam crawler initialization with only discussions
def test_steam_crawler_initialization_only_discussions():
    crawler = SteamCrawler(
        app_id=123456,
        app_name="Test Game",
        max_reviews=10,
        max_discussion_threads=5,
        max_discussion_comments=10,
        fetch_review=False,
        fetch_discussion=True,
        discussion_sort_mode="new",
        keywords=[],  # skip filtering
    )

    assert crawler.fetch_review is False
    assert crawler.fetch_discussion is True
    assert crawler.discussion_crawler is not None
    assert crawler.discussion_crawler.app_id == 123456
    assert crawler.discussion_crawler.max_threads == 5
    assert crawler.discussion_crawler.max_comments == 10
    assert crawler.discussion_crawler.sort_mode == "new"
    assert "data/steam_123456_Test_Game_discussions" in crawler.discussion_crawler.output_path
    assert bool(re.search(r"\d{8}_\d{6}", crawler.discussion_crawler.output_path)) == True


# 7. test steam crawler initialization with no reviews or discussions
def test_steam_crawler_initialization_no_reviews_or_discussions():
    with pytest.raises(ValueError, match="At least one of fetch_review or fetch_discussion must be True to initialize SteamCrawler."):
        SteamCrawler(
            app_id=123456,
            app_name="Test Game",
            max_reviews=10,
            fetch_review=False,
            fetch_discussion=False,
            keywords=[],  # skip filtering
        )
        
        
# 8. test steam crawler utility methods get add_app_id and get_app_name
# patch applies bottom-up, so to match the pass-in parameters, we need the order of the decorators to be reversed
@patch('crawlers.steam_crawler.SteamCrawler.get_app_name', return_value="Test Game")
@patch('crawlers.steam_crawler.SteamCrawler.get_app_id', return_value=123456)
def test_steam_crawler_utility_methods(mock_get_app_id, mock_get_app_name):
    crawler = SteamCrawler(app_name="Test Game")
    assert crawler.app_id == 123456
    mock_get_app_id.assert_called_once_with()
    crawler = SteamCrawler(app_id=123456)
    assert crawler.app_name == "Test_Game"
    mock_get_app_name.assert_called_once_with()
    

# 9. test fetch_review_data_structure including reviews
@patch("crawlers.steam_crawler.requests.get")
def test_fetch_review_data_structure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "reviews": [
            {
                "recommendationid": "123",
                "review": "Amazing game!",
                "timestamp_created": 1720000000,
                "voted_up": True,
                "votes_up": 5,
                "votes_funny": 1,
                "author": {
                    "steamid": "user123",
                    "playtime_forever": 1234
                },
                "weighted_vote_score": 0.9
            }
        ],
        "cursor": "cursor_string"
    }
    mock_get.return_value = mock_response

    crawler = SteamCrawler(
        app_id=123456,
        fetch_review=True,
        fetch_discussion=False,
        max_reviews=1,
        keywords=[]
    )

    results = list(crawler.fetch_data())
    assert len(results) == 1

    review = results[0]
    assert review["platform"] == "steam"
    assert review["id"] == "123"
    assert review["author"] == "user123"
    assert review["content"] == "Amazing game!"
    assert review["timestamp"] == "2024-07-03T09:46:40Z"
    assert review["source_url"] == "https://steamcommunity.com/profiles/user123/recommended/123456"
    assert review["metadata"]["voted_up"] is True
    assert review["metadata"]["votes_up"] == 5
    assert review["metadata"]["votes_funny"] == 1
    assert review["metadata"]["playtime_forever"] == 1234
    assert review["metadata"]["weighted_vote_score"] == 0.9
    
    
# 10. test fetch discussion data structure including threads and comments
@patch("crawlers.steam_discussion_crawler.sync_playwright")
def test_discussion_thread_and_comment_yielded(mock_playwright):
    thread_html = """
    <html>
        <body>
            <div class="forum_topic">
                <a class="forum_topic_overlay" href="https://steamcommunity.com/app/123/discussions/0/0000thread/"></a>
                <div class="forum_topic_name">Test Thread Title</div>
            </div>
        </body>
    </html>
    """
    thread_page_html = """
    <html>
        <body>
            <a class="hoverunderline forum_op_author">AuthorName</a>
            <span class="date" title="June 13, 2025 @ 9:49:09 pm PDT"> 5 hours ago </span>
            <div class="forum_op">
                <div class="content">This is the thread content.</div>
            </div>
            <div class="commentthread_comments">
                <div class="commentthread_comment responsive_body_text">
                    <div class="commentthread_comment_text">First comment here</div>
                    <div class="commentthread_comment_author"><bdi>Commenter</bdi></div>
                    <div class="forum_comment_permlink"><a href="#c12345"></a></div>
                    <span class="commentthread_comment_timestamp" title="June 13, 2025 @ 10:00:00 pm PDT"> 4 hours ago </span>
                </div>
            </div>
        </body>
    </html>
    """

    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_main_page = MagicMock()
    mock_thread_page = MagicMock()
    

    mock_main_page.content.return_value = thread_html
    mock_thread_page.content.return_value = thread_page_html
    
    mock_main_page.goto.return_value = None
    mock_thread_page.goto.return_value = None
    
    mock_main_page.wait_for_timeout.return_value = None
    mock_main_page.wait_for_selector.return_value = None
    
    mock_main_page.locator.return_value.is_visible.return_value = False
    mock_thread_page.locator.return_value.is_visible.return_value = False

    
    def mock_new_page():
        if mock_new_page.call_count == 0:
            mock_new_page.call_count += 1
            return mock_main_page
        elif mock_new_page.call_count == 1:
            mock_new_page.call_count += 1
            return mock_thread_page
        else:
            dummy_page = MagicMock()
            dummy_page.content.return_value = "<html></html>"
            dummy_page.goto.return_value = None
            dummy_page.locator.return_value.is_visible.return_value = False
            return dummy_page
    mock_new_page.call_count = 0
    mock_context.new_page.side_effect = mock_new_page

    mock_browser.new_context.return_value = mock_context
    mock_p = MagicMock()
    mock_p.chromium.launch.return_value = mock_browser
    mock_playwright.return_value.__enter__.return_value = mock_p

    crawler = SteamCrawler(app_id="123", fetch_review=False, fetch_discussion=True, max_discussion_threads=2, max_discussion_comments=10)
    results = list(crawler.discussion_crawler.fetch_data())

    assert len(results) == 2

    thread = results[0]
    comment = results[1]

    assert thread["platform"] == "steam"
    assert thread["id"] == "0000thread"
    assert thread["content"] == "Test Thread Title\n\nThis is the thread content."
    assert thread["author"] == "AuthorName"
    assert thread["timestamp"] == "2025-06-14T04:49:09Z"
    assert thread["source_url"] == "https://steamcommunity.com/app/123/discussions/0/0000thread/"
    assert thread["metadata"]["app_id"] == "123"
    assert thread["raw_data"]["timestamp_raw"] == "June 13, 2025 @ 9:49:09 pm PDT"
    assert thread["raw_data"]["timestamp_relative"] == "5 hours ago"
    
    assert comment["platform"] == "steam"
    assert comment["id"] == "12345"
    assert comment["content"] == "First comment here"
    assert comment["author"] == "Commenter"
    assert comment["timestamp"] == "2025-06-14T05:00:00Z"
    assert comment["source_url"] == "https://steamcommunity.com/app/123/discussions/0/0000thread/#c12345"
    assert comment["metadata"]["thread_id"] == "0000thread"
    assert comment["metadata"]["app_id"] == "123"
    assert comment["raw_data"]["timestamp_raw"] == "June 13, 2025 @ 10:00:00 pm PDT"
    assert comment["raw_data"]["timestamp_relative"] == "4 hours ago"
    
    
# 11. test keyword filtering in fetch_review_data
@patch("crawlers.steam_crawler.requests.get")
def test_keyword_filtering(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "reviews": [
            {
                "recommendationid": "123",
                "review": "Amazing game!",
                "timestamp_created": 1720000000,
                "voted_up": True,
                "votes_up": 5,
                "votes_funny": 1,
                "author": {
                    "steamid": "user123",
                    "playtime_forever": 1234
                },
                "weighted_vote_score": 0.9
            }
        ],
    }
    mock_get.return_value = mock_response
    
    crawler = SteamCrawler(
        app_id=123456,
        fetch_review=True,
        fetch_discussion=False
    )
    crawler.keywords = ["amazing", "great"]
    results = list(crawler.fetch_data())
    assert len(results) == 1
    assert results[0]["content"] == "Amazing game!"
    crawler2 = SteamCrawler(
        app_id=123456,
        fetch_review=True,
        fetch_discussion=False
    )
    crawler2.keywords = ["bad", "terrible"]
    results = list(crawler2.fetch_data())
    assert len(results) == 0
    
    
# 12. test keyword filtering in fetch_discussion_data
@patch("crawlers.steam_discussion_crawler.sync_playwright")
def test_discussion_keyword_filtering(mock_playwright):
    thread_html = """
    <html>
        <body>
            <div class="forum_topic">
                <a class="forum_topic_overlay" href="https://steamcommunity.com/app/123/discussions/0/0000thread/"></a>
                <div class="forum_topic_name">Test Thread Title</div>
            </div>
        </body>
    </html>
    """
    thread_page_html = """
    <html>
        <body>
            <a class="hoverunderline forum_op_author">AuthorName</a>
            <span class="date" title="June 13, 2025 @ 9:49:09 pm PDT"> 5 hours ago </span>
            <div class="forum_op">
                <div class="content">This is the thread content.</div>
            </div>
            <div class="commentthread_comments">
                <div class="commentthread_comment responsive_body_text">
                    <div class="commentthread_comment_text">First comment here</div>
                    <div class="commentthread_comment_author"><bdi>Commenter</bdi></div>
                    <div class="forum_comment_permlink"><a href="#c12345"></a></div>
                    <span class="commentthread_comment_timestamp" title="June 13, 2025 @ 10:00:00 pm PDT"> 4 hours ago </span>
                </div>
            </div>
        </body>
    </html>
    """

    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_main_page = MagicMock()
    mock_thread_page = MagicMock()
    

    mock_main_page.content.return_value = thread_html
    mock_thread_page.content.return_value = thread_page_html
    
    mock_main_page.goto.return_value = None
    mock_thread_page.goto.return_value = None
    
    mock_main_page.wait_for_timeout.return_value = None
    mock_main_page.wait_for_selector.return_value = None
    
    mock_main_page.locator.return_value.is_visible.return_value = False
    mock_thread_page.locator.return_value.is_visible.return_value = False

    
    def mock_new_page():
        if mock_new_page.call_count == 0:
            mock_new_page.call_count += 1
            return mock_main_page
        elif mock_new_page.call_count == 1:
            mock_new_page.call_count += 1
            return mock_thread_page
        else:
            dummy_page = MagicMock()
            dummy_page.content.return_value = "<html></html>"
            dummy_page.goto.return_value = None
            dummy_page.locator.return_value.is_visible.return_value = False
            return dummy_page
    mock_new_page.call_count = 0
    mock_context.new_page.side_effect = mock_new_page

    mock_browser.new_context.return_value = mock_context
    mock_p = MagicMock()
    mock_p.chromium.launch.return_value = mock_browser
    mock_playwright.return_value.__enter__.return_value = mock_p

    crawler = SteamCrawler(
        app_id="123",
        fetch_review=False,
        fetch_discussion=True,
        max_discussion_threads=2,
        max_discussion_comments=10,
        keywords=["Test", "content"]
    )
    
    results = list(crawler.discussion_crawler.fetch_data())
    assert len(results) == 2
    thread = results[0]
    comment = results[1]
    assert thread["content"] == "Test Thread Title\n\nThis is the thread content."
    assert comment["content"] == "First comment here"

    crawler.keywords = ["Nonexistent", "Keywords"]
    results = list(crawler.discussion_crawler.fetch_data())
    assert len(results) == 0
    
    
# 13. test rate limiting in fetch_review_data
@patch("crawlers.steam_crawler.requests.get")
def test_rate_limiting(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "reviews": [
            {
                "recommendationid": "123",
                "review": "Amazing game!",
                "timestamp_created": 1720000000,
                "voted_up": True,
                "votes_up": 5,
                "votes_funny": 1,
                "author": {
                    "steamid": "user123",
                    "playtime_forever": 1234
                },
                "weighted_vote_score": 0.9
            }
        ],
    }
    mock_get.return_value = mock_response

    crawler = SteamCrawler(
        app_id=123456,
        fetch_review=True,
        fetch_discussion=False,
        keywords=[]
    )

    start_time = datetime.now()
    print("start time:", start_time )
    
    # the last_request_time is set to 0 in the beginning, so the first time wait_for_rate_limit is called, it will not wait
    # we set last_request_time to time.time() to ensure the first call to wait_for_rate_limit will delay
    crawler.last_request_time = time.time()
    results = list(crawler.fetch_data())
    
    end_time = datetime.now()
    print("end time:", end_time)

    assert len(results) == 1
    assert (end_time - start_time).total_seconds() >=  crawler.rate_limit * 0.9, "Rate limit was not respected"
