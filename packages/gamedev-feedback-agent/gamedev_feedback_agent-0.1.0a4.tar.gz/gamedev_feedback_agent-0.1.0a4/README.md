# Game_Dev_Community_Feedback_Agent


### Environment Setup
see requirements.txt for dependencies.
You can set up a virtual environment and install the dependencies using:
```bash
pip install -r requirements.txt
```

### Setup Instructions
1. Reddit:
   - Create a Reddit app at https://www.reddit.com/prefs/apps
   - Get your client ID, client secret, and user agent.
2. Discord:
   - Create a Discord bot at https://discord.com/developers/applications
   - Get your bot token.
   - Ensure "MESSAGE CONTENT INTENT" is enabled in the bot settings.
   - Through OAuth2, generate invite links using scopes 'bot' and permissions 'View Channels', 'Read Message History', 'Send Messages'
   - Invite the bot to your server using the generated link.
3. PostgreSQL:
   - Install PostgreSQL and create a database.
   - Add your database URL to the `.env` file.
   - schema.sql contains the database schema, which you can run to set up the database tables.
   - you can use dev_reset.sql to reset the database to a clean state.


### Environment Variables
Before running the crawler, create a `.env` file in the project root with:
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

DISCORD_BOT_TOKEN=your_discord_bot_token

DATABASE_URL=your_postgres_database_url

### Data
This project stores crawled data in data/, which is ignored by Git. You can run the crawler to generate fresh data.

### Resources
The project stores resources in the resources/ directory, including the keywords for safety tests and others


### Intelligence Engine Pipeline
Data is processed through a pipeline that includes:
- Language Detection
- Translation
- Sentiment Analysis
- Priority Score Calculation
- Embedding Generation

Safety check pipeline includes:
- Toxicity Detection
- Spam Detection
- Scam Detection
- Sentiment Crisis Detection
- Trend Alerts Detection
- Review Bombing Detection


### CLI Usage
To install the CLI tool:
```bash
git clone https://github.com/QLhahaha/Game_Dev_Community_Feedback_Agent.git
cd Game_Dev_Community_Feedback_Agent
pip install -e .
```

Run the CLI tool with:
```bash
gdcfa
```

