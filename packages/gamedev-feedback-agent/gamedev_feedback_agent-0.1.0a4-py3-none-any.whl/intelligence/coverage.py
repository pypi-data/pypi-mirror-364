from intelligence.intelligence_config import IntelligenceConfig

from database.db_models import Post, Analysis, Embedding, Platform
from database.db_session import get_session, close_session

from sqlalchemy import and_
from typing import Optional, List

from datetime import datetime





def get_coverage_summary(session, platforms: Optional[List[str]] = None,
                         since: Optional[datetime] = None,
                         until: Optional[datetime] = None) -> dict:
    """Get coverage summary for posts.

    Args:
        session (sqlalchemy.orm.Session): The database session.
        platforms (Optional[List[str]], optional): The platforms to filter by. Defaults to None.
        since (Optional[datetime], optional): The start date for filtering posts. Defaults to None.
        until (Optional[datetime], optional): The end date for filtering posts. Defaults to None.

    Returns:
        dict: A summary of coverage across posts.
    """

    # Build base query
    query = session.query(Post)

    if platforms:
        # filter by platform id queried from the Platform table
        platform_ids = session.query(Platform.platform_id).filter(Platform.name.in_(platforms))
        query = query.filter(Post.platform_id.in_(platform_ids))

    if since:
        query = query.filter(Post.timestamp >= since)

    if until:
        query = query.filter(Post.timestamp <= until)

    posts = query.all()
    total = len(posts)
    post_ids = [p.post_id for p in posts]
    
    # get language detection coverage
    missing_language_detection = []
    for post in posts:
        if not post.language:
            missing_language_detection.append(post.post_id)
            
    # get translation coverage
    missing_translation = []
    for post in posts:
        if post.language != IntelligenceConfig.DEFAULT_LANGUAGE and not post.translated_content:
            missing_translation.append(post.post_id)
            
    
    # get sentiment analysis coverage
    # query the Analysis table for posts that have been analyzed
    valid_sentiment_query = (
        session.query(Analysis.post_id)
        .filter(
            and_(
                Analysis.post_id.in_(post_ids),
                Analysis.sentiment_label.isnot(None),
                Analysis.sentiment_label != "unknown"
            )
        )
    )
    valid_post_analysis = valid_sentiment_query.all()
    valid_post_analysis = [a.post_id for a in valid_post_analysis]
    # get post ids that are not in the valid sentiment query
    missing_sentiment = [p.post_id for p in posts if p.post_id not in valid_post_analysis]
    
    
    # get priority coverage
    valid_priority_query = (
        session.query(Analysis.post_id)
        .filter(
            and_(
                Analysis.post_id.in_(post_ids),
                Analysis.priority_score.isnot(None)
            )
        )
    )
    valid_post_priority = valid_priority_query.all()
    valid_post_priority = [a.post_id for a in valid_post_priority]
    # get post ids that are not in the valid priority query
    missing_priority = [p.post_id for p in posts if p.post_id not in valid_post_priority]
    
    
    # get embedding coverage
    # there are two types of embeddings, 1536 from openai and 768 from ollama
    valid_embedding_query = (
        session.query(Embedding.post_id, Embedding.embedding)
        .filter(
            and_(
                Embedding.post_id.in_(post_ids),
                Embedding.embedding.isnot(None)
            )
        )
    )
    valid_embedding = valid_embedding_query.all()
    valid_1536_embedding = [e.post_id for e in valid_embedding if len(e.embedding) == 1536]
    valid_768_embedding = [e.post_id for e in valid_embedding if len(e.embedding) == 768]
    missing_1536_embedding = [p.post_id for p in posts if p.post_id not in valid_1536_embedding]
    missing_768_embedding = [p.post_id for p in posts if p.post_id not in valid_768_embedding]
    
    # combine all missing posts into a single list
    
    missing_posts = missing_language_detection + missing_translation + missing_sentiment + missing_priority
    # only add the currently using embedding model
    if IntelligenceConfig.EMBEDDING_PROVIDER == "openai":
        missing_posts += missing_1536_embedding
    elif IntelligenceConfig.EMBEDDING_PROVIDER == "ollama":
        missing_posts += missing_768_embedding
    missing_posts = list(set(missing_posts))  # remove duplicates

    return {
        "total_post_count": total,
        "missing_posts": missing_posts,
        "missing_language_detection": missing_language_detection,
        "missing_translation": missing_translation,
        "missing_sentiment": missing_sentiment,
        "missing_priority": missing_priority,
        "missing_1536_embedding": missing_1536_embedding if len(missing_1536_embedding) < total else "no embeddings in 1536 dimension",
        "missing_768_embedding": missing_768_embedding if len(missing_768_embedding) < total else "no embeddings in 768 dimension",
    }