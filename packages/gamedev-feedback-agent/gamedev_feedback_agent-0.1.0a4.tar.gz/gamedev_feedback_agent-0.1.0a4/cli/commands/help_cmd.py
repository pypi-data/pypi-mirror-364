def show_help(arg) -> None:
    if not arg:
        print("""Available commands:
                    crawler <platform> <options>
                    scheduler list
                    scheduler run-now <job-id>
                    scheduler crawling --platform <platform> <options>
                    exit
                    help <command>
                    """)
        
    elif arg == "crawler":
        print("crawler <platform> <options>")
        print("Available platforms: reddit, steam, discord")
        print("available options for reddit: --subreddits <subreddit1,subreddit2,...> --post-id <post_id> --post-url <post_url> --max-posts <number> --max-comments <number> --post-sort <sort_type> --comment-sort <sort_type>)")
        print("available options for steam: --app-id <app_id> --fetch-review --fetch-discussion --max-reviews <number> --max-discussion-threads <number> --max-discussion-comments <number>")
        print("available options for discord: --channel-ids <channel_id1,channel_id2,...> --max-messages <number> --keywords <keyword1,keyword2,...>")
    
    elif arg == "scheduler":
        print("scheduler list\nscheduler run-now <job-id>\nscheduler crawling --platform <platform> <options>")
        print("use scheduler crawling --platform <platform> <options> to start a crawling job")
        print("Available platforms: reddit, steam, discord")
        print("available options for reddit: --subreddits <subreddit1,subreddit2,...> --post-id <post_id> --post-url <post_url>")
        print("available options for steam: --app-id <app_id>")
        print("available options for discord: --channel-ids <channel_id1,channel_id2,...>")
        print("available options for schedule: --interval <interval> --start-time <start_time> --end-time <end_time> --daily_at <time> --weekly_on <day_of_week> --day <day_of_week if weekly>")
    else:
        print(f"No help found for '{arg}'")
