#!/usr/bin/env python3
"""
Simple script to check the generated prompt without needing OpenAI API setup.
"""

import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def check_prompt_for_topic(topic: str = "Python programming"):
    """Check what prompt gets generated for a topic."""
    
    print("🔍 PROMPT CHECKER")
    print("=" * 60)
    print(f"Topic: {topic}")
    print("=" * 60)
    
    try:
        # Import the modules we need
        from src.models.persona import get_hardcoded_sonu_persona
        from src.prompts.initial_research import PERSONALIZED_TOC_PROMPT
        
        # Get persona data
        persona = get_hardcoded_sonu_persona()
        
        # Extract the same data that InitialResearchNode does
        goal = persona["goals"]["current_goals"][0]
        learning_style = persona["learning_profile"]["learning_style"]
        core_expertise = persona["knowledge_foundation"]["core_expertise"]
        specific_gaps = persona["knowledge_foundation"]["ai_knowledge_state"]["specific_gaps"]
        
        # Build the context dictionary (same logic as in InitialResearchNode)
        knowledge_bridges = "Marketing to AI, UX to AI, Frontend Dev to AI"
        expertise_str = "; ".join(
            f"{k}: {v['level']} ({v.get('confidence', '?')}/10)" 
            for k, v in core_expertise.items()
        )
        
        prompt_context = {
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
        
        print("\n📋 CONTEXT VARIABLES:")
        print("-" * 40)
        for key, value in prompt_context.items():
            print(f"{key}: {str(value)[:80]}{'...' if len(str(value)) > 80 else ''}")
        
        print(f"\n📝 COMPLETE RENDERED PROMPT:")
        print("=" * 80)
        
        # Render the complete prompt
        rendered_prompt = PERSONALIZED_TOC_PROMPT.format(**prompt_context)
        print(rendered_prompt)
        
        print("=" * 80)
        print("✅ Prompt check complete!")
        
        # Check prompt length
        print(f"\n📊 PROMPT STATISTICS:")
        print(f"Total characters: {len(rendered_prompt):,}")
        print(f"Estimated tokens: ~{len(rendered_prompt) // 4:,}")  # Rough estimate
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "Python programming"
    
    check_prompt_for_topic(topic) 