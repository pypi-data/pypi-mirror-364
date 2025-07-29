"""
Test the Petstore API client generation.
"""

from openapi_to_httpx.__tests__.conftest import BASE_URLS
from openapi_to_httpx.__tests__.fixtures.libraries.petstore import APIClient
from openapi_to_httpx.__tests__.fixtures.libraries.petstore.models import Order, Pet


class TestPetstore:
    """Test Petstore API operations."""
    
    def test_get_pet_by_id(self, httpx_mock):
        """Test getting a pet by ID."""
        mock_pet = {
            "id": 1,
            "name": "doggie",
            "category": {"id": 1, "name": "Dogs"},
            "photoUrls": ["http://example.com/photo1.jpg"],
            "tags": [{"id": 1, "name": "tag1"}],
            "status": "available"
        }
        
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['petstore']}/pet/1",
            json=mock_pet,
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['petstore'])
        response = client.get_pet_by_id(pet_id=1)
        
        assert response.status_code == 200
        assert isinstance(response.data, Pet)
        assert response.data.id == 1
        assert response.data.name == "doggie"
        assert response.data.status == "available"
    
    def test_add_pet(self, httpx_mock):
        """Test adding a new pet."""
        new_pet_data = {
            "id": 100,
            "name": "fluffy",
            "category": {"id": 2, "name": "Cats"},
            "photoUrls": ["http://example.com/fluffy.jpg"],
            "status": "available"
        }
        
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URLS['petstore']}/pet",
            json=new_pet_data,
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['petstore'])
        
        # Create Pet instance
        new_pet = Pet(
            id=100,
            name="fluffy",
            category={"id": 2, "name": "Cats"},
            photoUrls=["http://example.com/fluffy.jpg"],
            status="available"
        )
        
        response = client.add_pet(data=new_pet)
        
        assert response.status_code == 200
        assert response.data.id == 100
        assert response.data.name == "fluffy"
        
        # Verify request
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert "application/json" in request.headers.get("content-type", "")
    
    def test_find_pets_by_status(self, httpx_mock):
        """Test finding pets by status."""
        available_pets = [
            {
                "id": 1,
                "name": "dog1",
                "photoUrls": [],
                "status": "available"
            },
            {
                "id": 2,
                "name": "dog2",
                "photoUrls": [],
                "status": "available"
            }
        ]
        
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['petstore']}/pet/findByStatus?status=available",
            json=available_pets,
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['petstore'])
        response = client.find_pets_by_status(status="available")
        
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) == 2
        assert all(isinstance(pet, Pet) for pet in response.data)
        assert all(pet.status == "available" for pet in response.data)
    
    def test_delete_pet(self, httpx_mock):
        """Test deleting a pet."""
        httpx_mock.add_response(
            method="DELETE",
            url=f"{BASE_URLS['petstore']}/pet/99",
            status_code=204  # No content response
        )
        
        client = APIClient(base_url=BASE_URLS['petstore'])
        
        # Delete with API key header
        response = client.delete_pet(pet_id=99, api_key="special-key")
        
        assert response.status_code == 204
        
        # Verify headers
        request = httpx_mock.get_request()
        assert request.headers.get("api_key") == "special-key"
    
    def test_place_order(self, httpx_mock):
        """Test placing an order."""
        order_data = {
            "id": 10,
            "petId": 1,
            "quantity": 1,
            "shipDate": "2024-01-01T00:00:00Z",
            "status": "placed",
            "complete": False
        }
        
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URLS['petstore']}/store/order",
            json=order_data,
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['petstore'])
        
        new_order = Order(
            id=10,
            petId=1,
            quantity=1,
            shipDate="2024-01-01T00:00:00Z",
            status="placed",
            complete=False
        )
        
        response = client.place_order(data=new_order)
        
        assert response.status_code == 200
        assert isinstance(response.data, Order)
        assert response.data.id == 10
        assert response.data.status == "placed"