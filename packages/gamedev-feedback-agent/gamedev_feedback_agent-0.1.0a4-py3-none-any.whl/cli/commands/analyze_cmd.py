
import shlex
import argparse
from database.db_session import get_session, close_session
from database.db_models import Post, Analysis, Platform, Embedding
from intelligence.language import detect_post_language_all, translate_text
from intelligence.sentiment import get_text_sentiment, batch_get_text_sentiment, analyze_post_sentiment
from intelligence.priority_score import get_priority_score, FACTORS
from intelligence.embedding import get_text_embedding, batch_get_text_embeddings
from intelligence.process import process_post
from intelligence.intelligence_config import IntelligenceConfig
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Query


def handle(args: list[str]) -> None:
    """Handle the 'analyze' command.

    Args:
        args (list[str]): The arguments for the command.
    """
    if not args:
        print("Usage: analyze <command> [options]")
        return

    parser = argparse.ArgumentParser(prog="analyze")
    subparsers = parser.add_subparsers(dest="subcommand")

    # Subcommand: language-detect
    lang_parser = subparsers.add_parser("language-detect")
    lang_parser.add_argument("--show-stats", action="store_true")
    
    # Subcommand: translate
    translate_parser = subparsers.add_parser("translate")
    translate_parser.add_argument("--target-language", default=IntelligenceConfig.DEFAULT_LANGUAGE, help="Target language for translation")
    translate_parser.add_argument("--show-before-after", action="store_true")
    translate_parser.add_argument("--post_id", type=int, help="ID of the post to translate")
    translate_parser.add_argument("--all", action="store_true", help="Translate all posts in the database")
    translate_parser.add_argument("--threshold", type=float, default=IntelligenceConfig.LANGUAGE_CONFIDENCE_THRESHOLD,
                                  help="Confidence threshold for translation")
    
    
    # Subcommand: sentiment
    sentiment_parser = subparsers.add_parser("sentiment")
    sentiment_parser.add_argument("--unprocessed", action="store_true", help="Analyze unprocessed posts")
    sentiment_parser.add_argument("--platform", nargs="+", help="Platform to analyze (e.g., 'reddit', 'steam, 'discord')")
    sentiment_parser.add_argument("--since", type=str, help="Analyze posts since this date (YYYY-MM-DD)")
    sentiment_parser.add_argument("--until", type=str, help="Analyze posts until this date (YYYY-MM-DD)")
    sentiment_parser.add_argument("--english_only", action="store_true", help="Only analyze posts in English")
    sentiment_parser.add_argument("--batch_size", type=int, help="Number of posts to process in each batch")
    sentiment_parser.add_argument("--text", type=str, help="Text to analyze sentiment for")

    # Subcommand: priority_score
    priority_parser = subparsers.add_parser("priority_score")
    priority_parser.add_argument("--post_id", type=int, help="ID of the post to analyze")
    priority_parser.add_argument("--unprocessed", action="store_true", help="Analyze unprocessed posts")
    priority_parser.add_argument("--english_only", action="store_true", help="Only analyze posts in English")
    priority_parser.add_argument("--show_factors", action="store_true", help="Show individual factor scores")
    
    
    # Subcommand: embedding
    embedding_parser = subparsers.add_parser("embedding")
    embedding_parser.add_argument("--post_id", type=int, help="ID of the post to create embedding for")
    embedding_parser.add_argument("--unprocessed", action="store_true", help="Create embeddings for unprocessed posts")
    embedding_parser.add_argument("--english_only", action="store_true", help="Only create embeddings for posts in English")
    embedding_parser.add_argument("--batch_size", type=int, help="Number of posts to process in each batch")
    
    
    # Subcommand: process
    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("--post_id", type=int, nargs="+", help="ID of the post to process")
    process_parser.add_argument("--unprocessed", action="store_true", help="Process unprocessed posts")
    process_parser.add_argument("--lang_detect", action="store_true", help="Detect language of the post")
    process_parser.add_argument("--translate", action="store_true", help="Translate the post to the target language")
    process_parser.add_argument("--sentiment", action="store_true", help="Analyze sentiment of the post")
    process_parser.add_argument("--priority_score", action="store_true", help="Calculate priority score of the post")
    process_parser.add_argument("--embedding", action="store_true", help="Create embedding for the post")
    process_parser.add_argument("--english_only", action="store_true", help="Only process posts in English")
    process_parser.add_argument("--explain", action="store_true", help="Explain the analysis results")
    

    try:
        args = parser.parse_args(args)


        # subcommand language-detect
        if args.subcommand == "language-detect":
            detect_post_language_all(args.show_stats)

        # subcommand translate
        elif args.subcommand == "translate":
            # check if target language is valid
            if args.target_language and (len(args.target_language) != 2 and "zh" not in args.target_language.lower()):
                print(f"[Analyze Error] Invalid target language: '{args.target_language}'. Please use a valid ISO 639-1 language code.")
                return
            if args.post_id is not None:
                translate_post(args.post_id, args.target_language, args.threshold, args.show_before_after)
            elif args.all:
                translate_all_posts(args.target_language, args.threshold, args.show_before_after)
            else:
                print("Please specify either --post_id or --all to translate posts.")
            
        # subcommand sentiment
        elif args.subcommand == "sentiment":
            handle_sentiment(args)

        # subcommand priority_score
        elif args.subcommand == "priority_score":
            handle_priority_score(args)
            
        elif args.subcommand == "embedding":
            handle_embedding(args)
            
        elif args.subcommand == "process":
            handle_process(args)
            
        else:
            print(f"Unknown analyze subcommand: {args.subcommand}.")

    except SystemExit as e:
        print(f"[ArgParse Error] Invalid analyze command or arguments.")
    except Exception as e:
        print(f"[Analyze Error] An unexpected error occurred: {e}")
        return
        
        
        
        
