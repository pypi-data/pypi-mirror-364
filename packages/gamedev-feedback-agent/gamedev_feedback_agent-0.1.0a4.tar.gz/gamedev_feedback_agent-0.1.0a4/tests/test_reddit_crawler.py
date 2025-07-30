# tests/test_reddit_crawler.py
import time
import pytest
from unittest.mock import patch, MagicMock
from crawlers.reddit_crawler import RedditCrawler
from datetime import datetime

# 1. test RedditCrawler initialization
def test_reddit_crawler_initialization():
    with patch("crawlers.reddit_crawler.praw.Reddit") as mock_praw:
        mock_reddit_instance = mock_praw.return_value

        crawler = RedditCrawler(
            subreddits=["test"],
            post_sort="top",
            comment_sort="top",
            max_posts=1,
            max_comments=1,
            keywords=[],  # skip filtering
        )

        assert crawler.platform == "reddit"
        assert crawler.subreddits == ["test"]
        assert crawler.post_sort == "top"
        assert crawler.comment_sort == "top"
        assert crawler.max_posts == 1
        assert crawler.max_comments == 1
        assert crawler.reddit == mock_reddit_instance


# 2. test RedditCrawler default values
def test_reddit_crawler_default_values():
    crawler = RedditCrawler(
        subreddits=["test"],
    )

    assert crawler.post_sort == "top"
    assert crawler.comment_sort == "top"
    assert crawler.max_posts == 5
    assert crawler.max_comments == 20
    assert crawler.keywords == []  # default is empty list for keywords


# 3. test fetch_data yields expected post structure
def test_fetch_data_yields_expected_post_structure():
    # Mock post and comment objects
    mock_post = MagicMock()
    mock_post.id = "abc123"
    mock_post.title = "Test Post Title"
    mock_post.selftext = "Post content"
    mock_post.author = "tester"
    mock_post.created_utc = 1720000000
    mock_post.permalink = "/r/test/comments/abc123/test_post"
    mock_post.subreddit.display_name = "test"
    mock_post.subreddit.id = "subr123"
    mock_post.score = 100
    mock_post.num_comments = 2
    mock_post.link_flair_text = "Discussion"
    mock_post.is_self = True
    mock_post.url = "https://reddit.com/test"
    mock_post.subreddit = MagicMock()
    mock_post.subreddit.display_name = "test"
    mock_post.subreddit.id = "subr123"

    # Comments
    mock_comment = MagicMock()
    mock_comment.id = "comm1"
    mock_comment.body = "A comment"
    mock_comment.author = "commenter"
    mock_comment.created_utc = 1720000100
    mock_comment.permalink = "/r/test/comments/abc123/test_post/comm1"
    mock_comment.parent_id = "t3_abc123"
    mock_comment.link_id = "t3_abc123"
    mock_comment.score = -3
    mock_comment.depth = 0
    mock_comment.is_submitter = False

    mock_post.comments.list.return_value = [mock_comment]
    mock_post.comments.replace_more.return_value = None
    mock_post.comment_sort = "top"

    # Patch praw.Reddit instance and its .subreddit().top()
    with patch("crawlers.reddit_crawler.praw.Reddit") as mock_praw:
        mock_reddit_instance = mock_praw.return_value
        mock_subreddit = MagicMock()
        mock_subreddit.top.return_value = [mock_post]
        mock_reddit_instance.subreddit.return_value = mock_subreddit

        crawler = RedditCrawler(
            subreddits=["test"],
            post_sort="top",
            comment_sort="top",
            max_posts=1,
            max_comments=1,
            keywords=[],  # skip filtering
        )

        results = list(crawler.fetch_data())
        assert len(results) == 2  # 1 post + 1 comment

        # check post data
        assert isinstance(results[0], dict)
        post_data = results[0]
        assert post_data["id"] == "t3_abc123"
        assert post_data["platform"] == "reddit"
        assert "Post content" in post_data["content"]
        assert "Test Post Title" in post_data["content"]
        assert post_data["author"] == "tester"
        assert post_data["timestamp"] == "2024-07-03T09:46:40Z"
        assert post_data["source_url"] == "https://www.reddit.com/r/test/comments/abc123/test_post"
        assert post_data["metadata"]["subreddit"] == "test"
        assert post_data["metadata"]["subreddit_id"] == "subr123"
        assert post_data["metadata"]["upvotes"] == 100
        assert post_data["metadata"]["downvotes"] == 0
        assert post_data["metadata"]["num_comments"] == 2
        assert post_data["raw_data"]["flair"] == "Discussion"
        assert post_data["raw_data"]["is_self"] is True
        assert post_data["raw_data"]["url"] == "https://reddit.com/test"


        # check comment data
        assert isinstance(results[1], dict)
        comment_data = results[1]
        assert comment_data["id"] == "t1_comm1"
        assert "A comment" in comment_data["content"]
        assert comment_data["author"] == "commenter"
        assert comment_data["timestamp"] == "2024-07-03T09:48:20Z"
        assert comment_data["source_url"] == "https://www.reddit.com/r/test/comments/abc123/test_post/comm1"
        assert comment_data["metadata"]["parent_id"] == "t3_abc123"
        assert comment_data["metadata"]["link_id"] == "t3_abc123"
        assert comment_data["metadata"]["upvotes"] == 0
        assert comment_data["metadata"]["downvotes"] == 3
        assert comment_data["metadata"]["depth"] == 0
        assert comment_data["raw_data"]["is_submitter"] is False
        

