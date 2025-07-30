from intelligence.providers.base_provider import SentimentProvider
from intelligence.intelligence_config import IntelligenceConfig
from database.db_session import get_session, close_session
from database.db_models import Post, Analysis


# provider
def get_sentiment_provider() -> SentimentProvider:
    """Get the sentiment analysis provider based on the configuration.

    Returns:
        SentimentProvider: An instance of the configured sentiment provider.
    """
    if IntelligenceConfig.SENTIMENT_PROVIDER == "openai":
        from intelligence.providers.openai_provider import OpenAISentimentProvider
        return OpenAISentimentProvider()
    elif IntelligenceConfig.SENTIMENT_PROVIDER == "ollama":
        from intelligence.providers.ollama_provider import OllamaSentimentProvider
        return OllamaSentimentProvider()
    else:
        raise ValueError(f"Unknown sentiment provider: {IntelligenceConfig.SENTIMENT_PROVIDER}")
    
def get_fallback_sentiment_provider_list() -> list[str]:
    return IntelligenceConfig.PROVIDER_FALLBACK_ORDER

def get_sentiment_provider_by_name(name: str) -> SentimentProvider:
    """Get a sentiment provider by its name.

    Args:
        name (str): The name of the sentiment provider.

    Returns:
        SentimentProvider: An instance of the specified sentiment provider.
    """
    if name == "openai":
        from intelligence.providers.openai_provider import OpenAISentimentProvider
        return OpenAISentimentProvider()
    elif name == "ollama":
        from intelligence.providers.ollama_provider import OllamaSentimentProvider
        return OllamaSentimentProvider()
    else:
        raise ValueError(f"Unknown sentiment provider: {name}")



def get_text_sentiment(text: str) -> tuple[str, float]:
    """Get the sentiment of a text.

    Args:
        text (str): The text to analyze.

    Returns:
        tuple[str, float]: _The sentiment label and confidence score.
    """
    try:
        provider = get_sentiment_provider()
        return provider.analyze_sentiment(text)
    except Exception as e:
        # try fallback providers
        print(f"[Sentiment Analysis Error] {e}")
        fallback_providers = get_fallback_sentiment_provider_list()
        for provider_name in fallback_providers:
            if provider_name == IntelligenceConfig.SENTIMENT_PROVIDER:
                continue
            try:
                provider = get_sentiment_provider_by_name(provider_name)
                return provider.analyze_sentiment(text)
            except Exception as e:
                print(f"[Sentiment Analysis Fallback Error] {e}")
        return "unknown", 0.0
    

def batch_get_text_sentiment(texts: list[str]) -> list[tuple[int, str, float]]:
    """Get the sentiment for a batch of texts.

    Args:
        texts (list[str]): The texts to analyze.

    Returns:
        list[tuple[str, float]]: A list of tuples containing the sentiment label and confidence score for each text.
    """
    results = []
    try:
        provider = get_sentiment_provider()
        results = provider.batch_analyze_sentiment(texts)
        if not results:
            print("[Sentiment Analysis Batching Warning] No results returned from provider.")
        return results
    except Exception as e:
        print(f"[Sentiment Analysis Batching Error] {e}")
        return []



    

def analyze_post_sentiment(post_id: int, force_write = False) -> tuple[str, float]:
    """Analyze the sentiment of a post by its ID and write into Analysis table in the database.

    Args:
        post_id (int): The ID of the post to analyze.

    Returns:
        tuple[str, float]: The sentiment label and confidence score.
    """
    session = get_session()
    
    try:
        post = session.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            print(f"[Sentiment Analysis Error] Post with ID {post_id} not found.")
            return "unknown", 0.0
        
        # Check if sentiment analysis has already been done
        analysis = session.query(Analysis).filter(Analysis.post_id == post_id).first()
        if analysis and not force_write:
            print(f"[Sentiment Analysis Info] Post with ID {post_id} has already been analyzed.")
            return analysis.sentiment_label, analysis.sentiment_score

        sentiment, confidence = get_text_sentiment(post.content)
        if not analysis:
            analysis = Analysis(post_id=post_id, sentiment_label=sentiment, sentiment_score=confidence)
            session.add(analysis)
        else:
            analysis.sentiment_label = sentiment
            analysis.sentiment_score = confidence

        session.commit()
        return sentiment, confidence
    except Exception as e:
        print(f"[Sentiment Analysis Error] {e}")
        return "unknown", 0.0
    finally:
        close_session()
        
        
def project_to_01_range(label: str, confidence: int) -> float:
    """Project a value to the range [0, 1].
    neutral is 0.5, positive is 0.5 + confidence // 2, negative is 0.5 - confidence // 2

    Args:
        value (float): The value to project.

    Returns:
        float: The projected value in the range [0, 1].
    """
    if label == "positive":
        return 0.5 + confidence / 2
    elif label == "negative":
        return 0.5 - confidence / 2
    else:
        return 0.5