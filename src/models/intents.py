"""
Intent classification models for the Learning Agent.

This module defines the data structures for intent classification,
including the different types of intents the system can recognize
and the classification results for the book creation MVP.
"""

from enum import Enum
from typing import Dict, Any, Optional
from typing_extensions import TypedDict


class IntentType(str, Enum):
    """Enumeration of possible intent types for book creation system."""
    
    LEARN_TOPIC = "LEARN_TOPIC"           # Create a book about a topic
    ADD_KNOWLEDGE = "ADD_KNOWLEDGE"       # Add knowledge to existing book
    GENERATE_SUMMARY = "GENERATE_SUMMARY" # Create summary of learning
    UPDATE_PROFILE = "UPDATE_PROFILE"      # Update user preferences
    GENERAL = "GENERAL"                   # General chat/conversation
    UNKNOWN = "UNKNOWN"


class IntentClassification(TypedDict):
    """Result of intent classification for book creation."""
    
    intent: IntentType
    confidence: float
    topic: Optional[str]          # Extracted topic for book creation
    content: Optional[str]        # Content for knowledge addition
    metadata: Dict[str, Any]


class IntentClassifierConfig(TypedDict):
    """Configuration for the intent classifier."""
    
    model_name: str
    temperature: float
    max_tokens: int
    confidence_threshold: float 