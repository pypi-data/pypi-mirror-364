from intelligence.providers.base_provider import EmbeddingProvider
from intelligence.intelligence_config import IntelligenceConfig





def get_embedding_provider() -> EmbeddingProvider:
    """Get the embedding provider based on the configuration.

    Returns:
        EmbeddingProvider: An instance of the configured embedding provider.
    """
    if IntelligenceConfig.EMBEDDING_PROVIDER == "openai":
        from intelligence.providers.openai_provider import OpenAIEmbeddingProvider
        return OpenAIEmbeddingProvider()
    elif IntelligenceConfig.EMBEDDING_PROVIDER == "ollama":
        from intelligence.providers.ollama_provider import OllamaEmbeddingProvider
        return OllamaEmbeddingProvider()
    else:
        raise ValueError(f"Unknown embedding provider: {IntelligenceConfig.EMBEDDING_PROVIDER}")
    
def get_fallback_embedding_provider_list() -> list[str]:
    """Get the list of fallback embedding providers.

    Returns:
        list[str]: A list of provider names in the fallback order.
    """
    return IntelligenceConfig.PROVIDER_FALLBACK_ORDER

def get_embedding_provider_by_name(name: str) -> EmbeddingProvider:
    """Get an embedding provider by its name.

    Args:
        name (str): The name of the embedding provider.

    Returns:
        EmbeddingProvider: An instance of the specified embedding provider.
    """
    if name == "openai":
        from intelligence.providers.openai_provider import OpenAIEmbeddingProvider
        return OpenAIEmbeddingProvider()
    elif name == "ollama":
        from intelligence.providers.ollama_provider import OllamaEmbeddingProvider
        return OllamaEmbeddingProvider()
    else:
        raise ValueError(f"Unknown embedding provider: {name}")
    

def get_text_embedding(text: str) -> list[float]:
    """Get the embedding of a text.

    Args:
        text (str): The text to embed.

    Returns:
        list[float]: The embedding vector for the text.
    """
    try:
        provider = get_embedding_provider()
        return provider.create_embedding(text)
    except Exception as e:
        print(f"[Embedding Error] {e}")
        # try fallback providers
        fallback_providers = get_fallback_embedding_provider_list()
        for fallback_provider in fallback_providers:
            if fallback_provider == IntelligenceConfig.EMBEDDING_PROVIDER:
                continue
            try:
                provider = get_embedding_provider_by_name(fallback_provider)
                return provider.create_embedding(text)
            except Exception as e:
                print(f"[Fallback Embedding Error] {e}")
        return []  # Return an empty list if all providers fail


def batch_get_text_embeddings(texts: list[str]) -> tuple[str, list[list[float]]]:
    """Get embeddings for a batch of texts.

    Args:
        texts (list[str]): The list of texts to embed.

    Returns:
        tuple[str, list[list[float]]]: A tuple containing the provider name and a list of embedding vectors.
    """
    try:
        provider = get_embedding_provider()
        return provider.batch_create_embeddings(texts)
    except Exception as e:
        print(f"[Batch Embedding Error] {e}")
        # try fallback providers
        fallback_providers = get_fallback_embedding_provider_list()
        for fallback_provider in fallback_providers:
            if fallback_provider == IntelligenceConfig.EMBEDDING_PROVIDER:
                continue
            try:
                provider = get_embedding_provider_by_name(fallback_provider)
                return provider.batch_create_embeddings(texts)
            except Exception as e:
                print(f"[Fallback Batch Embedding Error] {e}")
        return "unknown", []  # Return an empty list if all providers fail
    
    