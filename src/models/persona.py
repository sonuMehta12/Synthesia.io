from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# --- TypedDict for compatibility with existing state ---
class UserPersonaDict(TypedDict, total=False):
    user_id: str
    created_at: str
    last_updated: str
    learning_profile: Dict[str, Any]
    goals: Dict[str, Any]
    expertise_profile: Dict[str, Any]
    learning_history: Dict[str, Any]
    knowledge_bridges: Dict[str, Any]
    current_context: Dict[str, Any]
    personalization_data: Dict[str, Any]

# --- Pydantic Model for validation and IDE support ---
class LearningStyle(BaseModel):
    explanation_preference: str
    example_types: List[str]
    visual_preferences: List[str]
    content_structure: str

class LearningProfile(BaseModel):
    learning_style: LearningStyle
    # Add more fields as needed

class Goal(BaseModel):
    goal_id: str
    primary_goal: str
    specific_outcome: str
    target_timeline: str
    priority: str
    success_metrics: List[str]

class Goals(BaseModel):
    current_goals: List[Goal]
    goal_hierarchy: Dict[str, Any]

class ExpertiseDomain(BaseModel):
    level: str
    years_experience: Optional[int]
    confidence: int
    last_assessed: str
    key_areas: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    methodologies: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    areas: Optional[List[str]] = None
    note: Optional[str] = None

class CoreExpertise(BaseModel):
    marketing: Optional[ExpertiseDomain]
    frontend_development: Optional[ExpertiseDomain]
    ux_research: Optional[ExpertiseDomain]
    ux_design: Optional[ExpertiseDomain]
    product_management: Optional[ExpertiseDomain]

class AIKnowledgeState(BaseModel):
    current_level: str
    specific_gaps: List[str]
    adjacent_strengths: List[str]

class KnowledgeFoundation(BaseModel):
    core_expertise: CoreExpertise
    ai_knowledge_state: AIKnowledgeState

class BookCompleted(BaseModel):
    title: str
    topic: str
    completion_date: str
    rating: int
    key_takeaways: List[str]
    application_success: str

class LearningPatterns(BaseModel):
    preferred_chapter_length: str
    completion_rate: int
    peak_learning_times: List[str]
    struggle_indicators: List[str]
    acceleration_factors: List[str]

class LearningHistory(BaseModel):
    books_completed: List[BookCompleted]
    learning_patterns: LearningPatterns

class UserPersona(BaseModel):
    user_id: str
    created_at: str
    last_updated: str
    learning_profile: LearningProfile
    goals: Goals
    knowledge_foundation: KnowledgeFoundation
    learning_history: LearningHistory
    # Add more fields as needed

# --- Hardcoded example for Sonu ---
def get_hardcoded_sonu_persona() -> UserPersonaDict:
    return {
        "user_id": "sonu_12",
        "created_at": "2024-10-15",
        "last_updated": "2025-01-15",
        "learning_profile": {
            "learning_style": {
                "explanation_preference": "simple explanations with rich context",
                "example_types": ["real-world applications", "case studies", "analogies"],
                "visual_preferences": ["mermaid diagrams", "mindmaps", "flowcharts"],
                "content_structure": "start basic, build to complete understanding",
            },
        },
        "goals": {
            "current_goals": [
                {
                    "goal_id": "pm_transition_2025",
                    "primary_goal": "become an AI product manager",
                    "specific_outcome": "get AI product manager entry level job",
                    "target_timeline": "6 months",
                    "priority": "high",
                    "success_metrics": [
                        "Land interviews at AI companies",
                        "Demonstrate AI product knowledge in interviews",
                        "Understand AI evaluation frameworks"
                    ],
                }
            ],
            "goal_hierarchy": {
                "ultimate_goal": "AI Product Manager Career",
                "intermediate_goals": [
                    "Understand AI/ML fundamentals",
                    "Learn AI product evaluation methods",
                    "Build AI product portfolio",
                    "Network in AI product community"
                ],
                "immediate_goals": [
                    "Learn AI evaluation frameworks",
                    "Understand LLM product development"
                ]
            },
        },
        "knowledge_foundation": {
            "core_expertise": {
                "marketing": {
                    "level": "intermediate",
                    "years_experience": 3,
                    "key_areas": ["digital marketing", "growth hacking", "customer acquisition"],
                    "confidence": 8,
                    "last_assessed": "2024-12-01"
                },
                "frontend_development": {
                    "level": "intermediate",
                    "technologies": ["React.js", "JavaScript", "CSS"],
                    "years_experience": 2,
                    "confidence": 7,
                    "last_assessed": "2024-11-15"
                },
                "ux_research": {
                    "level": "intermediate",
                    "methodologies": ["user interviews", "usability testing", "surveys"],
                    "confidence": 8,
                    "last_assessed": "2024-10-30"
                },
                "ux_design": {
                    "level": "beginner_to_intermediate",
                    "tools": ["Figma", "Adobe XD"],
                    "confidence": 6,
                    "last_assessed": "2024-09-20"
                },
                "product_management": {
                    "level": "beginner",
                    "areas": ["roadmap planning", "stakeholder management"],
                    "confidence": 5,
                    "last_assessed": "2024-08-15",
                    "note": "Traditional PM, no AI experience yet"
                }
            },
            "ai_knowledge_state": {
                "current_level": "complete_beginner",
                "specific_gaps": [
                    "AI/ML fundamentals",
                    "LLM capabilities and limitations",
                    "AI product evaluation methods",
                    "AI ethics and safety",
                    "AI product metrics and KPIs"
                ],
                "adjacent_strengths": [
                    "User research skills (can evaluate AI UX)",
                    "Technical background (can understand AI concepts)",
                    "Marketing knowledge (can position AI products)"
                ]
            }
        },
        "learning_history": {
            "books_completed": [
                {
                    "title": "Inspired - Marty Cagan",
                    "topic": "product_management",
                    "completion_date": "2024-09-01",
                    "rating": 5,
                    "key_takeaways": ["product discovery", "outcome-based roadmaps"],
                    "application_success": "high"
                },
                {
                    "title": "Don't Make Me Think - Steve Krug",
                    "topic": "ux_design",
                    "completion_date": "2024-07-15",
                    "rating": 5,
                    "key_takeaways": ["usability principles", "user-centered design"],
                    "application_success": "high"
                }
            ],
            "learning_patterns": {
                "preferred_chapter_length": "15-25 pages",
                "completion_rate": 85,
                "peak_learning_times": ["morning", "early_evening"],
                "struggle_indicators": [
                    "Stops reading when too many new concepts introduced at once",
                    "Needs practical examples within first 3 pages of theory"
                ],
                "acceleration_factors": [
                    "Real company case studies",
                    "Step-by-step implementation guides",
                    "Visual frameworks and diagrams"
                ]
            }
        },
        # Simulated RAG summary for 'ai_evaluations'
        "rag_existing_books_summary": "User has completed introductory readings on product management and UX, but has not yet studied AI evaluation frameworks. They are familiar with evaluation concepts from A/B testing and usability studies, which can serve as analogies."
    } 