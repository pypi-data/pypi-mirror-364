# intelligence/intelligence_config.py
import os



class IntelligenceConfig:    
    # default provider
    DEFAULT_TRANSLATION_PROVIDER = "ollama" # "openai" or "ollama"
    DEFAULT_SENTIMENT_PROVIDER = "ollama" # "openai" or "ollama"
    DEFAULT_EMBEDDING_PROVIDER = "ollama" # "openai" or "ollama"
    
    # settings
    # openai or ollama
    TRANSLATION_PROVIDER = DEFAULT_TRANSLATION_PROVIDER
    SENTIMENT_PROVIDER = DEFAULT_SENTIMENT_PROVIDER
    EMBEDDING_PROVIDER = DEFAULT_EMBEDDING_PROVIDER

    # Provider-specific configurations
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Model selection per provider
    OPENAI_TRANSLATION_MODEL = os.getenv("OPENAI_TRANSLATION_MODEL", "gpt-3.5-turbo")
    OPENAI_SENTIMENT_MODEL = os.getenv("OPENAI_SENTIMENT_MODEL", "gpt-3.5-turbo")
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
    
    OLLAMA_TRANSLATION_MODEL = os.getenv("OLLAMA_TRANSLATION_MODEL", "mistral")
    OLLAMA_SENTIMENT_MODEL = os.getenv("OLLAMA_SENTIMENT_MODEL", "llama3:instruct") # llama3.2
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    # Fallback configuration
    ENABLE_PROVIDER_FALLBACK = True
    PROVIDER_FALLBACK_ORDER = ["ollama", "openai"]  # Try local first
    
    PRIORITY_WEIGHTS = {
        "sentiment": 0.3,
        "engagement": 0.2,
        "keywords": 0.2,
        "recency": 0.2,
        "author": 0.1
    }
    ALERT_THRESHOLDS = {
        "high_priority": 80,
        "sentiment_spike": 0.7,
        "volume_spike": 2.0
    }
    
    # Language settings
    ENABLE_LANGUAGE_DETECTION = True
    DEFAULT_LANGUAGE = "en"
    LANGUAGE_CONFIDENCE_THRESHOLD = 0.8
    ENABLE_TRANSLATION = True
    
    # Sentiment
    SENTIMENT_LABELS = ["positive", "neutral", "negative"]
    
    
    @staticmethod
    def get_embedding_model_name() -> str:
        """Get the name of the embedding model based on the provider."""
        if IntelligenceConfig.EMBEDDING_PROVIDER == "openai":
            return "openai/" + IntelligenceConfig.OPENAI_EMBEDDING_MODEL
        elif IntelligenceConfig.EMBEDDING_PROVIDER == "ollama":
            return "ollama/" + IntelligenceConfig.OLLAMA_EMBEDDING_MODEL
        else:
            raise ValueError(f"Unknown embedding provider: {IntelligenceConfig.EMBEDDING_PROVIDER}")