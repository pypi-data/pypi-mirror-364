import os
from typing import List, Tuple
from typing import Optional
from datetime import datetime
import json
import re
from datetime import datetime, timedelta


from database.db_models import Post, Analysis, Embedding, Platform, Tag, PostTag, Alert

from intelligence.sentiment import project_to_01_range

from cli.context import get_context

DEFAULT_TOXIC_KEYWORDS_PATH = "resources/toxic_keywords.txt"
DEFAULT_SPAM_PATTERNS_PATH = "resources/spam_patterns.json"
DEFAULT_SCAM_PATTERNS_PATH = "resources/scam_patterns.json"



def load_keywords_txt(filepath: str) -> set:
    """Load toxic keywords from a text file.

    Args:
        filepath (str): Path to the keywords file.

    Returns:
        set: A set of toxic keywords.
    """
    if not os.path.exists(filepath):
        print(f"[Error] Toxic keywords file not found: {filepath}")
        return set()
    
    # get context and build path if needed
    context = get_context()
    if not os.path.isabs(filepath):
        filepath = context["workspace"] / filepath
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except Exception as e:
        print(f"[Error] Failed to load toxic keywords: {e}")
        return set()
    
def load_keywords_json(filepath: str) -> dict:
    """Load keywords from a JSON file.

    Args:
        filepath (str): Path to the keywords JSON file.

    Returns:
        dict: A dictionary of keywords.
    """
    if not os.path.exists(filepath):
        print(f"[Error] Toxic keywords JSON file not found: {filepath}")
        return {}
    
    # get context and build path if needed
    context = get_context()
    if not os.path.isabs(filepath):
        filepath = context["workspace"] / filepath

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to load keywords JSON: {e}")
        return {}
  
  
# toxic
def detect_toxic(session, sentiment_threshold: float = 0.8, platform: Optional[list[str]] = None, 
                since: Optional[str] = None, until: Optional[str] = None, toxic_keywords_file: Optional[str] = None) -> list[tuple[Post, str]]:
    """Detect if a post is toxic based on its content.

    Args:
        session (sqlalchemy.orm.Session): The database session.
        sentiment_threshold (float): The threshold above which the sentiment is considered toxic. Default is 0.8.

    Returns:
        list[tuple[Post, str]]: A list of tuples containing the post and its reason
    """

    # retrieve posts and their analysis for sentiment_label is negaive and sentiment_score is above threshold
    posts_analysis_query = session.query(Post, Analysis).join(Analysis).filter(
        Analysis.sentiment_label == "negative",
        Analysis.sentiment_score >= sentiment_threshold
    )
    
    if platform:
        platform_ids = session.query(Platform.platform_id).filter(Platform.name.in_(platform)).all()
        if not platform_ids:
            print(f"[Error] Invalid platforms found for names: {platform}")
            return []

        platform_ids = [p.platform_id for p in platform_ids]
        posts_analysis_query = posts_analysis_query.filter(Post.platform_id.in_(platform_ids))

    if since:
        try:
            since_date = datetime.strptime(since, "%Y-%m-%d")
            posts_analysis_query = posts_analysis_query.filter(Post.timestamp >= since_date)
        except ValueError:
            print(f"[Error] Invalid date format for 'since': {since}")

    if until:
        try:
            until_date = datetime.strptime(until, "%Y-%m-%d")
            posts_analysis_query = posts_analysis_query.filter(Post.timestamp <= until_date)
        except ValueError:
            print(f"[Error] Invalid date format for 'until': {until}")
            
    posts_analysis = posts_analysis_query.all()

    if toxic_keywords_file:
        try:
            toxic_keywords = load_keywords_txt(toxic_keywords_file)
        except Exception as e:
            print(f"[Error] Failed to load toxic keywords from {toxic_keywords_file}: {e}")
            toxic_keywords = set()
    else:
        toxic_keywords = load_keywords_txt(DEFAULT_TOXIC_KEYWORDS_PATH)

    toxic_posts = []
    for post, analysis in posts_analysis:
        is_toxic, reason = check_if_toxic(post, analysis, toxic_keywords, sentiment_threshold)
        if is_toxic:
            toxic_posts.append((post, reason))
    
    return toxic_posts


