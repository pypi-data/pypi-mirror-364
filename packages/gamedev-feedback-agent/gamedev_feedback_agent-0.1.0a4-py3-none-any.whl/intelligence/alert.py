import json
import os
from typing import Optional
from datetime import datetime, timedelta

from database.db_models import Post, Analysis, Embedding, Alert, Platform
from database.db_session import get_session, close_session

from intelligence.safety import detect_toxic, detect_spam, detect_scam, detect_sentiment_crisis, detect_trend_alerts, detect_review_bombing

from cli.context import get_context

ALERT_CONFIG_PATH = "resources/alert_config.json"
DEFAULT_ALERT_CONFIG = {
    "toxic_threshold": 0.8,
    "sentiment_crisis_threshold": 0.8,
    "sentiment_crisis_minimum_posts": 50,
    "sentiment_crisis_timeframe": "24h",
    "sentiment_alert_drop" : 0.3,
    "sentiment_alert_volume_spike_threshold": 2.0,
    "sentiment_alert_timeframe": "24h",
    "review_bombing_negative_ratio_threshold": 2.5,
    "review_bombing_volume_spike_threshold": 1.5,
    "review_bombing_minimum_posts": 50,
    "review_bombing_timeframe": "6h"
}

def load_alert_config(path: str = ALERT_CONFIG_PATH) -> dict | None:
    """
    Load alert configuration from a JSON file.
    
    Args:
        path (str): The file path to the JSON configuration file.

    Returns:
        dict: The alert configuration settings.
    """
    context = get_context()
    if not os.path.isabs(path):
        path = context["workspace"] / path
    
    try:
        with open(path, "r") as file:
            config = json.load(file)
        return config
    except Exception as e:
        return None
        

def change_alert_config(path: str = ALERT_CONFIG_PATH, **kwargs) -> bool:
    """
    Change alert configuration settings and save to a JSON file.
    
    Args:
        path (str): The file path to the JSON configuration file.
        **kwargs: Key-value pairs of configuration settings to update.
    """
    context = get_context()
    if not os.path.isabs(path):
        path = context["workspace"] / path
    
    config = load_alert_config(path)
    if config is None:
        print("[Error] Failed to load alert configuration.")
        return False

    changed = False
    # update existing, warning if not exists
    for key, value in kwargs.items():
        if key in config and config[key] != value:
            config[key] = value
            changed = True
        else:
            print(f"[Warning] Key '{key}' not found in alert configuration. Skipping it")
    
    if not changed:
        print("[Info] No changes made to the alert configuration.")
        return True
    
    try:
        with open(path, "w") as file:
            json.dump(config, file, indent=4)
        print(f"[Info] Alert configuration updated successfully.")
        return True
    except Exception as e:
        print(f"[Error] Failed to update alert configuration: {e}")
        return False
    

def dry_run_test():
    print("[Info] Running dry run test...")
    print("[Info] no alert will be inserted...")
    # Load the current alert configuration
    config = load_alert_config()
    if config is None:
        print("[Error] Failed to load alert configuration.")
        return

    session = get_session()
    
    # Detect toxic posts
    print("[Info] Detecting toxic posts...")
    toxic_posts = detect_toxic(session, sentiment_threshold=config["toxic_threshold"])
    if not toxic_posts:
        print("[Info] No toxic posts detected.")
    else:
        for post, reason in toxic_posts:
            print(f"[Alert] Toxic Post Detected: {post.content} | Reason: {reason}")
    print("[Info] Toxic detection completed.")
            
            
    # Detect spam posts
    print("[Info] Detecting spam posts...")
    spam_posts = detect_spam(session)
    if not spam_posts:
        print("[Info] No spam posts detected.")
    else:
        for post, reason in spam_posts:
            print(f"[Alert] Spam Post Detected: {post.post_id} | Reason: {reason}")
    print("[Info] Spam detection completed.")


    # Detect scam posts
    print("[Info] Detecting scam posts...")
    scam_posts = detect_scam(session, alert_high_risk=False)
    if not scam_posts:
        print("[Info] No scam posts detected.")
    else:
        for post, score, reason in scam_posts:
            print(f"[Alert] Scam Post Detected: {post.post_id} | Score: {score} | Reason: {reason}")
    print("[Info] Scam detection completed.")



    # Detect sentiment crisis
    print("[Info] Detecting sentiment crisis posts...")
    sentiment_crisis_posts = detect_sentiment_crisis(session, 
        threshold=config["sentiment_crisis_threshold"],
        minimum_posts=config["sentiment_crisis_minimum_posts"],
        timeframe=config["sentiment_crisis_timeframe"]
    )
    if not sentiment_crisis_posts:
        print("No sentiment crisis detected with the given criteria.") 
    else:
        print(f"Sentiment Crisis Detected: {len(sentiment_crisis_posts)} posts")
    print("[Info] Sentiment crisis detection completed.")
    
    
    # Detect sentiment trend alerts
    print("[Info] Detecting sentiment trend alerts...")
    trend_alerts = detect_trend_alerts(session, 
        sentiment_drop=config["sentiment_alert_drop"],
        volume_spike=config["sentiment_alert_volume_spike_threshold"],
        timeframe=config["sentiment_alert_timeframe"]
    )
    if not trend_alerts:
        print("[Info] No sentiment trend alerts detected.")
    else:
        trend_alerts_posts = trend_alerts["posts"]
        reasons = trend_alerts["alerts"]
        print(f"[Alert] Sentiment Trend Alerts Detected: {len(trend_alerts_posts)} posts")
        for reason, description in reasons:
            print(f"  {reason}: {description}")
    print("[Info] Sentiment trend alert detection completed.")
    
    
    # Detect review bombing
    print("[Info] Detecting review bombing posts...")
    review_bombing_posts = detect_review_bombing(session, 
        negative_ratio_threshold=config["review_bombing_negative_ratio_threshold"],
        volume_spike_threshold=config["review_bombing_volume_spike_threshold"],
        minimum_posts=config["review_bombing_minimum_posts"],
        timeframe=config["review_bombing_timeframe"]
    )
    if not review_bombing_posts:
        print("[Info] No review bombing detected.")
    else:
        print(f"[Alert] Review Bombing Detected: {len(review_bombing_posts)} posts")
    print("[Info] Review bombing detection completed.")
    
    
