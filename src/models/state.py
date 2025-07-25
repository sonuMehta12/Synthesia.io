"""
State management models for the Learning Agent.

This module defines the state structures used throughout the LangGraph
workflow, including user state, book requests, and generated content
for the book creation MVP.
"""

from typing import Dict, List, Any, Optional
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from .intents import IntentClassification, IntentType
from .persona import UserPersona


class BookRequest(TypedDict):
    """A request to create a book from user input."""
    
    request_id: str
    user_query: str
    intent: IntentType
    topic: Optional[str]
    created_at: str
    status: str  # "pending", "processing", "completed", "failed"


class GeneratedBook(TypedDict):
    """A complete book generated for the user."""
    
    book_id: str
    title: str
    topic: str
    content: str  # Markdown content
    sources: List[str]  # URLs/references used
    created_at: str
    word_count: int
    chapters: List[str]


class BookChapter(TypedDict):
    """A chapter in the personalized book."""
    
    chapter_number: int
    title: str
    summary: str
    personalization_rationale: str


class PersonalizedBookStructure(TypedDict):
    """The complete structure of a personalized book with ToC."""
    
    title: str
    introduction: str
    chapters: List[BookChapter]


class AgentState(TypedDict):
    """
    Main state for the Learning Agent LangGraph.
    
    This is the central state that flows through all nodes in the graph.
    It includes messages, user information, and book creation context.
    """
    
    # Messages for conversation flow (LangGraph standard)
    messages: Annotated[List[AnyMessage], add_messages]
    
    # User and book information - NOW USING RICH PERSONA SCHEMA
    user_profile: Optional[UserPersona]
    current_request: Optional[BookRequest]
    generated_book: Optional[GeneratedBook]
    
    # Intent classification results
    current_intent: Optional[IntentClassification]
    
    # Book creation context
    current_topic: Optional[str]
    learning_context: Dict[str, Any]
    
    # New structured book data
    context: Optional[Dict[str, Any]]  # Assembled context data (serializable)
    execution_plan: Optional[Dict[str, Any]]  # Strategic plan from Strategic Planner
    book_structure: Optional[PersonalizedBookStructure]
    user_feedback: Optional[str]
    book_content: Optional[str]
    
    # Legacy fields (deprecated but kept for backward compatibility)
    toc: Optional[List[Dict[str, Any]]]  # Will be removed after migration
    summaries: Optional[Dict[str, str]]  # Will be removed after migration
    
    # System metadata
    session_id: Optional[str]
    timestamp: str 