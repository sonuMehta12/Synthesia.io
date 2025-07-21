"""
Intent Classifier Agent for the Learning Agent.

This module implements the intent classification node, which is the first
node in the learning agent workflow. It analyzes user input and determines
the type of learning request for book creation.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from ..models.intents import IntentType, IntentClassification, IntentClassifierConfig
from ..models.state import AgentState
from ..prompts.intent_classification import (
    INTENT_CLASSIFICATION_PROMPT,
    CONFIDENCE_SCORING_PROMPT,
    TOPIC_EXTRACTION_PROMPT,
    create_intent_classification_chain,
    create_confidence_scoring_chain,
    create_topic_extraction_chain,
)
from ..utils.config import config

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Intent Classifier Agent for the Learning Agent.
    
    This agent analyzes user input and classifies it into one of the
    predefined intent types for book creation. It's the first node in the learning agent
    workflow and provides the foundation for routing to downstream nodes.
    """
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Intent Classifier.
        
        Args:
            llm_config: Optional LLM configuration. If None, uses default config.
        """
        self.config = llm_config or config.get_intent_classifier_config()
        self.llm = self._initialize_llm()
        self.classification_chain = self._create_classification_chain()
        self.confidence_chain = self._create_confidence_chain()
        self.topic_chain = self._create_topic_chain()
        
        logger.info(f"Intent Classifier initialized with model: {self.config['model_name']}")
    
    def _initialize_llm(self) -> ChatOpenAI | ChatAnthropic:
        """
        Initialize the LLM based on configuration.
        
        Returns:
            Configured LLM instance.
        """
        model_name = self.config["model_name"]
        
        if "gpt" in model_name.lower():
            return ChatOpenAI(
                model=model_name,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
            )
        elif "claude" in model_name.lower():
            return ChatAnthropic(
                model=model_name,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
            )
        else:
            # Default to OpenAI
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
            )
    
    def _create_classification_chain(self):
        """Create the intent classification chain."""
        return (
            {"user_input": RunnablePassthrough()}
            | INTENT_CLASSIFICATION_PROMPT
            | self.llm
            | StrOutputParser()
        )
    
    def _create_confidence_chain(self):
        """Create the confidence scoring chain."""
        return (
            {"user_input": RunnablePassthrough(), "classified_intent": RunnablePassthrough()}
            | CONFIDENCE_SCORING_PROMPT
            | self.llm
            | StrOutputParser()
        )
    
    def _create_topic_chain(self):
        """Create the topic extraction chain."""
        return (
            {"user_input": RunnablePassthrough(), "intent": RunnablePassthrough()}
            | TOPIC_EXTRACTION_PROMPT
            | self.llm
            | StrOutputParser()
        )
    
    def classify(self, user_input: str) -> IntentClassification:
        """
        Classify the intent of user input.
        
        Args:
            user_input: The user's input text to classify.
            
        Returns:
            IntentClassification with intent type, confidence, and metadata.
        """
        try:
            logger.info(f"Classifying intent for input: {user_input[:100]}...")
            
            # Step 1: Classify the intent
            intent_str = self.classification_chain.invoke(user_input)
            intent_type = self._parse_intent_type(intent_str)
            
            # Step 2: Score confidence
            confidence_str = self.confidence_chain.invoke({
                "user_input": user_input,
                "classified_intent": intent_str
            })
            confidence = self._parse_confidence(confidence_str)
            
            # Step 3: Extract topic (if applicable)
            topic = None
            if intent_type in [IntentType.LEARN_TOPIC, IntentType.ADD_KNOWLEDGE]:
                topic = self.topic_chain.invoke({
                    "user_input": user_input,
                    "intent": intent_str
                })
            
            # Step 4: Create classification result
            result = IntentClassification(
                intent=intent_type,
                confidence=confidence,
                topic=topic,
                content=user_input if intent_type == IntentType.ADD_KNOWLEDGE else None,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "model_used": self.config["model_name"],
                    "raw_intent": intent_str,
                    "raw_confidence": confidence_str,
                }
            )
            
            logger.info(f"Intent classified as {intent_type} with confidence {confidence}")
            return result
            
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            # Return unknown intent as fallback
            return IntentClassification(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                topic=None,
                content=None,
                metadata={"error": str(e)}
            )
    
    def _parse_intent_type(self, intent_str: str) -> IntentType:
        """
        Parse the intent string into an IntentType enum.
        
        Args:
            intent_str: Raw intent string from LLM.
            
        Returns:
            Parsed IntentType enum.
        """
        intent_str = intent_str.strip().upper()
        
        # Map common variations to enum values
        intent_mapping = {
            "LEARN_TOPIC": IntentType.LEARN_TOPIC,
            "LEARN": IntentType.LEARN_TOPIC,
            "STUDY": IntentType.LEARN_TOPIC,
            "TEACH": IntentType.LEARN_TOPIC,
            "CREATE": IntentType.LEARN_TOPIC,
            "GUIDE": IntentType.LEARN_TOPIC,
            "ADD_KNOWLEDGE": IntentType.ADD_KNOWLEDGE,
            "ADD": IntentType.ADD_KNOWLEDGE,
            "SAVE": IntentType.ADD_KNOWLEDGE,
            "UPDATE": IntentType.ADD_KNOWLEDGE,
            "INCLUDE": IntentType.ADD_KNOWLEDGE,
            "GENERATE_SUMMARY": IntentType.GENERATE_SUMMARY,
            "SUMMARY": IntentType.GENERATE_SUMMARY,
            "SUMMARIZE": IntentType.GENERATE_SUMMARY,
            "UPDATE_PROFILE": IntentType.UPDATE_PROFILE,
            "PROFILE": IntentType.UPDATE_PROFILE,
            "PREFERENCES": IntentType.UPDATE_PROFILE,
            "SETTINGS": IntentType.UPDATE_PROFILE,
            "GENERAL": IntentType.GENERAL,
            "CHAT": IntentType.GENERAL,
            "CONVERSATION": IntentType.GENERAL,
        }
        
        return intent_mapping.get(intent_str, IntentType.UNKNOWN)
    
    def _parse_confidence(self, confidence_str: str) -> float:
        """
        Parse confidence string into float.
        
        Args:
            confidence_str: Raw confidence string from LLM.
            
        Returns:
            Confidence as float between 0.0 and 1.0.
        """
        try:
            # Extract number from string - handle negative numbers
            import re
            # Look for numbers including negative ones
            numbers = re.findall(r"-?\d+\.?\d*", confidence_str)
            if numbers:
                confidence = float(numbers[0])
                # Ensure it's between 0 and 1
                return max(0.0, min(1.0, confidence))
            return 0.5  # Default confidence
        except (ValueError, TypeError):
            return 0.5  # Default confidence
    
    def classify_with_state(self, state: AgentState) -> AgentState:
        """
        Classify intent and update the agent state.
        
        This is the main method used as a LangGraph node. It takes the
        current state, extracts the user input from messages, classifies
        the intent, and updates the state with the classification result.
        
        Args:
            state: Current agent state.
            
        Returns:
            Updated agent state with intent classification.
        """
        try:
            # Extract user input from the last message
            messages = state.get("messages", [])
            if not messages:
                logger.warning("No messages found in state")
                return state
            
            # Get the last user message
            last_message = messages[-1]
            user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Classify the intent
            classification = self.classify(user_input)
            
            # Update state with classification result
            updated_state = {
                **state,
                "current_intent": classification,
                "timestamp": datetime.now().isoformat(),
            }
            
            # Add topic to state if available
            if classification.get("topic"):
                updated_state["current_topic"] = classification["topic"]
            
            logger.info(f"State updated with intent classification: {classification['intent']}")
            return updated_state
            
        except Exception as e:
            logger.error(f"Error in classify_with_state: {e}")
            # Return state with unknown intent
            return {
                **state,
                "current_intent": IntentClassification(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    topic=None,
                    content=None,
                    metadata={"error": str(e)}
                ),
                "timestamp": datetime.now().isoformat(),
            }
    
    def get_config(self) -> IntentClassifierConfig:
        """
        Get the current configuration.
        
        Returns:
            Current intent classifier configuration.
        """
        return self.config.copy()
    
    def update_config(self, new_config: IntentClassifierConfig) -> None:
        """
        Update the configuration.
        
        Args:
            new_config: New configuration to apply.
        """
        self.config.update(new_config)
        # Reinitialize LLM with new config
        self.llm = self._initialize_llm()
        logger.info("Intent Classifier configuration updated") 