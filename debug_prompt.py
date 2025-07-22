#!/usr/bin/env python3
"""
Debug script to inspect the initial research prompt generation.
Run this to see exactly what prompt is being generated for the LLM.
"""

import sys
import os

# Add src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now we can import with absolute paths
from src.agents.initial_research_node import InitialResearchNode
from src.models.persona import get_hardcoded_sonu_persona
from src.prompts.initial_research import PERSONALIZED_TOC_PROMPT


def inspect_prompt_generation(topic: str = "Python programming"):
    """
    Generate and display the prompt that would be sent to the LLM.
    
    Args:
        topic: The topic to generate a prompt for
    """
    print("🔍 PROMPT INSPECTION TOOL")
    print("=" * 60)
    print(f"Topic: {topic}")
    print("=" * 60)
    
    # Create the research node
    research_node = InitialResearchNode()
    
    # Get the persona data
    persona = get_hardcoded_sonu_persona()
    
    # Prepare the context (same as in the actual node)
    prompt_context = research_node._prepare_prompt_context(persona, topic)
    
    print("\n📋 PROMPT CONTEXT VARIABLES:")
    print("-" * 40)
    for key, value in prompt_context.items():
        print(f"{key}: {value[:100]}{'...' if len(str(value)) > 100 else ''}")
    
    print(f"\n📝 RENDERED PROMPT:")
    print("=" * 80)
    
    # Render the prompt template with the context
    try:
        rendered_prompt = PERSONALIZED_TOC_PROMPT.format(**prompt_context)
        print(rendered_prompt)
    except Exception as e:
        print(f"❌ Error rendering prompt: {e}")
        print("\n🔧 Missing variables:")
        # Find missing variables
        import re
        variables_in_template = re.findall(r'\{(\w+)\}', PERSONALIZED_TOC_PROMPT)
        missing_vars = [var for var in variables_in_template if var not in prompt_context]
        for var in missing_vars:
            print(f"  - {var}")
    
    print("=" * 80)
    print("✅ Prompt inspection complete!")


def compare_prompts_for_different_topics():
    """Compare how prompts differ for different topics."""
    topics = [
        "Python programming",
        "Machine learning", 
        "AI evaluations",
        "Product management",
        "Data science"
    ]
    
    print("🔍 COMPARING PROMPTS FOR DIFFERENT TOPICS")
    print("=" * 60)
    
    research_node = InitialResearchNode()
    persona = get_hardcoded_sonu_persona()
    
    for topic in topics:
        print(f"\n📖 Topic: {topic}")
        print("-" * 40)
        
        prompt_context = research_node._prepare_prompt_context(persona, topic)
        
        # Show key differences (you could expand this)
        print(f"Context prepared with {len(prompt_context)} variables")
        print(f"Primary goal: {prompt_context['primary_goal']}")
        print(f"Specific gaps: {prompt_context['specific_gaps'][:100]}...")


if __name__ == "__main__":
    # Allow command line topic specification
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "Python programming"
    
    print("Choose an option:")
    print("1. Inspect prompt for a specific topic")
    print("2. Compare prompts for different topics")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "2":
        compare_prompts_for_different_topics()
    else:
        inspect_prompt_generation(topic) 