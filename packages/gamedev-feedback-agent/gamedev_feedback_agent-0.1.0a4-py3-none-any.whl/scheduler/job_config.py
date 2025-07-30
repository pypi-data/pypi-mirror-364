JOB_CONFIGS = [
    {
        "name": "reddit_gamedev",
        "platform": "reddit",
        "cron": {"minute": "*/2"},
        "params": {
            "subreddits": ["gamedev"],
            "post_sort": "hot",
            "comment_sort": "top",
            "max_posts": 5,
            "max_comments": 10,
            "output_path": "data/reddit_gamedev.json"
        }
    },
    
    # {
    #     "name": "reddit_gaming",
    #     "platform": "reddit",
    #     "cron": {"minute": "*"},
    #     "params": {
    #         "subreddits": ["gaming"],
    #         "post_sort": "hot",
    #         "comment_sort": "top",
    #         "max_posts": 5,
    #         "max_comments": 10,
    #         "keywords": ["feedback", "bug"],
    #         "output_path": "data/reddit_gaming.json"
    #     }
    # },
    
    # {
    #     "name": "steam_csgo",
    #     "platform": "steam",
    #     "cron": {"minute": "*/10"},
    #     "params": {
    #         "app_id": "730",
    #         "max_reviews": 30,
    #         "max_discussion_threads": 10,
    #         "fetch_review": True,
    #         "fetch_discussion": True,
    #         "discussion_sort_mode": "new",
    #     }
    # },
    
    # {
    #     "name": "discord_test_channel",
    #     "platform": "discord",
    #     "cron": {"minute": "*/10"},
    #     "params": {
    #         "channel_ids": ["1384393182682284072"],
    #         "max_messages": 100,
    #     }
    # }
]
