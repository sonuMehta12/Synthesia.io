"""
UserCollabInterface: Presents the draft ToC to the user and collects feedback (single round).
This node works with the new PersonalizedBookStructure format.
"""
import logging
from typing import Dict, Any, List

from ..models.state import UserProfile, PersonalizedBookStructure

logger = logging.getLogger(__name__)


class UserCollabInterface:
    """
    Presents the draft ToC to the user and collects feedback (single round).
    For now, simulates user approval and returns the same book structure.
    """
    
    def __init__(self):
        """Initialize the User Collaboration Interface."""
        # Silent initialization
    
    def present_and_collect_feedback(
        self,
        book_structure: PersonalizedBookStructure,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Present book structure and collect a single round of feedback.
        
        Args:
            book_structure: The generated book structure with title, intro, and chapters
            user_profile: User profile for personalized feedback collection
            
        Returns:
            Dictionary with feedback results and updated book structure
        """
        try:
                    # Silent book structure presentation
            
            # TODO: Implement actual user interface for feedback collection
            # For now, simulate user approval with minor improvements
            
            # Print the structure for demo purposes (remove in production)
            self._display_book_structure(book_structure)
            
            # Simulate user feedback: approve as-is with minor suggestions
            simulated_feedback = self._generate_simulated_feedback(book_structure, user_profile)
            
            # Silent feedback collection
            
            return {
                "approved": True,
                "updated_book_structure": book_structure,  # No changes for now
                "user_feedback": simulated_feedback,
                # Legacy format for backward compatibility
                "updated_toc": [{"title": chapter["title"]} for chapter in book_structure["chapters"]],
                "updated_summaries": {chapter["title"]: chapter["summary"] for chapter in book_structure["chapters"]}
            }
            
        except Exception as e:
            logger.error(f"Error in user collaboration: {e}")
            return {
                "approved": False,
                "updated_book_structure": book_structure,
                "user_feedback": f"Error collecting feedback: {e}",
                "updated_toc": [],
                "updated_summaries": {}
            }
    
    def _display_book_structure(self, book_structure: PersonalizedBookStructure) -> None:
        """Display the book structure for user review (demo purposes)."""
        print("\n" + "="*60)
        print("📖 PERSONALIZED BOOK STRUCTURE")
        print("="*60)
        print(f"Title: {book_structure['title']}")
        print(f"\nIntroduction:\n{book_structure['introduction']}")
        print(f"\nChapters ({len(book_structure['chapters'])}):")
        
        for chapter in book_structure['chapters']:
            print(f"\n{chapter['chapter_number']}. {chapter['title']}")
            print(f"   Summary: {chapter['summary']}")
            print(f"   Why for you: {chapter['personalization_rationale']}")
        
        print("="*60)
    
    def _generate_simulated_feedback(
        self, 
        book_structure: PersonalizedBookStructure, 
        user_profile: UserProfile
    ) -> str:
        """Generate simulated user feedback based on the book structure."""
        
        chapter_count = len(book_structure['chapters'])
        learning_style = user_profile.get('learning_style', 'comprehensive') if user_profile else 'comprehensive'
        
        # Generate contextual feedback based on structure
        feedback_parts = []
        
        feedback_parts.append(f"The book title '{book_structure['title']}' looks great!")
        
        if chapter_count < 5:
            feedback_parts.append("Consider adding more chapters for comprehensive coverage.")
        elif chapter_count > 10:
            feedback_parts.append("The structure looks thorough, maybe group some topics together.")
        else:
            feedback_parts.append("The chapter structure looks well-balanced.")
        
        # Add learning style specific feedback
        if 'visual' in learning_style.lower():
            feedback_parts.append("Please ensure each chapter includes diagrams and visual aids.")
        elif 'practical' in learning_style.lower():
            feedback_parts.append("Make sure to include hands-on exercises in each chapter.")
        
        feedback_parts.append("Overall, this structure aligns well with my learning goals!")
        
        return " ".join(feedback_parts)
    
    # Legacy method for backward compatibility
    def present_and_collect_feedback_legacy(
        self,
        toc: List[Dict[str, Any]],
        summaries: Dict[str, str],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Legacy method for backward compatibility during migration."""
        logger.warning("Using legacy feedback collection method")
        
        # Convert legacy format to new structure
        book_structure = PersonalizedBookStructure(
            title="Learning Guide",
            introduction="A personalized learning guide based on your preferences.",
            chapters=[
                {
                    "chapter_number": i + 1,
                    "title": chapter["title"],
                    "summary": summaries.get(chapter["title"], "Chapter summary"),
                    "personalization_rationale": "Tailored to your learning journey"
                }
                for i, chapter in enumerate(toc)
            ]
        )
        
        return self.present_and_collect_feedback(book_structure, user_profile) 