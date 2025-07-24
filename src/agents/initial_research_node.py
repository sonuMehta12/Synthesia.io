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
            
            # Extract info from array structure for display
            agent_plans = execution_plan.get("agent_plans", [])
            activated_agents = []
            total_tasks = 0
            critical_tasks = 0
            
            for agent_plan in agent_plans:
                agent_name = agent_plan.get("child_agent_name", "unknown")
                is_activated = agent_plan.get("activation", False)
                research_plan = agent_plan.get("research_plan", [])
                
                if is_activated:
                    activated_agents.append(agent_name)
                    total_tasks += len(research_plan)
                    critical_tasks += len([task for task in research_plan if task.get("task_priority") == "critical"])
            
            print(f"   Activated Agents: {', '.join(activated_agents)}")
            print(f"   Total Tasks: {total_tasks}")
            print(f"   Critical Tasks: {critical_tasks}")
            print(f"   Learning Topic: {learning_topic}")
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
        
        Template outputs array structure:
        [
          {
            "child_agent_name": "knowledge_synthesizer",
            "activation": boolean,
            "research_plan": [
              {
                "task_name": "...",
                "task_status": "pending", 
                "task_priority": "critical|high|medium|low",
                "expected_outcome": "...",
                "user_resource_connection": "..."
              }
            ]
          },
          {
            "child_agent_name": "intelligence_gatherer",
            "activation": boolean,
            "research_plan": [...]
          }
        ]
        
        Args:
            raw_response: Raw string response from Strategic Planner LLM
            
        Returns:
            Validated execution plan dictionary conforming to template structure
            
        Raises:
            ValueError: If response cannot be parsed or fails validation
        """
        try:
            # Enhanced JSON cleaning - handle various formatting issues
            cleaned_response = raw_response.strip()
            
            # Remove common markdown formatting
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            # Remove extra whitespace and newlines at start/end
            cleaned_response = cleaned_response.strip()
            
            # Try to find JSON array bounds if response has extra text
            start_bracket = cleaned_response.find('[')
            end_bracket = cleaned_response.rfind(']')
            
            if start_bracket != -1 and end_bracket != -1 and start_bracket < end_bracket:
                # Extract just the JSON array part
                cleaned_response = cleaned_response[start_bracket:end_bracket + 1]
            
            # Additional cleaning - remove any leading/trailing non-JSON text
            cleaned_response = cleaned_response.strip()
            
            # Log the cleaned response for debugging
            print(f"🔍 Parsing Strategic Plan JSON (length: {len(cleaned_response)} chars)")
            if len(cleaned_response) < 200:
                print(f"🔍 JSON Preview: {cleaned_response[:100]}...")
            
            # Parse JSON - expecting array structure from template
            agent_plans = json.loads(cleaned_response)
            
            # Validate it's an array
            if not isinstance(agent_plans, list):
                raise ValueError("Strategic planner must return array of agent plans")
            
            # Validate each agent plan
            knowledge_synthesizer_found = False
            for agent_plan in agent_plans:
                # Validate required fields for each agent
                required_fields = ["child_agent_name", "activation", "research_plan"]
                for field in required_fields:
                    if field not in agent_plan:
                        raise ValueError(f"Missing required field in agent plan: {field}")
                
                # Check if knowledge_synthesizer is present and activated
                if agent_plan["child_agent_name"] == "knowledge_synthesizer":
                    knowledge_synthesizer_found = True
                    if not agent_plan.get("activation", False):
                        raise ValueError("knowledge_synthesizer must always be activated")
                
                # Validate research_plan structure
                research_plan = agent_plan["research_plan"]
                if not isinstance(research_plan, list):
                    raise ValueError("research_plan must be a list")
                
                # Validate each task in research plan
                for task in research_plan:
                    required_task_fields = ["task_name", "task_status", "task_priority", "expected_outcome", "user_resource_connection"]
                    for field in required_task_fields:
                        if field not in task:
                            raise ValueError(f"Missing required field in task: {field}")
                    
                    # Validate task_priority values
                    if task["task_priority"] not in ["critical", "high", "medium", "low"]:
                        raise ValueError(f"Invalid task_priority: {task['task_priority']}")
            
            # Ensure knowledge_synthesizer is present
            if not knowledge_synthesizer_found:
                raise ValueError("knowledge_synthesizer must be present in agent plans")
            
            # Convert array to structured format for internal use
            execution_plan = {
                "plan_id": f"plan_{uuid.uuid4().hex[:8]}",
                "agent_plans": agent_plans,  # Store original array structure
                "created_at": datetime.now().isoformat()
            }
            
            print(f"✅ Strategic Plan Parsed Successfully: {len(agent_plans)} agents")
            
            return execution_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from Strategic Planner: {e}")
            logger.error(f"Raw response (first 500 chars): {raw_response[:500]}")
            raise ValueError(f"Invalid JSON response from Strategic Planner LLM: {e}")
        
        except Exception as e:
            logger.error(f"Execution plan validation failed: {e}")
            logger.error(f"Raw response (first 500 chars): {raw_response[:500]}")
            raise ValueError(f"Execution plan validation failed: {e}")
    
    def _apply_execution_plan_guidance(self, execution_plan: Dict[str, Any]) -> str:
        """
        Convert execution plan into strategic guidance for Knowledge Synthesizer prompt.
        
        Extracts guidance from the array structure returned by strategic planner template:
        [
          {
            "child_agent_name": "knowledge_synthesizer",
            "activation": boolean,
            "research_plan": [
              {
                "task_name": "...",
                "task_priority": "critical|high|medium|low",
                "expected_outcome": "...",
                "user_resource_connection": "..."
              }
            ]
          }
        ]
        
        Args:
            execution_plan: Validated execution plan from Strategic Planner
            
        Returns:
            Formatted strategic guidance string to append to Knowledge Synthesizer prompt
        """
        guidance_parts = []
        
        # Extract agent plans from execution plan
        agent_plans = execution_plan.get("agent_plans", [])
        
        # Find knowledge synthesizer plan
        knowledge_synthesizer_plan = None
        for agent_plan in agent_plans:
            if agent_plan.get("child_agent_name") == "knowledge_synthesizer":
                knowledge_synthesizer_plan = agent_plan
                break
        
        if not knowledge_synthesizer_plan:
            return "**STRATEGIC GUIDANCE**: Use general comprehensive approach for ToC generation"
        
        # Extract strategic insights from research plan
        research_plan = knowledge_synthesizer_plan.get("research_plan", [])
        
        # Group tasks by priority
        critical_tasks = []
        high_priority_tasks = []
        focus_areas = []
        
        for task in research_plan:
            task_name = task.get("task_name", "")
            task_priority = task.get("task_priority", "medium")
            expected_outcome = task.get("expected_outcome", "")
            user_connection = task.get("user_resource_connection", "")
            
            # Collect focus areas from task names
            if "fundamental" in task_name.lower() or "basic" in task_name.lower():
                focus_areas.append("fundamentals")
            if "practical" in task_name.lower() or "application" in task_name.lower():
                focus_areas.append("practical_applications")
            if "advanced" in task_name.lower() or "expert" in task_name.lower():
                focus_areas.append("advanced_concepts")
            
            # Group by priority
            if task_priority == "critical":
                critical_tasks.append(f"{task_name}: {expected_outcome}")
            elif task_priority == "high":
                high_priority_tasks.append(f"{task_name}: {expected_outcome}")
        
        # Build strategic guidance
        if critical_tasks:
            guidance_parts.append(f"**CRITICAL PRIORITIES**: {'; '.join(critical_tasks)}")
        
        if high_priority_tasks:
            guidance_parts.append(f"**HIGH PRIORITY TASKS**: {'; '.join(high_priority_tasks)}")
        
        if focus_areas:
            unique_focus_areas = list(set(focus_areas))
            guidance_parts.append(f"**STRATEGIC FOCUS AREAS**: {', '.join(unique_focus_areas)}")
        
        # Extract user resource connections
        user_connections = [task.get("user_resource_connection", "") for task in research_plan if task.get("user_resource_connection")]
        if user_connections:
            guidance_parts.append(f"**USER RESOURCE INTEGRATION**: {'; '.join(user_connections[:2])}")  # Limit to first 2
        
        # Add quality guidance based on task complexity
        task_count = len(research_plan)
        if task_count >= 5:
            guidance_parts.append("**QUALITY STANDARD**: Comprehensive coverage - ensure deep personalization")
        elif task_count >= 3:
            guidance_parts.append("**QUALITY STANDARD**: Balanced approach - focus on core concepts with personalization")
        else:
            guidance_parts.append("**QUALITY STANDARD**: Focused approach - prioritize essential concepts")
        
        return "\n".join(guidance_parts) if guidance_parts else "**STRATEGIC GUIDANCE**: Apply general comprehensive ToC generation approach"
    
    def _create_fallback_execution_plan(self, learning_topic: str) -> Dict[str, Any]:
        """
        Create a fallback execution plan when Strategic Planner fails.
        
        This ensures the workflow can continue even if strategic planning fails,
        using reasonable defaults based on the learning topic. Returns array structure
        matching the strategic planner template.
        
        Args:
            learning_topic: The topic for which to create fallback plan
            
        Returns:
            Dictionary with fallback execution plan and planning_success: False
        """
        print("⚠️  FALLBACK EXECUTION PLAN - Strategic planning failed")
        print()
        
        # Create fallback array structure matching template
        fallback_agent_plans = [
            {
                "child_agent_name": "knowledge_synthesizer",
                "activation": True,
                "research_plan": [
                    {
                        "task_name": f"Generate comprehensive personalized ToC for {learning_topic}",
                        "task_status": "pending",
                        "task_priority": "critical",
                        "expected_outcome": f"Complete table of contents covering {learning_topic} fundamentals and applications",
                        "user_resource_connection": "Build foundation that complements any existing user knowledge"
                    },
                    {
                        "task_name": f"Identify prerequisite concepts for {learning_topic}",
                        "task_status": "pending", 
                        "task_priority": "high",
                        "expected_outcome": f"Clear understanding of what knowledge is needed before learning {learning_topic}",
                        "user_resource_connection": "Ensure learning path builds on user's current expertise level"
                    },
                    {
                        "task_name": f"Create practical application roadmap for {learning_topic}",
                        "task_status": "pending",
                        "task_priority": "medium",
                        "expected_outcome": f"Actionable projects and exercises for applying {learning_topic} knowledge",
                        "user_resource_connection": "Connect theoretical concepts to user's practical goals"
                    }
                ]
            },
            {
                "child_agent_name": "intelligence_gatherer",
                "activation": False,
                "research_plan": [
                    {
                        "task_name": "No intelligence gathering needed for fallback plan",
                        "task_status": "pending",
                        "task_priority": "low", 
                        "expected_outcome": "Intelligence gatherer not activated in fallback mode",
                        "user_resource_connection": "Fallback relies on existing knowledge synthesis only"
                    }
                ]
            }
        ]
        
        fallback_plan = {
            "plan_id": f"fallback_{uuid.uuid4().hex[:8]}",
            "agent_plans": fallback_agent_plans,
            "created_at": datetime.now().isoformat()
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