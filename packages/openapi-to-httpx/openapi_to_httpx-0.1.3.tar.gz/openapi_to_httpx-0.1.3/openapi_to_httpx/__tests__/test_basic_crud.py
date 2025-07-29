"""
Test basic CRUD operations using the generated client with pytest-httpx mocking.
"""
import pytest

# Import the generated client and models
from openapi_to_httpx.__tests__.fixtures.libraries.basic_crud import APIClient
from openapi_to_httpx.__tests__.fixtures.libraries.basic_crud.models import Pet


class TestBasicCrud:
    """Test basic CRUD operations."""
    
    def test_get_pet_by_id(self, httpx_mock):
        """Test GET endpoint with path and query parameters."""
        # Setup mock response
        mock_pet_data = {
            "id": 123,
            "name": "Fluffy",
            "tag": "cat"
        }
        
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/v1/pets/123?include_details=true",
            json=mock_pet_data,
            status_code=200
        )
        
        # Create client and make request
        client = APIClient(base_url="https://api.example.com/v1")
        response = client.get_pet_by_id(pet_id=123, include_details=True)
        
        # Verify response
        assert response.status_code == 200
        assert isinstance(response.data, Pet)
        assert response.data.id == 123
        assert response.data.name == "Fluffy"
        assert response.data.tag == "cat"
        
        # Verify the request was made correctly
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert str(request.url) == "https://api.example.com/v1/pets/123?include_details=true"
    
    def test_get_pet_without_optional_params(self, httpx_mock):
        """Test that optional parameters are handled correctly."""
        mock_pet_data = {
            "id": 456,
            "name": "Spot"
        }
        
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/v1/pets/456",
            json=mock_pet_data,
            status_code=200
        )
        
        client = APIClient(base_url="https://api.example.com/v1")
        response = client.get_pet_by_id(pet_id=456)
        
        assert response.status_code == 200
        assert response.data.id == 456
        assert response.data.name == "Spot"
        assert response.data.tag is None  # Optional field not provided
        
        # Verify no query params were sent
        request = httpx_mock.get_request()
        assert str(request.url) == "https://api.example.com/v1/pets/456"
    
    def test_404_error(self, httpx_mock):
        """Test 404 error handling."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/v1/pets/999",
            status_code=404,
            json={"error": "Pet not found"}
        )
        
        client = APIClient(base_url="https://api.example.com/v1")
        
        # The client should raise an exception for 404
        from openapi_to_httpx.__tests__.fixtures.libraries.basic_crud.base_client import NotFoundError
        
        with pytest.raises(NotFoundError) as exc_info:
            client.get_pet_by_id(pet_id=999)
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_client_with_context_manager(self, httpx_mock):
        """Test using the client as a context manager."""
        mock_pet_data = {"id": 789, "name": "Rex"}
        
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/v1/pets/789",
            json=mock_pet_data,
            status_code=200
        )
        
        with APIClient(base_url="https://api.example.com/v1") as client:
            response = client.get_pet_by_id(pet_id=789)
            assert response.data.name == "Rex"
    
    def test_response_metadata(self, httpx_mock):
        """Test that response includes headers and timing information."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/v1/pets/100",
            json={"id": 100, "name": "Max"},
            headers={"X-Rate-Limit": "100", "Content-Type": "application/json"},
            status_code=200
        )
        
        client = APIClient(base_url="https://api.example.com/v1")
        response = client.get_pet_by_id(pet_id=100)
        
        # Check response metadata
        assert response.status_code == 200
        assert "x-rate-limit" in response.headers
        assert response.headers["x-rate-limit"] == "100"
        assert response.response_time >= 0  # Should have timing info