def check_alerts(session, live: bool = False, platform: Optional[list[str]] = None) -> list[tuple[Alert, str]]:
    """Check for alerts based on the current alert configuration.

    Args:
        session (sqlalchemy.orm.Session): The database session.
        live (bool, optional): if true, return only live unreviewed alerts. Defaults to False.
        platform (Optional[list[str]], optional): The platforms to check for alerts. Defaults to None.
        
    Returns:
        list[tuple[Alert, str]]: A list of tuples containing the alert and its corresponding platform.
    """
    
    query = (
        session.query(Alert, Platform)
        .join(Post, Alert.post_id == Post.post_id)
        .join(Platform, Post.platform_id == Platform.platform_id)
    )
    if live:
        query = query.filter(Alert.reviewed == False)
    if platform:
        platform_ids = []
        for p in platform:
            p_id = session.query(Platform.platform_id).filter(Platform.name == p).first()
            if p_id:
                platform_ids.append(p_id[0])
            else:
                print(f"[Warning] Platform '{p}' not found. Skipping it.")

        query = query.filter(Post.platform_id.in_(platform_ids))
        
    query = query.order_by(Alert.triggered_at.desc())
    alerts_platforms = query.all()
    return [(alert, platform.name) for alert, platform in alerts_platforms]



def get_alert_history(session, since: Optional[str] = None, until: Optional[str] = None, severity: Optional[str] = None) -> list[Alert]:
    """
    Get the alert history within a specified timeframe.
    
    Args:
        session (sqlalchemy.orm.Session): The database session.
        since (Optional[str]): The start date for the history query.
        until (Optional[str]): The end date for the history query.
        
    Returns:
        list[Alert]: A list of Alert objects within the specified timeframe.
    """
    query = session.query(Alert)
    
    if since:
        since_date = datetime.fromisoformat(since)
        query = query.filter(Alert.triggered_at >= since_date)
    if until:
        until_date = datetime.fromisoformat(until)
        query = query.filter(Alert.triggered_at <= until_date)

    if severity:
        if severity.lower() == "critical":
            query = query.filter(Alert.alert_severity >= 5)
        elif severity.lower() == "high":
            query = query.filter(Alert.alert_severity >= 4)
        elif severity.lower() == "medium":
            query = query.filter(Alert.alert_severity == 3)
        elif severity.lower() == "low":
            query = query.filter(Alert.alert_severity == 2)
        elif severity.lower() == "info":
            query = query.filter(Alert.alert_severity == 1)
        else:
            print(f"[Warning] Unknown severity '{severity}'. No filtering applied.")
    
    alerts = query.all()
    if not alerts:
        print("[Info] No alerts found for the specified criteria.")
        return []
    
    return alerts



def get_alert_summary(session, show_recent: bool = False, count_by_type: bool = False) -> dict:
    """
    Get a summary of alerts.
    
    Args:
        session (sqlalchemy.orm.Session): The database session.
        show_recent (bool): If True, include recent alerts in the summary.
        count_by_type (bool): If True, count alerts by type.
        
    Returns:
        dict: A dictionary containing the alert summary.
    """
    query = session.query(Alert)
    
    # if show recent, show recent 3days and limit to 100
    if show_recent:
        query = query.filter(Alert.triggered_at >= datetime.now() - timedelta(days=3)).limit(100)
    
    alerts = query.all()
    
    summary = {
        "total_alerts": len(alerts),
        "severity_counts": {
            "critical": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "info": 0
        },
        "alerts": []
    }
    
    for alert in alerts:
        if alert.alert_severity >= 5:
            summary["severity_counts"]["critical"] += 1
        elif alert.alert_severity == 4:
            summary["severity_counts"]["high_severity"] += 1
        elif alert.alert_severity == 3:
            summary["severity_counts"]["medium_severity"] += 1
        elif alert.alert_severity == 2:
            summary["severity_counts"]["low_severity"] += 1
        elif alert.alert_severity == 1:
            summary["severity_counts"]["info"] += 1
    
    if count_by_type:
        type_counts = {}
        for alert in alerts:
            if alert.alert_type not in type_counts:
                type_counts[alert.alert_type] = 0
            type_counts[alert.alert_type] += 1
        summary["type_counts"] = type_counts
    
    # for alert in alerts:
    #     summary["alerts"].append({
    #         "alert_id": alert.alert_id,
    #         "alert_type": alert.alert_type,
    #         "triggered_at": alert.triggered_at,
    #         "reviewed": alert.reviewed,
    #         "severity": alert.alert_severity
    #     })
    
    return summary