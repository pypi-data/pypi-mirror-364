# test for discord_crawler.py
import pytest
import warnings
from datetime import datetime
import asyncio
from crawlers.discord_crawler import DiscordCrawler, StreamingDiscordClient
from unittest.mock import AsyncMock, patch, MagicMock


# 1. test discord crawler initialization with valid parameters
def test_discord_crawler_initialization():
    crawler = DiscordCrawler(
        channel_ids=["123456789"],
        max_messages=100,
        keywords=["test", "discord"],
        snapshot_mode=True,
    )

    assert crawler.channel_ids == ["123456789"]
    assert crawler.max_messages == 100
    assert crawler.keywords == ["test", "discord"]
    assert crawler.snapshot_mode is True


# 2. test default values for optional parameters
def test_discord_crawler_default_values():
    crawler = DiscordCrawler(
        channel_ids=["123456789"],
    )


    assert crawler.max_messages == 50
    assert crawler.snapshot_mode is True
    assert crawler.keywords == []


# 3. test discord crawler fetch_data generating a client and calling crawl_messages
@pytest.mark.asyncio
async def test_discord_fetch_data_with_mocked_client():
    fake_item = {
        "id": "msg123",
        "platform": "discord",
        "content": "Test message",
        "author": "tester#0001",
        "timestamp": "2025-06-24T00:00:00Z",
        "source_url": "https://discord.com/channels/1/2/msg123",
        "metadata": {
            "channel_id": "2",
            "channel_name": "general",
            "server_id": "1",
            "server_name": "Test Server"
        },
        "raw_data": {
            "id": "msg123",
            "mentions": [],
            "pinned": False
        }
    }

    # Patch StreamingDiscordClient so it returns a mock
    with patch("crawlers.discord_crawler.StreamingDiscordClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.crawl_messages = AsyncMock()

        # Simulate the crawl_messages calling the handler with a fake item
        def capture_message_handler(**kwargs):
            message_handler = kwargs["message_handler"]
            # Inject the fake item directly into the handler
            async def simulate_crawling():
                await message_handler(fake_item)
            mock_client.crawl_messages.side_effect = simulate_crawling
            return mock_client

        mock_client_class.side_effect = capture_message_handler

        crawler = DiscordCrawler(
            channel_ids=["2"],
            max_messages=1
        )

        results = [item async for item in crawler.fetch_data()]

        assert len(results) == 1
        assert results[0]["id"] == "msg123"
        assert results[0]["platform"] == "discord"
        assert results[0]["content"] == "Test message"
        assert results[0]["metadata"]["channel_name"] == "general"
        
        
# 4. test when having a client set up, data is yielded correctly
@pytest.mark.asyncio
async def test_fetch_data_yields_correct_data_with_client():
    # This is the mock message we'll simulate being received
    mock_message = {
        "id": "test123",
        "platform": "discord",
        "content": "Test content",
        "author": "tester#0001",
        "timestamp": "2025-06-24T00:00:00Z",
        "source_url": "https://discord.com/channels/1/2/test123",
        "metadata": {
            "channel_id": "2",
            "channel_name": "general",
            "server_id": "1",
            "server_name": "Test Server"
        },
        "raw_data": {
            "id": "test123",
            "mentions": [],
            "pinned": False
        }
    }

    with patch("crawlers.discord_crawler.StreamingDiscordClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.crawl_messages = AsyncMock()

        # Save the handler that will be passed to the client
        handler_ref = {}

        def capture_client_init(**kwargs):
            handler_ref["handler"] = kwargs["message_handler"]

            # Simulate crawl_messages calling the handler
            async def simulate_crawl():
                await handler_ref["handler"](mock_message)
            mock_client.crawl_messages.side_effect = simulate_crawl

            return mock_client

        mock_client_class.side_effect = capture_client_init

        crawler = DiscordCrawler(
            channel_ids=["2"],
            max_messages=1
        )

        results = [item async for item in crawler.fetch_data()]

        assert len(results) == 1
        assert results[0]["id"] == "test123"
        assert results[0]["content"] == "Test content"
        assert results[0]["platform"] == "discord"
        assert results[0]["metadata"]["channel_name"] == "general"
        assert results[0]["metadata"]["server_name"] == "Test Server"
        
        
# 5. test timeout handling in discord crawler
@pytest.mark.asyncio
async def test_discord_fetch_data_login_timeout():
    with patch("crawlers.discord_crawler.StreamingDiscordClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.crawl_messages = AsyncMock()
        mock_client.ready_event.wait = AsyncMock(side_effect=asyncio.TimeoutError)

        # Return the mock client when DiscordCrawler creates it
        mock_client_class.return_value = mock_client

        crawler = DiscordCrawler(
            channel_ids=["123456789"],
            max_messages=1
        )

        results = [item async for item in crawler.fetch_data()]

        # Assert crawl_messages was started
        mock_client.crawl_messages.assert_called_once()

        # Nothing yielded due to timeout
        assert results == []

        
# 6. test keyword filtering in discord crawler
@pytest.mark.asyncio
async def test_discord_keyword_filtering():
    # Fake message 1: should be filtered in
    msg1 = MagicMock()
    msg1.id = 1
    msg1.content = "Unity is amazing"
    msg1.author.bot = False
    msg1.author.name = "dev"
    msg1.author.discriminator = "0001"
    msg1.created_at = datetime(2025, 6, 24, 0, 0, 0)
    msg1.mentions = []
    msg1.pinned = False
    msg1.channel.name = "general"
    msg1.channel.id = 123
    msg1.channel.guild.name = "Test Server"
    msg1.channel.guild.id = 999

    # Fake message 2: should be filtered out
    msg2 = MagicMock()
    msg2.id = 2
    msg2.content = "Completely unrelated"
    msg2.author.bot = False
    msg2.author.name = "tester"
    msg2.author.discriminator = "0002"
    msg2.created_at = datetime(2025, 6, 24, 0, 1, 0)
    msg2.mentions = []
    msg2.pinned = False
    msg2.channel = msg1.channel  # reuse channel object

    # Fake channel with async history generator
    mock_channel = MagicMock()
    async def fake_history():
        yield msg1
        yield msg2

    mock_channel.history = MagicMock(return_value=fake_history())

    # Create real StreamingDiscordClient but patch channel lookup and connection
    client = StreamingDiscordClient(
        token="fake_token",
        channel_ids=[123],
        max_messages=2,
        message_handler=AsyncMock(),
        keywords=["unity"]
    )
    client.get_channel = MagicMock(return_value=mock_channel)
    client.fetch_channel = AsyncMock()
    client.login = AsyncMock()
    client.connect = AsyncMock()
    client.ready_event.set()  # Skip waiting

    collected = []

    async def capture(item):
        collected.append(item)

    client.message_handler = capture

    await client.crawl_messages()

    assert len(collected) == 1
    assert "Unity" in collected[0]["content"]
    assert collected[0]["id"] == "1"


# we don't need this yet, but if in the future we want snapshot mode is actually implemented
# we need to add a test for it