# 4. test fetch_data handles empty no subreddits or post_id or post_url
def test_fetch_data_with_no_inputs():
    reddit_crawler = RedditCrawler(
        subreddits=[],
        post_id=None,
        post_url=None,
        post_sort="top",
        comment_sort="top",
        max_posts=1,
        max_comments=1,
        keywords=[],  # skip filtering
    )
    with pytest.raises(ValueError, match="No subreddits, post_id, or post_url specified for RedditCrawler."):
        list(reddit_crawler.fetch_data())
        

# 5. test fetch_data handles invalid subreddit gracefully
def test_fetch_data_with_invalid_subreddit_is_handled():
    reddit_crawler = RedditCrawler(
        subreddits=["invalid_subreddit"],
        post_id=None,
        post_url=None,
        post_sort="top",
        comment_sort="top",
        max_posts=1,
        max_comments=1,
        keywords=[],
    )

    with patch("crawlers.reddit_crawler.praw.Reddit") as mock_praw:
        mock_reddit_instance = mock_praw.return_value
        mock_subreddit = MagicMock()

        # Simulate a .display_name access raising NotFound
        import prawcore
        mock_subreddit.display_name = property(lambda self: (_ for _ in ()).throw(prawcore.exceptions.NotFound))
        mock_reddit_instance.subreddit.return_value = mock_subreddit

        # This should NOT raise, and should return no results
        results = list(reddit_crawler.fetch_data())
        assert results == []
            

# 6. test fetch_data handles post_id
def test_fetch_data_with_post_id():
    # Create a mock Reddit post
    mock_post = MagicMock()
    mock_post.id = "post123"
    mock_post.title = "Test Post by ID"
    mock_post.selftext = "Some content"
    mock_post.author = "tester"
    mock_post.created_utc = 1720000000
    mock_post.permalink = "/r/test/comments/post123/test_post"
    mock_post.subreddit.display_name = "test"
    mock_post.subreddit.id = "subr123"
    mock_post.score = 100
    mock_post.num_comments = 0
    mock_post.comments.list.return_value = []
    mock_post.comments.replace_more.return_value = None

    # Patch Reddit client to return this mock post
    with patch("crawlers.reddit_crawler.praw.Reddit") as mock_praw:
        reddit_instance = mock_praw.return_value
        reddit_instance.submission.return_value = mock_post

        crawler = RedditCrawler(
            subreddits=[],
            post_id="post123",
            max_comments=0,
            keywords=[],
        )

        results = list(crawler.fetch_data())
        assert len(results) == 1
        post_data = results[0]
        assert post_data["id"] == "t3_post123"
        assert "Test Post by ID" in post_data["content"]
        assert post_data["metadata"]["subreddit"] == "test"
 
        
