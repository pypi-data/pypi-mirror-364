from datetime import datetime, timezone
from sqlalchemy import func

from intelligence.intelligence_config import IntelligenceConfig
from intelligence.sentiment import project_to_01_range


from database.db_session import get_session, close_session
from database.db_models import Post, Analysis, Author, Platform

FACTORS = ["sentiment", "engagement", "critical_keywords", "recency", "author"]



def get_priority_score(post_id: int) -> list[int]:
    """Calculate the priority score for a post based on its sentiment and language confidence.

    Args:
        post_id (int): The ID of the post to analyze.

    Returns:
        list[float]: A list containing the priority score, and the score of each of the factors
        (sentiment, engagement, critical keywords, recency, author)
    """
    sentiment_score = 0 # 0 - 30
    engagement_score = 0 # 0 - 25
    critical_keywords_score = 0 # 0 -20
    recency_score = 0 # 0 - 15
    author_score = 0 # 0 - 10

    # get post object and analysis object and platform name from database
    session = get_session()
    post = session.query(Post).filter(Post.post_id == post_id).first()
    analysis = session.query(Analysis).filter(Analysis.post_id == post_id).first()
    platform_name = session.query(Platform.name).filter(Platform.platform_id == post.platform_id).first()[0]
    close_session()
    
    if not post:
        print(f"[Priority Score Error] Post with ID {post_id} not found.")
        return [0, 0, 0, 0, 0, 0]
    if not analysis:
        print(f"[Priority Score Error] Analysis for post ID {post_id} not found.")
        return [0, 0, 0, 0, 0, 0]
    if not platform_name:
        print(f"[Priority Score Error] Platform for post ID {post_id} not found.")
        return [0, 0, 0, 0, 0, 0]
    try:
        scores = get_priority_score_from_post_analysis(post, analysis, platform_name)
    except Exception as e:
        print(f"[Priority Score Error] Failed to calculate priority score for post ID {post_id}: {e}")
        return [0, 0, 0, 0, 0, 0]

    total_score = scores[0]
    write_priority_score(session, post_id, total_score)

    return [total_score, scores[1], scores[2], scores[3], scores[4], scores[5]]


def get_priority_score_from_post_analysis(post: Post, analysis: Analysis, platform_name: str) -> list[int]:
    """Get the priority score and its factors from the post and its analysis.

    Args:
        post (Post): The post object.
        analysis (Analysis): The analysis object.
        platform_name (str): The name of the platform the post was made on.

    Returns:
        list[int]: A list containing the priority score and its factors.
    """
    sentiment_score = 0 # 0 - 30
    engagement_score = 0 # 0 - 25
    critical_keywords_score = 0 # 0 -20
    recency_score = 0 # 0 - 15
    author_score = 0 # 0 - 10

    
    if not post:
        print(f"[Priority Score Error] Invalid post object for priority score calculation.")
        return [0, 0, 0, 0, 0, 0]
    if not analysis:
        print(f"[Priority Score Error] Invalid analysis object for priority score calculation.")
        return [0, 0, 0, 0, 0, 0]

    try:
        sentiment_score = get_sentiment_score(analysis)
    except Exception as e:
        print(f"[Priority Score Error] Failed to calculate sentiment score for post ID {post.post_id}: {e}")
        sentiment_score = 0
        
    try:
        engagement_score = get_engagement_score(platform_name, post)
    except Exception as e:
        print(f"[Priority Score Error] Failed to calculate engagement score for post ID {post.post_id}: {e}")
        engagement_score = 0
    
    try:
        critical_keywords_score = get_critical_keywords_score(post)
    except Exception as e:
        print(f"[Priority Score Error] Failed to calculate critical keywords score for post ID {post.post_id}: {e}")
        critical_keywords_score = 0

    try:
        recency_score = get_recency_score(post)
    except Exception as e:
        print(f"[Priority Score Error] Failed to calculate recency score for post ID {post.post_id}: {e}")
        recency_score = 0

    try:
        author_score = get_author_score(post)
    except Exception as e:
        print(f"[Priority Score Error] Failed to calculate author score for post ID {post.post_id}: {e}")
        author_score = 0

    total_score = sentiment_score + engagement_score + critical_keywords_score + recency_score + author_score # 0 - 100
    return [total_score, sentiment_score, engagement_score, critical_keywords_score, recency_score, author_score]


