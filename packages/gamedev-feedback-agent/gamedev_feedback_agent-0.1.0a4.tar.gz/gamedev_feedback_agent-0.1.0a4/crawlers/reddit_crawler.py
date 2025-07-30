import praw
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Generator
import prawcore
from crawlers.base_crawler import BaseCrawler


class RedditCrawler(BaseCrawler):
    def __init__(self, subreddits: list[str] = None, post_id=None, post_url=None, post_sort: str = "top", comment_sort: str = "top", max_posts: int  = 5,max_comments: int = 20,**kwargs):
        super().__init__(**kwargs)
        self.platform = "reddit"
        self.subreddits = subreddits or []  # List of subreddits to crawl
        self.post_id = post_id.replace("t3_", "") if post_id else None  # Remove 't3_' prefix if present
        self.post_url = post_url

        self.post_sort = post_sort # Options: "top", "new", "hot", "controversial", "old"
        self.comment_sort = comment_sort # Options: "top", "new", "hot", "controversial", "old"
        self.max_posts = max_posts  # Maximum number of posts to fetch
        self.max_comments = max_comments # Maximum number of comments to fetch per post

        # Load credentials from .env
        load_dotenv()
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT")

        if not all([client_id, client_secret, user_agent]):
            raise EnvironmentError("Missing Reddit API credentials in .env file")

        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        # Reddit: 60 requests/minute
        self.requests_per_minute = 60
        self.rate_limit = 60.0 / self.requests_per_minute if self.requests_per_minute > 0 else 0
        
        # output path
        if not self.output_path or self.output_path == "data/output.json" or self.output_path == "data/reddit.json":
            if self.subreddits:
                self.output_path = f"data/reddit_{'_'.join(self.subreddits)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            elif self.post_id:
                self.output_path = f"data/reddit_post_{self.post_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            elif self.post_url:
                self.output_path = f"data/reddit_post_{self.post_url.split('/')[-3]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


    def fetch_data(self, write_to_database: bool = False) -> Generator[dict, None, None]:
        if self.post_id:
            print(f"[INFO] Fetching post data by ID: {self.post_id}")
            yield from self.fetch_post_data_by_id()
        elif self.post_url:
            print(f"[INFO] Fetching post data by URL: {self.post_url}")
            yield from self.fetch_post_data_by_url()
        elif self.subreddits:
            print(f"[INFO] Fetching data from subreddits: {', '.join(self.subreddits)}")
            yield from self.fetch_subreddits_data()
        else:
            raise ValueError("No subreddits, post_id, or post_url specified for RedditCrawler.")
            
            
    def fetch_post_data_by_id(self) -> Generator[dict, None, None]:
        """Fetch post data by ID.

        Yields:
            Generator[dict, None, None]: The post data in standard format.
        """
        self.wait_for_rate_limit() # apply rate limit before fetching post
        post = self.reddit.submission(id=self.post_id)
        post.comment_sort = self.comment_sort  # Set comment sort order before processing
        if not self.contains_keywords(post.title) and not self.contains_keywords(post.selftext):
            print(f"[INFO] Post {self.post_id} does not contain keywords, skipping.")
            return
        yield from self._process_post(post)


    def fetch_post_data_by_url(self) -> Generator[dict, None, None]:
        """Fetch post data by URL.

        Yields:
            Generator[dict, None, None]: The post data in standard format.
        """
        self.wait_for_rate_limit()
        post = self.reddit.submission(url=self.post_url)
        post.comment_sort = self.comment_sort  # Set comment sort order before processing
        if not self.contains_keywords(post.title) and not self.contains_keywords(post.selftext):
            print(f"[INFO] Post {self.post_url} does not contain keywords, skipping.")
            return
        yield from self._process_post(post)


    def fetch_subreddits_data(self) -> Generator[dict, None, None]:
        """
        Fetch data from all specified subreddits and yield posts and comments in standard format.
        """
        for subreddit_name in self.subreddits:
            print(f"[INFO] Fetching data from subreddit: {subreddit_name}")
            yield from self.fetch_subreddit_data(subreddit_name)

    def fetch_subreddit_data(self, subreddit_name) -> Generator[dict, None, None]:
        """
        Fetch top posts from the subreddit and yield them in standard format.
        """
        self.wait_for_rate_limit()
        subreddit = self.reddit.subreddit(subreddit_name)
        
        # check if subreddit exists
        try:
            s = subreddit.id  # This will raise an exception if the subreddit does not exist
        except prawcore.exceptions.NotFound:
            print(f"[ERROR] Subreddit '{subreddit_name}' not found.")
            return
        except Exception as e:
            print(f"[ERROR] Failed to fetch subreddit '{subreddit_name}': {e}")
            return

        # Select the appropriate post listing method based on comment_sort
        if self.post_sort == "top":
            posts = subreddit.top(limit=self.max_posts)
        elif self.post_sort == "new":
            posts = subreddit.new(limit=self.max_posts)
        elif self.post_sort == "hot":
            posts = subreddit.hot(limit=self.max_posts)
        elif self.post_sort == "controversial":
            posts = subreddit.controversial(limit=self.max_posts)
        elif self.post_sort == "old":
            # PRAW does not have a direct 'old', so use 'new' and reverse
            posts = reversed(list(subreddit.new(limit=self.max_posts)))
        else:
            posts = subreddit.hot(limit=self.max_posts)  # Default fallback


        post_count = 0  # Count valid posts
        for post in posts:
            # check if post contains keywords
            if not self.contains_keywords(post.title) and not self.contains_keywords(post.selftext):
                continue

            # check count
            if post_count >= self.max_posts:
                break
            
            # process post
            print(f"[POST] {post.id} - {post.title[:60]}...")  # Log post request
            post.comment_sort = self.comment_sort
            yield from self._process_post(post)
            post_count += 1


    def _process_post(self, post) -> Generator[dict, None, None]:
        """
        Process a single Reddit post and yield it in standard format.
        Assume this post is valid to yield.
        Process data only
        """
        # apply rate limit before processing post
        # reddit fetch multiple posts in one request, in order to maintain a rate limit, we apply a rate limit to each post
        # to do: adjust rate limit based on number of posts fetched in one request
        # This is to ensure we don't hit the rate limit too quickly when fetching multiple posts
        self.wait_for_rate_limit()
        
        
        post_data = {
            "id": "t3_" + post.id, # Reddit post IDs start with "t3_" as fullname
            "platform": "reddit",
            "type": "reddit_post",
            "content": post.title + "\n\n" + (post.selftext or ""),
            "author": str(post.author) if post.author else "[deleted]",
            "timestamp": datetime.utcfromtimestamp(post.created_utc).isoformat() + "Z",
            "source_url": f"https://www.reddit.com{post.permalink}",
            "metadata": {
                "subreddit": post.subreddit.display_name,
                "subreddit_id": post.subreddit.id,
                "upvotes": max(0, post.score), # score = upvotes - downvotes, so we use max(0, score) to avoid negative values
                "downvotes": max(0, -post.score), # if score is negative, we treat it as downvotes
                "num_comments": post.num_comments,
            },
            "raw_data": {
                "id": post.id,
                "flair": post.link_flair_text,
                "is_self": post.is_self,
                "url": post.url,
                "created_utc": post.created_utc,
                "upvotes": max(0, post.score), # score = upvotes - downvotes, so we use max(0, score) to avoid negative values
                "downvotes": max(0, -post.score), # if score is negative, we treat it as downvotes
                "subreddit": str(post.subreddit),
            }
        }

        yield post_data


        # load comments
        # apply rate limit
        self.wait_for_rate_limit()
        
        # Already sorted by comment_sort
        # Replace "more comments" with empty list to avoid fetching them
        post.comments.replace_more(limit=0)

        comment_count = 0  # Count valid comments
        
        for i, comment in enumerate(post.comments.list()):
            if comment.author is None or comment.body in ("[deleted]", "[removed]"):
                continue

            if comment_count >= self.max_comments:
                break

            comment_data = {
                "id": "t1_" + comment.id, # Reddit comment IDs start with "t1_" as fullname
                "platform": "reddit",
                "type": "reddit_comment",
                "content": comment.body,
                "author": str(comment.author),
                "timestamp": datetime.utcfromtimestamp(comment.created_utc).isoformat() + "Z",
                "source_url": f"https://www.reddit.com{comment.permalink}",
                "metadata": {
                    "subreddit": post.subreddit.display_name,
                    "subreddit_id": post.subreddit.id,
                    "parent_id": comment.parent_id,
                    "link_id": comment.link_id,
                    "upvotes": max(0, comment.score),
                    "downvotes": max(0, -comment.score),
                    "num_replies": len(comment.replies),
                    "depth": comment.depth,
                },
                "raw_data": { 
                    "id": comment.id,
                    "body": comment.body,
                    "created_utc": comment.created_utc,
                    "url": comment.permalink,
                    "is_submitter": comment.is_submitter
                }
            }

            yield comment_data
            comment_count += 1

