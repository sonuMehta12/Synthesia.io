#!/usr/bin/env python3
"""
Demo script for the Learning Agent Intent Classifier.

This script demonstrates the intent classification functionality
and allows users to test the system interactively for the book creation MVP.
"""

import os
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.intent_classifier import IntentClassifier
from src.agents.state_manager import StateManager
from src.models.intents import IntentType
from src.utils.config import config


def print_banner():
    """Print the demo banner."""
    print("🎓 Learning Agent - Intent Classification Demo")
    print("=" * 50)
    print("This demo showcases the first node of our learning agent:")
    print("🧠 Intent Classifier - Analyzes user input and determines intent")
    print("📊 State Manager - Manages user profiles and book requests")
    print("📚 Book Creation MVP - Ready for book generation workflow")
    print("=" * 50)


def print_intent_result(result: Dict[str, Any]):
    """Print the intent classification result in a formatted way."""
    print(f"\n📋 Classification Result:")
    print(f"   Intent: {result['intent']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    
    if result.get('topic'):
        print(f"   Topic: {result['topic']}")
    
    if result.get('content'):
        print(f"   Content: {result['content'][:100]}...")
    
    if result.get('metadata'):
        print(f"   Model: {result['metadata'].get('model_used', 'Unknown')}")
        print(f"   Timestamp: {result['metadata'].get('timestamp', 'Unknown')}")


def run_demo_tests():
    """Run predefined demo tests for book creation MVP."""
    print("\n🧪 Running Demo Tests")
    print("-" * 30)
    
    # Initialize the intent classifier
    classifier = IntentClassifier()
    
    # Test cases for book creation MVP
    test_cases = [
        {
            "input": "I want to learn Python programming",
            "description": "Learning request (will create a book)"
        },
        {
            "input": "Add this information about machine learning to my knowledge base",
            "description": "Knowledge addition request"
        },
        {
            "input": "Generate a summary of my learning progress",
            "description": "Summary generation request"
        },
        {
            "input": "Update my learning preferences to focus on practical projects",
            "description": "Profile update request"
        },
        {
            "input": "Tell me a joke",
            "description": "General chat request"
        },
        {
            "input": "Create a guide about web development",
            "description": "Book creation request"
        },
        {
            "input": "How are you today?",
            "description": "Casual conversation"
        },
        {
            "input": "What's the weather like?",
            "description": "General question (not book creation)"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        try:
            result = classifier.classify(test_case['input'])
            print_intent_result(result)
        except Exception as e:
            print(f"❌ Error: {e}")


def interactive_mode():
    """Run interactive mode for user testing."""
    print("\n🎮 Interactive Mode")
    print("-" * 20)
    print("Enter your requests and see how the intent classifier works!")
    print("Examples:")
    print("  • 'I want to learn Python' → LEARN_TOPIC")
    print("  • 'Add this tutorial' → ADD_KNOWLEDGE")
    print("  • 'Tell me a joke' → GENERAL")
    print("  • 'Update my settings' → UPDATE_PROFILE")
    print("Type 'quit' to exit.")
    
    classifier = IntentClassifier()
    
    while True:
        try:
            user_input = input("\n💬 Enter your request: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                print("Please enter a request.")
                continue
            
            print(f"\n🔍 Analyzing: {user_input}")
            result = classifier.classify(user_input)
            print_intent_result(result)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def show_agent_info():
    """Show information about the learning agent."""
    print("\n📋 Agent Information")
    print("-" * 20)
    
    # Configuration info
    print(f"Model: {config.get_intent_classifier_config()['model_name']}")
    print(f"Temperature: {config.get_intent_classifier_config()['temperature']}")
    print(f"Max Tokens: {config.get_intent_classifier_config()['max_tokens']}")
    print(f"Confidence Threshold: {config.get_intent_classifier_config()['confidence_threshold']}")
    
    # Available intents for book creation MVP
    print(f"\nAvailable Intent Types:")
    for intent in IntentType:
        if intent == IntentType.LEARN_TOPIC:
            print(f"   • {intent.value} - Create a book about a topic")
        elif intent == IntentType.ADD_KNOWLEDGE:
            print(f"   • {intent.value} - Add knowledge to existing book")
        elif intent == IntentType.GENERATE_SUMMARY:
            print(f"   • {intent.value} - Create summary of learning")
        elif intent == IntentType.UPDATE_PROFILE:
            print(f"   • {intent.value} - Update user preferences")
        elif intent == IntentType.GENERAL:
            print(f"   • {intent.value} - General chat/conversation")
        else:
            print(f"   • {intent.value}")
    
    # Configuration status
    print(f"\nConfiguration Status:")
    if config.OPENAI_API_KEY:
        print("   ✅ OpenAI API Key: Configured")
    else:
        print("   ❌ OpenAI API Key: Not configured")
    
    if config.ANTHROPIC_API_KEY:
        print("   ✅ Anthropic API Key: Configured")
    else:
        print("   ❌ Anthropic API Key: Not configured")


def main():
    """Main demo function."""
    print_banner()
    
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed!")
        print("Please set your API keys in the .env file or environment variables.")
        return
    
    # Show agent information
    show_agent_info()
    
    # Run demo tests
    run_demo_tests()
    
    # Ask if user wants interactive mode
    print("\n" + "=" * 50)
    response = input("Would you like to try interactive mode? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        interactive_mode()
    else:
        print("👋 Demo completed! Run 'python demo.py' again to try interactive mode.")


if __name__ == "__main__":
    main() 