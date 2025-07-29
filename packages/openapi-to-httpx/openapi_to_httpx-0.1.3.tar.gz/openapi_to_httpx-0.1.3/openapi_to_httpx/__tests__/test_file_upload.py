"""
Test file upload functionality.
"""

from openapi_to_httpx.__tests__.conftest import BASE_URLS
from openapi_to_httpx.__tests__.fixtures.libraries.file_upload import APIClient
from openapi_to_httpx.__tests__.fixtures.libraries.file_upload.base_client import File
from openapi_to_httpx.__tests__.fixtures.libraries.file_upload.models import (
    ProfileImageResponse,
    UploadFileWithMetadataForm,
    UploadProfileImageForm,
    UploadResponse,
    UploadSingleFileForm,
)


class TestFileUpload:
    """Test file upload operations."""
    
    def test_single_file_upload(self, httpx_mock, tmp_path):
        """Test uploading a single file."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URLS['file_upload']}/upload/single",
            json={
                "id": "12345",
                "filename": "test.txt",
                "size": 13,
                "mime_type": "text/plain",
                "url": "https://storage.example.com/12345",
                "uploaded_at": "2024-01-01T00:00:00Z"
            },
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['file_upload'])
        
        with open(test_file, "rb") as f:
            file_content = f.read()
            form_data = UploadSingleFileForm(file=File(content=file_content, filename="test.txt"))
            response = client.upload_single_file(data=form_data)
        
        assert response.status_code == 200
        assert isinstance(response.data, UploadResponse)
        assert response.data.id == "12345"
        assert response.data.filename == "test.txt"
        assert response.data.size == 13
    
    def test_file_upload_with_metadata(self, httpx_mock, tmp_path):
        """Test file upload with additional metadata."""
        test_file = tmp_path / "document.pdf"
        test_file.write_bytes(b"PDF content")
        
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URLS['file_upload']}/upload/with-metadata",
            json={"success": True, "file_id": "999"},
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['file_upload'])
        
        with open(test_file, "rb") as f:
            file_content = f.read()
            form_data = UploadFileWithMetadataForm(
                file=File(content=file_content, filename="document.pdf", content_type="application/pdf"),
                title="Important Document",
                description="A very important document",
                tags=["pdf", "important"],
                public=True
            )
            response = client.upload_file_with_metadata(data=form_data)
        
        assert response.status_code == 200
        assert response.data["success"] is True
        assert response.data["file_id"] == "999"
    
    def test_profile_image_upload(self, httpx_mock, tmp_path):
        """Test uploading a profile image."""
        image_file = tmp_path / "profile.jpg"
        image_file.write_bytes(b"JPEG data")
        
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URLS['file_upload']}/upload/profile-image/user123",
            json={
                "user_id": "user123",
                "image_url": "https://storage.example.com/profiles/user123.jpg",
                "thumbnail_url": "https://storage.example.com/profiles/user123_thumb.jpg",
                "dimensions": {"width": 800, "height": 600}
            },
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['file_upload'])
        
        with open(image_file, "rb") as f:
            file_content = f.read()
            form_data = UploadProfileImageForm(image=File(content=file_content, filename="profile.jpg", content_type="image/jpeg"))
            response = client.upload_profile_image(user_id="user123", data=form_data)
        
        assert response.status_code == 200
        assert isinstance(response.data, ProfileImageResponse)
        assert response.data.user_id == "user123"
        assert response.data.dimensions["width"] == 800
    
    def test_file_download(self, httpx_mock):
        """Test downloading a file."""
        file_content = b"This is the file content"
        
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URLS['file_upload']}/download/file/abc123",
            content=file_content,
            headers={"content-type": "application/octet-stream"},
            status_code=200
        )
        
        client = APIClient(base_url=BASE_URLS['file_upload'])
        response = client.download_file(file_id="abc123")
        
        assert response.status_code == 200
        assert response.data == file_content
        assert isinstance(response.data, bytes)