# handle functions        
def handle_sentiment(args: list[str]) -> None:
    """Handle sentiment analysis commands.

    Args:
        args (list[str]): The command-line arguments for the sentiment analysis.
    """
    if args.text and (args.unprocessed or args.platform or args.since or args.until):
        print("[Analyze Error] --text cannot be used with other options.")
        return
    elif args.text:
        # check text sentiment
        sentiment, confidence = get_text_sentiment(args.text)
        print(f"Sentiment: {sentiment}, Confidence: {confidence:.2f}")
    else:
        # process posts and write into database
        session = get_session()
        query = session.query(Post)
        if args.unprocessed:
            # filtered posts that has been in analysis table
            query = query.filter(~Post.post_id.in_(session.query(Analysis.post_id)))
        if args.platform:
            # union posts from multiple platforms
            platforms = [platform.strip().lower() for platform in args.platform]
            if not platforms:
                print("[Analyze Error] No valid platforms provided. Please specify at least one platform.")
                return
            # get platform ids
            platform_ids = []
            for platform in platforms:
                platform_id = session.query(Platform.platform_id).filter(Platform.name == platform).scalar()
                if platform_id is None:
                    print(f"[Analyze Error] Invalid platform: {platform}. Please use a valid platform name.")
                    return
                platform_ids.append(platform_id)
            query = query.filter(Post.platform_id.in_(platform_ids))
        if args.since:
            # filter posts since a specific date
            try:
                from datetime import datetime
                since_date = datetime.strptime(args.since, "%Y-%m-%d")
                query = query.filter(Post.timestamp >= since_date)
            except ValueError:
                print("[Analyze Error] Invalid date format for --since. Use YYYY-MM-DD.")
                return
        if args.until:
            # filter posts until a specific date
            try:
                from datetime import datetime
                until_date = datetime.strptime(args.until, "%Y-%m-%d")
                query = query.filter(Post.timestamp <= until_date)
            except ValueError:
                print("[Analyze Error] Invalid date format for --until. Use YYYY-MM-DD.")
                return
        if args.english_only:
            # filter posts that are in English
            subquery = session.query(Post.post_id).filter(
                Post.language == "en"
            )
            query = query.filter(Post.post_id.in_(subquery))
            
        # batch processing
        batch_size = args.batch_size
        if batch_size and batch_size > 1:
            posts = query.all()
            total_posts = len(posts)
            for i in range(0, total_posts, batch_size):
                print(f"[Sentiment Analysis] Processing batch {i // batch_size + 1} of {total_posts // batch_size + 1}...")
                batch_posts = posts[i:i + batch_size]
                batched_sentiments = batch_get_text_sentiment([post.content for post in batch_posts])
                if not batched_sentiments:
                    print(f"[Sentiment Analysis Error] No results returned for batch {i // batch_size + 1}.")
                    continue
                for j, post in enumerate(batch_posts):
                    try:
                        if len(batched_sentiments[j]) != 3:
                            print(f"[Sentiment Analysis Error] Unexpected result format for post ID {post.post_id}: {batched_sentiments[j]}. Expected (index, sentiment, confidence).")
                            continue
                        index, sentiment, confidence = batched_sentiments[j]
                        if index == -1 or confidence < 0 or confidence > 1 or sentiment == "unknown":
                            # skip mismatched or negative confidence results
                            print(f"[Sentiment Analysis Warning] Skipping post ID {post.post_id} due to invalid sentiment analysis results.")
                            continue
                        if index != j:
                            print(f"[Sentiment Analysis Warning] Index mismatch for post ID {post.post_id}: expected {j}, got {index}.")
                            continue
                        analysis = Analysis(post_id=post.post_id, sentiment_label=sentiment, sentiment_score=confidence)
                        session.add(analysis)
                        session.commit()
                        print(f"Post ID {post.post_id}: Sentiment: {sentiment}, Confidence: {confidence:.2f}")
                    except Exception as e:
                        session.rollback()
                        print(f"[Sentiment Analysis Error] Failed to analyze post ID {post.post_id}: {e}")
                        
        # not batched processing
        else:
            posts = query.all()
            if len(posts) == 0:
                print("[Sentiment Analysis Info] No posts found for the specified criteria.")
                return
            count = 0
            for post in posts:

                try:
                    sentiment, confidence = get_text_sentiment(post.content)
                    if confidence < 0 or sentiment == "unknown":
                        # skip posts with negative confidence or unknown sentiment
                        continue
                    analysis = Analysis(post_id=post.post_id, sentiment_label=sentiment, sentiment_score=confidence)
                    # check if analysis already exists
                    existing_analysis = session.query(Analysis).filter(Analysis.post_id == post.post_id).first()
                    if existing_analysis:
                        print(f"[Sentiment Analysis Warning] Post ID {post.post_id} already has sentiment analysis results. Rewriting it.")
                        existing_analysis.sentiment_label = sentiment
                        existing_analysis.sentiment_score = confidence
                    else:
                        session.add(analysis)
                    session.commit()
                    count += 1
                    print(f"Post ID {post.post_id}: Sentiment: {sentiment}, Confidence: {confidence:.2f}")
                except Exception as e:
                    session.rollback()
                    print(f"[Sentiment Analysis Error] Failed to analyze post ID {post.post_id}: {e}")
            print(f"Processed {count} posts for sentiment analysis.")
        close_session()
       
       
       
       
