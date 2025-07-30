# intelligence/providers/openai_provider.py
import openai
from intelligence.providers.base_provider import TranslationProvider, SentimentProvider, EmbeddingProvider
from intelligence.intelligence_config import IntelligenceConfig
from openai import OpenAI

class OpenAITranslationProvider(TranslationProvider):
    
    def get_client(self) -> OpenAI:
        """Get the OpenAI client instance.

        Returns:
            OpenAI: The OpenAI client instance.
            
        Raises:
            ValueError: If the OpenAI API key is not set.
        """
        if not IntelligenceConfig.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
        
        return OpenAI(api_key=IntelligenceConfig.OPENAI_API_KEY)
    
    
    
    def translate(self, text: str, target_lang: str = "English") -> str:
        """Translate text to the target language.

        Args:
            text (str): The text to translate.
            target_lang (str, optional): The target language to translate to. Defaults to "English".

        Returns:
            str: The translated text.
        """
        try:
            client = self.get_client()
        except ValueError as e:
            print(f"[OpenAI client Error] {e}")
            return text
        
        try:
            completion = client.chat.completions.create(
                model=IntelligenceConfig.OPENAI_TRANSLATION_MODEL,
                messages=[
                    {"role": "user", 
                    "content": f"Translate the following text to {target_lang}:\n\n{text}"}
                ]
            )

            return completion.choices[0].message.content.strip()

        except openai.OpenAIError as e:
            print(f"[OpenAI Translate Error] {e}")
            return text
        except Exception as e:
            print(f"[OpenAI Translate Error] An unexpected error occurred: {e}")
            return text
        
    
class OpenAISentimentProvider(SentimentProvider):
    def analyze_sentiment(self, text: str) -> tuple[str, float]:
        try:
            client = OpenAI(api_key=IntelligenceConfig.OPENAI_API_KEY)
        except ValueError as e:
            print(f"[OpenAI client Error] {e}")
            return "unknown", -1.0
        
        labels = IntelligenceConfig.SENTIMENT_LABELS
        if not labels:
            labels = ["positive", "neutral", "negative"]
        prompt = (
            "Analyze the following text and return the sentiment as one of the following: "
            f"{', '.join(labels)}. Also give a confidence score from 0.0 to 1.0.\n\n"
            f"Text: {text}\n"
            "Format your response as: sentiment|confidence"
        )
        
        try:
            completion = client.chat.completions.create(
                model=IntelligenceConfig.OPENAI_SENTIMENT_MODEL,
                messages=[
                    {"role": "user", 
                    "content": prompt}
                ]
            )
            response = completion.choices[0].message.content.strip()
            
            label, score = response.split("|")
            return label.strip().lower(), float(score.strip())
        except Exception as e:
            print(f"[OpenAI Sentiment Error] {e}")
            return "unknown", -1.0
        
        
    def batch_analyze_sentiment(self, texts: list[str]) -> list[tuple[int, str, float]]:
        """Batch analyze sentiment of multiple texts.

        Args:
            texts (list[str]): List of texts to analyze.

        Returns:
            list[tuple[str, float]]: List of tuples containing sentiment label and confidence score for each text.
        """
        try:
            client = OpenAI(api_key=IntelligenceConfig.OPENAI_API_KEY)
        except ValueError as e:
            print(f"[OpenAI client Error] {e}")
            return "unknown", -1.0
        
        result = []
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
            completion = client.chat.completions.create(
                model=IntelligenceConfig.OPENAI_TRANSLATION_MODEL,
                messages=[
                    {"role": "user", 
                    "content": prompt}
                ]
            )
            output = completion.choices[0].message.content.strip()
            if not output or "|" not in output:
                print(f"[OPENAI Sentiment Warning] Unexpected response format: {output}")
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
                print(f"[OPENAI Sentiment Warning] Mismatched results length: expected {len(texts)}, got {len(results)}")
                # Fill missing results with default values
                results += [(-1, "mismatch", -1.0)] * (len(texts) - len(results))
            return results
        except Exception as e:
            print(f"[OPENAI Sentiment Error] {e}, response: {output if output else 'No response'}")
            return [(-1, "unknown", -1.0)] * len(texts)
        
        
        
        
        
        
        
class OpenAIEmbeddingProvider(EmbeddingProvider):

    OPENAI_EMBEDDING_LENGTH = 1536

    def create_embedding(self, text: str, model: str = IntelligenceConfig.OPENAI_EMBEDDING_MODEL) -> tuple[str, list[float]]:
        model_name = f"openai/{IntelligenceConfig.OPENAI_EMBEDDING_MODEL}"
        
        try:
            client = OpenAI(api_key=IntelligenceConfig.OPENAI_API_KEY)
        except ValueError as e:
            print(f"[OpenAI client Error] {e}")
            return model_name, []
        
        
        try:
            response = client.embeddings.create(
                model=IntelligenceConfig.OPENAI_EMBEDDING_MODEL,
                input=text,
            )
            vector = response.data[0].embedding 
            return model_name, vector
        except Exception as e:
            print(f"[OpenAI Embedding Error] {e}")
            return model_name, []
        
    def batch_create_embeddings(self, texts: list[str], model: str = IntelligenceConfig.OPENAI_EMBEDDING_MODEL) -> tuple[str, list[list[float]]]:
        model_name = f"openai/{IntelligenceConfig.OPENAI_EMBEDDING_MODEL}"
        
        try:
            client = OpenAI(api_key=IntelligenceConfig.OPENAI_API_KEY)
        except ValueError as e:
            print(f"[OpenAI client Error] {e}")
            return model_name, []
        
        try:
            response = client.embeddings.create(
                model=IntelligenceConfig.OPENAI_EMBEDDING_MODEL,
                input=texts,  
            )
            # Sort by index in case they come unordered
            sorted_data = sorted(response.data, key=lambda x: x.index)
            vectors = [item.embedding for item in sorted_data]
            return model_name, vectors
        except Exception as e:
            print(f"[OpenAI Embedding Error] {e}")
            return model_name, [[] for _ in texts]