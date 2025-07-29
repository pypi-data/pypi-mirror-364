"""
Test edge cases like missing operationIds, special naming, polymorphic types.
"""

from openapi_to_httpx.__tests__.conftest import BASE_URLS
from openapi_to_httpx.__tests__.fixtures.libraries.edge_cases import APIClient
from openapi_to_httpx.__tests__.fixtures.libraries.edge_cases.models import ModelWithDashes, SnakeCaseModel


class TestEdgeCases:
    """Test edge case handling."""
    
    def test_snake_case_model(self, httpx_mock):
        """Test model with snake_case fields."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['edge_cases']}/snake_case_endpoint",
            json={"id": 1, "snake_case_field": "test"},
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['edge_cases'])
        response = client.get_snake_case_model()
        
        assert response.status_code == 200
        assert isinstance(response.data, SnakeCaseModel)
        assert response.data.id == 1
        assert response.data.snake_case_field == "test"
    
    def test_model_with_dashes(self, httpx_mock):
        """Test model with dashes in field names (converted to underscores)."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['edge_cases']}/with-dashes",
            json={
                "id": 42,
                "field_with_dashes": "converted"
            },
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['edge_cases'])
        response = client.get_model_with_dashes()
        
        assert isinstance(response.data, ModelWithDashes)
        assert response.data.id == 42
        assert response.data.field_with_dashes == "converted"
    
    def test_polymorphic_response(self, httpx_mock):
        """Test endpoint returning Any type."""
        # Can return different types
        test_data = {"anything": "goes", "numbers": [1, 2, 3]}
        
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['edge_cases']}/polymorphic",
            json=test_data,
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['edge_cases'])
        response = client.get_polymorphic_response()
        
        # Response should be dict since it's Any type
        assert response.data == test_data
        assert response.data["anything"] == "goes"
        assert response.data["numbers"] == [1, 2, 3]