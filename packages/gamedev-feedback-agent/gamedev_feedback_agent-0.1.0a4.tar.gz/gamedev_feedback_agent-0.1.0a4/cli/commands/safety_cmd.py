import argparse

from database.db_session import get_session, close_session
from database.db_models import Alert

from intelligence.safety import detect_toxic, check_if_toxic, check_if_spam, detect_spam, detect_scam, check_if_scam
from intelligence.safety import detect_sentiment_crisis, detect_trend_alerts, detect_review_bombing


def handle(args: list[str]) -> None:
    """Handle the safety command.

    Args:
        args (list[str]): The arguments for the safety command.
    """
    
    if not args:
        print("[Error] No subcommand provided for safety command.")
        return
    
    parser = argparse.ArgumentParser(prog="safety", description="Safety command for detecting toxic content.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    detect_toxic_parser = subparsers.add_parser("detect_toxic", help="Detect toxic posts in the database")
    detect_toxic_parser.add_argument("--threshold", type=float, default=0.8, help="Threshold for toxicity detection")
    detect_toxic_parser.add_argument("--platform", nargs="+", help="Filter by platforms")
    detect_toxic_parser.add_argument("--since", type=str, help="Filter posts since this date (YYYY-MM-DD)")
    detect_toxic_parser.add_argument("--until", type=str, help="Filter posts until this date (YYYY-MM-DD)")
    detect_toxic_parser.add_argument("--toxic_keywords_file", type=str, help="File containing toxic keywords")
    
    detect_spam_parser = subparsers.add_parser("detect_spam", help="Detect spam posts in the database")
    detect_spam_parser.add_argument("--spam_patterns_file", type=str, help="File containing spam patterns")
    detect_spam_parser.add_argument("--auto_flag", action="store_true", help="Automatically flag spam posts")
    
    detect_scam_parser = subparsers.add_parser("detect_scam", help="Detect scam posts in the database")
    detect_scam_parser.add_argument("--scam_patterns_file", type=str, help="File containing suspicious domains")
    detect_scam_parser.add_argument("--alert_high_risk", action="store_true", help="Alert for high-risk scam posts")
    
    detect_sentiment_crisis_parser = subparsers.add_parser("detect_sentiment_crisis", help="Detect sentiment crisis in the database")
    detect_sentiment_crisis_parser.add_argument("--timeframe", type=str, default="24h", help="Timeframe for sentiment crisis detection (e.g., '24h' for 24 hours, '2d' for 2 days)")
    detect_sentiment_crisis_parser.add_argument("--minimum_posts", type=int, default=50, help="Minimum number of posts required for sentiment crisis detection, default is 50")
    detect_sentiment_crisis_parser.add_argument("--threshold", type=float, default=0.8, help="Sentiment threshold for crisis detection, default is 0.8")

    detect_trend_alerts_parser = subparsers.add_parser("detect_trend_alerts", help="Detect trend alerts based on sentiment drop and volume spike")
    detect_trend_alerts_parser.add_argument("--sentiment_drop", type=float, default=0.3, help="Sentiment drop threshold for trend alerts, default is 0.3")
    detect_trend_alerts_parser.add_argument("--volume_spike", type=float, default=2.0, help="Volume spike threshold for trend alerts, default is 2.0")
    detect_trend_alerts_parser.add_argument("--timeframe", type=str, default="24h", help="Timeframe for trend alerts, e.g., '7d' for 7 days, '24h' for 24 hours")
    detect_trend_alerts_parser.add_argument("--alert", action="store_true", help="Add an alert for detected trends")

    detect_review_bombing_parser = subparsers.add_parser("detect_review_bombing", help="Detect review bombing based on sentiment analysis")
    detect_review_bombing_parser.add_argument("--ratio_threshold", type=float, default=2.5, help="Threshold for review bombing negative ratio detection, default is 2.5")
    detect_review_bombing_parser.add_argument("--volume_threshold", type=float, default=1.5, help="Threshold for review bombing detection, default is 1.5")
    detect_review_bombing_parser.add_argument("--minimum_posts", type=int, default=50, help="Minimum number of posts required for review bombing detection, default is 50")
    detect_review_bombing_parser.add_argument("--timeframe", type=str, default="6h", help="Timeframe for review bombing detection, default is 6h")
    detect_review_bombing_parser.add_argument("--platform", nargs="+", help="Filter by platforms")

    try:
        args = parser.parse_args(args)
        
        if args.subcommand == "detect_toxic":
            handle_detect_toxic(args)
            
        elif args.subcommand == "detect_spam":
            handle_detect_spam(args)
            
        elif args.subcommand == "detect_scam":
            handle_detect_scam(args)
            
        elif args.subcommand == "detect_sentiment_crisis":
            handle_detect_sentiment_crisis(args)
            
        elif args.subcommand == "detect_trend_alerts":
            handle_detect_trend_alerts(args)
            
        elif args.subcommand == "detect_review_bombing":
            handle_detect_review_bombing(args)
            
    except SystemExit as e:
        print(f"[ArgParse Error] Invalid safety command or arguments: {e}")
    except Exception as e:
        print(f"[Error] An unexpected error occurred: {e}")
        
        
def handle_detect_toxic(args: list[str]) -> None:
    session = get_session()
    try:
        toxic_posts = detect_toxic(session, sentiment_threshold=args.threshold, platform=args.platform, 
                                   since=args.since, until=args.until, toxic_keywords_file=args.toxic_keywords_file)
        
        if not toxic_posts:
            print("No toxic posts detected with the given criteria.")
            return
        
        for post, reason in toxic_posts:
            print(f"Toxic Post Detected: {post.post_id} | Reason: {reason}")
        
            # add alert for toxic posts 
            alert = Alert(
                post_id=post.post_id,
                alert_type="toxic",
                alert_severity=3,  # 3 for medium
                note=f"Toxic content detected: {reason}"
            )
            session.add(alert)
        
        try:
            session.commit()
        except Exception as e:
            print(f"[Error] Failed to add alert for toxic posts: {e}")
            session.rollback()
        
    except Exception as e:
        print(f"[Error] Failed to detect toxic posts: {e}")
    finally:
        close_session()
        
        
def handle_detect_spam(args: list[str]) -> None:
    session = get_session()
    try:
        spam_posts = detect_spam(session, spam_file=args.spam_patterns_file, auto_flag=args.auto_flag)
        
        if not spam_posts:
            print("No spam posts detected with the given criteria.")
            return
        
        for post, reason in spam_posts:
            print(f"Spam Post Detected: {post.post_id} | Reason: {reason}")
            # add alert for spam posts
            alert = Alert(
                post_id=post.post_id,
                alert_type="spam",
                alert_severity=1,  # 1 for informational
                note=f"Spam content detected: {reason}"
            )
            session.add(alert)
        try:
            session.commit()
        except Exception as e:
            print(f"[Error] Failed to add spam alerts: {e}")
            session.rollback()
            
    except Exception as e:
        print(f"[Error] Failed to detect spam posts: {e}")
    finally:
        close_session()
        
        
def handle_detect_scam(args: list[str]) -> None:
    session = get_session()
    try:
        scam_posts_and_scores = detect_scam(session, scam_file=args.scam_patterns_file, 
                                 alert_high_risk=args.alert_high_risk)

        if not scam_posts_and_scores:
            print("No scam posts detected with the given criteria.")
            return

        for post, score, reason in scam_posts_and_scores:
            print(f"Scam Post Detected: {post.post_id} | Score: {score} | Reason: {reason}")
    except Exception as e:
        print(f"[Error] Failed to detect scam posts: {e}")
    finally:
        close_session()
        
        
def handle_detect_sentiment_crisis(args: list[str]) -> None:
    session = get_session()
    try:
        posts = detect_sentiment_crisis(session, timeframe=args.timeframe, minimum_posts=args.minimum_posts, 
                                        threshold=args.threshold)
        
        if not posts:
            print("No sentiment crisis detected with the given criteria.")
            return
        
        print(f"Sentiment Crisis Detected in {len(posts)} posts:")
        print("Post IDs:", [post.post_id for post in posts])
        
        # add alert for sentiment crisis using first post id
        print(f"Adding alert for sentiment crisis based on post ID: {posts[0].post_id}")
        alert = Alert(
            post_id=posts[0].post_id,
            alert_type="sentiment_crisis",
            alert_severity=4,  # 4 for High
            note=f"Sentiment crisis detected based on recent posts. {len(posts)} posts with negative sentiment above threshold {args.threshold} in the last {args.timeframe}."
        )
        try:
            session.add(alert)
            session.commit()
        except Exception as e:
            print(f"[Error] Failed to add alert for sentiment crisis: {e}")
            session.rollback()

            
    except Exception as e:
        print(f"[Error] Failed to detect sentiment crisis: {e}")
    finally:
        close_session()
        
def handle_detect_trend_alerts(args: list[str]) -> None:
    session = get_session()
    try:
        trend_alerts = detect_trend_alerts(session, volume_spike=args.volume_spike, sentiment_drop=args.sentiment_drop, timeframe=args.timeframe)

        if not trend_alerts:
            print("No trend alerts detected with the given criteria.")
            return

        if not trend_alerts.get("alerts"):
            print("No posts found that triggered trend alerts.")
            return
        
        print("Trend Alerts Detected:")
        print("Alerts: ", trend_alerts.get("alerts", []))
        if args.alert:
            # add an alert using first post id
            if trend_alerts["posts"]:
                first_post = trend_alerts["posts"][0][0]
                alert = Alert(
                    post_id=first_post.post_id,
                    alert_type="trend_alert",
                    alert_severity=len(trend_alerts["alerts"]) + 1,  # 2 for Low, 3 for medium if both volume spike and sentiment drop
                    note=trend_alerts["alerts"]
                )
                try:
                    session.add(alert)
                    session.commit()
                except Exception as e:
                    print(f"[Error] Failed to add alert for trend: {e}")
                    session.rollback()
        
        
    except Exception as e:
        print(f"[Error] Failed to detect trend alerts: {e}")
    finally:
        close_session()
        
        
def handle_detect_review_bombing(args: list[str]) -> None:
    """
    Handle the detect_review_bombing subcommand.
    
    Args:
        args: The arguments passed to the detect_review_bombing command.
    """
    session = get_session()
    try:
        if_review_bombed, review_bombing_posts = detect_review_bombing(session, negative_ratio_threshold=args.ratio_threshold, volume_spike_threshold=args.volume_threshold,
                                                     minimum_posts=args.minimum_posts, timeframe=args.timeframe, platform=args.platform)
        
        if not if_review_bombed:
            print("No review bombing detected with the given criteria.")
            return
        print(f"Review Bombing Detected in {len(review_bombing_posts)} posts:")
        
        # add an alert for review bombing using first post id
        if review_bombing_posts:
            first_post = review_bombing_posts[0]
            alert = Alert(
                post_id=first_post.post_id,
                alert_type="review_bombing",
                alert_severity=4,  # 4 for high
                note=f"Review bombing detected based on sentiment analysis. {len(review_bombing_posts)} posts with negative sentiment above threshold {args.ratio_threshold} in the last {args.timeframe}."
            )
            try:
                session.add(alert)
                session.commit()
            except Exception as e:
                print(f"[Error] Failed to add alert for review bombing: {e}")
                session.rollback()
        
    except Exception as e:
        print(f"[Error] Failed to detect review bombing: {e}")
    finally:
        close_session()
        

