"""
Asynchronous client template that will be transformed by AST manipulation.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union

import httpx
from pydantic import BaseModel

from .base_client import BaseClient, Response


class AsyncClient(BaseClient):
    """
    Asynchronous API client.
    Will be transformed to inject OpenAPI-specific endpoints.
    """
    
    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        bearer_token: str | None = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        default_headers: dict[str, str] | None = None,
    ):
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            bearer_token=bearer_token,
            timeout=timeout,
            verify_ssl=verify_ssl,
            follow_redirects=follow_redirects,
            default_headers=default_headers,
        )
        self._client: httpx.AsyncClient | None = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                follow_redirects=self.follow_redirects,
                headers=self._get_headers(),
            )
        return self._client
    
    async def close(self) -> None:
        """Close async HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    # Example resource methods that will be transformed
    # These show the ideal pattern for CRUD operations
    
    async def get_resource(self, resource_id: str) -> Response[BaseModel]:
        """Get a single resource by ID."""
        client = self._get_client()
        response = await client.get(f"/resources/{resource_id}")
        self._handle_response(response)
        
        data = BaseModel.model_validate(response.json())
        
        return Response(
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    async def list_resources(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        sort_by: str | None = None,
        filter_by: dict[str, Any] | None = None,
    ) -> Response[list[BaseModel]]:
        """List resources with pagination and filtering."""
        params = {
            'limit': limit,
            'offset': offset,
        }
        
        if sort_by:
            params['sort'] = sort_by
        
        if filter_by:
            params.update(filter_by)
        
        client = self._get_client()
        response = await client.get("/resources", params=params)
        self._handle_response(response)
        
        data = [BaseModel.model_validate(item) for item in response.json()]
        
        return Response(
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    async def create_resource(self, data: BaseModel) -> Response[BaseModel]:
        """Create a new resource."""
        client = self._get_client()
        response = await client.post(
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
    
    async def update_resource(
        self,
        resource_id: str,
        data: BaseModel,
        *,
        partial: bool = True
    ) -> Response[BaseModel]:
        """Update a resource (PATCH by default, PUT if partial=False)."""
        client = self._get_client()
        method = 'patch' if partial else 'put'
        response = await getattr(client, method)(
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
    
    async def delete_resource(self, resource_id: str) -> Response[None]:
        """Delete a resource."""
        client = self._get_client()
        response = await client.delete(f"/resources/{resource_id}")
        self._handle_response(response)
        
        return Response(
            data=None,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )
    
    # Batch operations for efficiency
    async def batch_create(self, items: list[BaseModel]) -> Response[list[BaseModel]]:
        """Create multiple resources in a single request."""
        client = self._get_client()
        response = await client.post(
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
    
    # File upload examples - these will be used as patterns by the AST transformer
    async def upload_file(
        self,
        file_path: str,
        *,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> Response[BaseModel]:
        """Upload a file with optional metadata."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = metadata or {}
            
            if resource_id:
                data['resource_id'] = resource_id
            
            client = self._get_client()
            response = await client.post(
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
    
    async def upload_file_multipart(
        self,
        *,
        file: tuple[str, bytes, str] | tuple[str, bytes],  # (filename, content, content_type)
        title: str,
        description: str | None = None,
        tags: list[str] | None = None,
        public: bool = False,
    ) -> Response[BaseModel]:
        """Upload a file with form fields using multipart/form-data."""
        files = {'file': file}
        data = {
            'title': title,
            'public': str(public).lower(),
        }
        
        if description is not None:
            data['description'] = description
        
        if tags is not None:
            # Handle array fields in form data
            for i, tag in enumerate(tags):
                data[f'tags[{i}]'] = tag
        
        client = self._get_client()
        response = await client.post(
            "/upload/with-metadata",
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
    
    async def upload_multiple_files(
        self,
        files: list[tuple[str, bytes, str] | tuple[str, bytes]],
        *,
        folder: str | None = None,
    ) -> Response[BaseModel]:
        """Upload multiple files in a single request."""
        # Handle multiple files with the same field name
        files_dict = [('files', file) for file in files]
        
        data = {}
        if folder is not None:
            data['folder'] = folder
        
        client = self._get_client()
        response = await client.post(
            "/upload/multiple",
            files=files_dict,
            data=data if data else None
        )
        self._handle_response(response)
        
        result = BaseModel.model_validate(response.json())
        
        return Response(
            data=result,
            status_code=response.status_code,
            headers=dict(response.headers),
            response_time=response.elapsed.total_seconds()
        )