"""
Test Server-Sent Events functionality (async only).
"""
import json

import pytest

from openapi_to_httpx.__tests__.conftest import BASE_URLS
from openapi_to_httpx.__tests__.fixtures.libraries.sse_example_async import APIClient
from openapi_to_httpx.__tests__.fixtures.libraries.sse_example_async.models import Event


@pytest.mark.asyncio
class TestSSEExample:
    """Test Server-Sent Events handling."""
    
    async def test_sse_stream(self, httpx_mock):
        """Test streaming SSE events."""
        # Mock SSE response
        sse_data = """data: {"id": "1", "type": "message", "content": "Hello"}

data: {"id": "2", "type": "message", "content": "World"}

data: {"id": "3", "type": "close", "content": "Goodbye"}

"""
        
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['sse_example']}/api/v1/events/stream",
            text=sse_data,
            headers={"content-type": "text/event-stream"},
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['sse_example'])
        
        events = []
        async for line in client.stream_events():
            if line.startswith('data: '):
                # Parse SSE data line
                json_data = line[6:]  # Remove 'data: ' prefix
                event_data = json.loads(json_data)
                event = Event(**event_data)
                events.append(event)
        
        assert len(events) == 3
        assert all(isinstance(event, Event) for event in events)
        assert events[0].content == "Hello"
        assert events[1].content == "World"
        assert events[2].type == "close"
    
    async def test_sse_with_filter(self, httpx_mock):
        """Test SSE stream returns filtered events."""
        # Since the API doesn't support filtering, we test that it returns all events
        # and we can filter them client-side
        sse_data = """data: {"id": "1", "type": "error", "content": "Error occurred"}

data: {"id": "2", "type": "message", "content": "Regular message"}

data: {"id": "3", "type": "error", "content": "Another error"}

"""
        
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['sse_example']}/api/v1/events/stream",
            text=sse_data,
            headers={"content-type": "text/event-stream"},
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['sse_example'])
        
        all_events = []
        async for line in client.stream_events():
            if line.startswith('data: '):
                # Parse SSE data line
                json_data = line[6:]  # Remove 'data: ' prefix
                event_data = json.loads(json_data)
                event = Event(**event_data)
                all_events.append(event)
        
        # Filter error events client-side
        error_events = [e for e in all_events if e.type == "error"]
        
        assert len(all_events) == 3
        assert len(error_events) == 2
        assert all(event.type == "error" for event in error_events)
    
    async def test_sse_connection_error(self, httpx_mock):
        """Test SSE connection error handling."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['sse_example']}/api/v1/events/stream",
            status_code=500,
            json={"error": "Internal server error"}
        )
        
        client = APIClient(base_url=BASE_URLS['sse_example'])
        
        from openapi_to_httpx.__tests__.fixtures.libraries.sse_example_async.base_client import ApiError
        
        with pytest.raises(ApiError):
            async for _ in client.stream_events():
                pass