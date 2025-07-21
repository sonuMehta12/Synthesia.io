"""
Intent classification prompt templates for book creation system.

This module contains the prompt templates used for classifying user intents
in the learning agent system, specifically designed for book creation MVP.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from ..models.intents import IntentType


# System prompt for intent classification with book creation context
INTENT_CLASSIFICATION_SYSTEM_PROMPT = """You are an expert intent classifier for a book creation system. Your job is to analyze user input and classify it into one of the following intent categories:

**Available Intent Types:**
1. **LEARN_TOPIC** - User wants to learn a new skill, topic, or subject (will create a book)
   - Examples: "I want to learn Python", "Teach me machine learning", "Create a guide about web development"
   
2. **ADD_KNOWLEDGE** - User wants to add or update knowledge in the system
   - Examples: "Add this information about React", "Update my knowledge about databases", "Include this tutorial"
   
3. **GENERATE_SUMMARY** - User wants a summary of their learning progress or content
   - Examples: "Summarize my progress", "Give me a summary of what I've learned", "Show me my learning summary"
   
4. **UPDATE_PROFILE** - User wants to update their profile or preferences
   - Examples: "Change my learning style", "Update my preferences", "Modify my settings"

5. **GENERAL** - User wants to chat or have a general conversation (not book creation)
   - Examples: "Tell me a joke", "How are you?", "What's the weather?", "Just chatting"

**Classification Guidelines:**
- Analyze the user's intent carefully
- Consider context and user history if available
- Be confident in your classification
- If unclear, default to LEARN_TOPIC for learning-related requests
- For casual conversation, use GENERAL
- For ambiguous cases, choose the most likely intent

**Output Format:**
Respond with ONLY the intent type (e.g., "LEARN_TOPIC", "ADD_KNOWLEDGE", "GENERAL", etc.)
Do not include any additional text or explanation."""


# Main intent classification prompt
INTENT_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", INTENT_CLASSIFICATION_SYSTEM_PROMPT),
    ("human", "User input: {user_input}\n\nClassify the intent:"),
])


# Enhanced prompt with context (for future use)
INTENT_CLASSIFICATION_WITH_CONTEXT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", INTENT_CLASSIFICATION_SYSTEM_PROMPT),
    ("human", """User Profile Context:
{user_context}

Previous Messages:
{messages}

Current User Input: {user_input}

Classify the intent:"""),
])


# Confidence scoring prompt with book creation context
CONFIDENCE_SCORING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at evaluating the confidence of intent classifications for a book creation system. 
Given a user input and the classified intent, rate your confidence from 0.0 to 1.0.

Consider:
- Clarity of the user's intent
- Specificity of the request
- Ambiguity in the language
- Context provided
- Whether the intent aligns with book creation goals

Respond with ONLY a number between 0.0 and 1.0 (e.g., 0.95, 0.7, 0.3)"""),
    ("human", """User Input: {user_input}
Classified Intent: {classified_intent}

Rate your confidence (0.0-1.0):"""),
])


# Topic extraction prompt for book creation
TOPIC_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at extracting learning topics from user requests for book creation. 
Extract the specific topic, skill, or subject the user wants to learn about.

Guidelines:
- Extract the main topic being requested
- Be specific but concise
- If no clear topic, return "general learning"
- For knowledge addition, extract what knowledge is being added
- Focus on topics that would make good book subjects

Examples:
- "I want to learn Python" → "Python programming"
- "Teach me machine learning" → "Machine learning"
- "Add this React tutorial" → "React development"
- "Update my database knowledge" → "Database systems"
- "Create a guide about web development" → "Web development"

Respond with ONLY the extracted topic."""),
    ("human", """User Input: {user_input}
Intent: {intent}

Extract the topic:"""),
])


def create_intent_classification_chain():
    """
    Create a chain for intent classification.
    
    Returns:
        A LangChain runnable that takes user input and returns intent classification.
    """
    return (
        {"user_input": RunnablePassthrough()}
        | INTENT_CLASSIFICATION_PROMPT
        | StrOutputParser()
    )


def create_confidence_scoring_chain():
    """
    Create a chain for confidence scoring.
    
    Returns:
        A LangChain runnable that scores confidence of classifications.
    """
    return (
        {"user_input": RunnablePassthrough(), "classified_intent": RunnablePassthrough()}
        | CONFIDENCE_SCORING_PROMPT
        | StrOutputParser()
    )


def create_topic_extraction_chain():
    """
    Create a chain for topic extraction.
    
    Returns:
        A LangChain runnable that extracts topics from user input.
    """
    return (
        {"user_input": RunnablePassthrough(), "intent": RunnablePassthrough()}
        | TOPIC_EXTRACTION_PROMPT
        | StrOutputParser()
    ) 