def check_if_toxic(post: Post, analysis: Analysis, toxic_keywords: set, sentiment_threshold: float) -> tuple[bool, str]:
    """Check if a post is toxic.

    Args:
        post (Post): The post to check.
        analysis (Analysis): The analysis object containing sentiment and other data.
        toxic_keywords (set): A set of toxic keywords.
        sentiment_threshold (float): The threshold above which the sentiment is considered toxic.

    Returns:
        tuple[bool, str]: A tuple containing whether the post is toxic and the reason.
    """
    _content = post.content.lower() if not post.translated_content else post.translated_content.lower()
    
    # sentiment part
    if analysis.sentiment_label != "negative" or analysis.sentiment_score < sentiment_threshold:
        return False, "sentiment_label_not_negative"
    
    # toxic keywords part
    if any(keyword in _content for keyword in toxic_keywords):
        return True, "toxic_keyword"
    
    return False, "not_toxic"

# spam
def detect_spam(session, spam_file: Optional[str] = None, auto_flag: bool = False) -> list[tuple[Post, str]]:
    """Detect spam posts based on predefined criteria.
    Args:
        session (sqlalchemy.orm.Session): The database session.
        spam_file (Optional[str]): Path to the spam keywords file. If None, uses default.
        auto_flag (bool): If True, automatically flags posts as spam.
        
    Returns:
        list[tuple[Post, str]]: A list of tuples containing the post and its reason for being spam.
    """
    # check if a spam tag exists, if not create it
    spam_tag = session.query(Tag).filter(Tag.name == "spam").first()
    if not spam_tag:
        spam_tag = Tag(name="spam")
        session.add(spam_tag)
        session.commit()
        
    spam_tag_id = spam_tag.tag_id
    
    post_queries = session.query(Post)
    if spam_file:
        try:
            spam_keywords = load_keywords_json(spam_file)
        except Exception as e:
            print(f"[Error] Failed to load spam keywords from {spam_file}: {e}")
            spam_keywords = {}
    else:
        spam_keywords = load_keywords_json(DEFAULT_SPAM_PATTERNS_PATH)
        
    # retrireve regex patterns from the spam_keywords
    spam_patterns = {}
    if "regex_patterns" in spam_keywords:
        regex_patterns = spam_keywords["regex_patterns"]
        # compile regex patterns
        for key, pattern in regex_patterns.items():
            try:
                spam_patterns[key] = re.compile(pattern)
            except re.error as e:
                print(f"[Error] Invalid regex pattern for {key}: {pattern} - {e}")
        
        spam_keywords = {k: v for k, v in spam_keywords.items() if k != "regex_patterns"}
        
    posts = post_queries.all()
    spam_posts = []
    for post in posts:
        is_spam, reason = check_if_spam(post, spam_keywords, spam_patterns)
        if is_spam:
            if auto_flag:
                # add spam tag to postTag table
                post_tag = PostTag(post_id=post.post_id, tag_id=spam_tag_id)
                session.add(post_tag)
                session.commit()
            spam_posts.append((post, reason))
    
    return spam_posts
    
def check_if_spam(post: Post, spam_keywords: dict, spam_patterns: dict) -> tuple[bool, str]:
    """Check if a post is spam.

    Args:
        post (Post): The post to check.

    Returns:
        bool: True if the post is spam, False otherwise.
        str: The reason for the spam classification.
    """
    _content = post.content.lower() if not post.translated_content else post.translated_content.lower()
    for reason, keywords in spam_keywords.items():
        if any(keyword in _content for keyword in keywords):
            return True, reason
        
    # check regex patterns
    if spam_patterns:
        for reason, pattern in spam_patterns.items():
            if re.search(pattern, _content):
                return True, reason
        
    return False, "not_spam"




