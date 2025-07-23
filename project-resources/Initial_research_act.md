# Complete Multi-Agent TOC Generation System

## 1. Input Parser Agent

### Purpose
Transform raw user input into structured, actionable data that other agents can process efficiently.

### Detailed Process
1. **Text Preprocessing**
   - Clean and normalize input text
   - Extract key phrases and entities
   - Identify explicit vs implicit requirements

2. **Profile Extraction**
   - Current skills/background analysis
   - Learning goals identification
   - Timeline constraint detection
   - Expertise level assessment
   - Learning style preferences

3. **Validation & Scoring**
   - Confidence scores for each extraction
   - Flag ambiguous or missing information
   - Generate clarifying questions if needed

### Input Format
```
Raw user text: "I'm a marketing manager with 5 years experience. I know some UX basics and want to transition to AI product management in 6 months. I prefer hands-on learning with real examples."
```

### Output Format
```json
{
  "user_profile": {
    "current_background": {
      "primary_skill": "Marketing",
      "experience_years": 5,
      "confidence": 0.9
    },
    "secondary_skills": [
      {"skill": "UX", "level": "basic", "confidence": 0.8}
    ],
    "target_role": "AI Product Manager",
    "timeline": "6 months",
    "learning_preferences": ["hands-on", "real examples"],
    "knowledge_gaps": ["AI/ML fundamentals", "AI evaluation frameworks"]
  },
  "extraction_confidence": 0.85,
  "clarifying_questions": []
}
```

### Prompt Template
```
You are an expert learning consultant. Analyze this user request and extract key information:

USER REQUEST: {user_input}

Extract the following information with confidence scores (0-1):
1. Current professional background and skills
2. Target learning goals
3. Timeline constraints
4. Existing knowledge level
5. Preferred learning style
6. Identified knowledge gaps

Return structured JSON. If information is unclear or missing, generate specific clarifying questions.

Focus on actionable insights that will help design a personalized learning path.
```

---

## 2. State Manager

### Purpose
Central coordination hub that manages data flow, context, and state across all agents without executing business logic.

### Detailed Process
1. **Session Management**
   - Create unique session ID for each user request
   - Track agent execution order and dependencies
   - Manage context window limitations

2. **Data Routing**
   - Route outputs from one agent to appropriate next agents
   - Handle parallel vs sequential execution
   - Merge results from multiple agents when needed

3. **Context Summarization**
   - Monitor token usage across agents
   - Summarize lengthy outputs when context limits approached
   - Maintain essential information while reducing token count

4. **State Persistence**
   - Store intermediate results in Redis
   - Maintain execution history for debugging
   - Enable resume functionality if process fails

### Key Data Structures
```python
{
  "session_id": "uuid-123",
  "user_profile": {...},
  "knowledge_matches": [...],
  "research_plan": {...},
  "research_results": {...},
  "generated_toc": {...},
  "evaluation_scores": {...},
  "execution_log": [
    {"agent": "input_parser", "timestamp": "...", "status": "complete"},
    {"agent": "knowledge_retrieval", "timestamp": "...", "status": "running"}
  ]
}
```

---

## 3. Knowledge Retrieval Agent

### Purpose
Find existing TOCs, patterns, and successful learning paths similar to the user's profile.

### Detailed Process
1. **Vector Search**
   - Convert user profile to embedding
   - Search vector database of existing TOCs
   - Calculate similarity scores

2. **Pattern Matching**
   - Identify successful progression patterns
   - Find TOCs with similar source→target skill transitions
   - Analyze chapter structures and learning sequences

3. **Success Rate Analysis**
   - Retrieve completion rates for similar profiles
   - Identify which approaches worked best
   - Flag potential difficulty points

### Input
User profile JSON from Input Parser Agent

### Output
```json
{
  "similar_tocs": [
    {
      "toc_id": "marketing-to-pm-001",
      "similarity_score": 0.87,
      "success_rate": 0.73,
      "user_profile_match": {
        "background_match": 0.9,
        "goal_match": 0.85,
        "timeline_match": 0.8
      },
      "toc_summary": "Marketing professional transitioning to PM",
      "key_patterns": ["leverage marketing skills", "focus on metrics", "case studies"]
    }
  ],
  "progression_patterns": [
    "foundation → application → specialization",
    "leverage existing skills → bridge gaps → advanced topics"
  ],
  "risk_factors": ["AI technical concepts may be challenging", "6-month timeline is aggressive"]
}
```

