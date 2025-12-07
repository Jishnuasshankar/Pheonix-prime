#!/usr/bin/env python3
"""
Streaming Implementation Verification Script

Verifies that all WebSocket streaming components are properly integrated.
"""

import os
import sys
import asyncio
import inspect
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

def check_file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return Path(filepath).exists()

def check_string_in_file(filepath: str, search_string: str) -> bool:
    """Check if string exists in file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return search_string in content
    except:
        return False

def print_status(title: str, checks: list):
    """Print formatted status"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

# ============================================================================
# BACKEND CHECKS
# ============================================================================

def verify_backend():
    """Verify backend streaming implementation"""
    checks = []
    
    # 1. Core engine checks
    try:
        from core.engine import MasterXEngine
        engine = MasterXEngine()
        
        checks.append((
            "MasterXEngine imported successfully",
            True
        ))
        
        checks.append((
            "process_request_stream method exists",
            hasattr(engine, 'process_request_stream')
        ))
        
        checks.append((
            "process_request_stream is async generator",
            inspect.isasyncgenfunction(engine.process_request_stream)
        ))
        
        checks.append((
            "cancel_generation method exists",
            hasattr(engine, 'cancel_generation')
        ))
        
        checks.append((
            "_check_cancelled method exists",
            hasattr(engine, '_check_cancelled')
        ))
        
        checks.append((
            "_active_streams tracking exists",
            hasattr(engine, '_active_streams')
        ))
        
    except Exception as e:
        checks.append((f"Engine import failed: {e}", False))
    
    # 2. AI Provider streaming
    try:
        from core.ai_providers import ProviderManager
        
        checks.append((
            "ProviderManager imported successfully",
            True
        ))
        
        # Check generate_stream exists
        has_stream = check_string_in_file(
            '/app/backend/core/ai_providers.py',
            'async def generate_stream'
        )
        checks.append((
            "ProviderManager.generate_stream method exists",
            has_stream
        ))
        
        # Check specific provider streaming
        has_gemini_stream = check_string_in_file(
            '/app/backend/core/ai_providers.py',
            'async def _stream_gemini'
        )
        checks.append((
            "Gemini streaming implemented",
            has_gemini_stream
        ))
        
        has_groq_stream = check_string_in_file(
            '/app/backend/core/ai_providers.py',
            'async def _stream_groq'
        )
        checks.append((
            "Groq streaming implemented",
            has_groq_stream
        ))
        
    except Exception as e:
        checks.append((f"Provider import failed: {e}", False))
    
    # 3. WebSocket handlers
    has_chat_stream = check_string_in_file(
        '/app/backend/server.py',
        "message_type == 'chat_stream'"
    )
    checks.append((
        "WebSocket chat_stream handler exists",
        has_chat_stream
    ))
    
    has_stop_gen = check_string_in_file(
        '/app/backend/server.py',
        "message_type == 'stop_generation'"
    )
    checks.append((
        "WebSocket stop_generation handler exists",
        has_stop_gen
    ))
    
    # 4. Streaming models
    has_stream_models = check_string_in_file(
        '/app/backend/core/models.py',
        'class StreamChunk'
    )
    checks.append((
        "StreamChunk model defined",
        has_stream_models
    ))
    
    return print_status("BACKEND STREAMING VERIFICATION", checks)

# ============================================================================
# FRONTEND CHECKS
# ============================================================================

def verify_frontend():
    """Verify frontend streaming implementation"""
    checks = []
    
    # 1. Type definitions
    has_stream_event = check_string_in_file(
        '/app/frontend/src/types/chat.types.ts',
        'export type StreamEvent'
    )
    checks.append((
        "StreamEvent type defined",
        has_stream_event
    ))
    
    has_streaming_state = check_string_in_file(
        '/app/frontend/src/types/chat.types.ts',
        'export interface StreamingState'
    )
    checks.append((
        "StreamingState interface defined",
        has_streaming_state
    ))
    
    has_start_event = check_string_in_file(
        '/app/frontend/src/types/chat.types.ts',
        'export interface StreamStartEvent'
    )
    checks.append((
        "StreamStartEvent interface defined",
        has_start_event
    ))
    
    has_chunk_event = check_string_in_file(
        '/app/frontend/src/types/chat.types.ts',
        'export interface ContentChunkEvent'
    )
    checks.append((
        "ContentChunkEvent interface defined",
        has_chunk_event
    ))
    
    # 2. API implementation
    has_stream_api = check_string_in_file(
        '/app/frontend/src/services/api/chat.api.ts',
        'streamMessage:'
    )
    checks.append((
        "streamMessage API function exists",
        has_stream_api
    ))
    
    has_chat_stream = check_string_in_file(
        '/app/frontend/src/services/api/chat.api.ts',
        "type: 'chat_stream'"
    )
    checks.append((
        "chat_stream WebSocket message sent",
        has_chat_stream
    ))
    
    # 3. WebSocket client
    has_ws_events = check_string_in_file(
        '/app/frontend/src/services/websocket/native-socket.client.ts',
        'stream_start'
    ) and check_string_in_file(
        '/app/frontend/src/services/websocket/native-socket.client.ts',
        'content_chunk'
    )
    checks.append((
        "WebSocket streaming events registered",
        has_ws_events
    ))
    
    # 4. Component integration
    has_streaming_state_usage = check_string_in_file(
        '/app/frontend/src/components/chat/ChatContainer.tsx',
        'const [streamingState, setStreamingState]'
    )
    checks.append((
        "ChatContainer uses streamingState",
        has_streaming_state_usage
    ))
    
    has_stream_handler = check_string_in_file(
        '/app/frontend/src/components/chat/ChatContainer.tsx',
        'handleStreamEvent'
    )
    checks.append((
        "ChatContainer has stream event handler",
        has_stream_handler
    ))
    
    has_stream_call = check_string_in_file(
        '/app/frontend/src/components/chat/ChatContainer.tsx',
        'chatAPI.streamMessage'
    )
    checks.append((
        "ChatContainer calls streamMessage API",
        has_stream_call
    ))
    
    return print_status("FRONTEND STREAMING VERIFICATION", checks)

