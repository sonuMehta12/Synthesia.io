"""
Tests for the Intent Classifier Agent.

This module contains comprehensive tests for the intent classifier,
including unit tests, integration tests, and edge case handling
for the book creation MVP.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.models.intents import IntentType, IntentClassification
from src.models.state import AgentState
from src.agents.intent_classifier import IntentClassifier
from src.utils.config import config


class TestIntentClassifier:
    """Test suite for the IntentClassifier class."""
    
    @pytest.fixture
    def classifier(self):
        """Create a test instance of IntentClassifier."""
        return IntentClassifier()
    
    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for testing."""
        return "LEARN_TOPIC"
    
    @pytest.fixture
    def mock_confidence_response(self):
        """Mock confidence response for testing."""
        return "0.95"
    
    @pytest.fixture
    def mock_topic_response(self):
        """Mock topic extraction response for testing."""
        return "Python programming"
    
    def test_initialization(self, classifier):
        """Test that the classifier initializes correctly."""
        assert classifier is not None
        assert classifier.config is not None
        assert classifier.llm is not None
        assert classifier.classification_chain is not None
        assert classifier.confidence_chain is not None
        assert classifier.topic_chain is not None
    
    def test_parse_intent_type_valid(self, classifier):
        """Test parsing valid intent types including GENERAL."""
        test_cases = [
            ("LEARN_TOPIC", IntentType.LEARN_TOPIC),
            ("ADD_KNOWLEDGE", IntentType.ADD_KNOWLEDGE),
            ("GENERATE_SUMMARY", IntentType.GENERATE_SUMMARY),
            ("UPDATE_PROFILE", IntentType.UPDATE_PROFILE),
            ("GENERAL", IntentType.GENERAL),
            ("learn_topic", IntentType.LEARN_TOPIC),
            ("add_knowledge", IntentType.ADD_KNOWLEDGE),
            ("general", IntentType.GENERAL),
            ("CREATE", IntentType.LEARN_TOPIC),
            ("GUIDE", IntentType.LEARN_TOPIC),
            ("CHAT", IntentType.GENERAL),
            ("CONVERSATION", IntentType.GENERAL),
        ]
        
        for input_str, expected in test_cases:
            result = classifier._parse_intent_type(input_str)
            assert result == expected
    
    def test_parse_intent_type_invalid(self, classifier):
        """Test parsing invalid intent types."""
        invalid_inputs = ["INVALID", "RANDOM", "", "   "]
        
        for input_str in invalid_inputs:
            result = classifier._parse_intent_type(input_str)
            assert result == IntentType.UNKNOWN
    
    def test_parse_confidence_valid(self, classifier):
        """Test parsing valid confidence values."""
        test_cases = [
            ("0.95", 0.95),
            ("0.5", 0.5),
            ("1.0", 1.0),
            ("0.0", 0.0),
            ("Confidence: 0.85", 0.85),
            ("The confidence is 0.72", 0.72),
        ]
        
        for input_str, expected in test_cases:
            result = classifier._parse_confidence(input_str)
            assert result == expected
    
    def test_parse_confidence_invalid(self, classifier):
        """Test parsing invalid confidence values."""
        invalid_inputs = ["invalid", "abc", "", "confidence: invalid"]
        
        for input_str in invalid_inputs:
            result = classifier._parse_confidence(input_str)
            assert result == 0.5  # Default confidence
    
    def test_parse_confidence_bounds(self, classifier):
        """Test that confidence values are bounded between 0 and 1."""
        test_cases = [
            ("2.0", 1.0),  # Should be capped at 1.0
            ("-0.5", 0.0),  # Should be floored at 0.0
            ("1.5", 1.0),   # Should be capped at 1.0
        ]
        
        for input_str, expected in test_cases:
            result = classifier._parse_confidence(input_str)
            assert result == expected
    
    @patch('src.agents.intent_classifier.ChatOpenAI')
    def test_classify_learn_topic(self, mock_chat_openai, classifier, mock_llm_response, mock_confidence_response, mock_topic_response):
        """Test classifying a learning topic intent for book creation."""
        # Mock the LLM responses
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = mock_llm_response
        mock_chat_openai.return_value = mock_llm
        
        # Mock the entire chains instead of just the invoke method
        classifier.classification_chain = Mock()
        classifier.classification_chain.invoke = Mock(return_value=mock_llm_response)
        classifier.confidence_chain = Mock()
        classifier.confidence_chain.invoke = Mock(return_value=mock_confidence_response)
        classifier.topic_chain = Mock()
        classifier.topic_chain.invoke = Mock(return_value=mock_topic_response)
        
        # Test classification
        result = classifier.classify("I want to learn Python programming")
        
        # Verify the result
        assert result["intent"] == IntentType.LEARN_TOPIC
        assert result["confidence"] == 0.95
        assert result["topic"] == "Python programming"
        assert result["content"] is None
        assert "timestamp" in result["metadata"]
        assert "model_used" in result["metadata"]
    
    @patch('src.agents.intent_classifier.ChatOpenAI')
    def test_classify_add_knowledge(self, mock_chat_openai, classifier):
        """Test classifying an add knowledge intent."""
        # Mock the LLM responses
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = "ADD_KNOWLEDGE"
        mock_chat_openai.return_value = mock_llm
        
        # Mock the entire chains
        classifier.classification_chain = Mock()
        classifier.classification_chain.invoke = Mock(return_value="ADD_KNOWLEDGE")
        classifier.confidence_chain = Mock()
        classifier.confidence_chain.invoke = Mock(return_value="0.88")
        classifier.topic_chain = Mock()
        classifier.topic_chain.invoke = Mock(return_value="Machine learning")
        
        # Test classification
        user_input = "Add this information about machine learning"
        result = classifier.classify(user_input)
        
        # Verify the result
        assert result["intent"] == IntentType.ADD_KNOWLEDGE
        assert result["confidence"] == 0.88
        assert result["topic"] == "Machine learning"
        assert result["content"] == user_input
    
    @patch('src.agents.intent_classifier.ChatOpenAI')
    def test_classify_general_chat(self, mock_chat_openai, classifier):
        """Test classifying a general chat intent."""
        # Mock the LLM responses
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = "GENERAL"
        mock_chat_openai.return_value = mock_llm
        
        # Mock the entire chains
        classifier.classification_chain = Mock()
        classifier.classification_chain.invoke = Mock(return_value="GENERAL")
        classifier.confidence_chain = Mock()
        classifier.confidence_chain.invoke = Mock(return_value="0.92")
        
        # Test classification
        result = classifier.classify("Tell me a joke")
        
        # Verify the result
        assert result["intent"] == IntentType.GENERAL
        assert result["confidence"] == 0.92
        assert result["topic"] is None  # No topic extraction for general chat
        assert result["content"] is None
    
    @patch('src.agents.intent_classifier.ChatOpenAI')
    def test_classify_generate_summary(self, mock_chat_openai, classifier):
        """Test classifying a generate summary intent."""
        # Mock the LLM responses
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = "GENERATE_SUMMARY"
        mock_chat_openai.return_value = mock_llm
        
        # Mock the entire chains
        classifier.classification_chain = Mock()
        classifier.classification_chain.invoke = Mock(return_value="GENERATE_SUMMARY")
        classifier.confidence_chain = Mock()
        classifier.confidence_chain.invoke = Mock(return_value="0.92")
        
        # Test classification
        result = classifier.classify("Generate a summary of my learning progress")
        
        # Verify the result
        assert result["intent"] == IntentType.GENERATE_SUMMARY
        assert result["confidence"] == 0.92
        assert result["topic"] is None  # No topic extraction for summary
        assert result["content"] is None
    
    def test_classify_error_handling(self, classifier):
        """Test error handling in classification."""
        # Mock the classification chain to raise an exception
        classifier.classification_chain = Mock()
        classifier.classification_chain.invoke = Mock(side_effect=Exception("LLM Error"))
        
        # Test classification with error
        result = classifier.classify("Test input")
        
        # Verify error handling
        assert result["intent"] == IntentType.UNKNOWN
        assert result["confidence"] == 0.0
        assert result["topic"] is None
        assert result["content"] is None
        assert "error" in result["metadata"]
    
    def test_classify_with_state(self, classifier):
        """Test classifying intent with state management."""
        # Create a test state
        state = AgentState(
            messages=[Mock(content="I want to learn Python")],
            user_profile=None,
            current_request=None,
            generated_book=None,
            current_intent=None,
            current_topic=None,
            learning_context={},
            session_id=None,
            timestamp=None,
        )
        
        # Mock the classify method
        mock_classification = IntentClassification(
            intent=IntentType.LEARN_TOPIC,
            confidence=0.95,
            topic="Python programming",
            content=None,
            metadata={},
        )
        classifier.classify = Mock(return_value=mock_classification)
        
        # Test classification with state
        result = classifier.classify_with_state(state)
        
        # Verify the result
        assert result["current_intent"] == mock_classification
        assert result["current_topic"] == "Python programming"
        assert "timestamp" in result
    
    def test_classify_with_state_no_messages(self, classifier):
        """Test classifying with state that has no messages."""
        # Create a test state with no messages
        state = AgentState(
            messages=[],
            user_profile=None,
            current_request=None,
            generated_book=None,
            current_intent=None,
            current_topic=None,
            learning_context={},
            session_id=None,
            timestamp=None,
        )
        
        # Test classification with empty state
        result = classifier.classify_with_state(state)
        
        # Verify the result (should return original state)
        assert result == state
    
    def test_get_config(self, classifier):
        """Test getting the classifier configuration."""
        config = classifier.get_config()
        
        assert "model_name" in config
        assert "temperature" in config
        assert "max_tokens" in config
        assert "confidence_threshold" in config
    
    def test_update_config(self, classifier):
        """Test updating the classifier configuration."""
        original_config = classifier.get_config()
        
        # Update configuration
        new_config = {
            "model_name": "gpt-4",
            "temperature": 0.2,
            "max_tokens": 100,
            "confidence_threshold": 0.8,
        }
        
        classifier.update_config(new_config)
        
        # Verify the update
        updated_config = classifier.get_config()
        assert updated_config["model_name"] == "gpt-4"
        assert updated_config["temperature"] == 0.2
        assert updated_config["max_tokens"] == 100
        assert updated_config["confidence_threshold"] == 0.8