def detect_scam(session, scam_file: Optional[str] = None, alert_high_risk: Optional[bool] = False) -> list[list[Post, int, list[str]]]:
    """Detect scam posts based on predefined criteria.
    Score is in range 0 - 6, where we take 5 and 6 as high risk.

    Args:
        session (sqlalchemy.orm.Session): The database session.
        scam_file (Optional[str]): Path to the scam keywords file. If None, uses default.
        alert_high_risk (Optional[bool]): If True, alerts for high risk scams.

    Returns:
        list[tuple[Post, int, str]]: A list of tuples containing the post, its scam score, and the reason for the classification.
    """
    if scam_file:
        try:
            scam_all = load_keywords_json(scam_file)
        except Exception as e:
            print(f"[Error] Failed to load scam keywords from {scam_file}: {e}")
            scam_all = {}
    else:
        scam_all = load_keywords_json(DEFAULT_SCAM_PATTERNS_PATH)
        
    # retrieve regex patterns from the scam_keywords
    scam_patterns = {}
    if "regex_patterns" in scam_all:
        regex_patterns = scam_all["regex_patterns"]
        # compile regex patterns
        for key, pattern in regex_patterns.items():
            try:
                scam_patterns[key] = re.compile(pattern)
            except re.error as e:
                print(f"[Error] Invalid regex pattern for {key}: {pattern} - {e}")
        
    
    # retrieve suspicious domains from the scam_keywords
    suspicious_domain = []
    if "suspicious_domains" in scam_all:
        suspicious_domain = scam_all["suspicious_domains"]
        del scam_all["suspicious_domains"]
        
    # retrieve scam keywords from the scam_keywords
    scam_keywords = {}
    if "keywords" in scam_all:
        scam_keywords = scam_all["keywords"]

    posts = session.query(Post).all()
    scam_posts = []
    for post in posts:
        scam_score, reason = check_if_scam(post, scam_keywords, scam_patterns, suspicious_domain)
        if scam_score > 0:
            if alert_high_risk and scam_score >= 5:
                # alert high risk scam
                print(f"[ALERT ALERT ALERT] High risk scam detected: {post.post_id} | Reason: {reason}")
                alert = Alert(
                    post_id=post.post_id,
                    alert_type="scam",
                    alert_severity=4 if scam_score == 5 else 5,  # 4 for high risk, 5 for critical
                    note=reason
                )
                session.add(alert)
                session.commit()
            scam_posts.append((post, scam_score, reason))

    return scam_posts


def check_if_scam(post: Post, scam_keywords: dict, scam_patterns: dict, suspicious_domain: list) -> tuple[int, list[str]]:
    """check if a post is a scam.
    If three of them are true, it will be flagged as a high risk scam post.
    If two of them are true, it will be flagged as a medium risk scam post.
    If one of them is true, it will be flagged as a low risk scam post.

    Args:
        post (Post): The post to check.
        scam_keywords (dict): A dictionary of keywords associated with scams.
        scam_patterns (dict): A dictionary of regex patterns associated with scams.
        suspicious_domain (list): A list of suspicious domains.

    Returns:
        tuple[int, str]: A tuple containing an int indicating if the post is a scam and the reason for the classification.
        int values:
            0: not a scam
            1: likely not a scam
            2: very low risk scam
            3: low risk scam
            4: medium risk scam
            5: high risk scam
            6: critical scam
    """

    scam_score = 0
    reasons = []
    for level, keywords in scam_keywords.items():
        if level == "critical":
            if any(keyword in post.content.lower() for keyword in keywords):
                scam_score += 4
                reasons.append("critical_scam_keyword")
                break
        elif level == "high":
            if any(keyword in post.content.lower() for keyword in keywords):
                scam_score += 3
                reasons.append("high_scam_keyword")
                break
        elif level == "medium":
            if any(keyword in post.content.lower() for keyword in keywords):
                scam_score += 2
                reasons.append("medium_scam_keyword")
                break
        elif level == "low":
            if any(keyword in post.content.lower() for keyword in keywords):
                scam_score += 1
                reasons.append("low_scam_keyword")
                break

    if scam_patterns:
        for reason, pattern in scam_patterns.items():
            if re.search(pattern, post.content.lower()):
                scam_score += 1
                reasons.append("scam_pattern_detected")

    if any(domain in post.content.lower() for domain in suspicious_domain):
        scam_score += 1
        reasons.append("suspicious_domain_detected")

    return scam_score, reasons


