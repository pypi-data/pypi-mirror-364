from crawlers.reddit_crawler import RedditCrawler
from crawlers.steam_crawler import SteamCrawler
from crawlers.steam_discussion_crawler import SteamDiscussionCrawler
from crawlers.discord_crawler import DiscordCrawler

import argparse


def handle(args) -> None:
    """Handle the crawler command.

    Args:
        args (list[str]): The arguments for the command.
    """
    global_parser = argparse.ArgumentParser(add_help=False)
    global_parser.add_argument("--write_to_database", action="store_true", help="Insert crawled data into database after crawling")
    global_parser.add_argument("--analyze_immediately", action="store_true", help="Analyze data immediately after crawling")
    
    parser = argparse.ArgumentParser(prog="crawler", description="Run platform-specific community crawlers.", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="platform", required=True)

    # Reddit
    reddit_parser = subparsers.add_parser("reddit", help="Run Reddit crawler", parents=[global_parser])
    reddit_group = reddit_parser.add_mutually_exclusive_group(required=True)
    reddit_group.add_argument("--subreddits", nargs="+", help="Subreddits to crawl")
    reddit_group.add_argument("--post_id", help="Fetch a specific post by ID")
    reddit_group.add_argument("--post_url", help="Fetch a specific post by URL")
    reddit_parser.add_argument("--max_posts", type=int, default=5)
    reddit_parser.add_argument("--max_comments", type=int, default=20)
    reddit_parser.add_argument("--output", default="data/reddit.json")
    reddit_parser.add_argument("--post_sort", choices=["new", "top", "hot"], default="top")
    reddit_parser.add_argument("--comment_sort", choices=["new", "top", "hot"], default="top")
    reddit_parser.add_argument("--keywords", nargs="+")
    reddit_parser.set_defaults(func=run_reddit)

    # Steam
    steam_parser = subparsers.add_parser("steam", help="Run Steam crawler", parents=[global_parser])
    steam_parser.add_argument("--app_id", required=True)
    steam_parser.add_argument("--max_reviews", type=int, default=30)
    steam_parser.add_argument("--max_threads", type=int, default=10)
    steam_parser.add_argument("--output", default="data/steam.json")
    steam_parser.add_argument("--fetch_review", action="store_true")
    steam_parser.add_argument("--fetch_discussion", action="store_true")
    steam_parser.add_argument("--discussion_sort", choices=["mostrecent", "mostrecenttopic", "mostactive"], default="mostrecent")
    steam_parser.add_argument("--keywords", nargs="+")
    steam_parser.set_defaults(func=run_steam)

    # Steam Discussion
    steam_disc_parser = subparsers.add_parser("steam_discussion", help="Run Steam discussion crawler", parents=[global_parser])
    steam_disc_parser.add_argument("--app_id", required=True)
    steam_disc_parser.add_argument("--max_threads", type=int, default=10)
    steam_disc_parser.add_argument("--output", default="data/steam_discussion.json")
    steam_disc_parser.add_argument("--sort", choices=["mostrecent", "mostrecenttopic", "mostactive"], default="mostrecent")
    steam_disc_parser.add_argument("--keywords", nargs="+")
    steam_disc_parser.set_defaults(func=run_steam_discussion)

    # Discord
    discord_parser = subparsers.add_parser("discord", help="Run Discord crawler", parents=[global_parser])
    discord_parser.add_argument("--channels", nargs="+", type=int, required=True)
    discord_parser.add_argument("--max_messages", type=int, default=50)
    discord_parser.add_argument("--output", default="data/discord.json")
    discord_parser.add_argument("--keywords", nargs="+")
    discord_parser.set_defaults(func=run_discord)

    try:
        parsed_args = parser.parse_args(args)
        parsed_args.func(parsed_args)
    except SystemExit:
        # argparse throws SystemExit on --help or error; suppress to keep shell alive
        pass
    except Exception as e:
        print(f"[Error] {e}")


# Function to run the appropriate crawler based on parsed arguments
def run_reddit(args) -> None:
    crawler = RedditCrawler(
        subreddits=args.subreddits,
        post_id=args.post_id,
        post_url=args.post_url,
        max_posts=args.max_posts,
        max_comments=args.max_comments,
        output_path=args.output,
        post_sort=args.post_sort,
        comment_sort=args.comment_sort,
        keywords=args.keywords
    )
    crawler.run(args.write_to_database, args.analyze_immediately)


def run_steam(args) -> None:
    crawler = SteamCrawler(
        app_id=args.app_id,
        max_reviews=args.max_reviews,
        max_discussion_threads=args.max_threads,
        output_path=args.output,
        fetch_review=args.fetch_review,
        fetch_discussion=args.fetch_discussion,
        discussion_sort_mode=args.discussion_sort,
        keywords=args.keywords
    )
    crawler.run(args.write_to_database, args.analyze_immediately)


def run_steam_discussion(args) -> None:
    crawler = SteamDiscussionCrawler(
        app_id=args.app_id,
        max_threads=args.max_threads,
        output_path=args.output,
        sort_mode=args.sort,
        keywords=args.keywords
    )
    crawler.run(args.write_to_database, args.analyze_immediately)


def run_discord(args) -> None:
    crawler = DiscordCrawler(
        channel_ids=args.channels,
        max_messages=args.max_messages,
        output_path=args.output,
        keywords=args.keywords
    )
    crawler.run(args.write_to_database, args.analyze_immediately)
