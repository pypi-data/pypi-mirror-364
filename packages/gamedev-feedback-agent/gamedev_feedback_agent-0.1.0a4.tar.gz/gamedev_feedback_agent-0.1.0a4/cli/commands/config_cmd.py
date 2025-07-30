import argparse

from cli.context import get_context

import os
import re
from intelligence.intelligence_config import IntelligenceConfig



def handle(args=None) -> None:
    parser = argparse.ArgumentParser(prog="config", description="Configuration management commands")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    subparsers.add_parser("view", help="View the current configuration")
    subparsers.add_parser("edit", help="Edit the configuration")
    subparsers.add_parser("show_providers", help="Show available providers and models")
    
    provider_parser = subparsers.add_parser("set_provider", help="Manage provider")
    provider_parser.add_argument("type", choices=["translation", "sentiment", "embedding"], help="Type of provider to set")
    provider_parser.add_argument("name", help="Name of the provider (e.g., 'openai', 'ollama')")
    
    model_parser = subparsers.add_parser("set_model", help="Set model for a provider")
    model_parser.add_argument("provider", choices=["openai", "ollama"], help="Provider to set the model for")
    model_parser.add_argument("model_type", choices=["translation", "sentiment", "embedding"], help="Type of model to set")
    model_parser.add_argument("model_name", help="Name of the model to set")
    


    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        print("[Config Error] Invalid command or arguments.")
        return

    if parsed.subcommand == "view":
        print("Viewing configuration...")
        _context = get_context()
        if not _context:
            print("[Config Error] No workspace context found. Please initialize the workspace first.")
            return
        print("Current workspace context:")
        for key, value in _context.items():
            print(f"{key}: {value}")

        
    elif parsed.subcommand == "edit":
        print("Editing configuration...")
        
        
    elif parsed.subcommand == "set_provider":
        if not parsed.type or not parsed.name:
            print("[Config Error] Both type and name must be specified for set_provider.")
            return
        if parsed.type not in ["translation", "sentiment", "embedding"]:
            print("[Config Error] Invalid provider type. Must be one of: translation, sentiment, embedding.")
            return
        if parsed.name not in ["openai", "ollama"]:
            print("[Config Error] Invalid provider name. Must be one of: openai, ollama.")
            return
        
        print(f"Setting {parsed.type} provider to {parsed.name}...")
        IntelligenceConfig.TRANSLATION_PROVIDER = parsed.name if parsed.type == "translation" else IntelligenceConfig.TRANSLATION_PROVIDER
        IntelligenceConfig.SENTIMENT_PROVIDER = parsed.name if parsed.type == "sentiment" else IntelligenceConfig.SENTIMENT_PROVIDER
        IntelligenceConfig.EMBEDDING_PROVIDER = parsed.name if parsed.type == "embedding" else IntelligenceConfig.EMBEDDING_PROVIDER
        print(f"{parsed.type} provider set to {parsed.name}.")

    elif parsed.subcommand == "set_model":
        if not parsed.provider or not parsed.model_type or not parsed.model_name:
            print("[Config Error] Provider, model type, and model name must be specified for set_model.")
            return
        if parsed.provider not in ["openai", "ollama"]:
            print("[Config Error] Invalid provider. Must be one of: openai, ollama.")
            return
        if parsed.model_type not in ["translation", "sentiment", "embedding"]:
            print("[Config Error] Invalid model type. Must be one of: translation, sentiment, embedding.")
            return
        
        print(f"Setting {parsed.provider} {parsed.model_type} model to {parsed.model_name}...")
        if parsed.provider == "openai":
            setattr(IntelligenceConfig, f"OPENAI_{parsed.model_type.upper()}_MODEL", parsed.model_name)
        elif parsed.provider == "ollama":
            setattr(IntelligenceConfig, f"OLLAMA_{parsed.model_type.upper()}_MODEL", parsed.model_name)
        
        print(f"{parsed.provider} {parsed.model_type} model set to {parsed.model_name}.")
        
        
    elif parsed.subcommand == "show_providers":
        # display provider configurations
        print("Available providers and models:")
        print(f"OpenAI Translation Model: {IntelligenceConfig.OPENAI_TRANSLATION_MODEL}")
        print(f"OpenAI Sentiment Model: {IntelligenceConfig.OPENAI_SENTIMENT_MODEL}")
        print(f"OpenAI Embedding Model: {IntelligenceConfig.OPENAI_EMBEDDING_MODEL}")
        print(f"Ollama Translation Model: {IntelligenceConfig.OLLAMA_TRANSLATION_MODEL}")
        print(f"Ollama Sentiment Model: {IntelligenceConfig.OLLAMA_SENTIMENT_MODEL}")
        print(f"Ollama Embedding Model: {IntelligenceConfig.OLLAMA_EMBEDDING_MODEL}")
        # display current provider settings
        print(f"Current Translation Provider: {IntelligenceConfig.TRANSLATION_PROVIDER}")
        print(f"Current Sentiment Provider: {IntelligenceConfig.SENTIMENT_PROVIDER}")
        print(f"Current Embedding Provider: {IntelligenceConfig.EMBEDDING_PROVIDER}")
    
    else:
        print("[Config Error] Unknown subcommand.")
        return