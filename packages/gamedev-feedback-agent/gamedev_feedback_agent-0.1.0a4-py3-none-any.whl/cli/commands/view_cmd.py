import argparse
from sqlalchemy.orm import Session
from database.db_models import Platform, Post, Author, Game, Tag, GamePost, PostTag, Alert, Analysis, Embedding
from database.db_session import get_session, close_session
from sqlalchemy import or_, and_
from sqlalchemy import func

def handle(args) -> None:
    """Handle the view command.

    Args:
        args (list[str]): The arguments for the command.
    """
    parser = argparse.ArgumentParser(prog="view", description="Explore collected post data.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # view platforms
    subparsers.add_parser("platforms", help="List all platforms in the database")
    subparsers.add_parser("tags", help="List all tags in the database")
    subparsers.add_parser("games", help="List all games in the database")
    subparsers.add_parser("sources", help="List all sources in the database")

    # view tables
    tables_parser = subparsers.add_parser("tables", help="List all rows from a specified table")
    tables_parser.add_argument("table", help="Table name to display")

    # view posts
    post_parser = subparsers.add_parser("posts", help="View filtered posts")
    post_parser.add_argument("--platform")
    post_parser.add_argument("--type")
    post_parser.add_argument("--author")
    post_parser.add_argument("--language", nargs="+", help="Filter posts by language")
    post_parser.add_argument("--keywords")
    post_parser.add_argument("--since")
    post_parser.add_argument("--until")
    post_parser.add_argument("--tags", nargs="+", help="Filter posts by tags (comma-separated)")
    post_parser.add_argument("--limit", type=int, default=100, help="Limit number of posts to display")
    
    # view alerts
    alert_parser = subparsers.add_parser("alerts", help="View alerts in the database")
    alert_parser.add_argument("--platform", help="Filter alerts by platform")
    alert_parser.add_argument("--type", help="Filter alerts by type")
    alert_parser.add_argument("--since", help="Filter alerts since this date (YYYY-MM-DD)")
    alert_parser.add_argument("--until", help="Filter alerts until this date (YYYY-MM-DD)")
    alert_parser.add_argument("--game", help="Filter alerts by game")
    alert_parser.add_argument("--limit", type=int, default=100, help="Limit number of alerts to display")


    # view analysis
    analysis_parser = subparsers.add_parser("analysis", help="View analysis data")
    analysis_parser.add_argument("--post_id", help="Filter analysis by post ID")
    analysis_parser.add_argument("--platform", help="Filter analysis by platform name")
    analysis_parser.add_argument("--limit", type=int, default=100, help="Limit number of analysis results to display")

    # view stats
    stats_parser = subparsers.add_parser("stats", help="View statistics about posts")

    try:
        parsed = parser.parse_args(args)

        
        # # Try to connect *before* creating session (optional but cleaner)
        # try:
        #     with get_session().connect():
        #         pass  # Just open and close to verify connection
        # except Exception as e:
        #     print(f"[Database Error] Could not connect to the database: {e}")
        #     return

        session = get_session()

        # Subcommand platforms, tags, games, sources
        if parsed.subcommand == "platforms":
            platforms = session.query(Platform).order_by(Platform.name).all()
            if not platforms:
                print("No platforms found in the database.")
                return
            for p in platforms:
                print(f"- {p.name}")
        
        elif parsed.subcommand == "tags":
            tags = session.query(Tag).order_by(Tag.name).all()
            if not tags:
                print("No tags found in the database.")
                return
            for t in tags:
                print(f"- {t.name}")
                
        elif parsed.subcommand == "games":
            games = session.query(Game).order_by(Game.title).all()
            if not games:
                print("No games found in the database.")
                return
            for g in games:
                print(f"- {g.title} (studio: {g.studio})")
                
        elif parsed.subcommand == "sources":
            # list all sources (post types) in the database
            sources = session.query(Post.post_type).distinct().all()
            if not sources:
                print("No sources found in the database.")
                return
            for s in sources:
                print(f"- {s[0]}")

        # Subcommand tables
        if parsed.subcommand == "tables":
            if parsed.table == "Platform":
                rows = session.query(Platform).all()
            elif parsed.table == "Post":
                rows = session.query(Post).all()
            elif parsed.table == "Author":
                rows = session.query(Author).all()
            elif parsed.table == "Game":
                rows = session.query(Game).all()
            elif parsed.table == "Tag":
                rows = session.query(Tag).all()
            elif parsed.table == "GamePost":
                rows = session.query(GamePost).all()
            elif parsed.table == "PostTag":
                rows = session.query(PostTag).all()
            elif parsed.table == "Alert":
                rows = session.query(Alert).all()
            elif parsed.table == "Analysis":
                rows = session.query(Analysis).all()
            elif parsed.table == "Embedding":
                rows = session.query(Embedding).all()
            else:
                print(f"Unknown table: {parsed.table}")
                return

            if not rows:
                print(f"No rows found in table {parsed.table}.")
                return
            
            print(f"Rows in table {parsed.table}:")
            for row in rows:
                # pretty print the row
                row_data = ", ".join(f"{key}: {value}" for key, value in row.__dict__.items() if not key.startswith('_'))
                # replace platform id with platform name if applicable
                if hasattr(row, 'platform_id'):
                    platform_name = session.query(Platform.name).filter(Platform.platform_id == row.platform_id).first()
                    if platform_name:
                        row_data = row_data.replace(f"platform_id: {row.platform_id}", f"platform: {platform_name[0]}")
                row_data = row_data.replace("'", "")  # remove single quotes
                print(row_data)
        
        
        
        # Subcommand stats
        elif parsed.subcommand == "stats":
            total_posts = session.query(Post).count()
            total_platforms = session.query(Platform).count()
            total_authors = session.query(Author).count()
            total_games = session.query(Game).count()
            total_tags = session.query(Tag).count()
            total_analyses = session.query(Analysis).count()
            total_embeddings = session.query(Embedding).count()
            last_update = session.query(Post.timestamp).order_by(Post.timestamp.desc()).first()
            
            # for future use
            alert_count = session.query(Alert).count()

            print(f"Total Posts: {total_posts}")
            print(f"Total Platforms: {total_platforms}")
            print(f"Total Authors: {total_authors}")
            print(f"Total Games: {total_games}")
            print(f"Total Tags: {total_tags}")
            print(f"Total Analyses: {total_analyses}")
            print(f"Total Embeddings: {total_embeddings}")
            print(f"Total Alerts: {alert_count}")

            if last_update:
                print(f"Last Update: {last_update[0]}")
            else:
                print("No posts found in the database.")

            
            # Additional stats can be added here as needed



        # Subcommand posts
        elif parsed.subcommand == "posts":
            query = session.query(Post).join(Platform).outerjoin(Author, Post.author_id == Author.author_id)

            if parsed.platform:
                # check if platform exists
                platform_exists = session.query(Platform).filter(Platform.name == parsed.platform).first()
                if not platform_exists:
                    print(f"[Error] Platform '{parsed.platform}' does not exist in the database.")
                    return
                query = query.filter(Platform.name == parsed.platform)

            if parsed.author:
                # check if author exists
                author_exists = session.query(Author).filter(Author.username == parsed.author).first()
                if not author_exists:
                    print(f"[Error] Author '{parsed.author}' does not exist in the database.")
                    return
                query = query.filter(Author.username == parsed.author)

            if parsed.type:
                # check if post type is valid
                valid_types = session.query(Post.post_type).distinct().all()
                valid_types = [t[0] for t in valid_types]  # convert to list of strings
                if parsed.type not in valid_types:
                    print(f"[Error] Invalid post type: {parsed.type}. Must be one of: {valid_types}")
                    return
                query = query.filter(Post.post_type == parsed.type)
                print(f"Filtering posts by type: {parsed.type}")
                
            if parsed.language:
                # check if language is valid -> ISO 639-1 code
                # check if it is passed in with comma
                languages  = parsed.language
                if "," in parsed.language[0]:
                    languages = [lang.strip() for lang in parsed.language[0].split(",")]
                invalid_languages = [lang for lang in languages if (len(lang) != 2 or not lang.isalpha()) and "zh" not in lang]
                if invalid_languages:
                    print(f"[Error] Invalid language codes: {invalid_languages}. Must be 2-letter ISO 639-1 codes.")
                    return
                # filter posts by languages
                query = query.filter(Post.language.in_(languages))

            if parsed.keywords:
                # comma-separated keywords to select posts containing any of the keywords
                # plus-separated keywords to select posts containing all of the keywords
                # comma first, then plus
                groups = parsed.keywords.split(",")
                keyword_groups = []
                for group in groups:
                    terms = group.strip().split("+")
                    keyword_groups.append([t.strip() for t in terms if t.strip()])
                    
                conditions = []
                for group in keyword_groups:
                    and_clauses = [Post.content.ilike(f"%{term}%") for term in group]
                    conditions.append(and_(*and_clauses))
                query = query.filter(or_(*conditions))

            if parsed.since:
                query = query.filter(Post.timestamp >= parsed.since)

            if parsed.until:
                query = query.filter(Post.timestamp <= parsed.until)
                
            if parsed.tags:
                # filter posts by tags
                tag_conditions = []
                for tag in parsed.tags:
                    # get tag id from tag name
                    tag_obj = session.query(Tag).filter(Tag.name == tag).first()
                    if tag_obj:
                        tag_conditions.append(PostTag.tag_id == tag_obj.tag_id)
                query = query.join(PostTag).filter(or_(*tag_conditions))

            query = query.order_by(Post.timestamp.desc()).limit(parsed.limit)      

            posts = query.all()
            
            print(f"Found {len(posts)} posts:")
            for post in posts:
                post_platform_name = session.query(Platform.name).filter(Platform.platform_id == post.platform_id).first()
                print(f"[{post.post_id}] {post.timestamp} | {post_platform_name[0]} | {post.post_type} | {post.language} | {post.content[:60]}...")


        # Subcommand alerts
        elif parsed.subcommand == "alerts":
            alert_query = (
                session.query(Alert, Game.title.label("game_title"), Platform.name.label("platform_name"))
                .join(Post, Alert.post_id == Post.post_id)
                .join(GamePost, Post.post_id == GamePost.post_id)
                .join(Game, GamePost.game_id == Game.game_id)
                .join(Platform, Post.platform_id == Platform.platform_id)
            )

            # Optional filters
            if parsed.platform:
                alert_query = alert_query.filter(Platform.name == parsed.platform)

            if parsed.type:
                alert_query = alert_query.filter(Alert.alert_type == parsed.type)

            if parsed.since:
                alert_query = alert_query.filter(Alert.triggered_at >= parsed.since)

            if parsed.until:
                alert_query = alert_query.filter(Alert.triggered_at <= parsed.until)

            if parsed.game:
                alert_query = alert_query.filter(Game.title == parsed.game)

            alert_query = alert_query.order_by(Alert.triggered_at.desc()).limit(parsed.limit)

            # Execute and print
            results = alert_query.all()
            print(f"Found {len(results)} alerts:")
            for alert, game_title, platform_name in results:
                print(f"[{alert.alert_id}] {alert.triggered_at} | {platform_name} | {game_title} | {alert.alert_type}")

        # Subcommand analysis
        elif parsed.subcommand == "analysis":
            analysis_query = session.query(Analysis)

            if parsed.post_id:
                analysis_query = analysis_query.filter(Analysis.post_id == parsed.post_id)

            if parsed.platform:
                platform_id = session.query(Platform.platform_id).filter(Platform.name == parsed.platform).first()
                if not platform_id:
                    print(f"Platform '{parsed.platform}' not found.")
                    return
                analysis_query = analysis_query.join(Post).filter(Post.platform_id == platform_id[0])

            analysis_query = analysis_query.order_by(Analysis.post_id).limit(parsed.limit)

            analyses = analysis_query.all()
            print(f"Found {len(analyses)} analyses:")
            for analysis in analyses:
                print(f"[Post ID: {analysis.post_id} | Platform: {parsed.platform} | Sentiment: {analysis.sentiment_label} | Confidence: {analysis.sentiment_score} | Priority_Score: {analysis.priority_score}]")

            # Get total counts
            total_analyses = session.query(func.count(Analysis.post_id)).scalar()

            print(f"Total Analyses: {total_analyses}")

    except SystemExit as e:
        print(f"[ArgParse Error] Invalid view command or arguments.")
    except Exception as e:
        print(f"[View Error] {e}")
    finally:
        try:
            close_session()
        except:
            pass  # In case session was never created