# 7. test fetch_data handles post_url
def test_fetch_data_with_post_url():
    # Create a mock Reddit post
    mock_post = MagicMock()
    mock_post.id = "post456"
    mock_post.title = "Test Post by URL"
    mock_post.selftext = "Some content"
    mock_post.author = "tester"
    mock_post.created_utc = 1720000000
    mock_post.permalink = "/r/test/comments/post456/test_post"
    mock_post.subreddit.display_name = "test"
    mock_post.subreddit.id = "subr456"
    mock_post.score = 100
    mock_post.num_comments = 0
    mock_post.comments.list.return_value = []
    mock_post.comments.replace_more.return_value = None

    # Patch Reddit client to return this mock post
    with patch("crawlers.reddit_crawler.praw.Reddit") as mock_praw:
        reddit_instance = mock_praw.return_value
        reddit_instance.submission.return_value = mock_post

        crawler = RedditCrawler(
            subreddits=[],
            post_url="https://www.reddit.com/r/test/comments/post456/test_post",
            max_comments=0,
            keywords=[],
        )

        results = list(crawler.fetch_data())
        assert len(results) == 1
        post_data = results[0]
        assert post_data["id"] == "t3_post456"
        assert "Test Post by URL" in post_data["content"]
        assert post_data["metadata"]["subreddit"] == "test"


# 8. test fetch_data calls wait_for_rate_limit
def test_fetch_data_calls_wait_for_rate_limit():
    mock_post = MagicMock()
    mock_post.title = "Rate Limit Test"
    mock_post.selftext = ""
    mock_post.author = "user"
    mock_post.id = "abc123"
    mock_post.created_utc = 1720000000
    mock_post.permalink = "/r/test/comments/abc123/test"
    mock_post.subreddit.display_name = "test"
    mock_post.subreddit.id = "subr123"
    mock_post.score = 42
    mock_post.num_comments = 0
    mock_post.comments.list.return_value = []
    mock_post.comments.replace_more.return_value = None

    with patch("crawlers.reddit_crawler.praw.Reddit") as mock_praw:

        # Mock Reddit API return
        reddit_instance = mock_praw.return_value
        subreddit_mock = MagicMock()
        subreddit_mock.top.return_value = [mock_post]
        reddit_instance.subreddit.return_value = subreddit_mock

        crawler = RedditCrawler(subreddits=["test"], max_posts=1, max_comments=0)
        
        start_time = datetime.now()

        crawler.last_request_time = time.time()
        result = list(crawler.fetch_data())
        end_time = datetime.now()

        assert len(result) == 1
        assert (end_time - start_time).total_seconds() >= crawler.rate_limit * 0.9, \
            f"Expected at least {crawler.rate_limit} seconds between requests, but got {(end_time - start_time).total_seconds()} seconds"


# 9. test keyword filtering works
def test_keyword_filtering():
    # Create two posts, only one matches keyword
    matching_post = MagicMock()
    matching_post.id = "match123"
    matching_post.title = "Unity game dev experience"
    matching_post.selftext = ""
    matching_post.author = "user1"
    matching_post.created_utc = 1720000000
    matching_post.permalink = "/r/test/comments/match123/unity_post"
    matching_post.subreddit.display_name = "test"
    matching_post.subreddit.id = "subr123"
    matching_post.score = 10
    matching_post.num_comments = 0
    matching_post.comments.list.return_value = []
    matching_post.comments.replace_more.return_value = None

    non_matching_post = MagicMock()
    non_matching_post.id = "skip456"
    non_matching_post.title = "Random topic"
    non_matching_post.selftext = ""
    non_matching_post.author = "user2"
    non_matching_post.created_utc = 1720000001
    non_matching_post.permalink = "/r/test/comments/skip456/other_post"
    non_matching_post.subreddit.display_name = "test"
    non_matching_post.subreddit.id = "subr123"
    non_matching_post.score = 5
    non_matching_post.num_comments = 0
    non_matching_post.comments.list.return_value = []
    non_matching_post.comments.replace_more.return_value = None

    with patch("crawlers.reddit_crawler.praw.Reddit") as mock_praw:
        mock_instance = mock_praw.return_value
        mock_subreddit = MagicMock()
        mock_subreddit.top.return_value = [matching_post, non_matching_post]
        mock_instance.subreddit.return_value = mock_subreddit

        crawler = RedditCrawler(
            subreddits=["test"],
            post_sort="top",
            comment_sort="top",
            max_posts=5,
            max_comments=0,
            keywords=["unity", "dev"]
        )

        results = list(crawler.fetch_data())

        assert len(results) == 1
        assert results[0]["id"] == "t3_match123"
        assert "Unity game" in results[0]["content"]