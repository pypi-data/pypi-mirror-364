from datetime import datetime, timedelta
from typing import Optional
from collections import Counter
from itertools import groupby
from operator import itemgetter


from database.db_models import Post, Platform, Analysis, Embedding, Alert, Tag, PostTag

from intelligence.sentiment import project_to_01_range


def generate_brief_report(session, since: datetime, platform: Optional[list[str]] = None) -> dict:
    """Generate a brief report of posts and analyses within a specified date range.

    Args:
        session: Database session for querying.
        since (datetime): Start date for the report.
        until (datetime): End date for the report.
        platform (Optional[list[str]], optional): List of platforms to include in the report. Defaults to None.

    Returns:
        dict: A dictionary containing the report data.
        
    Raises:
        ValueError: If the 'since' parameter is not provided.
    """
    # check since
    if since == None:
        raise ValueError("The 'since' parameter must be provided.")
    
    # get platform ids
    platform_ids = None
    platforms = session.query(Platform).all()
    id_platform = {platform.platform_id: platform.name for platform in platforms}
    if platform:
        platform_ids = [platform.platform_id for platform in platforms if platform.name in platform]
            
    # query posts within the date range and platform
    posts_query = session.query(Post).filter(Post.timestamp >= since)
    if platform_ids:
        posts_query = posts_query.filter(Post.platform_id.in_(platform_ids))
        
    posts = posts_query.all()
    post_count = len(posts)
    post_types = Counter(post.post_type for post in posts if post.post_type)
    post_languages = Counter(post.language for post in posts if post.language)
    post_platforms = Counter(id_platform[post.platform_id] for post in posts)
    
    
    # query analyses within the date range and platform
    analyses_query = session.query(Analysis).join(Post).filter(Post.timestamp >= since)
    if platform_ids:
        analyses_query = analyses_query.filter(Post.platform_id.in_(platform_ids))
    analyses = analyses_query.all()
    analysis_count = len(analyses)
    sentiment_labels = Counter(analysis.sentiment_label for analysis in analyses if analysis.sentiment_label)
    average_sentiment_score_projected = sum(project_to_01_range(analysis.sentiment_label, analysis.sentiment_score) for analysis in analyses if analysis.sentiment_score) / analysis_count if analysis_count > 0 else 0
    average_priority_score = sum(analysis.priority_score for analysis in analyses if analysis.priority_score) / analysis_count if analysis_count > 0 else 0
    priority_summary = {"80-100": 0, "60-80": 0, "40-60": 0, "20-40": 0, "0-20": 0}
    for analysis in analyses:
        if analysis.priority_score is not None:
            if analysis.priority_score >= 80:
                priority_summary["80-100"] += 1
            elif analysis.priority_score >= 60:
                priority_summary["60-80"] += 1
            elif analysis.priority_score >= 40:
                priority_summary["40-60"] += 1
            elif analysis.priority_score >= 20:
                priority_summary["20-40"] += 1
            else:
                priority_summary["0-20"] += 1
    
    # query alerts within the date range and platform
    alerts_query = session.query(Alert).join(Post).filter(Alert.triggered_at >= since)
    alerts = alerts_query.all()
    alert_count = len(alerts)
    alert_types = Counter(alert.alert_type for alert in alerts if alert.alert_type)
    unreviewed_alert_count = len([alert for alert in alerts if not alert.reviewed])
    alert_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for alert in alerts:
        if alert.alert_severity == 5:
            alert_severity["critical"] += 1
        elif alert.alert_severity == 4:
            alert_severity["high"] += 1
        elif alert.alert_severity == 3:
            alert_severity["medium"] += 1
        elif alert.alert_severity == 2:
            alert_severity["low"] += 1
        elif alert.alert_severity == 1:
            alert_severity["info"] += 1

    # query tags associated with posts
    post_tags_query = session.query(PostTag, Tag.name).join(Tag).join(Post).filter(Post.timestamp >= since)
    if platform_ids:
        post_tags_query = post_tags_query.filter(Post.platform_id.in_(platform_ids))
    tags = post_tags_query.all()
    tag_counts = {}
    for post_tag, tag_name in tags:
        if tag_name not in tag_counts:
            tag_counts[tag_name] = 0
        tag_counts[tag_name] += 1
        
    
    # generate report
    report = {
        "post_count": post_count,
        "post_types": post_types,
        "post_languages": post_languages,
        "post_platforms": post_platforms,
        
        "analysis_count": analysis_count,
        "sentiment_labels": sentiment_labels,
        "average_sentiment_score_projected": average_sentiment_score_projected,
        
        "priority_summary": priority_summary,
        "average_priority_score": average_priority_score,
        
        "alert_count": alert_count,
        "alert_types": alert_types,
        "unreviewed_alert_count": unreviewed_alert_count,
        
        "alert_severity": alert_severity,
        "tag_counts": tag_counts
    }
    return report



