"""Pytest configuration and shared fixtures."""

import pytest

from openapi_to_httpx.__tests__.fixture_generator import generate_all_fixtures


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "schema(name): mark test to run only for specific schema")
    config.addinivalue_line("markers", "stripe: marks tests as requiring the large Stripe OpenAPI spec")
    config.addinivalue_line("markers", "asyncio: mark test as requiring async event loop")


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--runstripe", 
        action="store_true", 
        default=False, 
        help="run stripe tests"
    )


@pytest.fixture(scope="session", autouse=True)
def ensure_fixtures_generated():
    """Automatically generate all fixture clients before running tests."""
    generate_all_fixtures()


# Base URLs for testing
BASE_URLS = {
    "basic_crud": "https://api.example.com/v1",
    "petstore": "https://petstore.example.com",
    "stripe": "https://api.stripe.com",
    "edge_cases": "https://api.example.com",
    "file_upload": "https://api.fileupload.example.com/v1",
    "sse_example": "http://localhost:8000"
}