### Prompt Template
```
You are a learning path expert. Analyze this user profile against our knowledge base:

USER PROFILE: {user_profile}

Available TOC database contains {database_size} learning paths with success metrics.

Find the top 3 most relevant existing learning paths and explain:
1. Why they match this user's profile
2. What success rates they achieved
3. Key progression patterns that worked
4. Potential risk factors or challenges

Focus on transitions between similar skill sets and successful learning sequences.
```

---

## 4. Research Planning Agent

### Purpose
Identify what current, up-to-date information is needed beyond existing knowledge base.

### Detailed Process
1. **Gap Analysis**
   - Compare user needs against existing knowledge
   - Identify outdated information in knowledge base
   - Find domain-specific current trends

2. **Research Question Generation**
   - Create specific, searchable queries
   - Prioritize by impact on learning path
   - Consider user's timeline constraints

3. **Research Strategy**
   - Determine best sources for each question
   - Set research depth requirements
   - Define success criteria for research

### Input
- User profile
- Knowledge retrieval results
- Current date/context

### Output
```json
{
  "research_plan": {
    "priority_questions": [
      {
        "question": "What are current AI PM interview expectations in 2025?",
        "rationale": "User timeline requires job-ready preparation",
        "search_queries": ["AI product manager interview 2025", "AI PM hiring trends"],
        "expected_sources": ["job boards", "company blogs", "industry reports"],
        "priority": "high"
      }
    ],
    "nice_to_have": [
      {
        "question": "Latest AI evaluation frameworks used in industry",
        "priority": "medium"
      }
    ],
    "research_scope": "current trends, tools, market demand, success stories",
    "estimated_time": "15 minutes"
  }
}
```

### Prompt Template
```
You are a research strategist. Given this user profile and existing knowledge matches, identify what current information we need:

USER PROFILE: {user_profile}
EXISTING KNOWLEDGE: {knowledge_summary}
CURRENT DATE: {current_date}

Create a focused research plan that identifies:
1. Critical knowledge gaps not covered in existing resources
2. Time-sensitive information (trends, tools, market conditions)
3. Specific search queries that will find actionable insights
4. Priority levels based on user's timeline and goals

Limit to 5 high-impact research areas. Each should have clear search queries and expected value to the user.
```

---

## 5. Web Research Agent

### Purpose
Execute research plan by searching for current information and synthesizing findings.

### Detailed Process
1. **Search Execution**
   - Execute search queries from research plan
   - Follow up on promising leads
   - Validate source credibility

2. **Information Synthesis**
   - Extract key insights from search results
   - Identify patterns across sources
   - Summarize findings with citations

3. **Relevance Filtering**
   - Filter results for user-specific relevance
   - Remove outdated or contradictory information
   - Prioritize actionable insights

### Input
Research plan from Research Planning Agent

### Output
```json
{
  "research_results": [
    {
      "question": "Current AI PM interview expectations",
      "findings": [
        {
          "insight": "Technical depth expectations have increased significantly",
          "source": "anthropic.com/careers",
          "date": "2025-01",
          "relevance_score": 0.9
        }
      ],
      "synthesis": "AI PM roles now require deeper technical understanding...",
      "actionable_items": ["Include technical evaluation frameworks", "Add AI safety considerations"]
    }
  ],
  "research_confidence": 0.8,
  "coverage_gaps": ["Salary expectations", "Remote work trends"]
}
```

### Prompt Template
```
You are a research analyst. Execute this research plan and synthesize findings:

RESEARCH PLAN: {research_plan}
USER CONTEXT: {user_profile_summary}

For each research question:
1. Search comprehensively using provided queries
2. Evaluate source credibility and recency
3. Extract insights specifically relevant to the user's situation
4. Provide actionable recommendations

Synthesize findings into clear, user-specific insights with proper citations.
Focus on information that will improve the learning path design.
```

---

## 6. TOC Generator Agent

### Purpose
Create the actual table of contents using all gathered information.

### Detailed Process
1. **Structure Planning**
   - Analyze optimal learning progression
   - Balance foundational vs advanced topics
   - Consider user's timeline constraints

2. **Chapter Design**
   - Create logical chapter flow
   - Write compelling chapter titles
   - Develop personalization rationale

3. **Content Validation**
   - Ensure comprehensive coverage
   - Check for logical gaps or jumps
   - Validate against user goals

### Input
- User profile
- Knowledge matches
- Research results
- TOC schema requirements

### Output
Complete TOC JSON matching the provided schema

