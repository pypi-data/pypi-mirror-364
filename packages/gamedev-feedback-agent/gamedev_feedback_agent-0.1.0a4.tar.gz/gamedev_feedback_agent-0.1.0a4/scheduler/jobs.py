from crawlers.reddit_crawler import RedditCrawler
from crawlers.steam_crawler import SteamCrawler
from crawlers.discord_crawler import DiscordCrawler

# crawler jobs
# these functions are used to create crawler jobs for different platforms
def create_reddit_job(params) -> RedditCrawler:
    return RedditCrawler(**params)


def create_steam_job(params) -> SteamCrawler:
    return SteamCrawler(**params)


def create_discord_job(params) -> DiscordCrawler:
    return DiscordCrawler(**params)


PLATFORM_FACTORY = {
    "reddit": create_reddit_job,
    "steam": create_steam_job,
    "discord": create_discord_job  # Skipped in engine, launched externally
}