def get_sentiment_trend(session, since: datetime, platform: Optional[list[str]] = None, daily: bool = False, weekly: bool = False) -> list[dict]:
    """Get sentiment trend over time.

    Args:
        session: Database session for querying.
        since (datetime): Start date for the trend.
        platform (Optional[list[str]], optional): List of platforms to include in the trend. Defaults to None.

    Returns:
        list[dict]: A list of dictionaries containing the sentiment trend data.
            - each dictionary has:
                - 'date': the date (as a string in 'YYYY-MM-DD' format)
                - 'positive': count of positive sentiments
                - 'neutral': count of neutral sentiments
                - 'negative': count of negative sentiments
                - 'total': total number of analyses for that date
                - 'average_score': average sentiment score for that date
    """


    # check since
    if since == None:
        raise ValueError("The 'since' parameter must be provided.")
    
    # get platform ids
    platform_ids = None
    platforms = session.query(Platform).all()
    id_platform = {platform.platform_id: platform.name for platform in platforms}
    if platform:
        platform_ids = [platform.platform_id for platform in platforms if platform.name in platform]
    
    # determine time intervals
    # if given time window is less than a month, use daily intervals
    # or use weekly intervals
    time_interval = None
    if daily and weekly:
        raise ValueError("Cannot specify both 'daily' and 'weekly'. Choose one.")
    if daily:
        time_interval = "daily"
    elif weekly:
        time_interval = "weekly"
    else:
        time_interval = "daily" if (datetime.now() - since).days < 30 else "weekly"
    
    analyses_query = session.query(Analysis, Post.timestamp).join(Post).filter(Post.timestamp >= since)
    if platform_ids:
        analyses_query = analyses_query.filter(Post.platform_id.in_(platform_ids))
    # sort by timestamp
    analyses_query = analyses_query.order_by(Post.timestamp)
    keyfunc = lambda x: (x[1].isocalendar()[0], x[1].isocalendar()[1])  # (year, week)
    analyses_sorted = sorted(analyses_query, key=keyfunc)  # groupby needs sorted input
    
    
    sentiment_trend = []
    if time_interval == "daily":
        for date, group in groupby(analyses_query, key=lambda x: x[1].date()):
            group = list(group)
            average_score = sum(project_to_01_range(a[0].sentiment_label,a[0].sentiment_score) for a in group) / len(group) if group else 0
            difference_from_last = average_score - (sentiment_trend[-1]['average_score'] if sentiment_trend else 0)
            sentiment_trend.append({
                "date": str(date),
                "positive": sum(1 for a in group if a[0].sentiment_label == "positive"),
                "neutral": sum(1 for a in group if a[0].sentiment_label == "neutral"),
                "negative": sum(1 for a in group if a[0].sentiment_label == "negative"),
                "total": len(group),
                "average_score": average_score,
                "difference": difference_from_last
            })
            
    elif time_interval == "weekly":
        for (year, week), group in groupby(analyses_sorted, key=keyfunc):
            group = list(group)
            week_start = datetime.fromisocalendar(year, week, 1).date()  # Monday
            week_end = week_start + timedelta(days=6)
            week_range = f"{week_start} to {week_end}"
            scores = [project_to_01_range(a[0].sentiment_label, a[0].sentiment_score) for a in group]
            average_score = sum(scores) / len(scores) if scores else 0
            difference_from_last = average_score - (sentiment_trend[-1]['average_score'] if sentiment_trend else 0)
            sentiment_trend.append({
                "date": week_range,
                "positive": sum(1 for a in group if a[0].sentiment_label == "positive"),
                "neutral": sum(1 for a in group if a[0].sentiment_label == "neutral"),
                "negative": sum(1 for a in group if a[0].sentiment_label == "negative"),
                "total": len(group),
                "average_score": average_score,
                "difference": difference_from_last
    })

    return sentiment_trend