### Prompt Template
```
You are an expert curriculum designer. Create a comprehensive table of contents:

USER PROFILE: {user_profile}
EXISTING SUCCESSFUL PATTERNS: {knowledge_patterns}
CURRENT MARKET INSIGHTS: {research_synthesis}
REQUIRED SCHEMA: {toc_schema}

Design a learning path that:
1. Builds systematically on user's existing strengths
2. Addresses identified knowledge gaps
3. Incorporates current market requirements
4. Follows proven progression patterns
5. Fits within user's timeline

Each chapter must include:
- Clear learning objectives
- Personalization rationale explaining why it matters for this specific user
- Logical connection to previous and next chapters

Aim for 8-12 chapters with compelling titles that motivate learning.
```

---

## 7. Quality Evaluator Agent

### Purpose
Assess the generated TOC for quality, completeness, and alignment with user needs.

### Detailed Process
1. **Content Evaluation**
   - Assess logical progression
   - Check coverage completeness
   - Evaluate personalization quality

2. **User Alignment Check**
   - Verify alignment with stated goals
   - Check timeline feasibility
   - Assess skill level appropriateness

3. **Quality Scoring**
   - Generate numerical scores for different dimensions
   - Identify specific improvement areas
   - Compare against successful benchmarks

### Input
- Generated TOC
- Original user profile
- Quality rubric/benchmarks

### Output
```json
{
  "evaluation_results": {
    "overall_score": 8.2,
    "dimension_scores": {
      "logical_progression": 9.0,
      "personalization": 7.5,
      "completeness": 8.0,
      "timeline_feasibility": 8.5
    },
    "strengths": ["Strong connection to marketing background", "Clear skill progression"],
    "improvement_areas": ["More specific AI evaluation methods", "Additional practical exercises"],
    "recommendations": [
      "Add chapter on AI prompt engineering",
      "Include more hands-on project examples"
    ]
  }
}
```

### Prompt Template
```
You are a learning experience evaluator. Assess this generated TOC:

GENERATED TOC: {toc}
USER PROFILE: {user_profile}
SUCCESS BENCHMARKS: {quality_benchmarks}

Evaluate on these dimensions (1-10 scale):
1. Logical progression - Does each chapter build on the previous?
2. Personalization - How well does it leverage user's background?
3. Completeness - Are all necessary topics covered?
4. Timeline feasibility - Can this be completed in user's timeframe?
5. Market relevance - Does it address current industry needs?

Provide specific, actionable recommendations for improvement.
```

---

## 8. Synthesis Agent

### Purpose
Integrate feedback and create the final, polished TOC.

### Detailed Process
1. **Feedback Integration**
   - Analyze evaluator recommendations
   - Prioritize changes based on impact
   - Maintain overall coherence while improving

2. **Final Optimization**
   - Refine chapter titles and descriptions
   - Ensure consistent tone and style
   - Validate final schema compliance

3. **Quality Assurance**
   - Final consistency check
   - Ensure all requirements met
   - Prepare for user presentation

### Input
- Original TOC
- Evaluation results and recommendations
- User profile for final alignment check

### Output
Final, polished TOC ready for user review

---

## 9. User Feedback Agent

### Purpose
Present the final TOC to the user and collect feedback for potential iterations.

### Detailed Process
1. **Presentation Formatting**
   - Format TOC for optimal readability
   - Highlight personalization elements
   - Include evaluation scores/confidence

2. **Feedback Collection**
   - Generate specific feedback questions
   - Identify areas most likely needing adjustment
   - Provide easy modification options

3. **Iteration Planning**
   - If changes needed, create plan for modifications
   - Route feedback to appropriate agents
   - Manage iteration cycles

### Input
Final TOC + evaluation scores

### Output
- Formatted presentation for user
- Feedback collection interface
- Iteration plan if needed

---

## Inter-Agent Communication Protocols

### Data Flow Rules
1. **Sequential Dependencies**: Input Parser → Knowledge Retrieval → Research Planning → Web Research → TOC Generation → Evaluation → Synthesis → User Feedback
2. **Parallel Execution**: Knowledge Retrieval and Research Planning can run in parallel after Input Parser
3. **State Updates**: Each agent must update state manager with status and results
4. **Error Handling**: Failed agents should log errors and pass partial results where possible

### Context Management
- Maximum context per agent: 8K tokens
- State manager summarizes when approaching limits
- Essential information flagged for retention during summarization
- Full state persisted in external storage for debugging

This architecture ensures each agent has clear responsibilities, manageable complexity, and reliable communication patterns.