"""
Main application for the Learning Agent.

This module sets up the LangGraph workflow with the intent classifier
as the first node, demonstrating the complete learning agent system.
"""

import logging
import sys
from typing import Dict, Any

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .models.state import AgentState
from .agents.intent_classifier import IntentClassifier
from .agents.state_manager import StateManager
from .utils.config import config
from .agents.context_assembler import ContextAssembler
from .agents.initial_research_node import InitialResearchNode
from .agents.user_collab_interface import UserCollabInterface
from .agents.dummy_deep_research_node import DummyDeepResearchNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LearningAgent:
    """
    Main Learning Agent class that orchestrates the LangGraph workflow.
    
    This class sets up the complete learning agent system with the intent
    classifier as the first node, following LangGraph best practices.
    """
    
    def __init__(self):
        """Initialize the Learning Agent."""
        self.intent_classifier = IntentClassifier()
        self.state_manager = StateManager()
        self.context_assembler = ContextAssembler()
        self.initial_research_node = InitialResearchNode()
        self.user_collab_interface = UserCollabInterface()
        self.dummy_deep_research_node = DummyDeepResearchNode()
        self.graph = self._build_graph()
        
        logger.info("Learning Agent initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph ready for execution.
        """
        # Initialize the graph with our state schema
        builder = StateGraph(AgentState)
        
        # Add nodes to the graph
        builder.add_node("state_manager", self.state_manager.manage_state)
        builder.add_node("intent_classifier", self.intent_classifier.classify_with_state)
        builder.add_node("context_assembler", self._context_assembler_node)
        builder.add_node("initial_research_node", self._initial_research_node)
        builder.add_node("user_collab_interface", self._user_collab_interface_node)
        builder.add_node("dummy_deep_research_node", self._dummy_deep_research_node)
        
        # Define the workflow edges
        builder.add_edge(START, "state_manager")
        builder.add_edge("state_manager", "intent_classifier")
        builder.add_edge("intent_classifier", "context_assembler")
        builder.add_edge("context_assembler", "initial_research_node")
        builder.add_edge("initial_research_node", "user_collab_interface")
        builder.add_edge("user_collab_interface", "dummy_deep_research_node")
        builder.add_edge("dummy_deep_research_node", END)
        
        # Compile the graph with memory saver for state persistence
        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)
        
        logger.info("LangGraph workflow built successfully")
        return graph

    def _context_assembler_node(self, state: AgentState) -> AgentState:
        # Use mock data for now
        context = self.context_assembler.assemble_context(
            user_profile=state.get("user_profile"),
            intent_result=state.get("current_intent"),
            existing_books=None,  # Use mock inside assembler
            user_resources=None,  # Use mock inside assembler
        )
        return {**state, "context": context}

    def _initial_research_node(self, state: AgentState) -> AgentState:
        context = state.get("context")
        topic = state.get("current_topic")
        result = self.initial_research_node.generate_toc(context, topic)
        
        # Update state with new structured data
        updated_state = {
            **state, 
            "book_structure": result["book_structure"]
        }
        
        # Keep legacy fields for backward compatibility during migration
        if "toc" in result:
            updated_state["toc"] = result["toc"]
        if "summaries" in result:
            updated_state["summaries"] = result["summaries"]
            
        return updated_state

    def _user_collab_interface_node(self, state: AgentState) -> AgentState:
        book_structure = state.get("book_structure")
        user_profile = state.get("user_profile")
        
        # Handle both new and legacy formats
        if book_structure:
            # Use new structure
            feedback_result = self.user_collab_interface.present_and_collect_feedback(
                book_structure, user_profile
            )
            return {
                **state,
                "book_structure": feedback_result["updated_book_structure"],
                "user_feedback": feedback_result["user_feedback"],
                # Legacy compatibility
                "toc": feedback_result.get("updated_toc", []),
                "summaries": feedback_result.get("updated_summaries", {}),
            }
        else:
            # Fallback to legacy format
            toc = state.get("toc", [])
            summaries = state.get("summaries", {})
            feedback_result = self.user_collab_interface.present_and_collect_feedback_legacy(
                toc, summaries, user_profile
            )
            return {
                **state,
                "book_structure": feedback_result.get("updated_book_structure"),
                "toc": feedback_result["updated_toc"],
                "summaries": feedback_result["updated_summaries"],
                "user_feedback": feedback_result["user_feedback"],
            }

    def _dummy_deep_research_node(self, state: AgentState) -> AgentState:
        book_structure = state.get("book_structure")
        context = state.get("context")
        
        # Handle both new and legacy formats
        if book_structure:
            # Use new structure
            result = self.dummy_deep_research_node.generate_content(book_structure, context)
        else:
            # Fallback to legacy format
            toc = state.get("toc", [])
            summaries = state.get("summaries", {})
            result = self.dummy_deep_research_node.generate_content_legacy(toc, summaries, context)
            
        return {**state, "book_content": result["book_content"]}
    
    def process_user_input(self, user_input: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user input through the learning agent workflow.
        
        Args:
            user_input: The user's input text.
            config: Optional configuration for the graph execution.
            
        Returns:
            Dictionary with the processing results and final state.
        """
        try:
            # Prepare initial state
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "user_profile": None,
                "current_request": None,
                "generated_book": None,
                "current_intent": None,
                "current_topic": None,
                "learning_context": {},
                "session_id": None,
                "timestamp": None,
                "context": None,
                "book_structure": None,
                "user_feedback": None,
                "book_content": None,
                # Legacy fields for backward compatibility
                "toc": None,
                "summaries": None,
            }
            
            # Execute the graph
            if config is None:
                config = {"configurable": {"thread_id": "default"}}
            
            result = self.graph.invoke(initial_state, config)
            
            logger.info(f"User input processed successfully: {user_input[:50]}...")
            return {
                "success": True,
                "input": user_input,
                "intent": result.get("current_intent"),
                "topic": result.get("current_topic"),
                "session_id": result.get("session_id"),
                "timestamp": result.get("timestamp"),
                "book_structure": result.get("book_structure"),
                "user_feedback": result.get("user_feedback"),
                "book_content": result.get("book_content"),
                # Legacy fields for backward compatibility
                "toc": result.get("toc"),
                "summaries": result.get("summaries"),
                "full_state": result,
            }
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return {
                "success": False,
                "error": str(e),
                "input": user_input,
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the learning agent.
        
        Returns:
            Dictionary with agent information and configuration.
        """
        return {
            "agent_type": "Learning Agent",
            "version": "0.1.0",
            "nodes": ["state_manager", "intent_classifier"],
            "intent_classifier_config": self.intent_classifier.get_config(),
            "graph_compiled": self.graph is not None,
        }


def main():
    """Main function to run the learning agent."""
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    # Initialize the learning agent
    agent = LearningAgent()
    
    # Example usage
    print("🎓 Learning Agent - Intent Classification Demo")
    print("=" * 50)
    
    # Test cases
    test_inputs = [
        "I want to learn Python programming",
        "Add this information about machine learning to my knowledge base",
        "Generate a summary of my learning progress",
        "Update my learning preferences to focus on practical projects",
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n🧪 Test {i}: {test_input}")
        print("-" * 40)
        
        result = agent.process_user_input(test_input)
        
        if result["success"]:
            intent = result["intent"]
            print(f"✅ Intent: {intent['intent']}")
            print(f"📊 Confidence: {intent['confidence']:.2f}")
            if intent.get("topic"):
                print(f"🎯 Topic: {intent['topic']}")
            if result.get("session_id"):
                print(f"🆔 Session: {result['session_id']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    print(f"\n📋 Agent Info:")
    agent_info = agent.get_agent_info()
    for key, value in agent_info.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main() 