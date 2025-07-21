# 🎓 Learning Agent - AI-Powered Skill Development

A sophisticated AI agent that helps you learn new skills by creating personalized learning roadmaps, conducting multi-agent research, and generating comprehensive educational content.

## 🏗️ **Architecture Overview**

This project implements a multi-agent learning system using **LangGraph** for orchestration and **LangChain** for core components. The system follows a modular, state-driven architecture:

```mermaid
graph TB
    UserCommand[👤 User Command] --> TriggerRouter
    TriggerRouter[🎯 Trigger Router] --> StateManager
    StateManager[📊 State Manager] --> IntentClassifier
    IntentClassifier[🧠 Intent Classifier] --> RouterGate
    RouterGate{Route Decision} --> LearningOrchestrator
    RouterGate --> SummaryOrchestrator
    RouterGate --> KnowledgeProcessor
```

## 🚀 **Current Phase: Intent Classification (Phase 1)**

We're currently building the **first node** - the Intent Classifier. This node:

- **Analyzes user input** to determine the type of learning request
- **Classifies intents** into categories: Learning Request, Knowledge Addition, Summary Generation, Profile Update
- **Routes requests** to appropriate downstream nodes
- **Maintains state** using LangGraph's state management

## 📁 **Project Structure**

```
echo/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── intent_classifier.py      # 🎯 CURRENT FOCUS
│   │   └── state_manager.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   └── intents.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── intent_classification.py
│   └── utils/
│       ├── __init__.py
│       └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_intent_classifier.py
│   └── test_state_manager.py
├── docs/
│   └── development_roadmap.md
├── requirements.txt
└── README.md
```

## 🛠️ **Getting Started**

### 1. **Environment Setup**

```bash
# Clone the repository
git clone <your-repo-url>
cd echo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Environment Variables**

Create a `.env` file in the root directory:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional: For future database integration
# DATABASE_URL=postgresql://user:password@localhost:5432/learning_agent
# REDIS_URL=redis://localhost:6379
```

### 3. **Run the Intent Classifier**

```bash
# Run the intent classifier test
python -m pytest tests/test_intent_classifier.py -v

# Run the main application
python src/main.py
```

## 🧪 **Testing the Intent Classifier**

The intent classifier is designed to handle various types of learning requests:

```python
# Example usage
from src.agents.intent_classifier import IntentClassifier

classifier = IntentClassifier()

# Learning request
result = classifier.classify("I want to learn Python programming")
# Output: {"intent": "LEARN_TOPIC", "confidence": 0.95, "topic": "Python programming"}

# Knowledge addition
result = classifier.classify("Add this information about machine learning")
# Output: {"intent": "ADD_KNOWLEDGE", "confidence": 0.88, "content": "machine learning info"}

# Summary request
result = classifier.classify("Generate a summary of my learning progress")
# Output: {"intent": "GENERATE_SUMMARY", "confidence": 0.92}
```

## 📋 **Development Roadmap**

### **Phase 1: Intent Classification (Current)**
- ✅ Project structure setup
- ✅ State management foundation
- 🔄 Intent classifier implementation
- 🔄 Testing framework
- 🔄 Basic routing logic

### **Phase 2: Learning Orchestration (Next)**
- Context retrieval
- Simple research agent
- Roadmap generation
- Content creation

### **Phase 3: Multi-Agent Research**
- Parallel research agents
- Quality control systems
- Advanced synthesis

## 🤝 **Contributing**

This project follows Agile methodology with clear phases and deliverables. Each phase builds upon the previous one, ensuring a solid foundation for the learning agent.

## 📚 **Documentation**

- [Development Roadmap](docs/development_roadmap.md)
- [API Documentation](docs/api.md)
- [Testing Guide](docs/testing.md)

## 🎯 **Success Criteria**

**Phase 1 Goals:**
- ✅ Intent classification with 90%+ accuracy
- ✅ State persistence across sessions
- ✅ Clean, testable code structure
- ✅ Comprehensive error handling
- ✅ Performance optimization for concurrent users

---

*Built with ❤️ using LangGraph and LangChain* 