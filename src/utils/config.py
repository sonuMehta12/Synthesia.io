"""
Configuration management for the Learning Agent.

This module handles configuration loading, environment variables,
and default settings for the learning agent system.
"""

import os
from typing import Optional
from dotenv import load_dotenv

from ..models.intents import IntentClassifierConfig

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the Learning Agent."""
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Default LLM settings
    DEFAULT_MODEL: str = "gpt-4o-mini"  # or "claude-3-haiku-20240307"
    DEFAULT_TEMPERATURE: float = 0.1
    DEFAULT_MAX_TOKENS: int = 1000
    
    # Intent Classifier Configuration
    INTENT_CLASSIFIER_CONFIG: IntentClassifierConfig = {
        "model_name": "gpt-4o-mini",
        "temperature": 0.1,
        "max_tokens": 50,
        "confidence_threshold": 0.7,
    }
    
    # Database Configuration (for future use)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Session Configuration
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        required_keys = ["OPENAI_API_KEY"]
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            print(f"❌ Missing required environment variables: {missing_keys}")
            print("Please set these in your .env file or environment.")
            return False
        
        print("✅ Configuration validated successfully")
        return True
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """
        Get LLM configuration for LangChain.
        
        Returns:
            Dictionary with LLM configuration.
        """
        return {
            "model_name": cls.DEFAULT_MODEL,
            "temperature": cls.DEFAULT_TEMPERATURE,
            "max_tokens": cls.DEFAULT_MAX_TOKENS,
        }
    
    @classmethod
    def get_intent_classifier_config(cls) -> IntentClassifierConfig:
        """
        Get intent classifier configuration.
        
        Returns:
            IntentClassifierConfig with current settings.
        """
        return cls.INTENT_CLASSIFIER_CONFIG.copy()


# Global configuration instance
config = Config() 