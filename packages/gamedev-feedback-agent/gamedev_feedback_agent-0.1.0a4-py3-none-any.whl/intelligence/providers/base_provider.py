# intelligence/providers/base_provider.py
from abc import ABC, abstractmethod

class TranslationProvider(ABC):
    @abstractmethod
    def translate(self, text: str, target_lang: str = "English") -> str:
        pass


class SentimentProvider(ABC):
    @abstractmethod
    def analyze_sentiment(self, text: str) -> tuple[str, float]:
        """Analyze sentiment of the given text."""
        pass
    
    @abstractmethod
    def batch_analyze_sentiment(self, texts: list[str]) -> list[tuple[str, float]]:
        """Batch analyze sentiment of multiple texts."""
        pass
    
class EmbeddingProvider(ABC):
    @abstractmethod
    def create_embedding(self, text: str, model: str) -> tuple[str, list[float]]:
        """Create an embedding for the given text using the specified model."""
        pass

    @abstractmethod
    def batch_create_embeddings(self, texts: list[str], model: str) -> tuple[str, list[list[float]]]:
        """Batch create embeddings for multiple texts using the specified model."""
        pass