def write_priority_score(session, post_id: int, score: float) -> None:
    """Write the priority score to the database for a specific post.

    Args:
        session: The database session.
        post_id (int): The ID of the post.
        score (float): The priority score to write.
    """
    try:
        analysis = session.query(Analysis).filter(Analysis.post_id == post_id).first()
        if not analysis:
            print(f"[Priority Score Error] Analysis for post ID {post_id} not found.")
            return

        analysis.priority_score = score
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"[Priority Score Error] Failed to write priority score for post ID {post_id}: {e}")

def get_sentiment_score(analysis: Analysis) -> int:
    """Calculate the sentiment score for a post based on its analysis.

    Args:
        analysis (Analysis): The analysis object containing sentiment and confidence.

    Returns:
        int: The sentiment score based on the sentiment label and confidence.
        
    Raises:
        ValueError: If the analysis data is invalid or if the sentiment score is negative.
    """
    if not analysis or not analysis.sentiment_label or analysis.sentiment_score < 0:
        raise ValueError("Invalid analysis data")

    return get_sentiment_score_from_data(analysis.sentiment_label, analysis.sentiment_score)

def get_sentiment_score_from_data(sentiment: str, confidence: float) -> int:
    """Calculate the sentiment score for a post.

    Args:
        sentiment (str): The sentiment label (e.g., "positive", "neutral", "negative").
        confidence (float): The confidence level of the sentiment (0 to 1).

    Returns:
        int: The sentiment score based on the sentiment label and confidence.
    """
    projected_sentiment_factor = project_to_01_range(sentiment, confidence)
    if projected_sentiment_factor < 0 or projected_sentiment_factor > 1:
        print(f"[Priority Score Error] Invalid sentiment factor: {projected_sentiment_factor} for sentiment '{sentiment}' with confidence {confidence}.")
        return 0
    if projected_sentiment_factor < 0.2:
        return 30
    elif projected_sentiment_factor < 0.4:
        return 20
    elif projected_sentiment_factor < 0.6:
        return 5
    elif projected_sentiment_factor < 0.8:
        return 10
    else:
        return 25
    


# engagement score
def get_engagement_score(platform: str, post: Post) -> int:
    """Calculate the engagement score for a post.

    Args:
        platform (str): The platform where the post is made (e.g., "reddit", "steam", "discord").
        post (Post): The post object containing engagement metrics.

    Returns:
        int: The engagement score based on the platform and engagement metric.
        
    Raises:
        ValueError: If the post data is invalid or if the platform is unsupported.
    """
    if platform == "reddit":
        if post.upvotes >= 50 or post.replies >= 20:
            return 25
        elif post.upvotes >= 10 or post.replies >= 5:
            return 15
        else:
            return 5
    elif platform == "steam" and post.post_type == "steam_review":
        # votes helpful is recorded as upvotes in Post table in the database
        if post.upvotes >= 100:
            return 25
        elif post.upvotes >= 20:
            return 15
        else:
            return 5
    elif platform == "steam" and post.post_type == "steam_discussion_thread":
        if post.upvotes >= 100:
            return 25
        elif post.upvotes >= 20:
            return 15
        else:
            return 5
    elif platform == "steam" and post.post_type == "steam_discussion_comment":
        # there is no metrics for discussion comments, so we return 0
        return 0
    elif platform == "discord":
        # based on reactions, pinned, and mentions
        if post.replies > 10 or post.post_metadata.get("pinned", False) or len(post.post_metadata.get("mentions", [])) > 3:
            return 25
        elif post.replies > 5 or len(post.post_metadata.get("mentions", [])) > 1:
            return 15
        else:
            return 5
    else:
        raise ValueError("Unsupported platform")



# critical_keywords score
def get_critical_keywords_score(post: Post) -> int:
    """Calculate the critical keywords score for a post.

    Args:
        post (Post): The post object containing content and metadata.

    Returns:
        int: The critical keywords score based on the presence of critical keywords.
        
    Raises:
        ValueError: If the post data is invalid or if the content is empty.
    """
    if not post or not post.content:
        raise ValueError("Invalid post data")

    # check if content has translation
    if post.translated_content:
        return get_critical_keywords_score_from_content(post.translated_content)
    else:
        return get_critical_keywords_score_from_content(post.content)
    
