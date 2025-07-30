import abc
import time
import json
from typing import Any, Generator, AsyncGenerator
import inspect
import asyncio
import traceback
from database.db_bridge import bulk_insert_from_file, trigger_background_analysis
from pathlib import Path
from cli.context import get_context
import shutil


class BaseCrawler(abc.ABC):
    def __init__(self, requests_per_minute: float = 60.0, output_path: str = "data/output.json", keywords: list[str] = None):
        """
        Abstract base class for crawlers.

        :param requests_per_minute: Number of allowed requests per minute (float)
        :param output_path: Path to save JSON output
        :param keywords: List of keywords to filter the crawled data

        rate_limit: Minimum time delay in seconds between requests to respect API limits.
        """
        self.requests_per_minute = requests_per_minute
        self.rate_limit = 60.0 / requests_per_minute if requests_per_minute > 0 else 0
        self.output_path = output_path
        self.last_request_time = 0
        self.keywords = keywords or []

    def wait_for_rate_limit(self) -> None:
        """
        Enforce a minimum time delay between requests to respect API rate limits.
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
        
    @staticmethod
    def has_enough_disk_space(path: Path, required_bytes: int = 1024 * 1024) -> bool:
        """Check if there is at least `required_bytes` of free space on the disk where `path` is located."""
        usage = shutil.disk_usage(str(path))
        return usage.free >= required_bytes

    def save_to_json(self, data: Any) -> None:
        """Save data to a JSON file (newline-delimited format).

        Args:
            data (Any): The data to save
        
        load context to get the data_dir and replace the output_path if it starts with "data/"
        """
        path = Path(self.output_path)
        
        # If output_path starts with "data/", replace with workspace path
        if str(path).startswith("data/") or str(path).startswith("data\\"):
            context = get_context()
            data_dir = context["data_dir"]
            new_path = data_dir / path.name
        else:
            new_path = path

        new_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.has_enough_disk_space(new_path.parent, required_bytes=1024 * 1024):
            raise OSError(f"Not enough disk space in {new_path.parent}. Please free up space and try again.")

        try:
            with open(new_path, 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')

        except Exception as e:
            print(f"[ERROR] Failed to save data to {new_path}: {e}")

    def contains_keywords(self, content: str) -> bool:
        """
        Check if the content contains any of the specified keywords.
        
        :param content: The content string to check
        :return: True if any keyword is found, False otherwise
        """
        if not self.keywords:
            return True
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in self.keywords)

    def run(self, write_to_database: bool = False, analyze_immediately: bool = False) -> None:
        """
        Run the crawler: fetch data and save each item (supports async and sync).
        
        Args:
            write_to_database (bool): Whether to write the output to the database after crawling
            analyze_immediately (bool): Whether to analyze the data immediately after crawling
        """
        try:
            data_gen = self.fetch_data(write_to_database)

            if inspect.isasyncgen(data_gen):
                asyncio.run(self._run_async_generator(data_gen)) # Handle async generator, used for discord crawler
            else:
                for item in data_gen:
                    self.save_to_json(item)

        except KeyboardInterrupt:
            print("\n[INFO] Crawler manually stopped by user.")
        except Exception as e:
            print(f"[ERROR] Crawler failed: {e}")
            traceback.print_exc()
            
        
        if not write_to_database and analyze_immediately:
            print("[WARNING] no data written to database, analysis will not be performed.")
        
        if write_to_database:
            post_ids = bulk_insert_from_file(self.output_path)
            if post_ids == [-1]:
                print("[ERROR] Failed to write data to database. Please check the output file and try again.")
            else:
            
                if analyze_immediately:
                    print("[INFO] Analyzing data immediately after crawling...")
                    trigger_background_analysis(post_ids)

    # This method handles async generators specifically.
    async def _run_async_generator(self, async_gen: AsyncGenerator[dict, None]) -> None:
        async for item in async_gen:
            self.save_to_json(item)


    # async method to run the crawler
    # for discord crawler bot, we need to run the bot in a separate thread
    # works for both async and sync generators
    async def async_run(self, write_to_database: bool = False) -> None:
        data_gen = self.fetch_data(write_to_database)

        if inspect.isasyncgen(data_gen):
            async for item in data_gen:
                self.save_to_json(item)
        else:
            for item in data_gen:
                self.save_to_json(item)
        
        if write_to_database:
            bulk_insert_from_file(self.output_path)
                

    @abc.abstractmethod
    def fetch_data(self, write_to_database: bool = False) -> Generator[dict, None, None]:
        """
        Subclasses must implement this method to yield data items.

        Expected output format:
        {
            "id": str,
            "platform": str,
            "content": str,
            "author": str,
            "timestamp": str (ISO format),
            "source_url": str,
            "metadata": dict,
            "raw_data": dict
        }
        """
        # the passing in write_to_database is for steam crawler to indicate steam_discussion_crawler whether to write to database or not
        pass
