"""
ContextAssembler: Assembles all relevant context for the research node.
This is a placeholder/dummy node for the initial workflow.
"""
from typing import Dict, Any, List
from ..models.intents import IntentClassification
from ..models.state import UserProfile

# Mock data for simulation
MOCK_USER_PROFILE = {
    "user_id": "user_123",
    "name": "Alice",
    "learning_style": "simple explanation, rich examples and analogies with real world applications and mermaid diagrams and mindmaps",
    "content_preferences": {"format": "markdown", "depth": "comprehensive"},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}
MOCK_BOOK_SUMMARIES = [
    {"title": "Intro to AI", "topic": "AI", "summary": "A beginner's guide to AI."},
    {"title": "AI evals", "topic": "AI evals", "summary": "Overview of evaluation methods in AI."},
]
MOCK_USER_RESOURCES = []

class ContextAssembler:
    """
    Assembles all relevant context for the research node.
    For now, uses mock data for user profile, book summaries, and resources.
    """
    def assemble_context(
        self,
        user_profile: UserProfile = None,
        intent_result: IntentClassification = None,
        existing_books: List[Dict[str, Any]] = None,
        user_resources: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assemble context for all downstream nodes.
        
        UPDATED: Enhanced to provide centralized context hub for all nodes.
        Each node extracts what it needs from this assembled context.
        
        Args:
            user_profile: User profile data (from StateManager or database)
            intent_result: Intent classification result with topic extraction
            existing_books: List of existing books/knowledge for the user
            user_resources: List of user-provided resources
            
        Returns:
            Dictionary containing all assembled context for downstream nodes
        """
        # Extract topic from intent result safely
        topic_context = None
        if intent_result and isinstance(intent_result, dict):
            topic_context = intent_result.get("topic")
        elif intent_result and hasattr(intent_result, 'topic'):
            topic_context = intent_result.topic
        
        context = {
            # Core user context
            "user_profile": user_profile or MOCK_USER_PROFILE,
            "topic_context": topic_context,
            
            # Knowledge context
            "existing_knowledge": existing_books or MOCK_BOOK_SUMMARIES,
            "resource_context": user_resources or MOCK_USER_RESOURCES,
            
            # Future context types (for upcoming nodes)
            "user_feedback": None,      # Will be populated after ToC presentation
            "toc_feedback": None,       # Specific feedback on table of contents
            # More context types can be added here as we build more nodes
        }
        
        # In the future: optimize context window, summarize, rank, etc.
        return context 