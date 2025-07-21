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
        
        # Define the workflow edges
        builder.add_edge(START, "state_manager")
        builder.add_edge("state_manager", "intent_classifier")
        builder.add_edge("intent_classifier", END)
        
        # Compile the graph with memory saver for state persistence
        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)
        
        logger.info("LangGraph workflow built successfully")
        return graph
    
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
                "knowledge_state": None,
                "current_intent": None,
                "current_topic": None,
                "learning_context": {},
                "session_id": None,
                "timestamp": None,
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