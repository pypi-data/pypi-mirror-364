# steam crawler
# used to fetch game data from Steam targeting a specific game
# might be used to with unofficual steam API like steamDB to fetch data for a category of games

# to do: 
# for some games with restricted content, there will be a warning page 
# indicating that the content is restricted, so we need to handle that case to redirect to the actual game page

import requests
import time
from datetime import datetime
from crawlers.base_crawler import BaseCrawler
from crawlers.steam_discussion_crawler import SteamDiscussionCrawler
from typing import Generator

class SteamCrawler(BaseCrawler):
    # initialize using either app_id or app_name
    def __init__(self, app_id: str = None, app_name: str = None, max_reviews: int = 30, max_discussion_threads: int = 10, max_discussion_comments: int = 10,
                 fetch_review: bool = True, fetch_discussion: bool = False, discussion_sort_mode: str = "new", **kwargs):
        super().__init__(**kwargs)
        self.platform = "steam"
        self.app_id = app_id
        self.app_name = app_name
        self.max_reviews = max_reviews
        self.max_discussion_threads = max_discussion_threads
        self.max_discussion_comments = max_discussion_comments
        self.fetch_review = fetch_review
        self.fetch_discussion = fetch_discussion # whether to fetch discussions or not
        self.discussion_sort_mode = discussion_sort_mode
        self.discussion_crawler = None
        
        self.requests_per_minute = 30  # 30 requests per minute for Steam API
        self.rate_limit = 60.0 / self.requests_per_minute if self.requests_per_minute > 0 else 0
        
        # if review and discussion are both not needed, raise an error
        if not self.fetch_review and not self.fetch_discussion:
            raise ValueError("At least one of fetch_review or fetch_discussion must be True to initialize SteamCrawler.")

        # If app_id is not provided but app_name is, try to get app_id from app_name
        if not self.app_id and self.app_name:
            self.app_id = self.get_app_id()
            
        # If app_name is not provided but app_id is, try to get app_name from app_id
        if not self.app_name and self.app_id:
            self.app_name = self.get_app_name()
            
        if not self.app_id:
            raise ValueError("Either app_id or app_name must be provided to initialize SteamCrawler.")
        
        # replace forbidden characters in the app_name
        forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', " "]
        for char in forbidden_chars:
            self.app_name = self.app_name.replace(char, "_")
        
        # change the output path to include app_name and app_id
        if self.output_path is None or self.output_path == "data/steam.json" or self.output_path == "data/output.json":
            self.output_path = f"data/steam_{self.app_id}_{self.app_name}.json"

        discussion_output_path = self.output_path.replace(".json", "_discussions.json")
        
        self.output_path = self.output_path.replace(".json", "_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".json")
        discussion_output_path = discussion_output_path.replace(".json", "_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".json")

        # Initialize discussion crawler with the same app_id
        if self.fetch_discussion:
            # seperate discussion data from reviews
            discussion_output_path = discussion_output_path
            print(f"[INFO] Initializing discussion crawler for app {self.app_id}")
            self.discussion_crawler = SteamDiscussionCrawler(app_id=self.app_id, max_threads=self.max_discussion_threads, max_comments=self.max_discussion_comments,
                                                             output_path=discussion_output_path, sort_mode=self.discussion_sort_mode, keywords=self.keywords)


    def fetch_data(self, write_to_database: bool = False) -> Generator[dict, None, None]:
        """Fetch data from Steam API.

        Args:
            write_to_database (bool, optional): Whether to write data to the database. Defaults to False.

        Yields:
            Generator[dict, None, None]: The fetched data in standard format.
        """
        if self.fetch_review:
            print(f"[INFO] Fetching reviews for app {self.app_id}")
            yield from self.fetch_review_data()
        
        # If we reach here, we can also fetch discussions
        if self.fetch_discussion:
            print(f"[INFO] Fetching discussions for app {self.app_id}")
            self.discussion_crawler.run(write_to_database)



    def fetch_review_data(self) -> Generator[dict, None, None]:
        """Fetch review data from Steam API.

        Yields:
            Generator[dict, None, None]: The fetched review data in standard format.
        """
        print(f"[INFO] Fetching reviews for app {self.app_id}")
        cursor = "*"
        count = 0

        while count < self.max_reviews:
            self.wait_for_rate_limit()

            url = f"https://store.steampowered.com/appreviews/{self.app_id}"
            params = {
                "json": 1,
                "cursor": cursor,
                "num_per_page": 100,
                "review_type": "all",
                "purchase_type": "all",
                "language": "english"
            }

            try:
                response = requests.get(url, params=params, timeout = 5)
            except requests.exceptions.Timeout:
                print(f"[WARN] Request timed out while setching {url}")
                break
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Request failed: {e}")
                break
            if response.status_code != 200:
                print(f"[ERROR] Failed to fetch reviews: {response.status_code}")
                break

            data = response.json()
            reviews = data.get("reviews", [])
            if not reviews:
                print("[INFO] No more reviews found.")
                break

            for review in reviews:
                if count >= self.max_reviews:
                    break
                
                # Check if the review contains keywords
                if not self.contains_keywords(review["review"]):
                    continue

                clean_body = review["review"].replace("\n", " ")[:60]
                print(f"[REVIEW {count+1}] {clean_body}...")

                yield {
                    "id": review["recommendationid"],
                    "platform": self.platform,
                    "type": "steam_review",
                    "content": review["review"],
                    "author": review["author"]["steamid"],
                    "timestamp": datetime.utcfromtimestamp(review["timestamp_created"]).isoformat() + "Z",
                    "source_url": f"https://steamcommunity.com/profiles/{review['author']['steamid']}/recommended/{self.app_id}",
                    "metadata": {
                        "name": self.app_name,
                        "app_id": self.app_id,
                        "voted_up": review["voted_up"],
                        "votes_up": review["votes_up"],
                        "votes_funny": review["votes_funny"],
                        "playtime_forever": review["author"]["playtime_forever"],
                        "weighted_vote_score": review.get("weighted_vote_score")
                    },
                    "raw_data": review
                }

                count += 1

            # Check for cursor to continue pagination
            cursor = data.get("cursor")
            if not cursor:
                break
            
        
            
    def get_app_id(self) -> str:
        """
        Get the app ID by its name.
        Use unofficial Steam API to search for the app.
        steamdb.info is used for searching.
        """
        search_url = "https://steamdb.info/api/Search/"
        params = {"q": self.app_name}
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            for result in results:
                if result.get("name", "").lower() == self.app_name.lower():
                    self.app_id = str(result.get("appid"))
                    print(f"[INFO] Found App ID: {self.app_id} for App Name: {self.app_name}")
                    return self.app_id
            print(f"[WARN] No exact match found for App Name: {self.app_name}")
        else:
            print(f"[ERROR] Search API request failed with status code: {response.status_code}")
        return "Unknown_App_ID"


    def get_app_name(self) -> str:
        """
        Get the app name by its ID.
        Use unofficial Steam API to get the app name.
        """
        if not self.app_id:
            return None
        
        app_url = f"https://store.steampowered.com/api/appdetails?appids={self.app_id}"
        response = requests.get(app_url)
        if response.status_code == 200:
            data = response.json()
            if str(self.app_id) in data and data[str(self.app_id)].get("success"):
                self.app_name = data[str(self.app_id)].get("data", {}).get("name")
                print(f"[INFO] Found App Name: {self.app_name} for App ID: {self.app_id}")
                return self.app_name
            else:
                print(f"[ERROR] App details not found for App ID: {self.app_id}")
        else:
            print(f"[ERROR] App details request failed with status code: {response.status_code}")
        return "Unknown_App_Name"