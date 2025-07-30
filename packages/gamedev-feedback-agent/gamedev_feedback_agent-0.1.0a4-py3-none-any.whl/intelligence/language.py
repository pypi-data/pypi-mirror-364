# serve as a language processing module

# intelligence/language.py
from langdetect import detect, DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException

from database.db_session import get_session
from database.db_models import Post

from intelligence.intelligence_config import IntelligenceConfig
from intelligence.providers.base_provider import TranslationProvider

from collections import defaultdict



DetectorFactory.seed = 0  # makes results consistent

LANGUAGE_MAPPING = {
    "en": "English",
    "zh-cn": "Chinese",
    "zh-tw": "Chinese (Traditional)",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "sv": "Swedish",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "fi": "Finnish",
    "no": "Norwegian",
    "da": "Danish",
    "cs": "Czech",
    "hu": "Hungarian",
    "ro": "Romanian",
    "bg": "Bulgarian",
    "el": "Greek",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "mn": "Mongolian",
    "he": "Hebrew",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "it": "Italian",
    "pt": "Portuguese",
    "ar": "Arabic",
    "hi": "Hindi",
    # Add more mappings as needed
}

from typing import Tuple

def detect_language(text: str) -> Tuple[str, float]:
    """Detect the language of a given text.

    Args:
        text (str): The text to analyze.

    Returns:
        Tuple[str, float]: A tuple containing the detected language code and its confidence score.
        
        If detection fails, returns ("unknown", 0.0).
    """
    try:
        langs = detect_langs(text)
        return langs[0].lang, langs[0].prob
    except LangDetectException:
        return "unknown", 0.0
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "unknown", 0.0

# translation
def get_translation_provider() -> TranslationProvider:
    """Get the translation provider based on the configuration.

    Returns:
        TranslationProvider: An instance of the configured translation provider.
    """
    if IntelligenceConfig.TRANSLATION_PROVIDER == "openai":
        from intelligence.providers.openai_provider import OpenAITranslationProvider
        return OpenAITranslationProvider()
    elif IntelligenceConfig.TRANSLATION_PROVIDER == "ollama":
        from intelligence.providers.ollama_provider import OllamaTranslationProvider
        return OllamaTranslationProvider()
    else:
        raise ValueError(f"Unknown translation provider: {IntelligenceConfig.TRANSLATION_PROVIDER}")

def get_fallback_translation_provider_list() -> list[str]:
    return IntelligenceConfig.PROVIDER_FALLBACK_ORDER
    
def get_translation_provider_by_name(name: str) -> TranslationProvider:
    """Get a translation provider by its name.

    Args:
        name (str): The name of the translation provider.

    Returns:
        TranslationProvider: An instance of the specified translation provider.
    """
    if name == "openai":
        from intelligence.providers.openai_provider import OpenAITranslationProvider
        return OpenAITranslationProvider()
    elif name == "ollama":
        from intelligence.providers.ollama_provider import OllamaTranslationProvider
        return OllamaTranslationProvider()
    else:
        raise ValueError(f"Unknown translation provider: {name}")
    
# translation provider and corresponding fallback logic is here
def translate_text(text: str, target_lang: str = "English") -> str:
    """Translate text to the specified target language using the configured translation provider.

    Args:
        text (str): The text to translate.
        target_lang (str): The target language for translation.

    Returns:
        str: The translated text.
    """
    translated_text = None
    try:
        provider = get_translation_provider()
        translated_text = provider.translate(text, target_lang)
    except Exception as e:
        # Log the error and try fallback providers
        print(f"[Translation Error] {e}")
        print("Attempting fallback translation providers...")
        for fallback_provider_name in get_fallback_translation_provider_list():
            if fallback_provider_name == IntelligenceConfig.TRANSLATION_PROVIDER:
                # skip the main provider that already failed
                continue
            fallback_provider = get_translation_provider_by_name(fallback_provider_name)
            print(f"[Translation Fallback] Trying {fallback_provider_name}...")
            try:
                translated_text = fallback_provider.translate(text, target_lang)
                return translated_text
            except Exception as e:
                print(f"[Translation Fallback Error] {e}")

    return translated_text if translated_text else text  # Return original text if translation fails



# database related
def detect_post_language_all(show_stats: bool = False) -> None:
    """Process all posts in the database to detect their languages.

    Args:
        show_stats (bool): If True, prints statistics about language detection.
    """
    session = get_session()
    try:
        posts = session.query(Post).filter(Post.language == None).all()
        lang_counts = defaultdict(int)

        for post in posts:
            lang, confidence = detect_language(post.content)
            post.language = lang
            post.language_confidence = confidence
            lang_counts[lang] += 1

        session.commit()

        if show_stats:
            print("Detected languages:")
            for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
                print(f"  {lang}: {count} posts")

    except Exception as e:
        print(f"Error processing posts: {e}")
        session.rollback()
    finally:
        session.close()