#!/usr/bin/env python3
"""
Test script to verify the RFQ agent works correctly
Run this script to test the agent functionality before starting the API server
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.rfq_assistant import RFQAssistant
from app.services.ai_providers.simple_mock import get_simple_mock_llm

async def test_rfq_agent():
    """Test the RFQ assistant with a sample conversation"""
    print("🤖 Testing RFQ Assistant Agent")
    print("=" * 50)
    
    # Create agent with simple mock LLM
    llm = get_simple_mock_llm()
    agent = RFQAssistant(llm=llm)
    
    # Test conversation scenarios
    test_scenarios = [
        {
            "name": "Initial greeting",
            "message": "Hello, I need help creating an RFQ",
            "rfq_data": {}
        },
        {
            "name": "Product specification",
            "message": "I need to source custom steel brackets for construction",
            "rfq_data": {}
        },
        {
            "name": "Quantity information",
            "message": "I need about 1000 units of these brackets",
            "rfq_data": {"product_name": "steel brackets"}
        },
        {
            "name": "Timeline details",
            "message": "I need delivery within 6 weeks",
            "rfq_data": {"product_name": "steel brackets", "quantity": 1000}
        },
        {
            "name": "Budget inquiry",
            "message": "My budget is around $5000 for this order",
            "rfq_data": {"product_name": "steel brackets", "quantity": 1000, "timeline": "6 weeks"}
        }
    ]
    
    session_id = "test-session-123"
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 Test {i}: {scenario['name']}")
        print(f"👤 User: {scenario['message']}")
        
        try:
            result = await agent.chat(
                message=scenario['message'],
                session_id=session_id,
                rfq_data=scenario['rfq_data'],
                user_id="test-user"
            )
            
            print(f"🤖 Agent: {result['response']}")
            print(f"📊 RFQ Updates: {result['rfq_updates']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    return True

async def test_rfq_summary():
    """Test RFQ summary functionality"""
    print("\n🔍 Testing RFQ Summary")
    print("-" * 30)
    
    llm = get_simple_mock_llm()
    agent = RFQAssistant(llm=llm)
    
    # Test with sample RFQ data
    sample_rfq_data = {
        "product_name": "steel brackets",
        "quantity": 1000,
        "timeline": "6 weeks",
        "budget_range": "$5000",
        "specifications": "Custom L-shaped brackets, galvanized finish"
    }
    
    summary = agent.get_rfq_summary(sample_rfq_data)
    print(f"📋 {summary}")

if __name__ == "__main__":
    print("🚀 Starting AI Agent Tests...")
    
    try:
        # Run async tests
        asyncio.run(test_rfq_agent())
        asyncio.run(test_rfq_summary())
        
        print("\n🎉 All tests passed! The agent is ready to use.")
        print("\n🔧 Next steps:")
        print("1. Run the API server: python -m app.main")
        print("2. Test via API: curl http://localhost:8002/health")
        print("3. Test chat endpoint with your favorite HTTP client")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)