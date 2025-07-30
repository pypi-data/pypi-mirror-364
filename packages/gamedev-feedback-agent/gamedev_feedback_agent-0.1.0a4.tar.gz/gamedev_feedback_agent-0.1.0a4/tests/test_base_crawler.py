import time
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from crawlers.base_crawler import BaseCrawler
import asyncio
import shutil

# Dummy subclass for testing abstract fetch_data method
class DummyCrawler(BaseCrawler):
    def fetch_data(self, write_to_database=False):
        yield {"id": "1", "platform": "test", "content": "This is a test", "author": "test_user", 
               "timestamp": "2025-07-02T00:00:00Z", "source_url": "http://example.com",
               "metadata": {}, "raw_data": {}}


# 1. test rate limiting
def test_base_crawler_rate_limiting():
    crawler = DummyCrawler(requests_per_minute=30)
    start = time.time()
    crawler.last_request_time = start
    crawler.wait_for_rate_limit()
    assert time.time() - start >= 2  # 60 / 30 = 2 seconds delay


# 2. test keyword filtering
@pytest.mark.parametrize("keywords,content,expected", [
    (["test"], "This is a test", True),
    (["nomatch"], "This is a test", False),
    ([], "Anything", True),  # no keywords = accept all
])
def test_base_crawler_keyword_filtering(keywords, content, expected):
    crawler = DummyCrawler(keywords=keywords)
    assert crawler.contains_keywords(content) == expected



# 3. test JSON file saving
def test_base_crawler_json_saving():
    crawler = DummyCrawler()
    data = {"test": "value"}

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.json"
        crawler.output_path = str(path)
        crawler.save_to_json(data)

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 1
            assert json.loads(lines[0]) == data


# 4. test run method with write_to_database
patch("crawlers.base_crawler.has_enough_disk_space", return_value=True)
def test_base_crawler_error_handling(monkeypatch, capsys):
    class FailingCrawler(BaseCrawler):
        def fetch_data(self, write_to_database=False):
            raise RuntimeError("Simulated fetch failure")

    crawler = FailingCrawler()

    crawler.run()

    captured = capsys.readouterr()
    assert "[ERROR] Crawler failed: Simulated fetch failure" in captured.out
    

# 5. test sync generator handling
def test_run_handles_sync_generator(monkeypatch):
    class SyncCrawler(BaseCrawler):
        def fetch_data(self, write_to_database=False):
            yield {"id": "sync"}

    crawler = SyncCrawler()
    mock_save = MagicMock()
    crawler.save_to_json = mock_save

    crawler.run()
    mock_save.assert_called_once_with({"id": "sync"})
    
    
# 6. test async generator handling
@pytest.mark.asyncio
async def test_run_handles_async_generator_direct():
    class AsyncCrawler(BaseCrawler):
        async def fetch_data(self, write_to_database=False):
            for i in range(1):
                yield {"id": "async"}

    crawler = AsyncCrawler()
    mock_save = MagicMock()
    crawler.save_to_json = mock_save

    gen = crawler.fetch_data()
    await crawler._run_async_generator(gen)
    mock_save.assert_called_once_with({"id": "async"})
    
# 7 test has_enough_disk_space
def test_has_enough_disk_space(tmp_path):
    # Patch shutil.disk_usage to control free space
    crawler = DummyCrawler()
    with patch("shutil.disk_usage") as mock_disk_usage:
        mock_disk_usage.return_value = shutil._ntuple_diskusage(total=1000000, used=500000, free=600000)
        # Adjust arguments to match the method signature
        assert crawler.has_enough_disk_space("./", 500000) is True
        assert crawler.has_enough_disk_space("./", 700000) is False