from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# --- Core Models ---

class LearningPreferences(BaseModel):
    preferences: List[str] = Field(
        description="List of learning preferences like 'simple explanation', 'real world analogy', 'mermaid diagram'"
    )

class SMARTGoal(BaseModel):
    goal_id: str
    specific: str           # What exactly do you want to achieve?
    measurable: List[str]   # How will you measure progress/success?
    achievable: str         # Is this goal realistic?
    relevant: str          # Why is this goal important?
    time_bound: str        # When will you achieve this?
    priority: str          # "high", "medium", "low"

class SkillLevel(BaseModel):
    domain: str            # e.g., "Python Programming", "Digital Marketing"
    level: str            # "beginner", "intermediate", "advanced"
    confidence: int       # 1-10 scale

class CompletedBook(BaseModel):
    book_id: str
    title: str
    topic: str
    completion_date: str
    rating: Optional[int] = Field(None, description="1-5 star rating")
    key_takeaways: List[str] = []

# --- Main User Persona ---

class UserPersona(BaseModel):
    user_id: str
    created_at: str
    last_updated: str
    
    # Core learning setup
    learning_preferences: LearningPreferences
    goals: List[SMARTGoal]
    expertise: List[SkillLevel]
    
    # Knowledge tracking
    knowledge_gaps: List[str]  # Gaps between current state and goals
    completed_books: List[CompletedBook]
    summary: str  # What user has studied through the app - for RAG/context

# --- Example for Sonu ---

def get_sonu_persona() -> UserPersona:
    return UserPersona(
        user_id="sonu_12",
        created_at="2024-10-15",
        last_updated="2025-01-15",
        
        learning_preferences=LearningPreferences(
            preferences=[
                "simple explanation",
                "real world analogy", 
                "mermaid diagram",
                "case studies",
                "step-by-step guides"
            ]
        ),
        
        goals=[
            SMARTGoal(
                goal_id="ai_pm_transition_2025",
                specific="Become an AI Product Manager at a tech company",
                measurable=[
                    "Land 5+ AI PM interviews",
                    "Get 2+ job offers",
                    "Demonstrate AI product knowledge in interviews"
                ],
                achievable="Yes, with my UX and technical background",
                relevant="AI is the future, and I want to shape AI products",
                time_bound="6 months (by July 2025)",
                priority="high"
            )
        ],
        
        expertise=[
            SkillLevel(domain="Digital Marketing", level="intermediate", confidence=8),
            SkillLevel(domain="React.js Development", level="intermediate", confidence=7),
            SkillLevel(domain="UX Research", level="intermediate", confidence=8),
            SkillLevel(domain="UX Design", level="beginner", confidence=6),
            SkillLevel(domain="Product Management", level="beginner", confidence=5),
            SkillLevel(domain="AI/ML", level="beginner", confidence=2)
        ],
        
        knowledge_gaps=[
            "AI/ML fundamentals and terminology",
            "LLM capabilities and limitations", 
            "AI product evaluation frameworks",
            "AI ethics and safety considerations",
            "AI product metrics and KPIs",
            "Prompt engineering best practices",
            "AI model evaluation techniques"
        ],
        
        completed_books=[
            CompletedBook(
                book_id="inspired_cagan_001",
                title="Inspired - Marty Cagan",
                topic="Product Management",
                completion_date="2024-09-01",
                rating=5,
                key_takeaways=[
                    "Product discovery techniques",
                    "Outcome-based roadmaps",
                    "Customer problem validation"
                ]
            ),
            CompletedBook(
                book_id="dont_make_think_001", 
                title="Don't Make Me Think - Steve Krug",
                topic="UX Design",
                completion_date="2024-07-15",
                rating=5,
                key_takeaways=[
                    "Usability principles",
                    "User-centered design",
                    "Simple navigation design"
                ]
            )
        ],
        
        summary="Sonu has completed foundational readings in product management (Inspired by Marty Cagan) and UX design (Don't Make Me Think). He understands product discovery, outcome-based roadmaps, and usability principles. Currently learning AI fundamentals to transition into AI Product Management. Has strong UX research background that can be leveraged for AI product evaluation. No prior AI/ML study through the platform yet."
    )