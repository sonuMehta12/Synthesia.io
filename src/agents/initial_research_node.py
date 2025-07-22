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
from ..models.persona import get_hardcoded_sonu_persona
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
        
        Args:
            context: User context including profile and preferences
            topic: The topic to create a book about
            
        Returns:
            Dictionary containing the structured book data
        """
        try:
            # Get persona data
            persona = get_hardcoded_sonu_persona()
            
            # Prepare context for prompt
            prompt_context = self._prepare_prompt_context(persona, topic)
            
            logger.info(f"Generating ToC for topic: {topic}")
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
            return self._create_fallback_response(topic)
    
    def _prepare_prompt_context(self, persona: Dict[str, Any], topic: str) -> Dict[str, str]:
        """Prepare the context dictionary for the prompt template."""
        
        # Extract goal information
        goal = persona["goals"]["current_goals"][0]
        learning_style = persona["learning_profile"]["learning_style"]
        core_expertise = persona["knowledge_foundation"]["core_expertise"]
        specific_gaps = persona["knowledge_foundation"]["ai_knowledge_state"]["specific_gaps"]
        
        # Build knowledge bridges dynamically from user's expertise
        knowledge_bridges = self._generate_knowledge_bridges(core_expertise, "AI")
        
        # Format core expertise for display
        expertise_str = "; ".join(
            f"{k}: {v['level']} ({v.get('confidence', '?')}/10)" 
            for k, v in core_expertise.items()
        )
        
        return {
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
            "rag_existing_books_summary": persona.get("rag_existing_books_summary", "No prior books found on this topic."),
            "industry_benchmarks": "AI product management curriculum from top universities.",
            "current_trends": "Emphasis on practical AI evaluation, LLM safety, and real-world case studies.",
            "expert_recommendations": "Follow learning paths from leading AI PMs and product teams.",
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