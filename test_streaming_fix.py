#!/usr/bin/env python3
"""
Test Streaming Fix - Verify WebSocket streaming is working
"""

import asyncio
import websockets
import json
from datetime import datetime

BACKEND_URL = "ws://localhost:8001/api/ws"

async def test_streaming():
    """Test WebSocket streaming with a sample query"""
    
    # Test user credentials
    test_email = "EinsteinMind@gmail.com"
    test_password = "EinsteinMind22@"
    
    print("🔐 Step 1: Logging in to get token...")
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        # Login to get token
        async with session.post(
            "http://localhost:8001/api/auth/login",
            json={"email": test_email, "password": test_password}
        ) as resp:
            if resp.status != 200:
                print(f"❌ Login failed: {resp.status}")
                print(await resp.text())
                return
            
            data = await resp.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            
            print(f"✅ Logged in successfully. User ID: {user_id}")
    
    if not token:
        print("❌ No token received")
        return
    
    # Connect to WebSocket
    ws_url = f"{BACKEND_URL}?token={token}"
    print(f"\n🔌 Step 2: Connecting to WebSocket...")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected!")
            
            # Send a test message
            test_query = "How nested Learning can be used in upcoming Large Action Models"
            message_id = f"test-{datetime.now().timestamp()}"
            session_id = f"session-{datetime.now().timestamp()}"
            
            print(f"\n📤 Step 3: Sending test query: '{test_query}'")
            
            message = {
                "type": "chat_stream",
                "data": {
                    "message_id": message_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": test_query,
                    "context": {
                        "subject": "machine-learning"
                    }
                }
            }
            
            await websocket.send(json.dumps(message))
            print("✅ Message sent!")
            
            # Listen for events
            print("\n📥 Step 4: Receiving streaming events...\n")
            
            accumulated_content = ""
            event_count = 0
            content_chunks = 0
            
            async for response in websocket:
                try:
                    event = json.loads(response)
                    event_type = event.get("type")
                    event_data = event.get("data", {})
                    
                    event_count += 1
                    
                    if event_type == "stream_start":
                        print(f"🎬 [{event_count}] Stream started")
                        print(f"   Provider: {event_data.get('metadata', {}).get('provider')}")
                        print(f"   Category: {event_data.get('metadata', {}).get('category')}")
                    
                    elif event_type == "context_info":
                        print(f"🧠 [{event_count}] Context retrieved")
                        print(f"   Recent messages: {event_data.get('context', {}).get('recent_messages_used', 0)}")
                    
                    elif event_type == "emotion_update":
                        print(f"😊 [{event_count}] Emotion detected")
                        print(f"   Primary emotion: {event_data.get('emotion', {}).get('primary_emotion')}")
                    
                    elif event_type == "content_chunk":
                        content_chunks += 1
                        chunk_text = event_data.get("content", "")
                        accumulated_content += chunk_text
                        
                        # Print progress every 10 chunks
                        if content_chunks % 10 == 0:
                            print(f"📝 [{event_count}] Content streaming... ({len(accumulated_content)} chars, {content_chunks} chunks)")
                    
                    elif event_type == "stream_complete":
                        print(f"\n✅ [{event_count}] Stream complete!")
                        print(f"   Total content length: {len(event_data.get('full_content', ''))} chars")
                        print(f"   Total chunks received: {content_chunks}")
                        print(f"   Provider: {event_data.get('metadata', {}).get('provider_used')}")
                        print(f"   Response time: {event_data.get('metadata', {}).get('response_time_ms', 0):.0f}ms")
                        print(f"   Cost: ${event_data.get('metadata', {}).get('cost', 0):.4f}")
                        
                        # Show first 200 chars of content
                        print(f"\n📄 Content preview (first 200 chars):")
                        print(f"   {accumulated_content[:200]}...")
                        
                        break
                    
                    elif event_type == "stream_error":
                        print(f"❌ [{event_count}] Stream error!")
                        print(f"   Error: {event_data.get('error', {}).get('message')}")
                        print(f"   Code: {event_data.get('error', {}).get('code')}")
                        break
                    
                    else:
                        print(f"ℹ️  [{event_count}] Unknown event: {event_type}")
                
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse event: {e}")
                    print(f"   Raw response: {response}")
            
            print("\n" + "="*60)
            print("🎉 Test complete!")
            print("="*60)
            print(f"\nSummary:")
            print(f"  • Total events: {event_count}")
            print(f"  • Content chunks: {content_chunks}")
            print(f"  • Total content: {len(accumulated_content)} characters")
            
            if accumulated_content:
                print(f"\n✅ SUCCESS: Streaming is working correctly!")
            else:
                print(f"\n❌ FAILURE: No content received")
    
    except Exception as e:
        print(f"\n❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print(" TESTING WEBSOCKET STREAMING FIX")
    print("="*60)
    asyncio.run(test_streaming())
