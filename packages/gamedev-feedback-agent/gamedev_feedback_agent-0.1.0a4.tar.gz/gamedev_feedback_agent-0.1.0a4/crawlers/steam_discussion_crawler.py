import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
from crawlers.base_crawler import BaseCrawler
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz
from playwright.sync_api import sync_playwright
import re
from typing import Generator

# SteamDiscussionCrawler: A crawler for Steam discussion forums
# This crawler fetches discussion threads for a specific Steam app using its app_id.
# this will be initialized by steam_crawler.py and used to fetch discussion threads

# currently only supports fetching the first post in each thread without replies
class SteamDiscussionCrawler(BaseCrawler):
    def __init__(self, app_id: str, max_threads: int = 10, max_comments: int = 10, sort_mode: str = "mostrecent", **kwargs):
        super().__init__(**kwargs)
        self.platform = "steam"
        self.app_id = app_id
        self.max_comments = max_comments
        self.max_threads = max_threads
        self.sort_mode = sort_mode
        
        if not self.output_path or self.output_path == "data/output.json":
            self.output_path = f"data/steam_{self.app_id}_Discussions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        # check if data is already in the output path
        if not bool(re.search(r'\b\d{8}_\d{6}\b', self.output_path)):
            self.output_path = self.output_path.replace(".json", "_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".json")


    def fetch_data(self, write_to_database: bool = False) -> Generator[dict, None, None]:
        """Fetch discussion data from Steam API.

        Args:
            write_to_database (bool, optional): Whether to write data to the database. Defaults to False.

        Yields:
            Generator[dict, None, None]: The fetched discussion data in standard format.
        """
        base_url = f"https://steamcommunity.com/app/{self.app_id}/discussions/"
        page_number = 1
        count = 0

        while count < self.max_threads:
            self.wait_for_rate_limit()
            url = f"{base_url}?fp={page_number}&browsefilter={self.sort_mode}"
            print(f"[INFO] Scraping discussion list page {page_number} ({self.sort_mode})...")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                try:
                    page.goto(url)
                except Exception as e:
                    print(f"[ERROR] Failed to load page {url}: {e}")
                    browser.close()
                    break
                
                # wait a moment to let the warning load if it's slow
                page.wait_for_timeout(1000)
                
                # check for the warning page
                if "This content is not available in your region" in page.content():
                    print("[ERROR] This content is not available in your region.")
                    break
                # Bypass content warning if visible
                try:
                    if page.locator("button:has-text('View Community Hub')").is_visible():
                        print("[INFO] Mature content warning detected. Clicking 'View Community Hub'...")
                        page.click("button:has-text('View Community Hub')")
                        page.wait_for_load_state("load")
                except Exception as e:
                    print(f"[WARN] Failed to bypass content warning: {e}")
                
                try:
                    page.wait_for_selector("div.forum_topic", timeout=10000)  # timeout in ms (e.g., 10000 = 10 seconds)
                except TimeoutError:
                    print(f"[ERROR] Timeout occurred while waiting for selector on page {page_number}")
                    browser.close()
                    break

                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
        
                threads = soup.select("div.forum_topic")

                if not threads:
                    print("[INFO] No threads found.")
                    break

                for thread in threads:
                    if count >= self.max_threads:
                        break

                    url_el = thread.select_one("a.forum_topic_overlay")
                    thread_url = url_el["href"]
                    
                    title_el = thread.select_one("div.forum_topic_name")
                    thread_title = title_el.text.strip() if title_el else "No Title"

                    replies_el = thread.select_one("div.forum_topic_reply_count")
                    replies = replies_el.text.strip() if replies_el else "0"

                    # Fetch the full thread page
                    self.wait_for_rate_limit()
                    
                    # try:
                    #     thread_res = requests.get(thread_url, timeout = 5, headers={"User-Agent": "Mozilla/5.0"})
                    # except requests.RequestException.Timeout as e:
                    #     print(f"[ERROR] Request timed out for thread {thread_url}: {e}")
                    #     continue
                    # except requests.RequestException as e:
                    #     print(f"[ERROR] Request failed for thread {thread_url}: {e}")
                    #     continue
                    # if thread_res.status_code != 200:
                    #     print(f"[WARN] Failed to fetch thread page: {thread_url}")
                    #     continue
                    
                    thread_page = context.new_page()
                    thread_page.goto(thread_url)
                    try:
                        if thread_page.locator("button:has-text('View Community Hub')").is_visible():
                            print("[INFO] Clicking 'View Community Hub' on thread page...")
                            thread_page.click("button:has-text('View Community Hub')")
                            thread_page.wait_for_load_state("load")
                    except:
                        print("[WARN] Failed to bypass content warning on thread page, continuing anyway.")
                    
                    thread_content = thread_page.content()
                    thread_soup = BeautifulSoup(thread_content, "html.parser")

                    # Author
                    author_el = thread_soup.select_one("a.hoverunderline.forum_op_author")
                    author = author_el.text.strip() if author_el else None

                    # Timestamp
                    # example: June 13, 2025 @ 9:49:09 pm PDT
                    time_el = thread_soup.find("span", class_="date") if thread_soup.find("span", class_="date") else None
                    timestamp = self.parse_steam_datetime(time_el["title"]) if time_el else None

                    # Content (first post)
                    body_el = thread_soup.select_one("div.forum_op div.content")
                    content = body_el.get_text(separator="\n", strip=True) if body_el else ""
                    
                    # check if content or title contains keywords
                    if not self.contains_keywords(content) and not self.contains_keywords(thread_title):
                        print(f"[SKIPPED] Thread does not contain keywords: {thread_title}")
                        continue

                    print(f"[THREAD {count + 1}] {thread_title[:60]}... by {author} at {timestamp}")

                    yield {
                        "id": thread_url.rstrip("/").split("/")[-1],
                        "platform": self.platform,
                        "type": "steam_discussion_thread",
                        "content": thread_title + "\n\n" + content,
                        "author": author,
                        "timestamp": timestamp,
                        "source_url": thread_url,
                        "metadata": {
                            "app_id": self.app_id,
                            "replies": replies,
                        },
                        "raw_data": {
                            "title": thread_title,
                            "author": author,
                            "timestamp_raw": time_el["title"] if time_el else None,
                            "timestamp_relative": time_el.text.strip() if time_el else None,
                            "url": thread_url,
                            "content": content
                        }
                    }
                    
                    # crawl comments as well
                    comment_blocks = thread_soup.select_one("div.commentthread_comments")
                    comments_el = comment_blocks.select("div.commentthread_comment.responsive_body_text") if comment_blocks else []
                    comment_count = 0
                    for comment_el in comments_el:
                        if comment_count >= self.max_comments:
                            break
                        
                        # Comment content
                        comment_content_el = comment_el.select_one("div.commentthread_comment_text")
                        comment_content = comment_content_el.get_text(separator="\n", strip=True) if comment_content_el else ""
                        
                        # Comment timestamp
                        comment_time_el = thread_soup.find("span", class_="commentthread_comment_timestamp") if thread_soup.find("span", class_="commentthread_comment_timestamp") else None
                        comment_timestamp = self.parse_steam_datetime(comment_time_el["title"]) if comment_time_el else None

                        # Comment author
                        comment_author_el = comment_el.select_one("div.commentthread_comment_author")
                        comment_author = comment_author_el.find("bdi").get_text(strip=True) if comment_author_el else ""

                        # Comment URL (full URL)
                        comment_url_el = comment_el.select_one("div.forum_comment_permlink a")
                        comment_url = comment_url_el["href"] if comment_url_el else None
                        full_comment_url = thread_url + comment_url if comment_url else None
                        
                        
                        # Comment ID
                        comment_id = comment_url_el["href"].lstrip("#c") if comment_url_el else None

                        print(f"[COMMENT {comment_count}] {comment_content[:60]}... by {comment_author} at {comment_timestamp}")
                        yield {
                            "id": comment_id,
                            "platform": self.platform,
                            "type": "steam_discussion_comment",
                            "content": comment_content,
                            "author": comment_author,
                            "timestamp": comment_timestamp,
                            "source_url": full_comment_url,
                            "metadata": {
                                "thread_id": thread_url.rstrip("/").split("/")[-1],
                                "app_id": self.app_id
                            },
                            "raw_data": {
                                "content": comment_content,
                                "author": comment_author,
                                "timestamp_raw": comment_time_el["title"] if comment_time_el else None,
                                "timestamp_relative": comment_time_el.text.strip() if comment_time_el else None,
                                "url": comment_url # relative URL
                            }
                        }
                        comment_count += 1

                    thread_page.close()
                    count += 1

            page_number += 1
            
        print(f"[INFO] Fetched {count} discussion threads.")

    

    def parse_steam_datetime(self, raw: str) -> str:
        """
        Converts a Steam-style timestamp string to ISO UTC format.
        Example input: "June 13, 2025 @ 9:49:09 pm PDT"
        Returns: "2025-06-14T04:49:09Z"
        """
        try:
            # Remove the "@" and split off the timezone
            no_at = raw.replace("@", "").strip()
            dt_str, tz_abbr = no_at.rsplit(" ", 1)

            # Parse the datetime part
            dt = datetime.strptime(dt_str, "%B %d, %Y %I:%M:%S %p")

            # Map common Steam timezone abbreviations (add more if needed)
            tz_map = {
                "PDT": "America/Los_Angeles",
                "PST": "America/Los_Angeles",
                "EDT": "America/New_York",
                "EST": "America/New_York",
                "GMT": "GMT",
                "UTC": "UTC",
            }

            if tz_abbr not in tz_map:
                raise ValueError(f"Unknown timezone abbreviation: {tz_abbr}")

            # Attach local timezone
            local_tz = pytz.timezone(tz_map[tz_abbr])
            localized = local_tz.localize(dt)
            utc_dt = localized.astimezone(pytz.UTC)

            return utc_dt.isoformat().replace("+00:00", "Z")

        except Exception as e:
            print(f"[ERROR] Failed to parse time: {raw} → {e}")
            return None

