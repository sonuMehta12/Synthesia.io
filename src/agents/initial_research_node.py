"""
InitialResearchNode: Generates a draft Table of Contents (ToC) and summaries for the topic.
This is a placeholder/dummy node for the initial workflow.
"""
from typing import Dict, Any, List
from src.prompts.initial_research import PERSONALIZED_TOC_PROMPT
from src.models.persona import get_hardcoded_sonu_persona

class InitialResearchNode:
    def generate_toc(self, context: Dict[str, Any], topic: str) -> Dict[str, Any]:
        # TODO: Integrate real RAG for existing books on topic
        persona = get_hardcoded_sonu_persona()
        # Simulated RAG summary for 'ai_evaluations'
        rag_summary = persona.get("rag_existing_books_summary", "No prior books found on this topic.")
        # Simulate industry benchmarks, trends, expert recommendations
        industry_benchmarks = "AI product management curriculum from top universities."
        current_trends = "Emphasis on practical AI evaluation, LLM safety, and real-world case studies."
        expert_recommendations = "Follow learning paths from leading AI PMs and product teams."
        # Extract fields for prompt
        goal = persona["goals"]["current_goals"][0]
        learning_style = persona["learning_profile"]["learning_style"]
        core_expertise = persona["knowledge_foundation"]["core_expertise"]
        specific_gaps = persona["knowledge_foundation"]["ai_knowledge_state"]["specific_gaps"]
        # For knowledge bridges, just join keys for now
        knowledge_bridges = "Marketing to AI, UX to AI, Frontend Dev to AI"
        # Render prompt
        prompt = PERSONALIZED_TOC_PROMPT.format(
            primary_goal=goal["primary_goal"],
            specific_outcome=goal["specific_outcome"],
            target_timeline=goal["target_timeline"],
            success_metrics=", ".join(goal["success_metrics"]),
            explanation_preference=learning_style["explanation_preference"],
            example_types=", ".join(learning_style["example_types"]),
            visual_preferences=", ".join(learning_style["visual_preferences"]),
            content_structure=learning_style["content_structure"],
            core_expertise="; ".join(f"{k}: {v['level']} ({v.get('confidence', '?')}/10)" for k, v in core_expertise.items()),
            knowledge_bridges=knowledge_bridges,
            specific_gaps=", ".join(specific_gaps),
            rag_existing_books_summary=rag_summary,
            industry_benchmarks=industry_benchmarks,
            current_trends=current_trends,
            expert_recommendations=expert_recommendations,
        )
        print("\n--- Rendered Initial Research Prompt ---\n")
        print(prompt)
        print("\n--- End Prompt ---\n")
        # TODO: Call LLM with prompt and parse output
        toc = [
            {"title": "Introduction to AI Evaluations"},
            {"title": "Core Concepts in AI Evaluation"},
            {"title": "Practical Applications and Case Studies"},
            {"title": "Advanced Topics and Future Trends"},
        ]
        summaries = {section["title"]: f"Summary for {section['title']}..." for section in toc}
        return {"toc": toc, "summaries": summaries} 