class TestIntentClassifierIntegration:
    """Integration tests for the Intent Classifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create a test instance of IntentClassifier."""
        return IntentClassifier()
    
    def test_real_classification_flow(self, classifier):
        """Test the complete classification flow with real LLM calls."""
        # Skip if no API key is configured
        if not config.OPENAI_API_KEY:
            pytest.skip("No OpenAI API key configured")
        
        test_cases = [
            ("I want to learn Python programming", IntentType.LEARN_TOPIC),
            ("Add this information about machine learning", IntentType.ADD_KNOWLEDGE),
            ("Generate a summary of my progress", IntentType.GENERATE_SUMMARY),
            ("Update my learning preferences", IntentType.UPDATE_PROFILE),
            ("Tell me a joke", IntentType.GENERAL),
            ("How are you today?", IntentType.GENERAL),
        ]
        
        for user_input, expected_intent in test_cases:
            result = classifier.classify(user_input)
            
            # Verify basic structure
            assert "intent" in result
            assert "confidence" in result
            assert "metadata" in result
            
            # Verify confidence is within bounds
            assert 0.0 <= result["confidence"] <= 1.0
            
            # Verify intent is valid
            assert result["intent"] in IntentType
            
            # For learning topics, verify topic extraction
            if result["intent"] == IntentType.LEARN_TOPIC:
                assert result["topic"] is not None
                assert len(result["topic"]) > 0


class TestIntentClassifierPerformance:
    """Performance tests for the Intent Classifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create a test instance of IntentClassifier."""
        return IntentClassifier()
    
    def test_classification_speed(self, classifier):
        """Test that classification completes within reasonable time."""
        import time
        
        user_input = "I want to learn machine learning"
        
        start_time = time.time()
        result = classifier.classify(user_input)
        end_time = time.time()
        
        # Should complete within 10 seconds (adjust based on your requirements)
        assert end_time - start_time < 10.0
        
        # Verify result structure
        assert "intent" in result
        assert "confidence" in result
    
    def test_multiple_classifications(self, classifier):
        """Test multiple classifications in sequence."""
        inputs = [
            "I want to learn Python",
            "Add this tutorial about React",
            "Show me my learning summary",
            "Update my profile settings",
            "Tell me a joke",
        ]
        
        results = []
        for user_input in inputs:
            result = classifier.classify(user_input)
            results.append(result)
        
        # Verify all classifications completed
        assert len(results) == len(inputs)
        
        # Verify all results have required fields
        for result in results:
            assert "intent" in result
            assert "confidence" in result
            assert "metadata" in result


if __name__ == "__main__":
    pytest.main([__file__]) 