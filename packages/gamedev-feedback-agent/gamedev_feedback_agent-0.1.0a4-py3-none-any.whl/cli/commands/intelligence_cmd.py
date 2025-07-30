import argparse

from intelligence.coverage import get_coverage_summary
from intelligence.process import process_post
from intelligence.intelligence_config import IntelligenceConfig

from database.db_session import get_session, close_session
from database.db_models import Post


def handle(args: list[str]) -> None:
    """
    Handle the intelligence command with the provided arguments.
    
    Args:
        args: The arguments passed to the intelligence command.
    """

    parser = argparse.ArgumentParser(prog="intelligence")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    show_coverage_parser = subparsers.add_parser("show_coverage", help="Show coverage summary of posts")
    show_coverage_parser.add_argument("--platforms", nargs="+", help="Filter by platforms")
    show_coverage_parser.add_argument("--since", type=str, help="Filter posts since this date (YYYY-MM-DD)")
    show_coverage_parser.add_argument("--until", type=str, help="Filter posts until this date (YYYY-MM-DD)")
    show_coverage_parser.add_argument("--detailed", action="store_true", help="Show detailed coverage information")
    
    
    process_uncovered_parser = subparsers.add_parser("process_uncovered", help="Process uncovered posts")
    process_uncovered_parser.add_argument("--platforms", nargs="+", help="Filter by platforms")
    process_uncovered_parser.add_argument("--since", type=str, help="Filter posts since this date (YYYY-MM-DD)")
    process_uncovered_parser.add_argument("--until", type=str, help="Filter posts until this date (YYYY-MM-DD)")
    process_uncovered_parser.add_argument("--lang_detection", action="store_true", help="Only perform language detection")
    process_uncovered_parser.add_argument("--translation", action="store_true", help="Only perform translation")
    process_uncovered_parser.add_argument("--sentiment", action="store_true", help="Only perform sentiment analysis")
    process_uncovered_parser.add_argument("--priority", action="store_true", help="Only perform priority analysis")
    process_uncovered_parser.add_argument("--embedding", action="store_true", help="Only perform embedding generation")
    
    
    
    
    try:
        
        args = parser.parse_args(args)
        print(f"Executing intelligence command with subcommand: {args.subcommand}")
        
        if args.subcommand == "show_coverage":
            handle_show_coverage(args)
            
        elif args.subcommand == "process_uncovered":
            handle_process_uncovered(args)
        
    except SystemExit as e:
        print(f"[ArgParse Error] Invalid intelligence command or arguments.")

    except Exception as e:
        print(f"[Intelligence Error] An unexpected error occurred: {e}")

    
    
    
def handle_show_coverage(args: list[str]) -> None:
    """
    Handle the show_coverage subcommand.
    """
    session = get_session()
    try:
        coverage_summary = get_coverage_summary(session, args.platforms, args.since, args.until)
        
        if args.detailed:
            print("Detailed Coverage Summary:")
            # may add more details in the future
            for key, value in coverage_summary.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} : {value}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("Coverage Summary:")
            for key, value in coverage_summary.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)}")
                else:
                    print(f"  {key}: {value}")
    except Exception as e:
        print(f"[Intelligence Error] An unexpected error occurred: {e}")
    finally:
        close_session()
        
def handle_process_uncovered(args: list[str]) -> None:
    """
    Handle the process_uncovered subcommand.
    
    Args:
        args: The arguments passed to the process_uncovered command.
    """
    session = get_session()
    try:
        # get post_ids from the coverage summary
        coverage_summary = get_coverage_summary(session, args.platforms, args.since, args.until)
        if coverage_summary["total_post_count"] == 0:
            print("No posts found for the given filters.")
            return
        
        for post_id in coverage_summary["missing_posts"]:
            print(f"Processing post ID: {post_id}")
            # query to get the post by ID
            post = session.query(Post).filter(Post.post_id == post_id).first()
            if not post:
                print(f"Post with ID {post_id} not found.")
                continue
            
            if not args.lang_detection and not args.translation and not args.sentiment and not args.priority and not args.embedding:
                args.lang_detection = True
                args.translation = True
                args.sentiment = True
                args.priority = True
                args.embedding = True
            
            process_post(
                session,
                post,
                lang_detection=args.lang_detection,
                translation=args.translation,
                sentiment_analysis=args.sentiment,
                priority_score=args.priority,
                embedding_generation=args.embedding
            )
    except Exception as e:
        print(f"[Intelligence Error] An unexpected error occurred while processing uncovered posts: {e}")
    finally:
        close_session()