def get_critical_keywords_score_from_content(content: str) -> int:
    """Calculate the critical keywords score based on the content of a post.

    Args:
        content (str): The content of the post.

    Returns:
        int: The critical keywords score based on the presence of critical keywords. Maximum 20
    """
    CRITICAL = ["crash", "bug", "broken", "not working", "refund", "unplayable"] # 20 each
    HIGH_PRIORITY = ["performance", "lag", "slow", "glitch", "error", "problem"] # 15 each
    MEDIUM_PRIORITY = ["suggestion", "feature", "improvement", "feedback"] # 10 each
    LOW_PRIORITY = ["love", "amazing", "perfect", "brilliant", "masterpiece"] # 5 each
     
    content = content.lower()
    score = 0
    
    # parse content into words
    content = content.replace(",", " ").replace(".", " ").replace("!", " ").replace("?", " ").replace(";", " ")\
                        .replace(":", " ").replace("-", " ").replace("_", " ").replace("(", " ").replace(")", " ")\
                        .replace("[", " ").replace("]", " ").replace("{", " ").replace("}", " ").replace('"', " ")\
                        .replace("'", " ").replace("/", " ").replace("\\", " ").replace("|", " ").replace("`", " ")\
                        .replace("+", " ").replace("\n", " ").replace("\r", " ").replace("\t", " ")

    for word in content.split():
        if word in CRITICAL:
            score += 20
        elif word in HIGH_PRIORITY:
            score += 15
        elif word in MEDIUM_PRIORITY:
            score += 10
        elif word in LOW_PRIORITY:
            score += 5

    return min(score, 20)



# recency score
def get_recency_score(post: Post) -> int:
    """Calculate the recency score for a post.

    Args:
        post (Post): The post object containing metadata.

    Returns:
        int: The recency score based on the age of the post.
        
    Raises:
        ValueError: If the post data is invalid or if the timestamp is not a datetime object
    """
    if not post or not post.timestamp:
        raise ValueError("Invalid post data")
    return get_recency_score_from_timestamp(post.timestamp)

def get_recency_score_from_timestamp(timestamp: datetime) -> int:
    """Calculate the recency score based on the timestamp of the post.

    Args:
        timestamp (datetime): The timestamp of the post.

    Returns:
        int: The recency score based on the age of the post.
    """
    if not timestamp:
        print(f"[Priority Score Error] Invalid timestamp.")
        return 0
    
    # check if timestamp is a datetime object or in datetime string format
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            print(f"[Priority Score Error] Invalid timestamp format: {timestamp}.")
            return 0
    elif not isinstance(timestamp, datetime):
        print(f"[Priority Score Error] Timestamp is not a datetime object: {timestamp}.")
        return 0

    # Calculate the age of the post in hours
    post_age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600


    if post_age_hours < 6:
        return 15
    elif post_age_hours < 24:
        return 12
    elif post_age_hours < 72:
        return 8
    elif post_age_hours < 168:
        return 4
    elif post_age_hours < 672:
        return 2
    else:
        return 0 # older than a month, no score
    
    

# author score
def get_author_score(post: Post) -> int:
    """Calculate the author score for a post.

    Args:
        post (Post): The post object containing metadata.

    Returns:
        int: The author score based on the author's post history.
        
    Raises:
        ValueError: If the post data is invalid or if the author_id is not set.
    """
    # use author_id to get data from database
    if not post or not post.author_id:
        raise ValueError("Invalid post data")
    session = get_session()
    author_stats = get_author_post_stats(session, post.author_id)
    close_session()
    count, avg_engagement = author_stats
    if count >= 100 or avg_engagement >= 20:
        return 10
    elif count >= 20 or avg_engagement >= 5:
        return 6
    elif count >= 5 or avg_engagement >= 1:
        return 3
    else:
        return 1
    
def get_author_post_stats(session, author_id: int) -> tuple[int, float]:
    """Get the post statistics for a specific author.

    Args:
        session (_type_): The database session.
        author_id (int): The ID of the author.

    Returns:
        tuple[int, float]: A tuple containing the post count and average engagement.
    """
    try:
        result = session.query(
            func.count(Post.post_id),
            func.avg(
                func.coalesce(Post.upvotes, 0) + func.coalesce(Post.replies, 0)
            )
        ).filter(Post.author_id == author_id).one()

        count, avg_engagement = result
        return count, avg_engagement or 0
    except Exception as e:
        print(f"[Priority Score Error] Failed to get author stats for author ID {author_id}: {e}")
        return 0, 0.0
    
    
