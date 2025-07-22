#!/usr/bin/env python3
"""
Run the main system with detailed logging to see all prompts and responses.
This temporarily changes the log level to see debug information.
"""

import logging
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import using proper module path
from src.main import LearningAgent
from src.utils.config import config


def run_with_debug_logging(user_input: str = "I want to learn Python programming"):
    """
    Run the learning agent with detailed logging to see prompts and responses.
    
    Args:
        user_input: The input to test with
    """
    # Set up detailed logging
    logging.basicConfig(
        level=logging.INFO,  # Change to DEBUG if you want even more detail
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Override existing logging config
    )
    
    # Set specific loggers to INFO to see our debug output
    logger_names = [
        'src.agents.initial_research_node',
        'src.agents.intent_classifier', 
        'src.agents.user_collab_interface',
        'src.agents.dummy_deep_research_node'
    ]
    
    for logger_name in logger_names:
        logging.getLogger(logger_name).setLevel(logging.INFO)
    
    print("🔍 RUNNING LEARNING AGENT WITH DETAILED LOGGING")
    print("=" * 60)
    print(f"Input: {user_input}")
    print("=" * 60)
    
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed")
        return
    
    # Initialize and run the agent
    agent = LearningAgent()
    result = agent.process_user_input(user_input)
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULT:")
    print("=" * 60)
    
    if result["success"]:
        print(f"✅ Intent: {result['intent']['intent']}")
        print(f"📊 Confidence: {result['intent']['confidence']:.2f}")
        print(f"🎯 Topic: {result.get('topic', 'N/A')}")
        
        if result.get('book_structure'):
            book = result['book_structure']
            print(f"📖 Book Title: {book['title']}")
            print(f"📝 Chapters: {len(book['chapters'])}")
            print(f"📄 Book Content Length: {len(result.get('book_content', ''))}")
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "I want to learn Python programming"
    
    run_with_debug_logging(user_input) 