# sentiment crisis
def detect_sentiment_crisis(session, threshold: Optional[float] = None, minimum_posts: Optional[int] = None, timeframe: Optional[str] = None) -> list[Post]:
    """Detect sentiment crisis based on the sentiment score of posts.

    Args:
        session (sqlalchemy.orm.Session): The database session.
        threshold (float): The threshold above which the sentiment is considered a crisis. Default is 0.8.
        minimum_posts (Optional[int]): Minimum number of posts to consider a sentiment crisis. Default is None.
        timeframe (Optional[str]): Timeframe to consider for the sentiment crisis, e.g., "7d", "30d". Default is None.

    Returns:
        list[Post]: A list of posts that are considered part of a sentiment crisis.
    """
    if threshold is None:
        print("[Warning] No threshold provided for sentiment crisis detection. Using default threshold of 0.8.")
        threshold = 0.8
        
        
    query = session.query(Post).join(Analysis).filter(
        Analysis.sentiment_score >= threshold,
        Analysis.sentiment_label == "negative"
    )
    
    if timeframe:
        # assume timeframe is in format of xd or xh where x is a number
        try:
            if timeframe.endswith("d"):
                days = int(timeframe[:-1])
                query = query.filter(Post.timestamp >= datetime.now() - timedelta(days=days))
            elif timeframe.endswith("h"):
                hours = int(timeframe[:-1])
                query = query.filter(Post.timestamp >= datetime.now() - timedelta(hours=hours))
            else:
                print(f"[Error] Invalid timeframe format: {timeframe}. Expected format is 'xd' or 'xh'.")
        except ValueError:
            # shouldn't happen
            print(f"[Error] Invalid timeframe value: {timeframe}. Expected a number followed by 'd' or 'h'.")
    
    posts = query.all()
    if len(posts) < minimum_posts:
        print(f"Not enough posts found for sentiment crisis detection. Minimum required: {minimum_posts}, found: {len(posts)}.")
        return []
    
    # sort by timestamp to get the most recent posts first
    posts.sort(key=lambda x: x.timestamp, reverse=True)
    
    return posts