Below are the available commands and their usage:
Note that the starting prompt `gdcfa` is not included in the command examples.
```
# Available commands:
# crawler <platform> [--options]
    platform: reddit | steam | discord
    --options for global:
        --write_to_database
        --analyze_immediately
    --options for reddit:
        --subreddits
        --post_id
        --post_url
        --max_posts
        --max_comments
        --post_sort
        --comment_sort
        --output
        --keywords
    --options for steam:
        --app_id
        --max_reviews
        --max_threads
        --fetch_review
        --fetch_discussion
        --discussion_sort
        --output
        --keywords
    --options for discord:
        --channels
        --max_messages
        --output
        --keywords


# scheduler
scheduler list // list all scheduled jobs
scheduler clear // clear all scheduled jobs
scheduler status // show status of the scheduler, currently is same as `scheduler list`

scheduler pause <job_id> // pause a specific job
scheduler resume <job_id> // resume a specific job
scheduler delete <job_id> // delete a specific job
scheduler run_now <job_id> // run a specific job immediately

scheduler add --path <path> // add jobs from a job_config json file
scheduler crawling --platform <platform> [--options]
    --subreddits <subreddits> // specify subreddits (comma-separated)
    --post_id <post_id> // specify a specific post ID
    --post_url <post_url> // specify a specific post URL
    --app_id <app_id> // specify Steam app ID
    --channels <channels> // specify Discord channels (comma-separated)
    --start_time <start_time> // specify start time for the job (optional)
    --end_time <end_time> // specify end time for the job (optional)
    --interval <interval> // specify interval for the job
    --daily_at <daily_at> // specify daily time for the job 
    --weekly // weekly run of the job
    --day // specify the day of the week for weekly jobs (optional)


# view
view platforms // view all platforms in the database
view tags // view all tags in the database
view games // view all games in the database

view sources // view all sources(post type) in the database

view tables <table_name> // view all tables or a specific table
view stats // view general stats of the database

view posts [--options] // view posts with optional filters
    --platform <platform> // filter by platforms
    --tags <tags> // filter by tags
    --authors <authors> // filter by authors
    --keywords <keywords> // filter by keywords
    --since <date> // filter posts since a date
    --until <date> // filter posts until a date
    --limit <number> // limit the number of posts displayed

view alerts [--options] // view alerts with optional filters
    --platforms <platforms> // filter by platforms
    --type <type> // filter by alert type
    --since <date> // filter alerts since a date
    --until <date> // filter alerts until a date
    --game <game> // filter by game
    --limit <number> // limit the number of alerts displayed


# search
search <keyword> [--options]
    --platform <platform> // filter by platform
    --limit <number> // limit the number of posts displayed

search_similar --post_id [options]
search_similar <texts> [--options]
    --limit <number> // limit the number of similar posts displayed
    --min_similarity <threshold> // similarity threshold

search_hybrid <keyword> [--options]
    --semantic_weight <weight> // weight for semantic search
    --limit <number> // limit the number of hybrid search results displayed



# database
database list_json // list all JSON files in the data directory
database insert_json --path <path> // insert data from a JSON file into the database
database export_json --tables <tables> --path <path> // export a table to a JSON file
database add --table <table_name> --values <name=value, ...> // add a row to table, e.g.:
    database add --table users --values name=Alice,age=30
database show --table <table_name> // show all rows in a table


# analyze
analyze language_detect [--options]
    --show-stats // show language detection stats

analyze translate [--options]
    --target-language <language_code> // specify target language for translation
    --show-before-after // show before and after translation stats
    --post_id <post_id> // specify post ID to translate
    --threshold <threshold> // specify similarity threshold for translation

analyze sentiment [--options]
    --unprocessed // analyze unprocessed posts
    --platform <platform> // specify platform for sentiment analysis
    --since <date> // specify start date for sentiment analysis
    --until <date> // specify end date for sentiment analysis
    --english_only // analyze only English posts
    --batch_size <size> // specify batch size for sentiment analysis
    --text <text> // specify text for sentiment analysis

analyze priority_score [--options]
    --unprocessed // analyze unprocessed posts
    --post_id <post_id> // specify post ID for priority score analysis
    --english_only // analyze only English posts
    --batch_size <size> // specify batch size for priority score analysis

analyze embedding [--options]
    --unprocessed // analyze unprocessed posts
    --post_id <post_id> // specify post ID for embedding analysis
    --english_only // analyze only English posts
    --batch_size <size> // specify batch size for embedding analysis

analyze process [--options]
    --unprocessed // analyze unprocessed posts
    --post_id <post_id> // specify post ID for embedding analysis
    --english_only // analyze only English posts
    --explain // explain the embedding process
    --lang_detect // enable language detection for embedding
    --translate // enable translation for embedding
    --sentiment // enable sentiment analysis for embedding
    --priority_score // enable priority score analysis for embedding
    --embedding // enable embedding for posts

# intelligence
intelligence show_coverage [--options]
    --platform <platform> // specify platform for coverage
    --since <date> // specify start date for coverage, format: YYYY-MM-DD
    --until <date> // specify end date for coverage, format: YYYY-MM-DD

intelligence process_uncovered [--options]
    --platforms <platform> // specify platforms for processing uncovered posts
    --since <date> // specify start date for processing, format: YYYY-MM-DD
    --until <date> // specify end date for processing, format: YYYY-MM-DD
    --lang_detection // enable language detection for processing
    --translation // enable translation for processing
    --sentiment // enable sentiment analysis for processing
    --priority // enable priority score analysis for processing
    --embedding // enable embedding for processing


# safety
safety detect_toxic [--options]
    --threshold <threshold> // specify toxicity threshold for detection
    --platform <platform> // specify platform for toxicity detection
    --since <date> // specify start date for toxicity detection
    --until <date> // specify end date for toxicity detection

safety detect_spam [--options]
    --auto_flag // automatically flag spam posts by tags

safety detect_scam [--options]
    --alert_high_risk // alert high-risk posts

safety detect_sentiment_crisis [--options]
    --timeframe <timeframe> // specify timeframe for sentiment crisis detection
    --minimum_posts <number> // specify minimum number of posts for detection
    --threshold <threshold> // specify sentiment threshold for detection

safety detect_trend_alerts [--options]
    --sentiment_drop <threshold> // specify sentiment drop threshold for trend alerts
    --volume_spike <threshold> // specify volume spike threshold for trend alerts
    --timeframe <timeframe> // specify timeframe for trend alerts
    --alert // alert detected negative trend

safety detect_review_bombing [--options]
    --ratio_threshold <threshold> // specify ratio threshold for review bombing detection
    --volume_threshold <threshold> // specify volume threshold for review bombing detection
    --timeframe <timeframe> // specify timeframe for review bombing detection
    --minimum_posts <number> // specify minimum number of posts for detection
    --platform <platform> // specify platform for review bombing detection

# alert
alert configure [--options]
    --toxic_threshold <threshold> // specify toxicity threshold for alerts
    --sentiment_crisis_threshold <threshold> // specify sentiment crisis threshold for alerts
    --sentiment_crisis_minimum_posts <number> // specify minimum number of posts for sentiment crisis alerts
    --sentiment_crisis_timeframe <timeframe> // specify timeframe for sentiment crisis alerts
    --sentiment_alert_drop <threshold> // specify sentiment drop threshold for alerts
    --sentiment_alert_volume_spike_threshold <threshold> // specify volume spike threshold for alerts
    --sentiment_alert_timeframe <timeframe> // specify timeframe for sentiment alerts
    --review_bombing_negative_ratio_threshold <threshold> // specify negative ratio threshold for review bombing alerts
    --review_bombing_volume_spike_threshold <threshold> // specify volume spike threshold for review bombing alerts
    --review_bombing_minimum_posts <number> // specify minimum number of posts for review bombing alerts
    --review_bombing_timeframe <timeframe> // specify timeframe for review bombing alerts

alert show_config // show current alert configuration

alert dry_run_test // run a dry run test for alerts that only output to console

alert check [--options]
    --live // check live alerts
    --platform <platform> // specify platform for checking alerts

alert history [--opions]
    --since <date> // specify start date for alert history
    --until <date> // specify end date for alert history
    --severity <severity> // specify severity level for alert history, choices are "info", "low", "medium", "high", "critical"

alert summary [--options]
    --show_recent // show recent alerts
    --count_by_type // count alerts by type

alert mark_reviewed <alert_ids> // mark alerts as reviewed


# report
report brief [--options]
    --since <date> // specify start date for report
    --daily // generate daily report
    --weekly // generate weekly report
    --platform <platform> // specify platform for report

report trends [--options]
    --since <date> // specify start date for trends report
    --daily // generate daily trends report
    --weekly // generate weekly trends report
    --platform <platform> // specify platform for trends report

report priority_alerts [--options]
    --threshold <threshold> // specify priority threshold for alerts
    --explain // explain the priority alerts

report cross_platform [--options]
    --since <date> // specify start date for cross-platform report
    --platforms <platforms> // specify platforms for cross-platform report

# config
config view // view current context
config show_providers // show available providers

config set_provider [type] [provider_name] // set a provider for a specific type
    type: translation | sentiment | embedding
    provider_name: "ollama", "openai"

config set_model [provider] [model_type] [model_name] // set a model for a specific provider
    provider: "ollama", "openai"
    model_type: translation | sentiment | embedding
    model_name: e.g. "llama-3.1", "gpt-4o"
```


### Demo Link
[Database and CLI Demo](https://drive.google.com/file/d/1s9D8BOdvhu7x3LiR_Mw95YiecXvuKQZY/view?usp=sharing)
[Intelligence Engine Demo](https://drive.google.com/file/d/1_QCDFJ2pPCyjJ2ZKDJblqfhDwuPW1q79/view?usp=sharing)
[Advanced Intelligence Operations & System Integration Demo](https://drive.google.com/file/d/1QhvmhgWdRTIi4AC41v7DaO3kFfX3ST5U/view?usp=drive_link)