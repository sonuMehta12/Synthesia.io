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
from ..models.persona import UserPersona, get_sonu_persona

# Import prompt templates
from ..prompts.strategic_planner import STRATEGIC_PLANNING_PROMPT
from ..prompts.initial_research import PERSONALIZED_TOC_PROMPT

# Mock data for simulation - Updated with Sonu's existing AI knowledge
MOCK_BOOK_SUMMARIES = [
    {"title": "Intro to AI", "topic": "AI", "summary": "A beginner's guide to AI."},
    {"title": "AI evals", "topic": "AI evals", "summary": "Overview of evaluation methods in AI."},
]

MOCK_USER_RESOURCES = [
    {
        "title": "Personal AI/ML Learning Notes",
        "type": "learning_notes",
        "content": "Comprehensive notes covering AI/ML basics, including supervised vs unsupervised learning, neural networks fundamentals, and common algorithms like decision trees and linear regression.",
        "summary": "Sonu has solid foundational knowledge of AI/ML concepts and terminology through self-study and practical exploration."
    },
    {
        "title": "LangChain Experimentation Projects", 
        "type": "hands_on_projects",
        "content": "Multiple small projects using LangChain for building conversational AI applications, including document Q&A systems and simple chatbots using OpenAI and Anthropic APIs.",
        "summary": "Practical experience with LangChain framework for building AI applications, demonstrating hands-on familiarity with modern AI development tools."
    },
    {
        "title": "Prompt Engineering Practice Collection",
        "type": "practice_work", 
        "content": "Collection of prompt engineering experiments with various LLM APIs (OpenAI GPT-4, Claude, Gemini), including few-shot learning, chain-of-thought prompting, and role-based prompts for different use cases.",
        "summary": "Strong practical understanding of prompt engineering techniques and experience with multiple LLM APIs for different applications."
    },
    {
        "title": "AI Product Research Notes",
        "type": "research_compilation",
        "content": "Research compilation on successful AI products like ChatGPT, GitHub Copilot, and Notion AI, analyzing their product strategies, user adoption patterns, and market positioning from a product management perspective.",
        "summary": "Shows Sonu's product management mindset applied to AI products, demonstrating strategic thinking about AI in business contexts."
    }
]

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
        user_profile: UserPersona = None,
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
            user_profile: Rich UserPersona data (from StateManager or database)
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
        
        # Store all raw context data centrally - USE RICH PERSONA
        self.raw_context = {
            # Core user context - NOW USING RICH PERSONA SCHEMA
            "user_profile": user_profile or get_sonu_persona(),
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
        
        # Format context specifically for strategic planning needs - USING RICH PERSONA
        formatted_context = {
            "learning_topic": learning_topic,
            "user_profile_summary": self._format_user_profile_summary(user_profile),
            "learning_preferences": self._format_learning_preferences(user_profile),
            "current_expertise": self._format_current_expertise(user_profile),
            "knowledge_gaps": self._format_knowledge_gaps(user_profile),
            "goals_timeline": self._format_goals_timeline(user_profile),
            "user_resources_summary": self._format_user_resources(user_resources)
        }
        
        return STRATEGIC_PLANNING_PROMPT.format(**formatted_context)
    
    def _format_user_profile_summary(self, user_profile: UserPersona) -> str:
        """Create a concise user profile summary for strategic planning."""
        name = user_profile.user_id.replace("_", " ").title()  # Convert user_id to readable name
        learning_style = ", ".join(user_profile.learning_preferences.preferences)
        
        return f"User: {name}, Learning Style: {learning_style}"
    
    def _format_learning_preferences(self, user_profile: UserPersona) -> str:
        """Extract and format learning preferences for strategic analysis."""
        preferences = ", ".join(user_profile.learning_preferences.preferences)
        return f"Learning Preferences: {preferences}"
    
    def _format_current_expertise(self, user_profile: UserPersona) -> str:
        """Format user's current expertise for strategic planning."""
        expertise_items = []
        for skill in user_profile.expertise:
            domain_name = skill.domain
            level = skill.level
            confidence = skill.confidence
            expertise_items.append(f"{domain_name}: {level} (confidence: {confidence}/10)")
        return "; ".join(expertise_items)
    
    def _format_knowledge_gaps(self, user_profile: UserPersona) -> str:
        """Format user's knowledge gaps for strategic planning."""
        return "; ".join(user_profile.knowledge_gaps)
    
    def _format_goals_timeline(self, user_profile: UserPersona) -> str:
        """Format user's goals and timeline for strategic planning."""
        if user_profile.goals:
            goal = user_profile.goals[0]  # Take first goal
            return f"Goal: {goal.specific}, Timeline: {goal.time_bound}"
        else:
            learning_topic = self.raw_context["topic_context"] or "this topic"
            return f"Goal: Learn {learning_topic} effectively, Timeline: 6 months"
    
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
        
        # Extract data from rich UserPersona schema
        goal = user_profile.goals[0] if user_profile.goals else None
        learning_preferences = user_profile.learning_preferences.preferences
        
        # Build knowledge bridges dynamically from user's expertise
        knowledge_bridges = self._generate_knowledge_bridges(user_profile.expertise, learning_topic)
        
        # Format core expertise for display
        expertise_str = "; ".join(
            f"{skill.domain}: {skill.level} ({skill.confidence}/10)" 
            for skill in user_profile.expertise
        )
        
        formatted_context = {
            "learning_topic": learning_topic,
            "primary_goal": goal.specific if goal else f"Learn {learning_topic} effectively",
            "specific_outcome": goal.measurable[0] if goal and goal.measurable else f"Gain practical knowledge in {learning_topic}",
            "target_timeline": goal.time_bound if goal else "6 months",
            "success_metrics": ", ".join(goal.measurable) if goal and goal.measurable else f"Understand core concepts, Apply {learning_topic} in practice, Build confidence",
            "explanation_preference": learning_preferences[0] if learning_preferences else "clear explanations with rich context",
            "example_types": ", ".join(learning_preferences[1:3]) if len(learning_preferences) > 1 else "real-world applications, practical examples",
            "visual_preferences": ", ".join([pref for pref in learning_preferences if "diagram" in pref or "visual" in pref]) or "diagrams, mindmaps, flowcharts",
            "content_structure": "progressive complexity building on existing knowledge",
            "core_expertise": expertise_str,
            "knowledge_bridges": knowledge_bridges,
            "specific_gaps": ", ".join(user_profile.knowledge_gaps),
            "rag_existing_books_summary": user_profile.summary if user_profile.summary else self._summarize_existing_knowledge(existing_knowledge),
            "industry_benchmarks": f"Industry standards for {learning_topic} curriculum",
            "current_trends": f"Current best practices and emerging trends in {learning_topic}",
            "expert_recommendations": f"Learning paths recommended by {learning_topic} experts and practitioners",
        }
        
        return PERSONALIZED_TOC_PROMPT.format(**formatted_context)
    
    def _generate_knowledge_bridges(self, expertise: List, target_domain: str = "AI") -> str:
        """Generate knowledge bridges dynamically from user's expertise."""
        bridges = []
        
        for skill in expertise:
            # Only include domains where user has meaningful experience (confidence >= 6)
            if skill.confidence >= 6:
                bridges.append(f"{skill.domain} to {target_domain}")
        
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