def detect_trend_alerts(session, sentiment_drop: Optional[float] = None, volume_spike: Optional[float] = None, timeframe: Optional[str] = None) -> dict:
    """Detect trend alerts based on sentiment drop and volume spike.

    Args:
        session (sqlalchemy.orm.Session): The database session.
        sentiment_drop (Optional[float]): The threshold for sentiment drop to trigger an alert. Default is None.
        volume_spike (Optional[float]): The threshold for volume spike to trigger an alert. Default is None.
        timeframe (Optional[str]): Timeframe to consider for the trend alert, e.g., "7d", "30d". Default is None.

    Returns:
        dict: A dictionary containing the posts and alerts detected.
            - "posts": The list of posts that triggered the alerts.
            - "alerts": A tuple of alert and description.
    """
    if sentiment_drop is None:
        print("[Warning] No sentiment drop threshold provided for trend alert detection. Using default threshold of 0.2.")
        sentiment_drop = 0.3
        
    if volume_spike is None:
        print("[Warning] No volume spike threshold provided for trend alert detection. Using default threshold of 1.5.")
        volume_spike = 2.0
        
    curr_query = session.query(Post, Analysis).join(Analysis)
    previous_query = session.query(Post, Analysis).join(Analysis)
    
    if not timeframe:
        print("[Warning] No timeframe provided for trend alert detection. Using default timeframe of 24 hours.")
        timeframe = "24h"
    
    if timeframe:
        # assume timeframe is in format of xd or xh where x is a number
        try:
            if timeframe.endswith("d"):
                days = int(timeframe[:-1])
                curr_query = curr_query.filter(Post.timestamp >= datetime.now() - timedelta(days=days))
                previous_query = previous_query.filter(Post.timestamp >= datetime.now() - timedelta(days=days * 2),
                                                       Post.timestamp < datetime.now() - timedelta(days=days))
            elif timeframe.endswith("h"):
                hours = int(timeframe[:-1])
                curr_query = curr_query.filter(Post.timestamp >= datetime.now() - timedelta(hours=hours))
                previous_query = previous_query.filter(Post.timestamp >= datetime.now() - timedelta(hours=hours * 2), 
                                                       Post.timestamp < datetime.now() - timedelta(hours=hours))
            else:
                print(f"[Error] Invalid timeframe format: {timeframe}. Expected format is 'xd' or 'xh'.")
        except ValueError:
            print(f"[Error] Invalid timeframe value: {timeframe}. Expected a number followed by 'd' or 'h'.")
    

    # compare sentiment drop
    curr_posts_analysis = curr_query.all()
    previous_posts_analysis = previous_query.all()

    print("DEBUG - Current Posts Analysis Count:", len(curr_posts_analysis), "Previous Posts Analysis Count:", len(previous_posts_analysis))
    print(f"DEBUG - Current {[post.post_id for post, analysis in curr_posts_analysis]}")
    print(f"DEBUG - Previous {[post.post_id for post, analysis in previous_posts_analysis]}")

    if len(curr_posts_analysis) == 0 or len(previous_posts_analysis) == 0:
        print("[Warning] No posts found for the given timeframe. Cannot detect trend alerts.")
        return {"posts": [], "alerts": []}
    
    # calculate using project_to_01_range
    curr_average = sum(project_to_01_range(analysis.sentiment_label, analysis.sentiment_score) for post, analysis in curr_posts_analysis) / len(curr_posts_analysis)
    previous_average = sum(project_to_01_range(analysis.sentiment_label, analysis.sentiment_score) for post, analysis in previous_posts_analysis) / len(previous_posts_analysis)
    
    print(f"DEBUG - Current Average Sentiment: {curr_average:.2f}, Previous Average Sentiment: {previous_average:.2f}")
    
    alerts = []
    if curr_average < previous_average - sentiment_drop:
        alerts.append(("sentiment drop", f"Current average sentiment is {curr_average:.2f}, previous average was {previous_average:.2f}."))
        
    # compare volume spike
    curr_volume = len(curr_posts_analysis)
    previous_volume = len(previous_posts_analysis)
    if float(curr_volume) >= previous_volume * volume_spike:
        alerts.append(("volume spike", f"Current volume is {curr_volume}, previous volume was {previous_volume}."))
        

    # sort posts by timestamp to get the most recent posts first
    curr_posts_analysis.sort(key=lambda x: x[0].timestamp, reverse=True)

    return {
        "posts": curr_posts_analysis,
        "alerts": alerts
    }
    
    
