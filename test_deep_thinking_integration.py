#!/usr/bin/env python3
"""
Deep Thinking Integration Test
Tests the full flow from frontend → backend reasoning API → response
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
TEST_USER_ID = "test_user_deep_thinking_123"
TEST_MESSAGE = "Explain how photosynthesis works in plants step by step"

async def test_reasoning_endpoint():
    """Test the reasoning chat endpoint"""
    
    print("=" * 80)
    print("DEEP THINKING INTEGRATION TEST")
    print("=" * 80)
    print(f"\nBackend URL: {BACKEND_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Test Message: {TEST_MESSAGE}")
    print("\n" + "=" * 80)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Test 1: Standard Chat Endpoint (baseline)
        print("\n[TEST 1] Standard Chat Endpoint (baseline)")
        print("-" * 80)
        try:
            standard_response = await client.post(
                f"{BACKEND_URL}/api/v1/chat",
                json={
                    "user_id": TEST_USER_ID,
                    "message": TEST_MESSAGE,
                    "session_id": None
                }
            )
            
            if standard_response.status_code == 200:
                data = standard_response.json()
                print(f"✅ Standard chat successful")
                print(f"   Session ID: {data.get('session_id')}")
                print(f"   Response length: {len(data.get('message', ''))} chars")
                print(f"   Provider: {data.get('provider_used')}")
                print(f"   Response time: {data.get('response_time_ms')}ms")
                print(f"   Emotion: {data.get('emotion_state', {}).get('primary_emotion', 'N/A')}")
            else:
                print(f"❌ Standard chat failed: HTTP {standard_response.status_code}")
                print(f"   Response: {standard_response.text}")
                
        except Exception as e:
            print(f"❌ Standard chat error: {e}")
        
        # Test 2: Reasoning Chat Endpoint (Deep Thinking enabled)
        print("\n[TEST 2] Reasoning Chat Endpoint (Deep Thinking)")
        print("-" * 80)
        try:
            reasoning_response = await client.post(
                f"{BACKEND_URL}/api/v1/chat/reasoning",
                json={
                    "user_id": TEST_USER_ID,
                    "message": TEST_MESSAGE,
                    "enable_reasoning": True,
                    "thinking_mode": None,  # Auto-select
                    "max_reasoning_depth": 5,
                    "context": {}
                }
            )
            
            if reasoning_response.status_code == 200:
                data = reasoning_response.json()
                print(f"✅ Reasoning chat successful")
                print(f"   Session ID: {data.get('session_id')}")
                print(f"   Reasoning Enabled: {data.get('reasoning_enabled')}")
                print(f"   Thinking Mode: {data.get('thinking_mode')}")
                print(f"   Response length: {len(data.get('message', ''))} chars")
                print(f"   Provider: {data.get('provider_used')}")
                print(f"   Response time: {data.get('response_time_ms')}ms")
                
                # Check reasoning chain
                reasoning_chain = data.get('reasoning_chain')
                if reasoning_chain:
                    print(f"\n   🧠 Reasoning Chain Details:")
                    print(f"      Chain ID: {reasoning_chain.get('id')}")
                    print(f"      Query: {reasoning_chain.get('query')[:50]}...")
                    print(f"      Thinking Mode: {reasoning_chain.get('thinking_mode')}")
                    print(f"      Total Steps: {len(reasoning_chain.get('steps', []))}")
                    print(f"      Complexity Score: {reasoning_chain.get('complexity_score'):.2f}")
                    print(f"      Total Confidence: {reasoning_chain.get('total_confidence'):.2f}")
                    print(f"      Processing Time: {reasoning_chain.get('processing_time_ms'):.0f}ms")
                    print(f"      Token Budget Used: {reasoning_chain.get('token_budget_used')}")
                    print(f"      Token Budget Allocated: {reasoning_chain.get('token_budget_allocated')}")
                    
                    # Display reasoning steps
                    print(f"\n   📋 Reasoning Steps:")
                    for step in reasoning_chain.get('steps', [])[:3]:  # Show first 3 steps
                        print(f"      Step {step.get('step_number')}: {step.get('content')[:60]}...")
                        print(f"         Strategy: {step.get('strategy')} | Confidence: {step.get('confidence'):.2f}")
                    
                    if len(reasoning_chain.get('steps', [])) > 3:
                        print(f"      ... and {len(reasoning_chain.get('steps', [])) - 3} more steps")
                    
                    # Conclusion
                    if reasoning_chain.get('conclusion'):
                        print(f"\n   💡 Conclusion: {reasoning_chain.get('conclusion')[:100]}...")
                else:
                    print(f"   ⚠️  No reasoning chain generated (reasoning may be disabled)")
                    
                # Emotion state
                emotion = data.get('emotion_state')
                if emotion:
                    print(f"\n   😊 Emotion State:")
                    print(f"      Primary: {emotion.get('primary_emotion')}")
                    print(f"      Arousal: {emotion.get('arousal'):.2f}")
                    print(f"      Valence: {emotion.get('valence'):.2f}")
                    print(f"      Learning Readiness: {emotion.get('learning_readiness')}")
                    
            else:
                print(f"❌ Reasoning chat failed: HTTP {reasoning_response.status_code}")
                print(f"   Response: {reasoning_response.text}")
                
        except Exception as e:
            print(f"❌ Reasoning chat error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Health Check
        print("\n[TEST 3] Health Check")
        print("-" * 80)
        try:
            health_response = await client.get(f"{BACKEND_URL}/api/health")
            if health_response.status_code == 200:
                health = health_response.json()
                print(f"✅ Backend is healthy")
                print(f"   Status: {health.get('status')}")
                print(f"   Version: {health.get('version')}")
            else:
                print(f"❌ Health check failed: HTTP {health_response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_reasoning_endpoint())