# ============================================================================
# INTEGRATION CHECKS
# ============================================================================

def verify_integration():
    """Verify end-to-end integration"""
    checks = []
    
    # 1. Message flow
    backend_sends_start = check_string_in_file(
        '/app/backend/core/engine.py',
        "type': 'stream_start"
    ) or check_string_in_file(
        '/app/backend/core/engine.py',
        'type": "stream_start'
    )
    checks.append((
        "Backend sends stream_start event",
        backend_sends_start
    ))
    
    backend_sends_chunk = check_string_in_file(
        '/app/backend/core/engine.py',
        "type': 'content_chunk"
    ) or check_string_in_file(
        '/app/backend/core/engine.py',
        'type": "content_chunk'
    )
    checks.append((
        "Backend sends content_chunk events",
        backend_sends_chunk
    ))
    
    backend_sends_complete = check_string_in_file(
        '/app/backend/core/engine.py',
        "type': 'stream_complete"
    ) or check_string_in_file(
        '/app/backend/core/engine.py',
        'type": "stream_complete'
    )
    checks.append((
        "Backend sends stream_complete event",
        backend_sends_complete
    ))
    
    frontend_handles_start = check_string_in_file(
        '/app/frontend/src/components/chat/ChatContainer.tsx',
        "case 'stream_start'"
    ) or check_string_in_file(
        '/app/frontend/src/components/chat/ChatContainer.tsx',
        "event.type === 'stream_start'"
    )
    checks.append((
        "Frontend handles stream_start",
        frontend_handles_start
    ))
    
    # 2. Cancellation flow
    frontend_sends_stop = check_string_in_file(
        '/app/frontend/src/services/api/chat.api.ts',
        "send('stop_generation'"
    )
    checks.append((
        "Frontend can send stop_generation",
        frontend_sends_stop
    ))
    
    backend_handles_cancel = check_string_in_file(
        '/app/backend/core/engine.py',
        'cancel_generation'
    )
    checks.append((
        "Backend handles cancellation",
        backend_handles_cancel
    ))
    
    # 3. Error handling
    backend_sends_error = check_string_in_file(
        '/app/backend/core/engine.py',
        "type': 'stream_error"
    ) or check_string_in_file(
        '/app/backend/core/engine.py',
        'type": "stream_error'
    )
    checks.append((
        "Backend sends error events",
        backend_sends_error
    ))
    
    frontend_handles_error = check_string_in_file(
        '/app/frontend/src/components/chat/ChatContainer.tsx',
        "case 'stream_error'"
    ) or check_string_in_file(
        '/app/frontend/src/components/chat/ChatContainer.tsx',
        "event.type === 'stream_error'"
    )
    checks.append((
        "Frontend handles errors",
        frontend_handles_error
    ))
    
    return print_status("INTEGRATION VERIFICATION", checks)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all verifications"""
    print("\n" + "="*70)
    print("  🔍 WEBSOCKET STREAMING IMPLEMENTATION VERIFICATION")
    print("="*70)
    
    backend_ok = verify_backend()
    frontend_ok = verify_frontend()
    integration_ok = verify_integration()
    
    print("\n" + "="*70)
    print("  📊 SUMMARY")
    print("="*70)
    
    if backend_ok and frontend_ok and integration_ok:
        print("✅ All checks passed! Streaming is fully implemented.")
        print("\n🎉 Ready for integration testing and deployment!")
        return 0
    else:
        print("❌ Some checks failed. Review the output above.")
        if not backend_ok:
            print("   - Backend streaming needs attention")
        if not frontend_ok:
            print("   - Frontend streaming needs attention")
        if not integration_ok:
            print("   - Integration layer needs attention")
        return 1

if __name__ == '__main__':
    sys.exit(main())
