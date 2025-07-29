## Rules

If you ever make changes to the architecture in a way that modifies or invalidates some of the statements in this CLAUDE.md, point out to the user what they are in bullet point style. Then offer to update the CLAUDE.md file with the updates that you've just communicated once the user approves.

## Overview

This is a unique OpenAPI client generator for Python that uses AST (Abstract Syntax Tree) transformation instead of traditional templating. The key innovation is using separate optimized templates for sync and async clients, then transforming them via AST manipulation to inject OpenAPI-specific details.

## Architecture

### Core Components

1. **Client Templates** (`openapi_to_httpx/templates/`)
   - `sync_client.py` - Synchronous client template with blocking HTTP calls
   - `async_client.py` - Asynchronous client template with async/await patterns  
   - `base_client.py` - Shared base functionality (auth, error handling, utilities)
   - `ideal_client.py` - Legacy template (preserved for reference but unused)
   - Template selection based on generation mode parameter

2. **AST Transformer** (`openapi_to_httpx/ast_transform/transformer.py`)
   - Parses selected template into an AST
   - Injects OpenAPI endpoints, models, and parameters
   - Handles sync vs async method generation
   - Supports streaming responses (SSE) with special handling

3. **Code Generator** (`openapi_to_httpx/generator.py`)
   - Orchestrates the transformation process
   - Separates models from client code
   - Uses Jinja2 templates for auxiliary files
   - Supports both sync and async generation modes

4. **Schema Parser** (`openapi_to_httpx/schema_parser.py`)
   - Loads OpenAPI specs from files or URLs
   - Built-in examples in `openapi_to_httpx/__tests__/fixtures/`:
     - Petstore (petstore.json): 13 endpoints, 6 models
     - Stripe (stripe.json): 398 endpoints, 1186 models
     - SSE Example (sse_example.json): 3 streaming endpoints

5. **Naming Strategy** (`openapi_to_httpx/naming_strategy.py`)
   - Converts OpenAPI paths to Python method names
   - Handles conflict resolution and duplicate detection
   - Supports operationId overrides and path-based naming

6. **CLI Interface** (`openapi_to_httpx/cli.py`)
   - Full command-line interface built with Click
   - Supports file paths and URLs for schema input
   - Configurable output directory and client naming

## Key Design Decisions

### Response[T] Pattern
All non-streaming methods return `Response[T]` objects containing:
- `data: T` - The typed response data
- `status_code: int` - HTTP status code
- `headers: Dict[str, str]` - Response headers
- `response_time: float` - Request duration

### Server-Sent Events (SSE) Support
Full support for streaming responses with `text/event-stream` content type:
- **Detection**: Automatically detects SSE endpoints from content type
- **Async Streaming**: Generates `AsyncIterator[str]` methods for SSE endpoints
- **Error Handling**: Uses `_handle_streaming_response()` to avoid reading response body
- **Real-time Data**: Yields raw SSE lines for client-side parsing

Example generated SSE method:
```python
async def stream_events(self) -> AsyncIterator[str]:
    """Stream Events - Stream real-time events via Server-Sent Events"""
    client = self._get_client()
    async with client.stream("GET", "/api/v1/events/stream") as response:
        self._handle_streaming_response(response)
        async for line in response.aiter_lines():
            if line:
                yield line
```

### Explicit Imports
The generator analyzes the AST to create explicit imports like:
```python
from .models import Pet, Category, Order, User
```
Instead of using `from .models import *`

### Idiomatic Python
- Snake_case method names (e.g., `get_pet_by_id`)
- Optional parameters with defaults
- Keyword-only arguments after `*`
- Context managers for resource management

### Type Safety
- Full type hints for all parameters and returns
- Pydantic models for request/response validation
- Generic types for collections (e.g., `List[Pet]`)

## Testing & Code Quality

### Running Tests

```bash
# Install dependencies including dev dependencies
uv sync

# Run all tests
uv run pytest

# Run specific test
uv run pytest openapi_to_httpx/__tests__/test_basic_crud.py::TestBasicCrud::test_get_pet_by_id

# Generate test client manually (async by default)
uv run openapi-to-httpx openapi_to_httpx/__tests__/fixtures/petstore.json -o ./test_output

# Generate sync client
uv run openapi-to-httpx openapi_to_httpx/__tests__/fixtures/petstore.json -o ./test_output --mode sync
```

_Always_ run python commands with uv.

### Code Quality Checks

```bash
# Run all checks (lint, type-check, tests)
make check

# Run individual checks
make lint          # Run ruff linter
make type-check    # Run ty type checker  
make test          # Run pytest tests

# Other useful commands
make install       # Install package and dependencies
make clean         # Remove generated files and caches
uv run update-test-fixtures  # Regenerate all test fixture libraries
```

### Tool Configuration

All tools are configured in `pyproject.toml`:
- **Ruff** (`[tool.ruff]`): Handles linting and import sorting
- **Ty** (`[tool.ty]`): Experimental type checker with some rules disabled for AST manipulation
- **Pytest** (`[tool.pytest.ini_options]`): Runs all tests in `openapi_to_httpx/__tests__`

### Test Structure

The test suite is organized by feature area:
- **test_basic_crud.py**: Basic CRUD operations (GET, POST, PUT, DELETE)
- **test_petstore.py**: Petstore OpenAPI example validation  
- **test_sse_example.py**: Server-Sent Events streaming tests
- **test_file_upload.py**: File upload and multipart forms
- **test_edge_cases.py**: Model naming, polymorphism, edge cases
- **test_naming_strategy.py**: Method name generation algorithms

