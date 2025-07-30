import argparse
from datetime import datetime

from intelligence.alert import load_alert_config, change_alert_config, dry_run_test, check_alerts, get_alert_history, get_alert_summary

from database.db_session import get_session, close_session
from database.db_models import Alert

def handle(args: list[str]) -> None:
    """Handle alert-related commands.

    Args:
        args (list[str]): The command-line arguments.
    """
    
    if not args:
        print("Usage: alert <command> [options]")
        return

    parser = argparse.ArgumentParser(prog="alert", description="Manage alert configurations.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    configure_parser = subparsers.add_parser("configure", help="Configure alert settings")
    configure_parser.add_argument("--toxic_threshold", type=float, help="Set the toxic threshold")
    configure_parser.add_argument("--sentiment_crisis_threshold", type=float, help="Set the sentiment crisis threshold")
    configure_parser.add_argument("--sentiment_crisis_minimum_posts", type=int, help="Set the minimum posts for sentiment crisis")
    configure_parser.add_argument("--sentiment_crisis_timeframe", type=str, help="Set the timeframe for sentiment crisis")
    configure_parser.add_argument("--sentiment_alert_drop", type=float, help="Set the sentiment alert drop")
    configure_parser.add_argument("--sentiment_alert_volume_spike_threshold", type=float, help="Set the sentiment alert volume spike threshold")
    configure_parser.add_argument("--sentiment_alert_timeframe", type=str, help="Set the sentiment alert timeframe")
    configure_parser.add_argument("--review_bombing_negative_ratio_threshold", type=float, help="Set the review bombing negative ratio threshold")
    configure_parser.add_argument("--review_bombing_volume_spike_threshold", type=float, help="Set the review bombing volume spike threshold")
    configure_parser.add_argument("--review_bombing_minimum_posts", type=int, help="Set the minimum posts for review bombing")
    configure_parser.add_argument("--review_bombing_timeframe", type=str, help="Set the timeframe for review bombing")
    
    
    show_config_parser = subparsers.add_parser("show_config", help="Show current alert configuration")
    
    dry_run_test_parser = subparsers.add_parser("dry_run_test", help="Run a dry run test for alert configuration")
    
    
    check_parser = subparsers.add_parser("check", help="Check alerts")
    check_parser.add_argument("--live", action="store_true", help="Check only live unreviewed alerts")
    check_parser.add_argument("--platform", nargs="+", help="Filter alerts by platform")
    
    history_parser = subparsers.add_parser("history", help="Show alert history")
    history_parser.add_argument("--since", type=str, help="Filter alerts since this date (YYYY-MM-DD)")
    history_parser.add_argument("--until", type=str, help="Filter alerts until this date (YYYY-MM-DD)")
    history_parser.add_argument("--severity", type=str, choices=["info", "low", "medium", "high", "critical"], help="Filter alerts by severity")
    
    summary_parser = subparsers.add_parser("summary", help="Show summary of alerts")
    summary_parser.add_argument("--show_recent", action="store_true", help="Show recent alerts")
    summary_parser.add_argument("--count_by_type", action="store_true", help="Count alerts by type")
    
    
    mark_reviewed_parser = subparsers.add_parser("mark_reviewed", help="Mark alerts as reviewed")
    mark_reviewed_parser.add_argument("alert_ids", nargs="+", help="List of alert IDs to mark as reviewed")
    
    
    try:
        args = parser.parse_args(args)
        
        if args.subcommand == "configure":
            handle_configure(args)
        elif args.subcommand == "show_config":
            handle_show_config()
        elif args.subcommand == "dry_run_test":
            handle_dry_run_test()
        elif args.subcommand == "check":
            handle_check(args)
        elif args.subcommand == "history":
            handle_history(args)
        elif args.subcommand == "summary":
            handle_summary(args)
        elif args.subcommand == "mark_reviewed":
            handle_mark_reviewed(args)
        else:
            print(f"[Error] Unknown subcommand: {args.subcommand}")
            
    except SystemExit as e:
        print(f"[ArgParse Error] Invalid alert command or arguments.")
    except Exception as e:
        print(f"[Alert Error] An unexpected error occurred: {e}")
        
        
def handle_configure(args: argparse.Namespace) -> None:
    """Handle the alert configuration command.

    Args:
        args (argparse.Namespace): The parsed arguments.
    """
    print("Configuring alert settings...")

    config_updates = {}
    
    if args.toxic_threshold is not None:
        config_updates["toxic_threshold"] = args.toxic_threshold
    if args.sentiment_crisis_threshold is not None:
        config_updates["sentiment_crisis_threshold"] = args.sentiment_crisis_threshold
    if args.sentiment_crisis_minimum_posts is not None:
        config_updates["sentiment_crisis_minimum_posts"] = args.sentiment_crisis_minimum_posts
    if args.sentiment_crisis_timeframe is not None:
        config_updates["sentiment_crisis_timeframe"] = args.sentiment_crisis_timeframe
    if args.sentiment_alert_drop is not None:
        config_updates["sentiment_alert_drop"] = args.sentiment_alert_drop
    if args.sentiment_alert_volume_spike_threshold is not None:
        config_updates["sentiment_alert_volume_spike_threshold"] = args.sentiment_alert_volume_spike_threshold
    if args.sentiment_alert_timeframe is not None:
        config_updates["sentiment_alert_timeframe"] = args.sentiment_alert_timeframe
    if args.review_bombing_negative_ratio_threshold is not None:
        config_updates["review_bombing_negative_ratio_threshold"] = args.review_bombing_negative_ratio_threshold
    if args.review_bombing_volume_spike_threshold is not None:
        config_updates["review_bombing_volume_spike_threshold"] = args.review_bombing_volume_spike_threshold
    if args.review_bombing_minimum_posts is not None:
        config_updates["review_bombing_minimum_posts"] = args.review_bombing_minimum_posts
    if args.review_bombing_timeframe is not None:
        config_updates["review_bombing_timeframe"] = args.review_bombing_timeframe
    
    success = change_alert_config(**config_updates)
    
    if success:
        print("Alert configuration updated successfully.")
    else:
        print("[Error] Failed to update alert configuration.")
    
    
    
    
def handle_show_config() -> None:
    print("Showing current alert configuration:")
    
    configs = load_alert_config()
    if configs is None:
        print("[Error] Failed to load alert configuration.")
        return

    for key, value in configs.items():
        print(f"  {key}: {value}")
        

def handle_dry_run_test() -> None:
    print("Running dry run test for alert configuration...")
    
    try:
        dry_run_test()
    except Exception as e:
        print(f"[Error] An unexpected error occurred during dry run test: {e}")
        

def handle_check(args: argparse.Namespace) -> None:
    """Handle the check command for alerts.

    Args:
        args (argparse.Namespace): The parsed arguments.
    """
    
    session = get_session()
    
    try:
        alerts_platforms = check_alerts(session, live=args.live, platform=args.platform)
        if not alerts_platforms:
            print("No alerts found.")
            return
        print("Alerts found:")
        print(f"{'Alert ID':<10} | {'Type':<25} | {'Reviewed':<8} | {'Platform':<10} | {'Severity':<8}")
        print("-" * 60)

        for alert, platform in alerts_platforms:
            print(f"{alert.alert_id:<10} | {alert.alert_type:<25} | {str(alert.reviewed):<8} | {platform:<10} | {alert.alert_severity:<8}")

    except Exception as e:
        print(f"[Error] An unexpected error occurred while checking alerts: {e}")
    finally:
        close_session()
        
        
def handle_history(args: argparse.Namespace) -> None:
    """Handle the history command for alerts.

    Args:
        args (argparse.Namespace): The parsed arguments.
    """
    session = get_session()
    
    try:
        history = get_alert_history(session, since=args.since, until=args.until, severity=args.severity)
        
        if not history:
            print("No alert history found.")
            return
        
        print("Alert History:")
        print(f"{'Alert ID':<10} | {'Type':<20} | {'Severity':<8} | {'Date':<30}")
        print("-" * 70)

        for alert in history:
            readable_date = alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S") if alert.triggered_at else "N/A"
            print(f"{alert.alert_id:<10} | {alert.alert_type:<20} | {alert.alert_severity:<8} | {readable_date:<30}")

    except Exception as e:
        print(f"[Error] An unexpected error occurred while retrieving alert history: {e}")
    finally:
        close_session()
        
def handle_summary(args: argparse.Namespace) -> None:
    """Handle the summary command for alerts.

    Args:
        args (argparse.Namespace): The parsed arguments.
    """
    session = get_session()
    
    try:
        summary = get_alert_summary(session, show_recent=args.show_recent, count_by_type=args.count_by_type)
        
        if not summary:
            print("No alert summary found.")
            return
        
        print("Alert Summary:")
        print(f"{'Total Alerts':<15}: {summary['total_alerts']}")
        for severity_level, count in summary['severity_counts'].items():
            print(f"  {severity_level.capitalize()} Alerts: {count}")
    
        if args.count_by_type:
            print("Alert Counts by Type:")
            for alert_type, count in summary["type_counts"].items():
                print(f"  {alert_type}: {count}")
    except Exception as e:
        print(f"[Error] An unexpected error occurred while summarizing alerts: {e}")
    finally:
        close_session()
        
def handle_mark_reviewed(args: argparse.Namespace) -> None:
    """Handle the mark_reviewed command for alerts.

    Args:
        args (argparse.Namespace): The parsed arguments.
    """
    session = get_session()
    
    try:
        alert_ids = [int(alert_id) for alert_id in args.alert_ids]
        alerts = session.query(Alert).filter(Alert.alert_id.in_(alert_ids)).all()
        if not alerts:
            print("No alerts found with the provided IDs.")
            return
        for alert in alerts:
            alert.reviewed = True
            session.add(alert)
        try:
            session.commit()
            print(f"Marked {len(alerts)} alerts as reviewed.")
        except Exception as e:
            print(f"[Error] An unexpected error occurred while committing changes: {e}")
            session.rollback()
    except Exception as e:
        print(f"[Error] An unexpected error occurred while marking alerts as reviewed: {e}")
    finally:
        close_session()