def get_priority_alert(session, threshold: int = 80, explain: bool = False) -> list[dict]:
    """Get alerts with priority score above a certain threshold.

    Args:
        session: Database session for querying.
        threshold (int): Priority score threshold. Defaults to 80.
        explain (bool): Whether to include explanations for the alerts. Defaults to False.

    Returns:
        list[dict]: A list of dictionaries containing alerts with priority score above the threshold.
            - each dictionary has:
                - 'alert_id': ID of the alert
                - 'post_id': ID of the associated post
                - 'priority_score': priority score of the alert
                - 'explanation': explanation of the alert (if explain is True)
    """

    alert_analysis_query = session.query(Alert, Analysis).join(Analysis, Alert.post_id == Analysis.post_id).filter(Analysis.priority_score >= threshold)

    if explain:
        return [{
            "alert_id": alert.alert_id,
            "post_id": alert.post_id,
            "priority_score": analysis.priority_score,
            "explanation": alert.note if alert.note else "No explanation provided"
        } for alert, analysis in alert_analysis_query]
    else:
        return [{
            "alert_id": alert.alert_id,
            "post_id": alert.post_id,
            "priority_score": analysis.priority_score
        } for alert, analysis in alert_analysis_query]
        
        
def get_cross_platform_data(session, since: Optional[datetime] = None, platform: Optional[list[str]] = None) -> dict:
    """Get cross-platform data for a specified date range.

    Args:
        session: Database session for querying.
        since (datetime): Start date for the data.
        platform (Optional[list[str]], optional): List of platforms to include in the data. If not provided, all platforms are included.

    Returns:
        dict: A dictionary containing cross-platform data.
    """  
    
    # get platforms
    platforms = session.query(Platform).all()
    if platform:
        platforms = [p for p in platforms if p.name in platform]


    cross_platform_data = {}
    for platform in platforms:
        platform_id = platform.platform_id
        platform_name = platform.name
        
        # query posts for the platform
        posts_query = session.query(Post).filter(Post.platform_id == platform_id)
        if since:
            posts_query = posts_query.filter(Post.timestamp >= since)
        posts = posts_query.all()
        
        # query analyses for the platform
        analyses_query = session.query(Analysis).join(Post).filter(Post.platform_id == platform_id)
        if since:
            analyses_query = analyses_query.filter(Post.timestamp >= since)
        analyses = analyses_query.all()
        
        alert_count_query = session.query(Alert).filter(Alert.post_id.in_([p.post_id for p in posts]))
        if since:
            alert_count_query = alert_count_query.filter(Alert.triggered_at >= since)
        alert_count = alert_count_query.count()
        
        # aggregate data
        analyses_len = len(analyses)
        cross_platform_data[platform_name] = {
            "post_count": len(posts),
            "analysis_count": len(analyses),
            "positive %": sum(1 for a in analyses if a.sentiment_label == "positive") / analyses_len * 100 if analyses_len > 0 else 0,
            "neutral %": sum(1 for a in analyses if a.sentiment_label == "neutral") / analyses_len * 100 if analyses_len > 0 else 0,
            "negative %": sum(1 for a in analyses if a.sentiment_label == "negative") / analyses_len * 100 if analyses_len > 0 else 0,
            "average_sentiment_score": sum(project_to_01_range(a.sentiment_label, a.sentiment_score) for a in analyses if a.sentiment_score) / analyses_len if analyses_len > 0 else 0,
            "average_priority_score": sum(a.priority_score for a in analyses if a.priority_score) / analyses_len if analyses_len > 0 else 0,
            "alert_count": alert_count,
        }
        
    return cross_platform_data