def handle_priority_score(args: list[str]) -> None:
    """Handle the priority score calculation for a post.

    Args:
        args (list[str]): The arguments passed to the command.
    """
    # check if post_id or unprocessed is provided
    if args.post_id:
        # process single post
        post_id = args.post_id
        priority_scores = get_priority_score(post_id)
        print(f"Priority score for post {post_id}: {priority_scores[0]}")
        if args.show_factors:
            print(f"Factors contributing to priority score for post {post_id}:")
            for i in range(1, len(priority_scores)):
                print(f"  {FACTORS[i-1]}: {priority_scores[i]}")
    else:
        session = get_session()
        query = session.query(Post)
        if args.unprocessed:
            # filter posts that have not been processed yet
            subquery = session.query(Analysis.post_id).filter(Analysis.priority_score != None)
            query = query.filter(~Post.post_id.in_(subquery))
        if args.english_only:
            # filter posts that are in English
            subquery = session.query(Post.post_id).filter(
                Post.language == "en"
            )
            query = query.filter(Post.post_id.in_(subquery))
        posts = query.all()
        if not posts:
            print("[Priority Score Error] No posts found for the specified criteria.")
            return
        count = 0
        for post in posts:
    
            priority_scores = get_priority_score(post.post_id)
            print(f"Priority score for post {post.post_id}: {priority_scores[0]}")
            if args.show_factors:
                print(f"Factors contributing to priority score for post {post.post_id}:")
                for i in range(1, len(priority_scores)):
                    print(f"  {FACTORS[i-1]}: {priority_scores[i]}")
            # priority score should not be zero, if zero, then there must be an error
            if priority_scores[0] != 0:
                count += 1
        print(f"Processed {count} posts for priority score calculation.")




