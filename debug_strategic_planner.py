"""
Debug script to test strategic planner directly and see raw LLM response
"""
from src.agents.context_assembler import ContextAssembler
from src.models.persona import get_sonu_persona
from src.models.intents import IntentType
from langchain_openai import ChatOpenAI
from src.utils.config import config

def test_strategic_planner():
    print("🔍 DEBUGGING STRATEGIC PLANNER")
    print("=" * 50)
    
    # Set up context assembler with rich persona
    context_assembler = ContextAssembler()
    
    # Simulate intent classification result
    mock_intent = {
        "intent": IntentType.LEARN_TOPIC,
        "topic": "Python programming",
        "confidence": 0.9
    }
    
    # Assemble context with rich persona
    context_assembler.assemble_context(
        user_profile=get_sonu_persona(),
        intent_result=mock_intent,
        existing_books=None,
        user_resources=None
    )
    
    # Get populated prompt
    populated_prompt = context_assembler.get_populated_prompt("strategic_planner")
    
    print("📋 POPULATED PROMPT (first 500 chars):")
    print(populated_prompt[:500] + "...")
    print()
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=config.DEFAULT_MODEL,
        temperature=0.1,
        max_tokens=1500,
    )
    
    # Get raw response
    print("🤖 INVOKING STRATEGIC PLANNER LLM...")
    raw_response = llm.invoke(populated_prompt)
    
    # Extract content
    if hasattr(raw_response, 'content'):
        response_content = raw_response.content
    else:
        response_content = str(raw_response)
    
    print("📄 RAW LLM RESPONSE:")
    print("=" * 50)
    print(response_content)
    print("=" * 50)
    
    print(f"\n📊 Response Length: {len(response_content)} characters")
    print(f"📊 Starts with: '{response_content[:20]}...'")
    print(f"📊 Ends with: '...{response_content[-20:]}'")

if __name__ == "__main__":
    test_strategic_planner() 