def detect_review_bombing(session, negative_ratio_threshold: Optional[float] = None, minimum_posts: Optional[int] = None, volume_spike_threshold: Optional[float] = None,
                          timeframe: Optional[str] = None, platform: Optional[list[str]] = None) -> tuple[bool, list[Post]]:
    """Detect review bombing based on the sentiment score of posts.

    Args:
        session (sqlalchemy.orm.Session): The database session.
        threshold (float): The threshold above which the sentiment is considered a review bomb.
        minimum_posts (Optional[int]): Minimum number of posts to consider a review bombing. Default is None.
        timeframe (Optional[str]): Timeframe to consider for the review bombing, e.g., "7d", "30d". Default is None.

    Returns:
        tuple[bool, list[Post]]: A tuple containing a boolean indicating if review bombing is detected and a list of posts that are considered part of the review bombing.
    """
    if negative_ratio_threshold is None:
        print("[Warning] No threshold provided for review bombing detection. Using default threshold of 2.5.")
        negative_ratio_threshold = 2.5
        
    if volume_spike_threshold is None:
        print("[Warning] No volume spike threshold provided for review bombing detection. Using default threshold of 1.5.")
        volume_spike_threshold = 1.5
        
    current_query = session.query(Post, Analysis).join(Analysis)
    previous_query = session.query(Post, Analysis).join(Analysis) # calculate 10 times the timeframe
    
    if not timeframe:
        print("[Warning] No timeframe provided for review bombing detection. Using default timeframe of 6 hours.")
        timeframe = "6h"
      
    platform_ids = []  
    if platform:
        platform_ids = session.query(Platform.platform_id).filter(Platform.name.in_(platform)).all()
        if not platform_ids:
            print(f"[Error] Invalid platforms found for names: {platform}")
            return False, []
        
        platform_ids = [p.platform_id for p in platform_ids]
        current_query = current_query.filter(Post.platform_id.in_(platform_ids))
        previous_query = previous_query.filter(Post.platform_id.in_(platform_ids))
        
    if timeframe:
        # assume timeframe is in format of xd or xh where x is a number
        try:
            if timeframe.endswith("d"):
                days = int(timeframe[:-1])
                current_query = current_query.filter(Post.timestamp >= datetime.now() - timedelta(days=days))
                previous_query = previous_query.filter(Post.timestamp >= datetime.now() - timedelta(days=days * 10),
                                                       Post.timestamp < datetime.now() - timedelta(days=days))
            elif timeframe.endswith("h"):
                hours = int(timeframe[:-1])
                current_query = current_query.filter(Post.timestamp >= datetime.now() - timedelta(hours=hours))
                previous_query = previous_query.filter(Post.timestamp >= datetime.now() - timedelta(hours=hours * 10), 
                                                       Post.timestamp < datetime.now() - timedelta(hours=hours))
            else:
                print(f"[Error] Invalid timeframe format: {timeframe}. Expected format is 'xd' or 'xh'.")
        except ValueError:
            print(f"[Error] Invalid timeframe value: {timeframe}. Expected a number followed by 'd' or 'h'.")
            
            
    current_posts_analysis = current_query.all()
    previous_posts_analysis = previous_query.all()
    
    print("DEBUG - Current Posts Analysis Count:", len(current_posts_analysis), "Previous Posts Analysis Count:", len(previous_posts_analysis))
    print(f"DEBUG - Current {[post.post_id for post, analysis in current_posts_analysis]}")
    print(f"DEBUG - Previous {[post.post_id for post, analysis in previous_posts_analysis]}")

    if len(current_posts_analysis) == 0 or len(previous_posts_analysis) == 0:
        print("[Warning] No posts found for the given timeframe. Cannot detect review bombing.")
        return False, []
    

    # check minimum posts
    if len(current_posts_analysis) < minimum_posts:
        print(f"[Warning] Not enough posts found for review bombing detection. Minimum required: {minimum_posts}, found: {len(current_posts_analysis)}.")
        return False, []

    # check current has a volume spikes
    if len(current_posts_analysis) <= volume_spike_threshold * len(previous_posts_analysis) / 10: # average posts number in previous window
        print(f"[Warning] Current posts volume is not enough to detect review bombing. Current: {len(current_posts_analysis)}, Previous: {len(previous_posts_analysis)}.")
        return False, []

    # calculate negative posts ratio in current window and previous window
    current_negative_count = sum(1 for post, analysis in current_posts_analysis if analysis.sentiment_label == "negative")
    previous_negative_count = sum(1 for post, analysis in previous_posts_analysis if analysis.sentiment_label == "negative")
    
    current_negative_ratio = current_negative_count / len(current_posts_analysis) if current_posts_analysis else 0
    previous_negative_ratio = previous_negative_count / len(previous_posts_analysis) if previous_posts_analysis else 0
    
    result = False
    return_posts = []
    # use 0.1 to avoid too less negative posts in previous window leading to false positive
    if current_negative_ratio >= negative_ratio_threshold * max(0.1, previous_negative_ratio): 
        result = True
        print(f"[ALERT] Review bombing detected! Current negative ratio: {current_negative_ratio:.2f}, Previous negative ratio: {previous_negative_ratio:.2f}.")
        return_posts = [post for post, analysis in current_posts_analysis if analysis.sentiment_label == "negative"]
    
    return result, return_posts