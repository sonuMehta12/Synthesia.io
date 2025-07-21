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
        Assemble context for research.
        For now, returns mock data.
        """
        context = {
            "user_profile": user_profile or MOCK_USER_PROFILE,
            "learning_preferences": (user_profile or MOCK_USER_PROFILE).get("content_preferences", {}),
            "topic_context": intent_result["topic"] if intent_result else None,
            "existing_knowledge": existing_books or MOCK_BOOK_SUMMARIES,
            "resource_context": user_resources or MOCK_USER_RESOURCES,
        }
        # In the future: optimize context window, summarize, rank, etc.
        return context 