def handle_embedding(args: list[str]) -> None:
    """Handle the creation of embeddings for posts.

    Args:
        args (list[str]): The arguments passed to the command.
    """
    session = get_session()
    
    if args.post_id is not None:
        post_id = args.post_id
        post = session.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            print(f"[Embedding Error] Post with ID {post_id} not found.")
            return
        embedding_content = post.content if not post.translated_content else post.translated_content
        model, embedding = get_text_embedding(embedding_content)
        # create or update Embedding record in the database
        try:
            embedding_record = session.query(Embedding).filter(Embedding.post_id == post_id, Embedding.model == model).first()
            if embedding_record:
                if embedding_record.embedding is not None and len(embedding_record.embedding) > 0:
                    print(f"[Embedding Warning] Post {post.post_id} already has an embedding. Replacing it with new embedding.")
                embedding_record.embedding = embedding
            else:
                embedding_record = Embedding(post_id=post_id, embedding=embedding, model=model, content=embedding_content,)
                session.add(embedding_record)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[Embedding Error] Failed to create/update embedding for post {post_id}: {e}")
        print(f"Embedding for post {post_id} genetrated successfully: {embedding[:5]} ...")  # print first 5 elements of the embedding
        return
    else:
        # process multiple posts
        query = session.query(Post)
        if args.unprocessed:
            # filter posts that have not been processed yet by this model
            model = IntelligenceConfig.get_embedding_model_name()
            if not model:
                print("[Embedding Error] No embedding model specified. Please set the EMBEDDING_PROVIDER.")
                return
            subquery = select(Embedding.post_id).where(
                Embedding.embedding != None,
                Embedding.model == model
            )
            query = query.filter(~Post.post_id.in_(subquery))
        
        if args.english_only:
            # filter posts that are in English
            subquery = session.query(Post.post_id).filter(
                Post.language == "en"
            )
            query = query.filter(Post.post_id.in_(subquery))

            
        posts = query.all()
        if not posts:
            print("[Embedding INFO] No posts found for the specified criteria.")
            return
        elif len(posts) == 0:
            print("[Embedding INFO] No posts to process for embedding.")
            return
        
        if args.batch_size:
            # batch processing
            batch_size = args.batch_size
            total_posts = len(posts)
            for i in range(0, total_posts, batch_size):
                print(f"[Embedding] Processing batch {i // batch_size + 1} of {(total_posts - 1) // batch_size + 1}...")
                batch_posts = posts[i:i + batch_size]
                try:
                    batched_embeddings = batch_get_text_embeddings([post.content if not post.translated_content else post.translated_content for post in batch_posts])
                    if not batched_embeddings:
                        print(f"[Embedding Error] No results returned for batch {i // batch_size + 1}.")
                        continue
                    model, embeddings = batched_embeddings
                    for j, post in enumerate(batch_posts):
                        embedding_content = post.content if not post.translated_content else post.translated_content
                        embedding = embeddings[j]
                        # create or update Embedding record in the database
                        embedding_record = session.query(Embedding).filter(Embedding.post_id == post.post_id, Embedding.model == model).first()
                        if embedding_record:
                            if embedding_record.embedding is not None and len(embedding_record.embedding) > 0:
                                print(f"[Embedding Warning] Post {post.post_id} already has an embedding. Replacing it with new embedding.")
                            embedding_record.embedding = embedding
                        else:
                            embedding_record = Embedding(post_id=post.post_id, embedding=embedding, model=model, content=embedding_content,)
                            session.add(embedding_record)
                        session.commit()
                        print(f"Post ID {post.post_id}: Embedding created/updated successfully.")
                except Exception as e:
                    session.rollback()
                    print(f"[Embedding Error] Failed to create/update embeddings for batch starting at index {i}: {e}")
                
                
        else:
            # process posts one by one
            count = 0
            print(f"[Embedding] Processing {len(posts)} posts...")
            for post in posts:
                try:
                    embedding_content = post.content if not post.translated_content else post.translated_content
                    model, embedding = get_text_embedding(embedding_content)
                    # create or update Embedding record in the database
                    embedding_record = session.query(Embedding).filter(Embedding.post_id == post.post_id, Embedding.model == model).first()
                    if embedding_record:
                        if embedding_record.embedding is not None and len(embedding_record.embedding) > 0:
                            print(f"[Embedding Warning] Post {post.post_id} already has an embedding. Replacing it with new embedding.")
                        embedding_record.embedding = embedding
                    else:
                        embedding_record = Embedding(post_id=post.post_id, embedding=embedding, model=model, content=embedding_content,)
                        session.add(embedding_record)
                    session.commit()
                    count += 1
                    print(f"Embedding for post {post.post_id} created/updated successfully: {embedding[:5]} ...")  # print first 5 elements of the embedding
                except Exception as e:
                    session.rollback()
                    print(f"[Embedding Error] Failed to create/update embedding for post {post.post_id}: {e}")
            print(f"Processed {count} posts for embedding creation.")



