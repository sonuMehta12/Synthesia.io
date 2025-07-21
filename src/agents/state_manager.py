"""
State Manager Agent for the Learning Agent.

This module implements the state management node, which handles user profiles,
book requests, and state management in the learning agent workflow.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from ..models.state import AgentState, UserProfile, BookRequest, GeneratedBook
from ..models.intents import IntentType
from ..utils.config import config

logger = logging.getLogger(__name__)

# Mock data for simulation (should match ContextAssembler)
MOCK_USER_PROFILE = {
    "user_id": "user_123",
    "name": "Alice",
    "learning_style": "visual",
    "content_preferences": {"format": "markdown", "depth": "comprehensive"},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}

class StateManager:
    """
    State Manager Agent for the Learning Agent.
    
    This agent manages user profiles, book requests, and state data.
    It's responsible for loading and updating user context throughout
    the learning agent workflow for book creation.
    """
    
    def __init__(self):
        """Initialize the State Manager."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("State Manager initialized")
    
    def load_user_context(self, user_id: str) -> UserProfile:
        """
        Load user profile and context.
        
        Args:
            user_id: Unique identifier for the user.
            
        Returns:
            UserProfile with user information and preferences.
        """
        # For now, return mock profile
        return MOCK_USER_PROFILE.copy()
    
    def create_book_request(self, user_id: str, user_query: str, intent: IntentType, topic: Optional[str] = None) -> BookRequest:
        """
        Create a new book request.
        
        Args:
            user_id: Unique identifier for the user.
            user_query: The original user query.
            intent: The classified intent.
            topic: Optional extracted topic.
            
        Returns:
            New BookRequest.
        """
        request_id = str(uuid.uuid4())
        request = BookRequest(
            request_id=request_id,
            user_query=user_query,
            intent=intent,
            topic=topic,
            created_at=datetime.now().isoformat(),
            status="pending",
        )
        
        self.logger.info(f"New book request created: {request_id} for topic: {topic}")
        return request
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> UserProfile:
        """
        Update user profile with new information.
        
        Args:
            user_id: Unique identifier for the user.
            updates: Dictionary of profile updates.
            
        Returns:
            Updated UserProfile.
        """
        current_profile = self.load_user_context(user_id)
        
        # Apply updates
        updated_profile = {**current_profile, **updates}
        updated_profile["updated_at"] = datetime.now().isoformat()
        
        # TODO: Save to database
        self.logger.info(f"Profile updated for user {user_id}")
        
        return UserProfile(**updated_profile)
    
    def manage_state(self, state: AgentState) -> AgentState:
        """
        Manage and update the agent state.
        
        This is the main method used as a LangGraph node. It ensures
        the state has all necessary user context and book request information.
        
        Args:
            state: Current agent state.
            
        Returns:
            Updated agent state with user context and book request info.
        """
        try:
            # Use mock user profile if not present
            user_profile = state.get("user_profile")
            if not user_profile:
                user_profile = MOCK_USER_PROFILE.copy()
                self.logger.info("Using mock user profile.")
            user_id = user_profile.get("user_id", "user_123")
            
            # Create book request if intent is available
            current_request = state.get("current_request")
            current_intent = state.get("current_intent")
            current_topic = state.get("current_topic")
            
            if current_intent and not current_request:
                # Create new book request
                user_query = ""
                if state.get("messages"):
                    last_message = state["messages"][-1]
                    user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
                
                new_request = self.create_book_request(
                    user_id=user_id,
                    user_query=user_query,
                    intent=current_intent["intent"],
                    topic=current_topic
                )
                self.logger.info(f"Created book request for intent: {current_intent['intent']}")
            else:
                new_request = current_request
            
            # Update state with managed information
            updated_state = {
                **state,
                "user_profile": user_profile,
                "current_request": new_request,
                "timestamp": datetime.now().isoformat(),
            }
            
            self.logger.info("State management completed successfully")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"Error in manage_state: {e}")
            # Return state with error information
            return {
                **state,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user book creation statistics.
        
        Args:
            user_id: Unique identifier for the user.
            
        Returns:
            Dictionary with user book creation statistics.
        """
        # TODO: Implement database integration
        return {
            "total_books_requested": 0,
            "books_completed": 0,
            "favorite_topics": [],
            "last_updated": datetime.now().isoformat(),
        } 