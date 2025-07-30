import argparse
from datetime import datetime, timedelta
from collections import Counter

from intelligence.report import generate_brief_report, get_sentiment_trend, get_priority_alert, get_cross_platform_data

from database.db_session import get_session, close_session

from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich.table import Table


def handle(args: list[str]) -> None:
    """Handle the report command.

    Args:
        args (list[str]): Arguments for the report command.
    """
    
    if not args:
        print("Usage: report <command> [options]")
        return
    
    parser = argparse.ArgumentParser(prog="report", description="Generate reports on community feedback.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    brief_parser = subparsers.add_parser("brief", help="Generate a brief report of posts and analyses.")
    brief_parser.add_argument("--since", type=str, help="Start date for the report (YYYY-MM-DD).")
    brief_parser.add_argument("--daily", action="store_true", help="Generate daily report.")
    brief_parser.add_argument("--weekly", action="store_true", help="Generate weekly report.")
    brief_parser.add_argument("--platform", type=str, nargs="+", help="List of platforms to include in the report.")
    
    trend_parser = subparsers.add_parser("trends", help="Generate a trends report (not implemented yet).")
    trend_parser.add_argument("--since", type=str,required=True, help="Start date for the trends report (YYYY-MM-DD).")
    trend_parser.add_argument("--daily", action="store_true", help="Generate daily trends report.")
    trend_parser.add_argument("--weekly", action="store_true", help="Generate weekly trends report.")
    trend_parser.add_argument("--platform", type=str, nargs="+", help="List of platforms to include in the trends report.")
    
    priority_alert_parser = subparsers.add_parser("priority_alerts", help="Generate a report of priority alerts (not implemented yet).")
    priority_alert_parser.add_argument("--threshold", type=float, default=80, help="Priority threshold for the post that the alert corresponds to.")
    priority_alert_parser.add_argument("--explain", action="store_true", help="Include explanations for each alert.")

    cross_platform_parser = subparsers.add_parser("cross_platform", help="Generate a cross-platform report (not implemented yet).")
    cross_platform_parser.add_argument("--since", type=str, help="Start date for the cross-platform report (YYYY-MM-DD).")
    cross_platform_parser.add_argument("--platform", type=str, nargs="+", help="List of platforms to include in the cross-platform report. If not specified, all platforms will be included.")


    try:
        args = parser.parse_args(args)
        
        if args.command == "brief":
            handle_brief(args)
        elif args.command == "trends":
            handle_trends(args)
        elif args.command == "priority_alerts":
            handle_priority_alerts(args)
        elif args.command == "cross_platform":
            handle_cross_platform(args)
        else:
            print(f"Unknown command: {args.command}")
            return
        
        
    except SystemExit as e:
        print(f"[ArgParse Error] Invalid report command or arguments: {e}")
    except Exception as e:
        print(f"[Error] An unexpected error occurred: {e}")
        
        
        
def handle_brief(args: argparse.Namespace) -> None:
    """Handle the brief report command.

    Args:
        args (argparse.Namespace): Arguments for the brief report command.
    """
    if not args.since and not args.daily and not args.weekly:
        print("no timeframe specified")
        return
    
    if args.since and (args.daily or args.weekly):
        print("Cannot specify both 'since' and 'daily'/'weekly'. Use one of them.")
        return

    if args.daily and args.weekly:
        print("Cannot specify both 'daily' and 'weekly'. Use one of them.")
        return
    
    # convert to datetime
    if args.since:
        try:
            since = datetime.strptime(args.since, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format for 'since'. Use YYYY-MM-DD.")
            return
    elif args.daily:
        since = datetime.now() - timedelta(days=1)
    elif args.weekly:
        since = datetime.now() - timedelta(weeks=1)

    session = get_session()
    try:
        report = generate_brief_report(session, since=since, platform=args.platform)
        pretty_print_report_brief(report)
    except Exception as e:
        print(f"[Error] An unexpected error occurred while generating the report: {e}")
    finally:
        close_session()
        
        
def handle_trends(args: argparse.Namespace) -> None:
    """Handle the trends report command.    

    Args:
        args (argparse.Namespace): Arguments for the trends report command.
    """
    if not args.since:
        print("--since is required for trends report")
        return

    try:
        since = datetime.strptime(args.since, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format for 'since'. Use YYYY-MM-DD.")
        return


    session = get_session()
    try:
        report = get_sentiment_trend(session, since=since, platform=args.platform, daily=args.daily, weekly=args.weekly)
        print("Sentiment Trend Report:")
        if not report:
            print("No data available for the specified period.")
            return
        # for sentiment_dict in report:
        #     date = sentiment_dict['date']
        #     total = sentiment_dict['total']
        #     average = sentiment_dict['average_score']
        #     difference = sentiment_dict.get('difference', 0)
        #     print(f"{date}:  (Count: {total})  {average:.2f} | Difference: {difference:.2f}")
        pretty_print_sentiment_trend(report)
    except Exception as e:
        print(f"[Error] An unexpected error occurred while generating the report: {e}")
    finally:
        close_session()

def handle_priority_alerts(args: argparse.Namespace) -> None:
    """Handle the priority alerts report command.

    Args:
        args (argparse.Namespace): Arguments for the priority alerts report command.
    """
    session = get_session()
    try:
        priority_alerts = get_priority_alert(session, threshold=args.threshold, explain=args.explain)
        if not priority_alerts:
            print("No priority alerts found.")
            return
        
        console = Console()
        table = Table(title="Priority Alerts", show_lines=True)
        table.add_column("Alert ID", style="red", no_wrap=True)
        table.add_column("Post ID", style="blue", no_wrap=True)
        table.add_column("Priority", style="yellow", justify="right")
        if args.explain:
            table.add_column("Explanation", style="cyan")

        for alert in priority_alerts:
            row = [
                str(alert['alert_id']),
                str(alert['post_id']),
                f"{alert['priority_score']:.2f}"
            ]
            if args.explain:
                row.append(alert.get('explanation', ''))
            table.add_row(*row)

        console.print(table)
    except Exception as e:
        print(f"[Error] An unexpected error occurred while generating the priority alerts report: {e}")
    finally:
        close_session()
        
        

def handle_cross_platform(args: argparse.Namespace) -> None:
    """Handle the cross-platform report command (not implemented yet).

    Args:
        args (argparse.Namespace): Arguments for the cross-platform report command.
    """
    since = None
    if args.since:
        try:
            since = datetime.strptime(args.since, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format for 'since'. Use YYYY-MM-DD.")
            return
    
    session = get_session()
    try:
        report = get_cross_platform_data(session, since=since, platform=args.platform)
        if not report:
            print("No cross-platform data available for the specified period.")
            return
        
        console = Console()

        table = Table(title="Cross-Platform Report", show_lines=True)
        table.add_column("Platform", style="bold cyan")
        table.add_column("Posts", style="magenta", justify="right")
        table.add_column("Analyses", style="blue", justify="right")
        table.add_column("Positive %", style="green", justify="right")
        table.add_column("Neutral %", style="yellow", justify="right")
        table.add_column("Negative %", style="red", justify="right")
        table.add_column("Avg Sentiment", style="bold green", justify="right")
        table.add_column("Avg Priority", style="bold magenta", justify="right")
        table.add_column("Alerts", style="red", justify="right")

        for platform, data in report.items():
            table.add_row(
                platform,
                str(data.get("post_count", 0)),
                str(data.get("analysis_count", 0)),
                f"{data.get('positive %', 0):.1f}%",
                f"{data.get('neutral %', 0):.1f}%",
                f"{data.get('negative %', 0):.1f}%",
                f"{data.get('average_sentiment_score', 0):.2f}",
                f"{data.get('average_priority_score', 0):.2f}",
                str(data.get("alert_count", 0)),
            )

        console.print(table)
    except Exception as e:
        print(f"[Error] An unexpected error occurred while generating the cross-platform report: {e}")
    finally:
        close_session()
    
        
        
        
def pretty_print_report_brief(report: dict) -> None:
    console = Console()

    # 1. Posts Overview
    post_panel = Panel.fit(
        f"[bold]Total Posts:[/bold] {report['post_count']}\n"
        f"[cyan]Types:[/cyan] {dict(report['post_types'])}\n"
        f"[cyan]Languages:[/cyan] {dict(report['post_languages'])}\n"
        f"[cyan]Platforms:[/cyan] {dict(report['post_platforms'])}",
        title="[blue]Posts Overview[/blue]", border_style="blue"
    )

    # 2. Sentiment Analysis
    sentiment_panel = Panel.fit(
        f"[bold]Analyses:[/bold] {report['analysis_count']}\n"
        f"[green]Sentiment Labels:[/green] {dict(report['sentiment_labels'])}\n"
        f"[green]Avg Sentiment Score 0-1:[/green] [yellow]{report['average_sentiment_score_projected']:.2f}[/yellow]",
        title="[green]Sentiment[/green]", border_style="green"
    )

    # 3. Priority
    prio_str = '\n'.join([f"{k}: {v}" for k, v in report['priority_summary'].items()])
    priority_panel = Panel.fit(
        f"[bold]Priority Buckets:[/bold]\n{prio_str}\n"
        f"[cyan]Avg Priority Score:[/cyan] [yellow]{report['average_priority_score']:.2f}[/yellow]",
        title="[red]Priority Alerts[/red]", border_style="red"
    )

    # 4. Alerts
    alert_panel = Panel.fit(
        f"[bold]Total Alerts:[/bold] {report['alert_count']}\n"
        f"[magenta]Types:[/magenta] {dict(report['alert_types'])}\n"
        f"[magenta]Severity:[/magenta] {dict(report['alert_severity'])}\n"
        f"[magenta]Unreviewed:[/magenta] {report['unreviewed_alert_count']}",
        title="[magenta]Safety & Alerts[/magenta]", border_style="magenta"
    )

    # 5. Tags
    tags_str = ', '.join([f"{k}({v})" for k, v in report['tag_counts'].items()])
    tags_panel = Panel.fit(
        tags_str if tags_str else "[grey]No tags[/grey]",
        title="[yellow]Top Tags[/yellow]", border_style="yellow"
    )

    # Print everything
    console.print(post_panel)
    console.print(sentiment_panel)
    console.print(priority_panel)
    console.print(alert_panel)
    console.print(tags_panel)
    
    
def pretty_print_sentiment_trend(report: list[dict]):
    console = Console()
    if not report:
        console.print("[yellow]No data available for the specified period.[/yellow]")
        return

    table = Table(title="Sentiment Trend Report", show_lines=True)
    table.add_column("Date", style="cyan", no_wrap=True)
    table.add_column("Total Posts", style="magenta")
    table.add_column("Average", style="green")
    table.add_column("Δ vs Last", style="bold")

    for sentiment_dict in report:
        date = sentiment_dict['date']
        total = str(sentiment_dict['total'])
        if sentiment_dict['average_score'] > 0.8:
            average = f"[bold green]{sentiment_dict['average_score']:.2f}[/bold green] ⭐️"
        elif sentiment_dict['average_score'] < 0.2:
            average = f"[bold red]{sentiment_dict['average_score']:.2f}[/bold red] ⚠️"
        else:
            average = f"{sentiment_dict['average_score']:.2f}"
        difference = sentiment_dict.get('difference', 0)
        # Color the difference: green if up, red if down, yellow if flat
        if difference > 0:
            diff_str = f"[green]+{difference:.2f}[/green]"
        elif difference < 0:
            diff_str = f"[red]{difference:.2f}[/red]"
        else:
            diff_str = f"[yellow]{difference:.2f}[/yellow]"

        table.add_row(date, total, average, diff_str)

    console.print(table)
    
    
    
