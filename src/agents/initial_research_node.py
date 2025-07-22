"""
InitialResearchNode: Generates a draft Table of Contents (ToC) and summaries for the topic.
This node calls the LLM with a personalized prompt and parses the structured JSON response.
"""
import json
import logging
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..prompts.initial_research import PERSONALIZED_TOC_PROMPT
from ..models.state import PersonalizedBookStructure, BookChapter
from ..utils.config import config

logger = logging.getLogger(__name__)


class InitialResearchNode:
    """
    Generates personalized Table of Contents using LLM.
    
    This node takes user context and topic, creates a personalized prompt,
    calls the LLM, and parses the structured JSON response into typed data.
    """
    
    def __init__(self):
        """Initialize the Initial Research Node."""
        self.llm = ChatOpenAI(
            model=config.DEFAULT_MODEL,
            temperature=0.3,  # Slightly higher for creativity in ToC generation
            max_tokens=2000,  # Enough for detailed ToC with multiple chapters
        )
        self.prompt_template = PromptTemplate.from_template(PERSONALIZED_TOC_PROMPT)
        
        # Create the LLM chain
        self.generation_chain = (
            self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("InitialResearchNode initialized successfully")
    
    def generate_toc(self, context: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """
        Generate a personalized Table of Contents for the given topic.
        
        UPDATED: Now uses assembled context from ContextAssembler instead of hardcoded persona.
        This ensures all nodes use centralized context and supports scalable architecture.
        
        Args:
            context: Assembled context from ContextAssembler containing user_profile, 
                    existing_knowledge, topic_context, and other centralized data
            topic: The topic to create a book about (fallback if topic_context not available)
            
        Returns:
            Dictionary containing the structured book data
        """
        try:
            # UPDATED: Extract data from assembled context instead of hardcoded persona
            # This allows ContextAssembler to provide data from various sources (DB, APIs, etc.)
            learning_topic = context.get("topic_context", topic)
            
            # Prepare context for prompt using assembled data
            prompt_context = self._prepare_prompt_context(context, learning_topic)
            
            logger.info(f"Generating ToC for topic: {learning_topic}")
            logger.debug(f"Prompt context prepared with {len(prompt_context)} fields")
            
            # Generate the ToC using LLM
            raw_response = self.generation_chain.invoke(prompt_context)
            
            # Parse and validate the JSON response
            book_structure = self._parse_and_validate_response(raw_response)
            
            logger.info(f"Successfully generated ToC with {len(book_structure['chapters'])} chapters")
            
            # Return the new structured format only
            return {
                "book_structure": book_structure
            }
            
        except Exception as e:
            logger.error(f"Error generating ToC: {e}")
            # Return fallback data structure
            return self._create_fallback_response(learning_topic)
    
    def _prepare_prompt_context(self, context: Dict[str, Any], learning_topic: str) -> Dict[str, str]:
        """
        Prepare the context dictionary for the prompt template.
        
        UPDATED: Now extracts data from assembled context instead of hardcoded persona.
        This method is responsible for formatting assembled context data into the specific
        format required by the PERSONALIZED_TOC_PROMPT template.
        
        Args:
            context: Assembled context from ContextAssembler
            learning_topic: The specific topic the user wants to learn
            
        Returns:
            Dictionary formatted for PERSONALIZED_TOC_PROMPT template
        """
        # Extract user profile from assembled context
        user_profile = context.get("user_profile", {})
        existing_knowledge = context.get("existing_knowledge", [])
        
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
            
            return {
                "learning_topic": learning_topic,  # CRITICAL: Add the learning topic
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
            
            return {
                "learning_topic": learning_topic,  # CRITICAL: Add the learning topic
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
    
    def _generate_knowledge_bridges(self, core_expertise: Dict[str, Any], target_domain: str = "AI") -> str:
        """
        Generate knowledge bridges dynamically from user's expertise.
        
        Args:
            core_expertise: Dictionary of user's expertise areas
            target_domain: The domain to bridge to (e.g., "AI", "ML")
            
        Returns:
            Comma-separated string of knowledge bridges
        """
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
        """
        Summarize existing books/knowledge for prompt context.
        
        Args:
            existing_knowledge: List of existing books/resources from assembled context
            
        Returns:
            Formatted summary string for prompt template
        """
        if not existing_knowledge:
            return "No prior books found on this topic."
        
        summaries = []
        for book in existing_knowledge[:3]:  # Limit to top 3 for context window
            title = book.get("title", "Unknown")
            topic = book.get("topic", "General")
            summary = book.get("summary", "No summary available")
            summaries.append(f"'{title}' (Topic: {topic}) - {summary}")
        
        return "; ".join(summaries)
    
    def _parse_and_validate_response(self, raw_response: str) -> PersonalizedBookStructure:
        """
        Parse the LLM response and validate it matches our expected schema.
        
        Args:
            raw_response: Raw string response from LLM
            
        Returns:
            Validated PersonalizedBookStructure
            
        Raises:
            ValueError: If response cannot be parsed or validated
        """
        try:
            # Clean the response (remove any markdown formatting)
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            parsed_data = json.loads(cleaned_response)
            
            # Validate required fields
            required_fields = ["title", "introduction", "chapters"]
            for field in required_fields:
                if field not in parsed_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate chapters structure
            if not isinstance(parsed_data["chapters"], list):
                raise ValueError("Chapters must be a list")
            
            if len(parsed_data["chapters"]) == 0:
                raise ValueError("Must have at least one chapter")
            
            # Validate each chapter
            for i, chapter in enumerate(parsed_data["chapters"]):
                required_chapter_fields = ["chapter_number", "title", "summary", "personalization_rationale"]
                for field in required_chapter_fields:
                    if field not in chapter:
                        raise ValueError(f"Chapter {i+1} missing required field: {field}")
            
            logger.info("JSON response successfully validated")
            return PersonalizedBookStructure(
                title=parsed_data["title"],
                introduction=parsed_data["introduction"],
                chapters=[
                    BookChapter(
                        chapter_number=chapter["chapter_number"],
                        title=chapter["title"],
                        summary=chapter["summary"],
                        personalization_rationale=chapter["personalization_rationale"]
                    )
                    for chapter in parsed_data["chapters"]
                ]
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {raw_response[:500]}...")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            raise ValueError(f"Response validation failed: {e}")
    
    def _create_fallback_response(self, topic: str) -> Dict[str, Any]:
        """Create a fallback response when LLM generation fails."""
        logger.warning("Using fallback ToC generation")
        
        fallback_structure = PersonalizedBookStructure(
            title=f"Learning {topic}: A Personalized Guide",
            introduction=f"This book is designed to help you learn {topic} based on your specific background and goals.",
            chapters=[
                BookChapter(
                    chapter_number=1,
                    title=f"Introduction to {topic}",
                    summary=f"Fundamental concepts and overview of {topic}",
                    personalization_rationale="Starting with basics to build a solid foundation"
                ),
                BookChapter(
                    chapter_number=2,
                    title=f"Core Concepts in {topic}",
                    summary=f"Deep dive into the essential elements of {topic}",
                    personalization_rationale="Building on your existing knowledge to accelerate learning"
                ),
                BookChapter(
                    chapter_number=3,
                    title=f"Practical Applications of {topic}",
                    summary=f"Real-world examples and hands-on practice with {topic}",
                    personalization_rationale="Connecting theory to practice for immediate application"
                ),
            ]
        )
        
        return {
            "book_structure": fallback_structure
        } 