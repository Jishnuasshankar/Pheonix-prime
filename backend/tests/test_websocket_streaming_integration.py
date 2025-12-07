"""
Integration Test: WebSocket Streaming for MasterX Chat

Tests the complete streaming flow from WebSocket message receipt
to AI response streaming.

Run: pytest tests/test_websocket_streaming_integration.py -v
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import List, Dict, Any

# Import components under test
from core.engine import MasterXEngine
from core.models import ChatRequest, StreamStartEvent
from services.websocket_service import handle_websocket_message, manager


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    ws = AsyncMock()
    ws.send_text = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


@pytest.fixture
def mock_database():
    """Mock MongoDB database"""
    db = Mock()
    
    # Mock collections
    db.users = Mock()
    db.sessions = Mock()
    db.messages = Mock()
    db.emotions = Mock()
    db.performance_metrics = Mock()
    
    # Mock queries
    db.users.find_one = AsyncMock(return_value={
        '_id': 'test-user-123',
        'email': 'test@example.com'
    })
    
    db.sessions.find_one = AsyncMock(return_value={
        '_id': 'test-session-123',
        'user_id': 'test-user-123',
        'created_at': datetime.utcnow()
    })
    
    db.messages.insert_one = AsyncMock()
    db.emotions.insert_one = AsyncMock()
    
    return db


@pytest.fixture
def sample_chat_stream_message():
    """Sample WebSocket chat_stream message"""
    return {
        'type': 'chat_stream',
        'data': {
            'message_id': 'msg-test-123',
            'session_id': 'session-test-123',
            'user_id': 'user-test-123',
            'message': 'Explain photosynthesis',
            'context': {
                'subject': 'biology',
                'enable_reasoning': False,
                'enable_rag': False
            }
        }
    }


# ============================================================================
# UNIT TESTS - Engine Streaming
# ============================================================================

class TestEngineStreaming:
    """Test MasterXEngine.process_request_stream()"""
    
    @pytest.mark.asyncio
    async def test_process_request_stream_exists(self):
        """Verify process_request_stream method exists"""
        engine = MasterXEngine()
        assert hasattr(engine, 'process_request_stream')
        assert asyncio.iscoroutinefunction(engine.process_request_stream)
    
    
    @pytest.mark.asyncio
    async def test_process_request_stream_yields_events(self, mock_websocket, mock_database):
        """Test that streaming yields proper event sequence"""
        engine = MasterXEngine()
        
        # Initialize with mock DB
        with patch('core.engine.get_database', return_value=mock_database):
            await engine.initialize_intelligence_layer(mock_database)
        
        # Mock provider streaming
        async def mock_generate_stream(*args, **kwargs):
            """Mock streaming response"""
            yield "Photosynthesis"
            yield " is the process"
            yield " by which plants"
            yield " convert light"
        
        with patch.object(engine.provider_manager, 'generate_stream', mock_generate_stream):
            events = []
            
            async for event in engine.process_request_stream(
                websocket=mock_websocket,
                user_id='test-user-123',
                message='Explain photosynthesis',
                session_id='test-session-123',
                message_id='test-msg-123',
                context={'subject': 'biology'},
                subject='biology'
            ):
                events.append(event)
        
        # Verify event sequence
        assert len(events) > 0, "Should yield at least one event"
        
        # Check for key event types
        event_types = [e['type'] for e in events]
        
        assert 'stream_start' in event_types, "Should emit stream_start"
        assert 'content_chunk' in event_types, "Should emit content_chunk"
        assert 'stream_complete' in event_types, "Should emit stream_complete"
        
        # Verify stream_start has required fields
        start_events = [e for e in events if e['type'] == 'stream_start']
        assert len(start_events) > 0
        
        start_data = start_events[0]['data']
        assert 'message_id' in start_data
        assert 'session_id' in start_data
        assert 'ai_message_id' in start_data
    
    
    @pytest.mark.asyncio
    async def test_cancellation_mechanism(self, mock_websocket, mock_database):
        """Test generation can be cancelled mid-stream"""
        engine = MasterXEngine()
        
        with patch('core.engine.get_database', return_value=mock_database):
            await engine.initialize_intelligence_layer(mock_database)
        
        # Mock slow streaming
        async def slow_stream(*args, **kwargs):
            for i in range(100):
                await asyncio.sleep(0.01)  # Simulate slow generation
                yield f"chunk-{i}"
        
        with patch.object(engine.provider_manager, 'generate_stream', slow_stream):
            message_id = 'cancel-test-123'
            events = []
            
            # Start streaming in background
            async def stream_task():
                async for event in engine.process_request_stream(
                    websocket=mock_websocket,
                    user_id='test-user',
                    message='Test',
                    session_id='test-session',
                    message_id=message_id,
                    context={},
                    subject='general'
                ):
                    events.append(event)
            
            task = asyncio.create_task(stream_task())
            
            # Cancel after short delay
            await asyncio.sleep(0.05)
            engine.cancel_generation(message_id)
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=2.0)
            except asyncio.TimeoutError:
                pytest.fail("Stream did not stop after cancellation")
            
            # Verify cancellation event was emitted
            event_types = [e['type'] for e in events]
            assert 'generation_stopped' in event_types, "Should emit generation_stopped on cancel"


# ============================================================================
# INTEGRATION TESTS - WebSocket Handler
# ============================================================================

class TestWebSocketStreamingHandler:
    """Test WebSocket message handling for chat_stream"""
    
    @pytest.mark.asyncio
    async def test_chat_stream_handler_exists(self):
        """Verify chat_stream handler is registered"""
        # This test verifies the handler exists in the code
        # Actual handler testing requires mocking the entire WebSocket infrastructure
        
        import inspect
        from services.websocket_service import handle_websocket_message
        
        source = inspect.getsource(handle_websocket_message)
        assert 'chat_stream' in source, "Handler should process chat_stream messages"
        assert 'stop_generation' in source, "Handler should process stop_generation messages"
    
    
    @pytest.mark.asyncio
    async def test_stop_generation_handler(self, mock_database):
        """Test stop_generation message handling"""
        user_id = 'test-user-123'
        message_id = 'test-msg-123'
        
        stop_message = {
            'type': 'stop_generation',
            'data': {
                'message_id': message_id,
                'session_id': 'test-session-123'
            }
        }
        
        # Mock engine
        with patch('services.websocket_service.MasterXEngine') as MockEngine:
            mock_engine = MockEngine.return_value
            mock_engine.cancel_generation = Mock()
            
            # Mock database
            with patch('services.websocket_service.get_database', return_value=mock_database):
                # Call handler
                await handle_websocket_message(user_id, stop_message)
                
                # Verify cancel was called
                mock_engine.cancel_generation.assert_called_once_with(message_id)


# ============================================================================
# INTEGRATION TESTS - Event Flow
# ============================================================================

class TestStreamingEventFlow:
    """Test complete event flow from request to response"""
    
    @pytest.mark.asyncio
    async def test_stream_event_order(self, mock_websocket, mock_database):
        """Verify events are emitted in correct order"""
        engine = MasterXEngine()
        
        with patch('core.engine.get_database', return_value=mock_database):
            await engine.initialize_intelligence_layer(mock_database)
        
        # Mock provider
        async def mock_stream(*args, **kwargs):
            yield "Hello"
            yield " World"
        
        with patch.object(engine.provider_manager, 'generate_stream', mock_stream):
            events = []
            
            async for event in engine.process_request_stream(
                websocket=mock_websocket,
                user_id='test-user',
                message='Test',
                session_id='test-session',
                message_id='test-msg',
                context={},
                subject='general'
            ):
                events.append(event)
        
        # Verify order
        event_types = [e['type'] for e in events]
        
        # stream_start should be first
        assert event_types[0] == 'stream_start', "First event should be stream_start"
        
        # stream_complete should be last
        assert event_types[-1] == 'stream_complete', "Last event should be stream_complete"
        
        # content_chunk should be in the middle
        assert 'content_chunk' in event_types, "Should have content_chunk events"
    
    
    @pytest.mark.asyncio
    async def test_error_handling_in_stream(self, mock_websocket, mock_database):
        """Test error handling during streaming"""
        engine = MasterXEngine()
        
        with patch('core.engine.get_database', return_value=mock_database):
            await engine.initialize_intelligence_layer(mock_database)
        
        # Mock provider that fails
        async def failing_stream(*args, **kwargs):
            yield "Start"
            raise Exception("Provider failure!")
        
        with patch.object(engine.provider_manager, 'generate_stream', failing_stream):
            events = []
            
            async for event in engine.process_request_stream(
                websocket=mock_websocket,
                user_id='test-user',
                message='Test',
                session_id='test-session',
                message_id='test-msg',
                context={},
                subject='general'
            ):
                events.append(event)
        
        # Verify error event
        event_types = [e['type'] for e in events]
        assert 'stream_error' in event_types, "Should emit stream_error on failure"
        
        # Check error has proper structure
        error_events = [e for e in events if e['type'] == 'stream_error']
        error_data = error_events[0]['data']
        
        assert 'error' in error_data
        assert 'code' in error_data['error']
        assert 'message' in error_data['error']
        assert 'partial_content' in error_data


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestStreamingPerformance:
    """Test streaming performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_first_token_latency(self, mock_websocket, mock_database):
        """Measure time to first token"""
        engine = MasterXEngine()
        
        with patch('core.engine.get_database', return_value=mock_database):
            await engine.initialize_intelligence_layer(mock_database)
        
        async def fast_stream(*args, **kwargs):
            yield "First"
            yield "Second"
        
        with patch.object(engine.provider_manager, 'generate_stream', fast_stream):
            start_time = asyncio.get_event_loop().time()
            first_content_time = None
            
            async for event in engine.process_request_stream(
                websocket=mock_websocket,
                user_id='test-user',
                message='Test',
                session_id='test-session',
                message_id='test-msg',
                context={},
                subject='general'
            ):
                if event['type'] == 'content_chunk' and first_content_time is None:
                    first_content_time = asyncio.get_event_loop().time()
                    break
            
            if first_content_time:
                latency = (first_content_time - start_time) * 1000  # Convert to ms
                print(f"\n⏱️ First token latency: {latency:.2f}ms")
                
                # Acceptable latency threshold (adjust based on requirements)
                assert latency < 5000, f"First token latency too high: {latency}ms"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
