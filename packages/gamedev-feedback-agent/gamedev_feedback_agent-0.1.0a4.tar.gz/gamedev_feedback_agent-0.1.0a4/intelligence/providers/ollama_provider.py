# intelligence/providers/ollama_provider.py
import requests
from intelligence.providers.base_provider import TranslationProvider, SentimentProvider, EmbeddingProvider
from intelligence.intelligence_config import IntelligenceConfig
import json

class OllamaTranslationProvider(TranslationProvider):
    def translate(self, text: str, target_lang="English") -> str:
        prompt = f"Translate the following to {target_lang}:\n\n{text}"
        res = None
        try:
            res = requests.post(
                f"{IntelligenceConfig.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": IntelligenceConfig.OLLAMA_TRANSLATION_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=15
            )
            # Use json.loads to handle weird formatting safely
            raw = res.text.strip()
            first_line = raw.splitlines()[0]  # take first line only
            parsed = json.loads(first_line)

            return parsed["response"].strip()
        except Exception as e:
            print(f"[Ollama Translate Error] {e}")
            print("Raw Ollama response:\n", res.text if res else "No response")
            return text
        
        
class OllamaSentimentProvider(SentimentProvider):
    def analyze_sentiment(self, text: str) -> tuple[str, float]:
        labels = IntelligenceConfig.SENTIMENT_LABELS
        if not labels:
            labels = ["positive", "neutral", "negative"]
        prompt = (
            "Classify the sentiment of this text as one of the following: "
            f"{', '.join(labels)}. Also give a confidence score between 0.0 and 1.0.\n\n"
            f"Text: {text}\n"
            "Respond in this format: sentiment|confidence"
        )
        res = None
        try:
            res = requests.post(
                f"{IntelligenceConfig.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": IntelligenceConfig.OLLAMA_SENTIMENT_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=15
            )
            output = res.json()["response"].strip()
            
            label, score = self.extract_sentiment_from_response(output)
            return label, score
        except Exception as e:
            print(f"[Ollama Sentiment Error] {e}, response: {res}")
            return "unknown", 0.0
        
    
    def batch_analyze_sentiment(self, texts: list[str]) -> list[tuple[int, str, float]]:
        """Batch analyze sentiment of multiple texts.

        Args:
            texts (list[str]): The texts to analyze.

        Returns:
            list[tuple[str, float]]: A list of tuples containing the sentiment and confidence score for each text.
        """
        labels = IntelligenceConfig.SENTIMENT_LABELS
        if not labels:
            labels = ["positive", "neutral", "negative"]
        
        # combine all texts into a single prompt
        prompt = (
            "classify the sentiments of the following texts as one of the following: "
            f"{', '.join(labels)}. Also give a confidence score between 0.0 and 1.0.\n\n"
            f"Texts: {texts}\n"
            "Respond in this format: index:sentiment|confidence, use newline to separate each text response.\n"
            "where index is the position of the text in the list, starting from 0.\n"
            "Strictly follow the format. Do not use any other text in the response, just the results.\n"
        )
        try:
            res = requests.post(
                f"{IntelligenceConfig.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": IntelligenceConfig.OLLAMA_SENTIMENT_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=15
            )
            output = res.json()["response"].strip()
            if not output or "|" not in output:
                print(f"[Ollama Sentiment Warning] Unexpected response format: {output}")
                return [(-1, "unknown", -1.0)] * len(texts)
            results = []
            i = 0
            for line in output.splitlines():
                if "|" not in line:
                    continue
                label, score = line.split("|")
                label = label.strip().lower()
                index = i
                if ":" in label:
                    # handle index:label format
                    index = int(label.split(":")[0].strip())
                    label = label.split(":")[1].strip()
                results.append((index, label.strip().lower(), float(score.strip())))
                i += 1
            if len(results) != len(texts):
                print(f"[Ollama Sentiment Warning] Mismatched results length: expected {len(texts)}, got {len(results)}")
                # Fill missing results with default values
                results += [(-1, "mismatch", -1.0)] * (len(texts) - len(results))
            return results
        except Exception as e:
            print(f"[Ollama Sentiment Error] {e}, response: {res.text if res else 'No response'}")
            return [(-1, "unknown", -1.0)] * len(texts)

    @staticmethod
    def extract_sentiment_from_response(response: str) -> tuple[str, float]:
        """Extract sentiment and confidence from the response string."""
        if not response or "|" not in response and "positive" not in response.lower() and "negative" not in response.lower() and "neutral" not in response.lower():
            print(f"[Ollama Sentiment Warning] Unexpected response format: {response}")
            return "unknown", -1.0

        part_lists = response.split("|")
        label = "unknown"
        score = 0.0
        if len(part_lists) == 2:
            # response is in format: label|score
            label_part, score_part = part_lists
            for l in IntelligenceConfig.SENTIMENT_LABELS:
                if l in label_part.lower():
                    label = l
                    break
        else:
            # assume response is sentiment|label, ...
            label = part_lists[1].strip()
            score_part = ",".join(part_lists[2:]).strip()
        # sometimes it is returned in sentiment : label or sentiment|label
        if label not in IntelligenceConfig.SENTIMENT_LABELS:
            print(f"[Ollama Sentiment Warning] Unrecognized label: {label}")
            label = "unknown"
            score = 0.0
            return label, score
        else:
            # check the first few characters of the score part
            score_part = score_part.strip()
            # score can be condifience : score, so use first float in string
            score = 0.0
            score = next((float(s) for s in score_part.split() if s.replace('.', '', 1).isdigit()), 0.0)
            if score < 0.0 or score > 1.0:
                print(f"[Ollama Sentiment Warning] Score out of range: {score}")
                score = 0.0
            return label, score
        
        
        
class OllamaEmbeddingProvider(EmbeddingProvider):
    OLLAMA_EMBEDDING_LENGTH = 768
    
    def create_embedding(self, text: str) -> tuple[str, list[float]]:
        try:
            res = requests.post(
                f"{IntelligenceConfig.OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": IntelligenceConfig.OLLAMA_EMBEDDING_MODEL,
                    "prompt": text,
                    "stream": False
                },
                timeout=15
            )
            res.raise_for_status()
            data = res.json()
            if "embedding" not in data or not isinstance(data["embedding"], list):
                raise ValueError("No embedding returned.")
            # check length
            if len(data["embedding"]) != self.OLLAMA_EMBEDDING_LENGTH:
                raise ValueError(f"Embedding length mismatch: expected {self.OLLAMA_EMBEDDING_LENGTH}, got {len(data['embedding'])}")
            return f"ollama/{IntelligenceConfig.OLLAMA_EMBEDDING_MODEL}", [float(x) for x in data["embedding"]]
        except Exception as e:
            print(f"[Ollama Embedding Error] {e}, response: {res.text if 'res' in locals() else 'No response'}")
            return "ollama/unknown", []

    def batch_create_embeddings(self, texts: list[str]) -> tuple[str, list[list[float]]]:
        embeddings = []
        for text in texts:
            model, embedding = self.create_embedding(text)
            embeddings.append(embedding)
        return f"ollama/{IntelligenceConfig.OLLAMA_EMBEDDING_MODEL}", embeddings