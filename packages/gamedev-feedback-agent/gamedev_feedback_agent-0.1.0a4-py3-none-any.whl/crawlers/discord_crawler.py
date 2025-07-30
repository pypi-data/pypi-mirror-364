import discord
import asyncio
from datetime import datetime
from crawlers.base_crawler import BaseCrawler
from dotenv import load_dotenv
import os
import re
from typing import AsyncGenerator


class DiscordCrawler(BaseCrawler):
    def __init__(self, channel_ids: list, max_messages=50, snapshot_mode=True, **kwargs):
        super().__init__(**kwargs)
        
        self.channel_ids = channel_ids
        self.max_messages = max_messages
        self.platform = "discord"
        self.snapshot_mode = snapshot_mode

        # Load token from environment variable or directly
        load_dotenv()
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            raise ValueError("Discord bot token is required. Set it in .env or pass it directly.")
        self.token = token
        
        # Discord: 50 * 60 = 3000 requests/minute
        self.requests_per_minute = 3000
        self.rate_limit = 60.0 / self.requests_per_minute if self.requests_per_minute > 0 else 0
        
        # output path     
        if not self.output_path or self.output_path == "data/output.json" or self.output_path == "data/discord.json":
            self.output_path = f"data/discord_messages_{'_'.join(map(str, self.channel_ids))}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        if not bool(re.search(r'\b\d{8}_\d{6}\b', self.output_path)):
            self.output_path = self.output_path.replace(".json", "_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".json")



    def fetch_data(self, write_to_database: bool = False) -> AsyncGenerator[dict, None]:
        """Fetch data from Discord channels.

        Args:
            write_to_database (bool, optional): Whether to write data to the database. Defaults to False.

        Returns:
            asyncio.AsyncGenerator[dict, None]: _description_
        """
        return self._crawl_generator()


    async def _crawl_generator(self) -> AsyncGenerator[dict, None]:
        """A generator that crawls Discord messages.

        Yields:
            dict: The fetched message data in standard format.
        """
        queue = asyncio.Queue()

        async def handler(item):
            if self.rate_limit:
                await asyncio.sleep(self.rate_limit)  # ✅ add rate limit here
            await queue.put(item)

        client = StreamingDiscordClient(
            token=self.token,
            channel_ids=self.channel_ids,
            max_messages=self.max_messages,
            message_handler=handler,
            keywords=self.keywords
        )

        producer = asyncio.create_task(client.crawl_messages())

        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield item
            except asyncio.TimeoutError:
                if producer.done():
                    break

        await producer
            
# This class is for streaming messages to enable yielding each message as it is processed. 
class StreamingDiscordClient(discord.Client):
    def __init__(self, token, channel_ids, max_messages, message_handler, keywords=None, snapshot_mode=True, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.token = token
        self.channel_ids = channel_ids
        self.max_messages = max_messages
        self.message_handler = message_handler
        self.ready_event = asyncio.Event()
        self.keywords = keywords or []
        self.snapshot_mode = snapshot_mode

    def contains_keywords(self, content: str) -> bool:
        if not self.keywords:
            return True
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in self.keywords)


    async def on_ready(self):
        """Event handler for when the client is ready."""
        print(f"[INFO] Logged in as {self.user}")
        self.ready_event.set()
        print("[INFO] Ready event set, client is ready to crawl messages.")


    async def crawl_messages(self) -> None:
        """Crawl messages from the specified Discord channels.
        """
        print("[INFO] Starting Discord message crawler...")
        # login and connect to Discord
        if not self.token:
            print("[ERROR] Discord bot token is not set.")
            return
        try:
            await asyncio.wait_for(self.login(self.token), timeout=10)
            connect_task = asyncio.create_task(self.connect())
        except asyncio.TimeoutError:
            print("[ERROR] Login or connection timed out.")
            return

        # Wait for the client to be ready
        try:
            await asyncio.wait_for(self.ready_event.wait(), timeout=10)
        except asyncio.TimeoutError:
            print("[ERROR] Ready event timed out.")
            return

        # Wait for a short period to ensure the connection is established
        print("[INFO] Waiting for connection to be established...")
        await asyncio.sleep(1)
        for cid in self.channel_ids:
            try:
                channel = self.get_channel(cid) or await self.fetch_channel(cid)
            except discord.Forbidden:
                print(f"[ERROR] Forbidden from accessing channel {cid}")
            if not channel:
                print(f"[ERROR] Cannot access channel: {cid}")
                continue

            print(f"[INFO] Fetching from channel {channel.name}...")
            matched_messages = 0
            async for message in channel.history(limit=None):
                if message.author.bot:
                    continue
                
                if matched_messages >= self.max_messages:
                    print(f"[INFO] Reached max messages limit ({self.max_messages}) for channel {channel.name}. Stopping.")
                    break
                
                if not self.contains_keywords(message.content):
                    print(f"[SKIPPED] Message does not contain keywords: {message.content[:60]}...")
                    continue

                matched_messages += 1
                print(f"[MESSAGE {matched_messages}] ......")
                item = {
                    "id": str(message.id),
                    "platform": "discord",
                    "type": "discord_message",
                    "content": message.content,
                    "author": f"{message.author.name}#{message.author.discriminator}",
                    "timestamp": message.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "source_url": f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{message.id}",
                    "metadata": {
                        "channel_id": str(channel.id),
                        "channel_name": channel.name,
                        "server_id": str(channel.guild.id),
                        "server_name": channel.guild.name,
                        "mentions": [m.name for m in message.mentions],
                        "pinned": message.pinned,
                        "reactions_count": len(message.reactions),
                        "is_reply": message.reference is not None,
                    },
                    "raw_data": {
                        "id": str(message.id),
                        "mentions": [m.name for m in message.mentions],
                        "pinned": message.pinned,
                        "reactions": [{ "emoji": str(reaction.emoji), "count": reaction.count } for reaction in message.reactions]
                    }
                }

                await self.message_handler(item)

        # close the connection if snapshot mode is enabled
        if self.snapshot_mode:
            print("[INFO] Snapshot mode enabled. Closing connection.")
            await self.close()
            await connect_task