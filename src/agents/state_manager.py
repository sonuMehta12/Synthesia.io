"""
State Manager Agent for the Learning Agent.

This module implements the state management node, which handles user profiles,
book requests, and state management in the learning agent workflow.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from ..models.state import AgentState, BookRequest, GeneratedBook
from ..models.persona import UserPersona, get_sonu_persona
from ..models.intents import IntentType
from ..utils.config import config

logger = logging.getLogger(__name__)


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
    
    def load_user_context(self, user_id: str) -> UserPersona:
        """
        Load user profile and context.
        
        Args:
            user_id: Unique identifier for the user.
            
        Returns:
            UserPersona with rich user information and learning preferences.
        """
        # Return the rich persona instead of simple mock
        return get_sonu_persona()
    
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
        
        # Silent request creation
        return request
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> UserPersona:
        """
        Update user profile with new information.
        
        Args:
            user_id: Unique identifier for the user.
            updates: Dictionary of profile updates.
            
        Returns:
            Updated UserPersona.
        """
        current_profile = self.load_user_context(user_id)
        
        # TODO: Implement proper UserPersona updates with validation
        # For now, return the base persona (since it's a Pydantic model, not a dict)
        # In future, implement proper persona updating logic
        
        # Silent profile update
        return current_profile
    
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
            # Use rich persona instead of simple mock
            user_profile = state.get("user_profile")
            if not user_profile:
                user_profile = get_sonu_persona()
                # Silent rich persona usage
            user_id = user_profile.user_id
            
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
                # Silent book request creation
            else:
                new_request = current_request
            
            # Update state with managed information
            updated_state = {
                **state,
                "user_profile": user_profile,
                "current_request": new_request,
                "timestamp": datetime.now().isoformat(),
            }
            
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