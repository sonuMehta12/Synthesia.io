"""
InitialResearchNode: Multi-Agent ToC Generator (Strategic Planner + Knowledge Synthesizer)

UPDATED: Now contains both Strategic Planner and Knowledge Synthesizer agents in a single file.
This follows the multi-agent architecture where the Strategic Planner analyzes user context
and creates execution plans, then the Knowledge Synthesizer generates ToC based on that plan.

Architecture Pattern:
- Strategic Planner: Analyzes context using chain-of-thought reasoning, creates execution plans
- Knowledge Synthesizer: Generates personalized ToC using execution plan guidance
- ContextAssembler: Handles all context formatting and prompt population
- Single file approach: All ToC generation agents in one place for easy management

Multi-Agent Flow:
1. planner_agent() - Strategic analysis and execution plan creation
2. generate_toc() - Knowledge synthesis guided by execution plan
"""
import json
import logging
import uuid
from typing import Dict, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from .context_assembler import ContextAssembler
from ..models.state import PersonalizedBookStructure, BookChapter
from ..utils.config import config

logger = logging.getLogger(__name__)


class InitialResearchNode:
    """
    Multi-Agent ToC Generator: Strategic Planner + Knowledge Synthesizer
    
    This class contains all ToC generation agents in a single file following the multi-agent
    architecture pattern. It implements both strategic planning and knowledge synthesis
    for generating highly personalized Table of Contents.
    
    Agents:
    1. Strategic Planner (planner_agent): 
       - Analyzes user learning DNA and topic complexity using chain-of-thought reasoning
       - Evaluates user resources and integration strategies
       - Decides agent activation and creates structured execution plans
       - Sets quality standards and success criteria
    
    2. Knowledge Synthesizer (generate_toc):
       - Generates personalized ToC using execution plan guidance
       - Applies strategic insights for focus areas and quality standards
       - Uses ContextAssembler for centralized context management
       - Returns structured book data with personalization rationale
    
    Architecture Benefits:
    - Single file approach for easy management and understanding
    - Sequential execution: planner_agent() → generate_toc()
    - Strategic guidance improves ToC quality and personalization
    - Extensible for future agents (Intelligence Gatherer, Quality Assurance)
    """
    
    def __init__(self):
        """Initialize both Strategic Planner and Knowledge Synthesizer agents."""
        # Strategic Planner LLM - Lower temperature for analytical thinking
        self.planning_llm = ChatOpenAI(
            model=config.DEFAULT_MODEL,
            temperature=0.1,  # Lower temperature for strategic analysis and planning
            max_tokens=1500,  # Sufficient for detailed execution plans
        )
        
        # Knowledge Synthesizer LLM - Higher temperature for creative ToC generation
        self.synthesis_llm = ChatOpenAI(
            model=config.DEFAULT_MODEL,
            temperature=0.3,  # Slightly higher for creativity in ToC generation
            max_tokens=2000,  # Enough for detailed ToC with multiple chapters
        )
        
        # Silent initialization
    
    def planner_agent(self, context_assembler: ContextAssembler) -> Dict[str, Any]:
        """
        Strategic Planner: Master orchestrator that analyzes user context and creates execution plans.
        
        This agent implements chain-of-thought reasoning to:
        1. Analyze user learning DNA and topic complexity
        2. Evaluate user-provided resources and integration strategies  
        3. Decide which sub-agents to activate (Knowledge Synthesizer, Intelligence Gatherer)
        4. Create structured execution plans with success criteria and quality standards
        5. Set strategic guidance for downstream agents
        
        Args:
            context_assembler: ContextAssembler with pre-assembled user context
                              Must contain user_profile, topic_context, existing_knowledge, user_resources
            
        Returns:
            Dictionary containing:
            - execution_plan: Structured JSON plan with user analysis, topic analysis, 
                            agent activation decisions, synthesis strategy, success criteria
            - planning_success: Boolean indicating if planning was successful
            
        Raises:
            RuntimeError: If context_assembler lacks required assembled context
        """
        try:
            # Validate context assembler has required context
            if not context_assembler.raw_context:
                raise RuntimeError("ContextAssembler must have assembled context before strategic planning")
            
            # Get populated strategic planning prompt from ContextAssembler
            populated_prompt = context_assembler.get_populated_prompt("strategic_planner")
            
            # Extract learning topic for logging
            learning_topic = context_assembler.raw_context.get("topic_context", "Unknown Topic")
            
            # Silent analysis
            
            # Invoke Strategic Planner LLM for analysis
            raw_response = self.planning_llm.invoke(populated_prompt)
            
            # Extract content from LLM response
            if hasattr(raw_response, 'content'):
                response_content = raw_response.content
            else:
                response_content = str(raw_response)
            
            # Parse and validate execution plan
            execution_plan = self._parse_and_validate_execution_plan(response_content)
            
            # Add metadata to execution plan
            execution_plan["created_at"] = datetime.now().isoformat()
            execution_plan["learning_topic"] = learning_topic
            
            # Output the execution plan (always visible)
            print("📋 STRATEGIC EXECUTION PLAN GENERATED:")
            print(f"   Plan ID: {execution_plan['plan_id']}")
            print(f"   User Strengths: {execution_plan['user_analysis'].get('learning_strengths', 'N/A')}")
            print(f"   Critical Gaps: {execution_plan['user_analysis'].get('critical_gaps', 'N/A')}")
            print(f"   Topic Complexity: {execution_plan['topic_analysis'].get('complexity_level', 'N/A')}")
            print(f"   Quality Threshold: {execution_plan['synthesis_strategy'].get('quality_threshold', 'N/A')}")
            
            activated_agents = [agent for agent, config in execution_plan["agent_activation"].items() if config.get("activated", False)]
            print(f"   Activated Agents: {', '.join(activated_agents)}")
            print()  # Empty line for readability
            
            return {
                "execution_plan": execution_plan,
                "planning_success": True
            }
            
        except Exception as e:
            logger.error(f"Strategic planning failed: {e}")
            # Return fallback execution plan to ensure workflow continues
            learning_topic = context_assembler.raw_context.get("topic_context", "Unknown Topic")
            return self._create_fallback_execution_plan(learning_topic)
    
    def generate_toc(self, context_assembler: ContextAssembler, execution_plan: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Knowledge Synthesizer: Generate personalized ToC using execution plan guidance.
        
        UPDATED: Now uses execution plan from Strategic Planner to guide ToC generation.
        This enables context-aware synthesis that applies strategic insights for optimal
        personalization, quality standards, and focus areas.
        
        Args:
            context_assembler: ContextAssembler instance with pre-assembled context
                              Must have been initialized with assemble_context() before calling this method
            execution_plan: Optional execution plan from Strategic Planner containing:
                           - agent_activation: Tasks and focus areas for Knowledge Synthesizer
                           - synthesis_strategy: Quality thresholds and personalization depth
                           - user_analysis: Learning strengths and gaps to leverage
            
        Returns:
            Dictionary containing the structured book data with strategic guidance applied
        """
        try:
            # Get fully populated prompt from ContextAssembler
            populated_prompt = context_assembler.get_populated_prompt("knowledge_synthesizer")
            
            # Extract learning topic for logging
            learning_topic = context_assembler.raw_context.get("topic_context", "Unknown Topic")
            
            # Apply execution plan guidance if available
            plan_guidance = ""
            if execution_plan:
                plan_guidance = self._apply_execution_plan_guidance(execution_plan)
                # Silent synthesis
            
            # Enhance prompt with execution plan guidance
            if plan_guidance:
                populated_prompt = f"{populated_prompt}\n\n## STRATEGIC GUIDANCE\n{plan_guidance}"
            
            # Invoke Knowledge Synthesizer LLM
            raw_response = self.synthesis_llm.invoke(populated_prompt)
            
            # Extract content from LLM response
            if hasattr(raw_response, 'content'):
                response_content = raw_response.content
            else:
                response_content = str(raw_response)
            
            # Parse and validate the JSON response
            book_structure = self._parse_and_validate_response(response_content)
            
            # Silent ToC generation success
            
            # Return the structured format
            return {
                "book_structure": book_structure
            }
            
        except Exception as e:
            logger.error(f"Error generating ToC: {e}")
            # Return fallback data structure
            learning_topic = context_assembler.raw_context.get("topic_context", "Unknown Topic")
            return self._create_fallback_response(learning_topic)
    
    def _parse_and_validate_execution_plan(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse and validate the Strategic Planner LLM response into structured execution plan.
        
        Args:
            raw_response: Raw string response from Strategic Planner LLM
            
        Returns:
            Validated execution plan dictionary with required fields
            
        Raises:
            ValueError: If response cannot be parsed or fails validation
        """
        try:
            # Clean the response (remove markdown formatting)
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            execution_plan = json.loads(cleaned_response)
            
            # Validate required top-level fields
            required_fields = [
                "plan_id", "user_analysis", "topic_analysis", 
                "agent_activation", "synthesis_strategy", "success_criteria"
            ]
            for field in required_fields:
                if field not in execution_plan:
                    raise ValueError(f"Missing required field in execution plan: {field}")
            
            # Validate agent_activation structure
            agent_activation = execution_plan["agent_activation"]
            if "knowledge_synthesizer" not in agent_activation:
                raise ValueError("knowledge_synthesizer must be present in agent_activation")
            
            # Validate knowledge_synthesizer is always activated
            if not agent_activation["knowledge_synthesizer"].get("activated", False):
                raise ValueError("knowledge_synthesizer must always be activated")
            
            # Validate synthesis_strategy has required fields
            synthesis_strategy = execution_plan["synthesis_strategy"]
            required_synthesis_fields = ["integration_approach", "personalization_depth", "quality_threshold"]
            for field in required_synthesis_fields:
                if field not in synthesis_strategy:
                    raise ValueError(f"Missing required field in synthesis_strategy: {field}")
            
            # Validate quality threshold is reasonable
            quality_threshold = synthesis_strategy.get("quality_threshold", 0)
            if not isinstance(quality_threshold, (int, float)) or quality_threshold < 50 or quality_threshold > 100:
                raise ValueError("quality_threshold must be a number between 50 and 100")
            
            return execution_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from Strategic Planner: {e}")
            raise ValueError(f"Invalid JSON response from Strategic Planner LLM: {e}")
        
        except Exception as e:
            logger.error(f"Execution plan validation failed: {e}")
            raise ValueError(f"Execution plan validation failed: {e}")
    
    def _apply_execution_plan_guidance(self, execution_plan: Dict[str, Any]) -> str:
        """
        Convert execution plan into strategic guidance for Knowledge Synthesizer prompt.
        
        Args:
            execution_plan: Validated execution plan from Strategic Planner
            
        Returns:
            Formatted strategic guidance string to append to Knowledge Synthesizer prompt
        """
        guidance_parts = []
        
        # Extract key strategic insights
        user_analysis = execution_plan.get("user_analysis", {})
        topic_analysis = execution_plan.get("topic_analysis", {})
        agent_activation = execution_plan.get("agent_activation", {})
        synthesis_strategy = execution_plan.get("synthesis_strategy", {})
        
        # Strategic focus areas from planner
        knowledge_task = agent_activation.get("knowledge_synthesizer", {})
        focus_areas = knowledge_task.get("focus_areas", [])
        if focus_areas:
            guidance_parts.append(f"**STRATEGIC FOCUS AREAS**: {', '.join(focus_areas)}")
        
        # User learning strengths to leverage
        learning_strengths = user_analysis.get("learning_strengths", "")
        if learning_strengths:
            guidance_parts.append(f"**LEVERAGE USER STRENGTHS**: {learning_strengths}")
        
        # Critical gaps to address
        critical_gaps = user_analysis.get("critical_gaps", "")
        if critical_gaps:
            guidance_parts.append(f"**ADDRESS CRITICAL GAPS**: {critical_gaps}")
        
        # Quality and personalization requirements
        quality_threshold = synthesis_strategy.get("quality_threshold", 75)
        personalization_depth = synthesis_strategy.get("personalization_depth", "moderate")
        guidance_parts.append(f"**QUALITY STANDARD**: Achieve {quality_threshold}% quality threshold")
        guidance_parts.append(f"**PERSONALIZATION DEPTH**: {personalization_depth}")
        
        # Topic complexity considerations
        complexity_level = topic_analysis.get("complexity_level", "intermediate")
        guidance_parts.append(f"**TOPIC COMPLEXITY**: {complexity_level} - adjust depth accordingly")
        
        return "\n".join(guidance_parts)
    
    def _create_fallback_execution_plan(self, learning_topic: str) -> Dict[str, Any]:
        """
        Create a fallback execution plan when Strategic Planner fails.
        
        This ensures the workflow can continue even if strategic planning fails,
        using reasonable defaults based on the learning topic.
        
        Args:
            learning_topic: The topic for which to create fallback plan
            
        Returns:
            Dictionary with fallback execution plan and planning_success: False
        """
        print("⚠️  FALLBACK EXECUTION PLAN - Strategic planning failed")
        print()
        
        fallback_plan = {
            "plan_id": f"fallback_{uuid.uuid4().hex[:8]}",
            "user_analysis": {
                "learning_strengths": "General knowledge and learning experience",
                "critical_gaps": f"Fundamental concepts in {learning_topic}",
                "learning_style_match": "Comprehensive approach with practical examples",
                "timeline_pressure": "Moderate - standard learning timeline"
            },
            "topic_analysis": {
                "complexity_level": "intermediate",
                "topic_maturity": "established",
                "current_research_needed": False,
                "practical_urgency": "moderate"
            },
            "agent_activation": {
                "knowledge_synthesizer": {
                    "activated": True,
                    "primary_task": f"Generate comprehensive personalized ToC for {learning_topic}",
                    "focus_areas": ["fundamentals", "practical_applications", "skill_building"],
                    "company_db_priority": "medium"
                },
                "intelligence_gatherer": {
                    "activated": False,
                    "primary_task": "Not activated for fallback plan",
                    "research_focus": [],
                    "time_range": "all_time"
                }
            },
            "synthesis_strategy": {
                "integration_approach": "Single agent output - no synthesis needed",
                "user_resource_priority": "medium",
                "personalization_depth": "moderate",
                "quality_threshold": 75
            },
            "success_criteria": {
                "primary_metrics": ["topic_coverage", "personalization_quality"],
                "quality_standards": ["clear_structure", "actionable_content"],
                "timeline_checkpoints": ["initial_generation", "user_feedback"]
            }
        }
        
        return {
            "execution_plan": fallback_plan,
            "planning_success": False
        }
    
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
            logger.error(f"Invalid JSON from Knowledge Synthesizer: {e}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        except Exception as e:
            logger.error(f"ToC validation failed: {e}")
            raise ValueError(f"Response validation failed: {e}")
    
    def _create_fallback_response(self, topic: str) -> Dict[str, Any]:
        """Create a fallback response when LLM generation fails."""
        # Silent fallback usage
        
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