def handle_process(args: list[str]) -> None:
    """Process the given arguments for post analysis.

    Args:
        args (list[str]): The arguments to process.
    """
    try:
        session = get_session()
        flags = {
            "lang_detect": args.lang_detect,
            "translate": args.translate,
            "sentiment": args.sentiment,
            "priority_score": args.priority_score,
            "embedding": args.embedding,
        }
        if not any(flags.values()):
            # set all true if no flags are provided
            flags = {
                "lang_detect": True,
                "translate": True,
                "sentiment": True,
                "priority_score": True,
                "embedding": True,
            }
        # check some dependencies
        # priority score requires sentiment analysis
        if flags["priority_score"] and not flags["sentiment"]:
            print("[Process Error] Priority score calculation requires sentiment analysis to be enabled. Please set --sentiment to True.")
            return
        # translation requires language detection
        if flags["translate"] and not flags["lang_detect"]:
            print("[Process Error] Translation requires language detection to be enabled. Please set --lang_detect to True.")
            return    
        
        if args.post_id is not None:
            # Process the post
            for post_id in args.post_id:
                print(f"[Process Info] Processing post {post_id}...")
                post = session.query(Post).filter(Post.post_id == post_id).first()
                try:
                    process_post(session, post, lang_detection=flags["lang_detect"],
                                translation=flags["translate"], sentiment_analysis=flags["sentiment"],
                                priority_score=flags["priority_score"], embedding_generation=flags["embedding"],
                                explain=args.explain, rewrite=True)
                except Exception as e:
                    print(f"[Process Error] Failed to process post {post.post_id}: {e}")
        query = session.query(Post)
        if args.unprocessed:
            # if any of the flags are set, filter posts that have not been processed yet
            query = get_unprocessed_posts(session, flags, query)
        if args.english_only:
            # filter posts that are in English
            subquery = session.query(Post.post_id).filter(
                Post.language == "en"
            )
            query = query.filter(Post.post_id.in_(subquery))
        posts = query.all()
        if not posts:
            print("[Process Info] No unprocessed posts found.")
            return
        print(f"[Process Info] Found {len(posts)} unprocessed posts to process.")
        count = 0
        # get the post_ids and rebind later to prevent out of session issue
        post_ids = [post.post_id for post in posts]
        for post_id in post_ids:
            print(f"[Process Info] Processing post {post_id}...")
            post = session.query(Post).filter(Post.post_id == post_id).first()
            if not post:
                print(f"[Process Error] Failed to rebind post {post_id}.")
                continue
            try:
                process_post(session, post, lang_detection=flags["lang_detect"],
                            translation=flags["translate"], sentiment_analysis=flags["sentiment"],
                            priority_score=flags["priority_score"], embedding_generation=flags["embedding"],
                            explain=args.explain, rewrite=True)
                count += 1
            except Exception as e:
                print(f"[Process Error] Failed to process post {post.post_id}: {e}")
        print(f"[Process Info] Processed {count} unprocessed posts.")
    except Exception as e:
        print(f"[Process Error] An error occurred while processing posts: {e}")
        return        
    finally:
        close_session()



