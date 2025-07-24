"""
ContextAssembler: Central context hub and prompt factory for multi-agent ToC architecture.

This module serves two primary functions:
1. **Context Hub**: Gathers all raw context data from various sources in one place
2. **Prompt Factory**: Formats raw context into node-specific populated prompts

Architecture Pattern:
- Raw context stored once, formatted multiple ways for different nodes
- Each node gets exactly the context format it needs via get_populated_prompt()
- Easy to add new nodes by adding new formatting methods
- Centralized context management prevents data duplication across nodes
"""
from typing import Dict, Any, List
from ..models.intents import IntentClassification
from ..models.state import UserProfile

# Import prompt templates
from ..prompts.strategic_planner import STRATEGIC_PLANNING_PROMPT
from ..prompts.initial_research import PERSONALIZED_TOC_PROMPT

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
    Central context hub and prompt factory for multi-agent architecture.
    
    This class implements the "assemble once, format many" pattern:
    1. assemble_context() - Gathers all raw context data once
    2. get_populated_prompt() - Formats context for specific nodes on demand
    
    Benefits:
    - Eliminates data duplication across nodes
    - Provides clean node interface: just pass node name, get populated prompt
    - Easy to add new nodes without touching existing ones
    - Centralized context logic for maintainability
    """
    
    def __init__(self):
        """Initialize the context assembler with empty raw context storage."""
        self.raw_context = {}
    
    def assemble_context(
        self,
        user_profile: UserProfile = None,
        intent_result: IntentClassification = None,
        existing_books: List[Dict[str, Any]] = None,
        user_resources: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Step 1: Assemble all raw context data from various sources.
        
        This method is called once per request to gather all needed context data
        from different sources (database, APIs, user input, etc.) and store it
        centrally for use by multiple nodes.
        
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
        
        # Store all raw context data centrally
        self.raw_context = {
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
        return self.raw_context
    
    def get_populated_prompt(self, node_name: str) -> str:
        """
        Step 2: Get fully populated prompt for a specific node.
        
        This is the main interface method that nodes use. Each node simply calls:
        populated_prompt = context_assembler.get_populated_prompt("my_node_name")
        
        Args:
            node_name: Name of the node requesting the prompt
                      Supported: "strategic_planner", "knowledge_synthesizer", "intelligence_gatherer"
                      
        Returns:
            Fully populated prompt string ready for LLM invocation
            
        Raises:
            ValueError: If node_name is not supported
            RuntimeError: If raw_context hasn't been assembled yet
        """
        if not self.raw_context:
            raise RuntimeError("Context must be assembled before getting populated prompts. Call assemble_context() first.")
        
        # Route to appropriate prompt formatting method based on node name
        if node_name == "strategic_planner":
            return self._populate_strategic_planner_prompt()
        elif node_name == "knowledge_synthesizer":
            return self._populate_knowledge_synthesizer_prompt()
        elif node_name == "intelligence_gatherer":
            return self._populate_intelligence_gatherer_prompt()
        else:
            raise ValueError(f"Unknown node: {node_name}. Supported nodes: strategic_planner, knowledge_synthesizer, intelligence_gatherer")
    
    # ============================================================================
    # STRATEGIC PLANNER PROMPT FORMATTING
    # ============================================================================
    
    def _populate_strategic_planner_prompt(self) -> str:
        """
        Format raw context for Strategic Planner prompt template.
        
        Strategic Planner needs:
        - High-level user profile summary
        - Learning preferences and style information
        - Current expertise and knowledge gaps
        - Goals and timeline constraints
        - User-provided resources for analysis
        
        Returns:
            Populated STRATEGIC_PLANNING_PROMPT ready for LLM
        """
        user_profile = self.raw_context["user_profile"]
        learning_topic = self.raw_context["topic_context"] or "Unknown Topic"
        user_resources = self.raw_context["resource_context"]
        
        # Format context specifically for strategic planning needs
        formatted_context = {
            "learning_topic": learning_topic,
            "user_profile_summary": self._format_user_profile_summary(user_profile),
            "learning_preferences": self._format_learning_preferences(user_profile),
            "current_expertise": self._format_current_expertise(user_profile),
            "knowledge_gaps": self._format_knowledge_gaps(user_profile),
            "goals_timeline": self._format_goals_timeline(user_profile),
            "user_resources": self._format_user_resources(user_resources)
        }
        
        return STRATEGIC_PLANNING_PROMPT.format(**formatted_context)
    
    def _format_user_profile_summary(self, user_profile: Dict[str, Any]) -> str:
        """Create a concise user profile summary for strategic planning."""
        name = user_profile.get("name", "User")
        user_id = user_profile.get("user_id", "unknown")
        learning_style = user_profile.get("learning_style", "Not specified")
        
        return f"Name: {name} (ID: {user_id}), Learning Style: {learning_style}"
    
    def _format_learning_preferences(self, user_profile: Dict[str, Any]) -> str:
        """Extract and format learning preferences for strategic analysis."""
        learning_style = user_profile.get("learning_style", "comprehensive with practical examples")
        content_prefs = user_profile.get("content_preferences", {})
        
        format_pref = content_prefs.get("format", "markdown")
        depth_pref = content_prefs.get("depth", "comprehensive")
        
        return f"Style: {learning_style}, Format: {format_pref}, Depth: {depth_pref}"
    
    def _format_current_expertise(self, user_profile: Dict[str, Any]) -> str:
        """Format user's current expertise for strategic planning."""
        # Try to extract from detailed persona first, fallback to simple format
        if "knowledge_foundation" in user_profile and "core_expertise" in user_profile["knowledge_foundation"]:
            # Detailed persona format
            core_expertise = user_profile["knowledge_foundation"]["core_expertise"]
            expertise_items = []
            for domain, details in core_expertise.items():
                level = details.get("level", "unknown")
                confidence = details.get("confidence", "?")
                domain_name = domain.replace("_", " ").title()
                expertise_items.append(f"{domain_name}: {level} (confidence: {confidence}/10)")
            return "; ".join(expertise_items)
        else:
            # Simple format fallback
            return "General learning background and experience"
    
    def _format_knowledge_gaps(self, user_profile: Dict[str, Any]) -> str:
        """Format user's knowledge gaps for strategic planning."""
        # Try to extract from detailed persona first
        if "knowledge_foundation" in user_profile and "ai_knowledge_state" in user_profile["knowledge_foundation"]:
            specific_gaps = user_profile["knowledge_foundation"]["ai_knowledge_state"].get("specific_gaps", [])
            return "; ".join(specific_gaps) if specific_gaps else "Knowledge gaps to be identified"
        else:
            # Fallback for simple profile
            return "Fundamental concepts and practical applications"
    
    def _format_goals_timeline(self, user_profile: Dict[str, Any]) -> str:
        """Format user's goals and timeline for strategic planning."""
        # Try to extract from detailed persona first
        if "goals" in user_profile and "current_goals" in user_profile["goals"]:
            goal = user_profile["goals"]["current_goals"][0]
            primary_goal = goal.get("primary_goal", "Learn effectively")
            timeline = goal.get("target_timeline", "3-6 months")
            return f"Goal: {primary_goal}, Timeline: {timeline}"
        else:
            # Fallback for simple profile
            learning_topic = self.raw_context["topic_context"] or "this topic"
            return f"Goal: Learn {learning_topic} effectively, Timeline: 3-6 months"
    
    def _format_user_resources(self, user_resources: List[Dict[str, Any]]) -> str:
        """Format user-provided resources for strategic analysis."""
        if not user_resources:
            return "No user-provided resources"
        
        resource_summaries = []
        for resource in user_resources[:3]:  # Limit to top 3 for context window
            title = resource.get("title", "Unnamed Resource")
            type_info = resource.get("type", "unknown type")
            resource_summaries.append(f"'{title}' ({type_info})")
        
        return "; ".join(resource_summaries)
    
    # ============================================================================
    # KNOWLEDGE SYNTHESIZER PROMPT FORMATTING
    # ============================================================================
    
    def _populate_knowledge_synthesizer_prompt(self) -> str:
        """
        Format raw context for Knowledge Synthesizer prompt template.
        
        Knowledge Synthesizer needs:
        - Detailed user persona data for personalization
        - Learning topic information
        - Existing knowledge summary
        - Specific formatting for ToC generation
        
        Returns:
            Populated PERSONALIZED_TOC_PROMPT ready for LLM
        """
        user_profile = self.raw_context["user_profile"]
        learning_topic = self.raw_context["topic_context"] or "Unknown Topic"
        existing_knowledge = self.raw_context["existing_knowledge"]
        
        # Use existing _prepare_prompt_context logic from initial_research_node
        # This ensures compatibility with current ToC generation
        
        # Try to get detailed persona data first, fallback to mock profile structure
        if "goals" in user_profile and "learning_profile" in user_profile:
            # Detailed persona format (from get_hardcoded_sonu_persona)
            goal = user_profile["goals"]["current_goals"][0]
            learning_style = user_profile["learning_profile"]["learning_style"]
            core_expertise = user_profile["knowledge_foundation"]["core_expertise"]
            specific_gaps = user_profile["knowledge_foundation"]["ai_knowledge_state"]["specific_gaps"]
            
            # Build knowledge bridges dynamically from user's expertise
            knowledge_bridges = self._generate_knowledge_bridges(core_expertise, "AI")
            
            # Format core expertise for display
            expertise_str = "; ".join(
                f"{k}: {v['level']} ({v.get('confidence', '?')}/10)" 
                for k, v in core_expertise.items()
            )
            
            formatted_context = {
                "learning_topic": learning_topic,
                "primary_goal": goal["primary_goal"],
                "specific_outcome": goal["specific_outcome"],
                "target_timeline": goal["target_timeline"],
                "success_metrics": ", ".join(goal["success_metrics"]),
                "explanation_preference": learning_style["explanation_preference"],
                "example_types": ", ".join(learning_style["example_types"]),
                "visual_preferences": ", ".join(learning_style["visual_preferences"]),
                "content_structure": learning_style["content_structure"],
                "core_expertise": expertise_str,
                "knowledge_bridges": knowledge_bridges,
                "specific_gaps": ", ".join(specific_gaps),
                "rag_existing_books_summary": user_profile.get("rag_existing_books_summary", 
                                                            self._summarize_existing_knowledge(existing_knowledge)),
                "industry_benchmarks": "AI product management curriculum from top universities.",
                "current_trends": "Emphasis on practical AI evaluation, LLM safety, and real-world case studies.",
                "expert_recommendations": "Follow learning paths from leading AI PMs and product teams.",
            }
        else:
            # Simple mock profile format - create reasonable defaults
            learning_style_str = user_profile.get("learning_style", "comprehensive with practical examples")
            
            formatted_context = {
                "learning_topic": learning_topic,
                "primary_goal": f"Learn {learning_topic} effectively",
                "specific_outcome": f"Gain practical knowledge in {learning_topic}",
                "target_timeline": "3-6 months",
                "success_metrics": f"Understand core concepts, Apply {learning_topic} in practice, Build confidence",
                "explanation_preference": "clear explanations with rich context",
                "example_types": "real-world applications, practical examples, case studies",
                "visual_preferences": "diagrams, mindmaps, flowcharts",
                "content_structure": "start basic, build to comprehensive understanding",
                "core_expertise": "General knowledge and learning experience",
                "knowledge_bridges": f"Existing knowledge to {learning_topic}",
                "specific_gaps": f"Fundamental concepts in {learning_topic}",
                "rag_existing_books_summary": self._summarize_existing_knowledge(existing_knowledge),
                "industry_benchmarks": f"Standard curriculum for {learning_topic}.",
                "current_trends": f"Current best practices and trends in {learning_topic}.",
                "expert_recommendations": f"Follow learning paths recommended by {learning_topic} experts.",
            }
        
        return PERSONALIZED_TOC_PROMPT.format(**formatted_context)
    
    def _generate_knowledge_bridges(self, core_expertise: Dict[str, Any], target_domain: str = "AI") -> str:
        """Generate knowledge bridges dynamically from user's expertise."""
        bridges = []
        
        for domain, details in core_expertise.items():
            # Only include domains where user has meaningful experience (confidence >= 6)
            confidence = details.get("confidence", 0)
            if confidence >= 6:
                # Convert snake_case to Title Case
                domain_name = domain.replace("_", " ").title()
                bridges.append(f"{domain_name} to {target_domain}")
        
        return ", ".join(bridges) if bridges else f"General knowledge to {target_domain}"
    
    def _summarize_existing_knowledge(self, existing_knowledge: List[Dict[str, Any]]) -> str:
        """Summarize existing books/knowledge for prompt context."""
        if not existing_knowledge:
            return "No prior books found on this topic."
        
        summaries = []
        for book in existing_knowledge[:3]:  # Limit to top 3 for context window
            title = book.get("title", "Unknown")
            topic = book.get("topic", "General")
            summary = book.get("summary", "No summary available")
            summaries.append(f"'{title}' (Topic: {topic}) - {summary}")
        
        return "; ".join(summaries)
    
    # ============================================================================
    # INTELLIGENCE GATHERER PROMPT FORMATTING (Placeholder)
    # ============================================================================
    
    def _populate_intelligence_gatherer_prompt(self) -> str:
        """
        Format raw context for Intelligence Gatherer prompt template.
        
        TODO: Implement when Intelligence Gatherer prompt template is created.
        For now, returns a placeholder.
        
        Returns:
            Placeholder prompt for Intelligence Gatherer
        """
        learning_topic = self.raw_context["topic_context"] or "Unknown Topic"
        
        return f"""
        # Intelligence Gatherer Research Task
        
        **Research Topic**: {learning_topic}
        **Task**: Conduct web research to find current, actionable information
        
        TODO: Implement full Intelligence Gatherer prompt template
        """ 