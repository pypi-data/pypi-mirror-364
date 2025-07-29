# openapi-to-httpx

[![CI](https://github.com/piercefreeman/openapi-to-httpx/actions/workflows/ci.yml/badge.svg)](https://github.com/piercefreeman/openapi-to-httpx/actions/workflows/ci.yml)

An OpenAPI client generator for Python that uses AST transformation to create type-safe HTTP clients.

AST generation of code is a pain, which is why most generation libraries like [openapi-generator](https://github.com/OpenAPITools/openapi-generator) rely on mustache/jinja code template to populate. But code templates are brittle, rely on manually stringing together whitespace in languages like Python, and have so many edge cases codified in the template they'll make your head spin. Luckily LLMs have _very_ strong performance in writing AST parsers for input code.

Unlike traditional code generators that use templates, this tool:
1. Defines an ideal, idiomatic Python client structure
2. Uses AST (Abstract Syntax Tree) manipulation to inject OpenAPI-specific details
3. Generates clean, type-safe code with full IDE support

This is an experiment in programming 95% of this AST logic via LLMs and agents alone. This trades some code interpretability for speed of development - but we figure that in the AST parsing game, this is best left for machines versus human rules anyway.

## Installation

```bash
uv sync
```

## Quick Start

```bash
# Generate from a URL
uv run openapi-to-httpx https://api.example.com/openapi.json -o ./my_client

# Generate from a local file
uv run openapi-to-httpx ./my-api.yaml -o ./my_client

# Use the built-in Petstore example
uv run openapi-to-httpx --petstore -o ./petstore_client
```

## Generated Client Usage

By default we'll generate an async client so you can use it with non-blocking function calls.

```python
from my_client import APIClient
from my_client.models import Pet

# Initialize the client
client = APIClient(
    base_url="https://api.example.com",
    api_key="your-api-key"  # or bearer_token="..."
)

# No context manager needed!
# All methods return Response[T] with data, status_code, headers, response_time
response = await client.get_pet_by_id(123)
print(f"Pet name: {response.data.name}")
print(f"Response time: {response.response_time}s")

# Create a new pet
new_pet = Pet(name="Fluffy", photoUrls=["https://..."])
response = await client.add_pet(new_pet)

# List pets
response = await client.find_pets_by_status(status="available")
for pet in response.data:
    print(pet.name)
```

We also support generating a synchronous client by overriding the CLI:

```bash
uv run openapi-to-httpx --mode sync {args}
```

## Improving API names

All OpenAPI schemas need to have an `operationId`. If you're using a framework to auto-generate these OpenAPI schemas (like FastAPI or gin-swagger), these names might be overly verbose like:

```bash
stop_execution_api_v1_execute__session_id__stop__execution_id__delete
```

That's pretty verbose. In every OpenAPI markup library under the sun you can override these names. Do something like this in FastAPI:

```python
@app.delete("/api/v1/execute/{session_id}/stop/{execution_id}", operation_id="stopExecution")
async def stop_execution_api_v1_execute__session_id__stop__execution_id__delete():
    ...
```

## Test Conventions

Testing auto-generated code is not trivial. We take the following general approach to keep our testing relatively straightforward:

- Specify all desired behavior and edge cases within full OpenAPI files. These files will demonstrate the issue at play.
- Generate the full client implementations and place these in `fixtures/libraries` so we can import the real code and benefit from our static typechecking to flag any errors
- Mock out the expected endpoints with pytest-httpx
- Add a new unit test that will call the client implementations and assert values. Because we're dealing with the actual client code, this lets us stress test the expected response as real runtime Python objects

## Features

- **Type-safe**: Full type hints for all parameters and return values
- **Idiomatic Python**: Direct method calls, snake_case naming, optional parameters
- **Rich responses**: Returns Response[T] with data, status_code, headers, and timing
- **Error handling**: Custom exceptions for common HTTP errors
- **Pydantic models**: Auto-generated models with validation
- **Clean separation**: Models in separate file for better organization
- **Connection pooling**: Reuses httpx clients for efficiency
- **CI/CD Ready**: GitHub Actions workflow with linting, type checking, and tests

## How It Works

1. **Template Definition** (`ideal_client.py`): Defines the perfect Python HTTP client interface
2. **AST Parsing**: Parses the template into an Abstract Syntax Tree
3. **Schema Analysis**: Reads the OpenAPI specification
4. **AST Transformation**: Injects endpoints, models, and parameters into the AST
5. **Code Generation**: Outputs clean, formatted Python code