# helper functions
def translate_post(post_id: int, target_lang: str, threshold: float, show_before_after: bool = False) -> None:
    """Translate a post's content to the specified target language.

    Args:
        post_id (int): The ID of the post to translate.
        target_lang (str): The target language for translation.
        show_before_after (bool): If True, shows the content before and after translation.
    """
    session = get_session()
    
    try:
        post = session.query(Post).filter(Post.post_id == post_id).first()
    except Exception as e:
        print(f"[ANALYZE ERROR] Failed to query post with ID {post_id}: {e}")
        return
    
    if not post:
        print(f"[ANALYZE ERROR] Post with ID {post_id} not found.")
        return
    
    if post.language_confidence < threshold:
        print(f"[ANALYZE WARNING] Post {post_id} has low language confidence ({post.language_confidence}).")

    
    try:
        if post.language == target_lang:
            print(f"[ANALYZE INFO] Post {post_id} is already in the target language: {target_lang}. No translation needed.")
            return
        if post.translated_content:
            print(f"[ANALYZE WARNING] Post {post_id} already has translated content. Replacing it with new translation.")

        original_content = post.content
        translated_content = translate_text(original_content, target_lang)
    except Exception as e:
        print(f"[ANALYZE ERROR] Failed to translate post {post_id} content to {target_lang}: {e}")
        return
    
    if show_before_after:
        print(f"Original Content:\n{original_content}\n")
        print(f"Translated Content:\n{translated_content}\n")
    
    post.translated_content = translated_content
    session.commit()
    
    close_session()
    

def translate_all_posts(target_lang: str, threshold: float, show_before_after: bool = False) -> None:
    """Translate all posts in the database to the specified target language.

    Args:
        target_lang (str): The target language for translation.
        show_before_after (bool): If True, shows the content before and after translation.
    """
    session = get_session()
    
    try:
        posts = session.query(Post).filter(Post.language != target_lang).all()
    except Exception as e:
        print(f"[ANALYZE ERROR] Failed to query posts: {e}")
        return
    
    for post in posts:
        try:
            if post.language_confidence < threshold:
                print(f"[ANALYZE WARNING] Post {post.post_id} has low language confidence ({post.language_confidence}). Skipping translation.")
                continue
            if post.language == target_lang:
                print(f"[ANALYZE INFO] Post {post.post_id} is already in the target language: {target_lang}. No translation needed.")
                continue
            if post.translated_content:
                print(f"[ANALYZE WARNING] Post {post.post_id} already has translated content. Skipping it with new translation.")
                continue
            original_content = post.content
            translated_content = translate_text(original_content, target_lang)
        except Exception as e:
            print(f"[ANALYZE ERROR] Failed to translate post {post.post_id} content to {target_lang}: {e}")
            continue

        if show_before_after:
            print(f"Original Content:\n{original_content}\n")
            print(f"Translated Content:\n{translated_content}\n")

        post.translated_content = translated_content
        session.commit()
    
    close_session()
        
    print(f"Translated {len(posts)} posts to {target_lang}.")


def get_unprocessed_posts(session, flags: dict, query) -> Query:
    if flags.get("sentiment") or flags.get("priority_score"):
        query = query.outerjoin(Analysis, Post.post_id == Analysis.post_id)
    if flags.get("embedding"):
        query = query.outerjoin(Embedding, Post.post_id == Embedding.post_id)

    filters = []

    if flags.get("lang_detect"):
        filters.append(Post.language == None)

    if flags.get("translate"):
        filters.append(or_(Post.translated_content == None, Post.language != "en"))

    if flags.get("sentiment"):
        filters.append(or_(Analysis.post_id == None, Analysis.sentiment_label == None))

    if flags.get("priority_score"):
        filters.append(or_(Analysis.post_id == None, Analysis.priority_score == None))
    
    if flags.get("embedding"):
        filters.append(or_(Embedding.post_id == None, Embedding.embedding == None))

    if filters:
        query = query.filter(or_(*filters))

    return query.distinct()