The tests use:
- `pytest-httpx` for mocking HTTP responses
- `importlib` to dynamically load and test the generated modules
- Actual function calls to verify the complete generation pipeline

#### Fixture System

Test fixtures are automatically generated from OpenAPI schemas:
- **Schemas**: Located in `openapi_to_httpx/__tests__/fixtures/`
- **Generated Libraries**: Created in `openapi_to_httpx/__tests__/fixtures/libraries/`
- **Automation**: `update-test-fixtures` command regenerates all client libraries
- **Modes**: Each schema generates both sync and async client versions

The fixture generator (`openapi_to_httpx/__tests__/fixture_generator.py`) automates:
- Client library generation from all schemas
- Both sync and async versions for comprehensive testing  
- Ensuring consistent test environment across runs

## Sync vs Async Clients

The generator supports generating either synchronous or asynchronous clients:

### CLI Usage
```bash
# Generate async client (default)
openapi-to-httpx schema.yaml

# Generate sync client
openapi-to-httpx schema.yaml --mode sync

# Full example with options
openapi-to-httpx https://api.example.com/openapi.json -o ./my_client -n MyAPIClient --mode async
```

### Implementation Details
- **Separate Templates**: `sync_client.py` and `async_client.py` with optimized patterns
- **Shared Base**: Both inherit from `base_client.py` for common functionality
- **AST Transformation**: The transformer generates `FunctionDef` or `AsyncFunctionDef` based on mode
- **Context Managers**: Sync clients support `with` statement, async clients support `async with`
- **SSE Support**: Only async clients support Server-Sent Events streaming

## Common Tasks

### Adding a New Feature
1. Modify the appropriate client template (`sync_client.py` or `async_client.py`)
2. Update the AST transformer to handle the new pattern
3. Add tests to validate the transformation
4. Regenerate fixtures with `uv run update-test-fixtures`

### Debugging AST Transformation
- Use `ast.dump()` to inspect AST nodes
- The transformer walks the AST and modifies nodes in-place
- Check `generated_methods` and `generated_models` dictionaries
- Enable verbose logging in transformer for detailed output

### Customizing Output
- Jinja2 templates in `openapi_to_httpx/templates/output/` for README, __init__, etc.
- Client templates (`sync_client.py`, `async_client.py`) define the core structure
- AST transformation handles the dynamic OpenAPI-specific parts

## Implementation Notes

### AST Transformation Process
1. Select template based on mode (sync/async)
2. Parse selected client template into AST
3. Transform BaseClient → APIClient (or custom name)
4. Remove example methods from template
5. Generate methods from OpenAPI paths
6. Generate Pydantic models from schemas
7. Inject model imports
8. Unparse AST back to Python code

### Method Generation
For each OpenAPI endpoint:
- Convert operationId or path to snake_case method name
- Extract parameters (path, query, header)
- Determine request/response types
- Handle special cases (SSE, file uploads, binary responses)
- Build method signature with proper type hints
- Generate sync or async request logic with error handling

### Streaming Response Handling
For endpoints with `text/event-stream` content type:
- Generate `AsyncIterator[str]` return type (async mode only)
- Use `client.stream()` for streaming HTTP connection
- Call `_handle_streaming_response()` instead of `_handle_response()`
- Avoid reading response body to prevent `ResponseNotRead` errors
- Yield raw SSE lines for client-side parsing

### Model Generation
- Creates Pydantic models from OpenAPI schemas
- Handles nested objects and references
- Adds Field() annotations for descriptions
- Marks required vs optional fields
- Supports complex types (polymorphism, discriminated unions)

## Known Patterns

### List Responses
When an endpoint returns an array, the transformer:
1. Detects `List[Model]` return type
2. Generates list comprehension for parsing
3. Returns `Response[List[Model]]`

### Request Body Handling
- **Models**: `data.model_dump(exclude_unset=True)`
- **Lists of models**: List comprehension with model_dump
- **Primitives**: Direct JSON serialization
- **File uploads**: Multipart form data with proper tuple formatting

### Error Handling
Pre-defined exception hierarchy:
- `ApiError` - Base exception
- `ValidationError` - Request validation
- `AuthenticationError` - 401 responses
- `NotFoundError` - 404 responses

Streaming responses use `_handle_streaming_response()` to avoid body access.

## CI/CD

### GitHub Actions

The project uses GitHub Actions for continuous integration. The workflow (`.github/workflows/ci.yml`) runs on every push and pull request to main/master branches.

#### CI Jobs

1. **Lint** - Runs ruff to check code style and imports
2. **Type Check** - Runs ty to validate type hints
3. **Test** - Runs pytest on Python 3.11 and 3.12
4. **Integration** - Generates clients to verify the tool works end-to-end

All jobs use `uv` for fast dependency management and run in parallel for efficiency.

## Current Features

### ✅ Implemented
- **Sync/Async Generation**: Full support for both modes with optimized templates
- **Server-Sent Events**: Complete SSE streaming support (async only)
- **File Uploads**: Multi-file and metadata upload support
- **Type Safety**: Full Pydantic model generation and type hints
- **Error Handling**: Comprehensive exception hierarchy
- **CLI Interface**: Complete command-line tool with all options
- **Test Automation**: Fixture generation and comprehensive test coverage
- **Method Naming**: Advanced naming strategy with conflict resolution

### 🚧 Future Enhancements

1. **Webhooks**: Handle OpenAPI 3.1 webhooks  
2. **Custom Auth**: Plugin system for auth methods
3. **Pagination**: Automatic pagination handling
4. **Retries**: Configurable retry logic with backoff
5. **Request Middleware**: Plugin system for request/response modification
6. **OpenAPI 3.1**: Full support for latest OpenAPI specification features