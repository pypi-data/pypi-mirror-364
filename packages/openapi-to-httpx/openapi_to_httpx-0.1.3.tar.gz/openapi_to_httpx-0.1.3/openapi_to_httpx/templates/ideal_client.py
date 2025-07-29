"""
Ideal client API template that will be transformed by AST manipulation.
This represents the most idiomatic Python HTTP client interface.
"""
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar

import httpx
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R')


@dataclass
class Response(Generic[T]):
    """Wrapper for API responses with metadata."""
    data: T
    status_code: int
    headers: Dict[str, str]
    response_time: float


class ApiError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class ValidationError(ApiError):
    """Raised when request validation fails."""
    pass


class AuthenticationError(ApiError):
    """Raised when authentication fails."""
    pass


class NotFoundError(ApiError):
    """Raised when resource is not found."""
    pass


class BaseClient:
    """
    Base client with ideal Python patterns.
    Will be transformed to inject OpenAPI-specific endpoints.
    """
    
    def __init__(
        self,
        base_url: str,
        *,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        default_headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.default_headers = default_headers or {}
        
        # Will be populated by AST transformation
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Construct headers with authentication."""
        headers = self.default_headers.copy()
        
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        elif self.bearer_token:
            headers['Authorization'] = f'Bearer {self.bearer_token}'
            
        return headers
    
    def _get_sync_client(self) -> httpx.Client:
        """Get or create sync HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                follow_redirects=self.follow_redirects,
                headers=self._get_headers(),
            )
        return self._sync_client
    
    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                follow_redirects=self.follow_redirects,
                headers=self._get_headers(),
            )
        return self._async_client
    
    def close(self) -> None:
        """Close all HTTP clients."""
        if self._sync_client:
            self._sync_client.close()
        if self._async_client:
            # This will be handled in async context
            pass
    
    async def aclose(self) -> None:
        """Async close all HTTP clients."""
        if self._sync_client:
            self._sync_client.close()
        if self._async_client:
            await self._async_client.aclose()
    
    
    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and errors."""
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed", status_code=401)
        elif response.status_code == 404:
            raise NotFoundError("Resource not found", status_code=404)
        elif response.status_code >= 400:
            raise ApiError(
                f"API error: {response.text}",
                status_code=response.status_code,
                response_body=response.text
            )
        
        return response
    
    # Example resource methods that will be transformed
    # These show the ideal pattern for CRUD operations
    
    def get_resource(self, resource_id: str) -> Response[BaseModel]:
        """Get a single resource by ID."""
        # This will be transformed to use the actual endpoint and model
        client = self._get_sync_client()
        response = client.get(f"/resources/{resource_id}")
        self._handle_response(response)
        
        # Model will be injected by AST transformation
        data = BaseModel.model_validate(response.json())
        
        return Response(
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    async def aget_resource(self, resource_id: str) -> Response[BaseModel]:
        """Async get a single resource by ID."""
        client = self._get_async_client()
        response = await client.get(f"/resources/{resource_id}")
        self._handle_response(response)
        
        data = BaseModel.model_validate(response.json())
        
        return Response(
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    def list_resources(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        filter_by: Optional[Dict[str, Any]] = None,
    ) -> Response[List[BaseModel]]:
        """List resources with pagination and filtering."""
        params = {
            'limit': limit,
            'offset': offset,
        }
        
        if sort_by:
            params['sort'] = sort_by
        
        if filter_by:
            params.update(filter_by)
        
        client = self._get_sync_client()
        response = client.get("/resources", params=params)
        self._handle_response(response)
        
        # Model will be injected by AST transformation
        data = [BaseModel.model_validate(item) for item in response.json()]
        
        return Response(
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    def create_resource(self, data: BaseModel) -> Response[BaseModel]:
        """Create a new resource."""
        client = self._get_sync_client()
        response = client.post(
            "/resources",
            json=data.model_dump(exclude_unset=True)
        )
        self._handle_response(response)
        
        result = BaseModel.model_validate(response.json())
        
        return Response(
            data=result,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    def update_resource(
        self,
        resource_id: str,
        data: BaseModel,
        *,
        partial: bool = True
    ) -> Response[BaseModel]:
        """Update a resource (PATCH by default, PUT if partial=False)."""
        client = self._get_sync_client()
        method = 'patch' if partial else 'put'
        response = getattr(client, method)(
            f"/resources/{resource_id}",
            json=data.model_dump(exclude_unset=partial)
        )
        self._handle_response(response)
        
        result = BaseModel.model_validate(response.json())
        
        return Response(
            data=result,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    def delete_resource(self, resource_id: str) -> Response[None]:
        """Delete a resource."""
        client = self._get_sync_client()
        response = client.delete(f"/resources/{resource_id}")
        self._handle_response(response)
        
        return Response(
            data=None,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    # Batch operations for efficiency
    def batch_create(self, items: List[BaseModel]) -> Response[List[BaseModel]]:
        """Create multiple resources in a single request."""
        client = self._get_sync_client()
        response = client.post(
            "/resources/batch",
            json=[item.model_dump(exclude_unset=True) for item in items]
        )
        self._handle_response(response)
        
        results = [BaseModel.model_validate(item) for item in response.json()]
        
        return Response(
            data=results,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    # File upload example
    def upload_file(
        self,
        file_path: str,
        *,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Response[BaseModel]:
        """Upload a file with optional metadata."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = metadata or {}
            
            if resource_id:
                data['resource_id'] = resource_id
            
            client = self._get_sync_client()
            response = client.post(
                "/upload",
                files=files,
                data=data
            )
            self._handle_response(response)
            
            result = BaseModel.model_validate(response.json())
            
            return Response(
                data=result,
                status_code=response.status_code,
                headers=dict(response.headers),
                response_time=response.elapsed.total_seconds()
            )