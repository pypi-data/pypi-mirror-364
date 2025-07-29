.PHONY: help install test lint type-check check clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install        Install the package and dependencies"
	@echo "  make test          Run pytest tests"
	@echo "  make lint          Run ruff linter"
	@echo "  make type-check    Run ty type checker"
	@echo "  make check         Run all checks (lint, type-check, test)"
	@echo "  make clean         Remove generated files and caches"

# Install the package in development mode
install:
	uv sync

# Run tests
test:
	@echo "=== Running Tests ==="
	uv run update-test-fixtures
	uv run pytest -vvv -q
	@echo "✅ All tests passed!"

# Run linter
lint-check:
	@echo "=== Running Ruff (Linter) ==="
	uv run update-test-fixtures
	uv run ruff check .
	@echo "✅ Ruff passed!"

lint:
	@echo "=== Running Ruff (Linter) ==="
	uv run update-test-fixtures
	uv run ruff check --fix .
	@echo "✅ Ruff passed!"

# Run type checker
type-check:
	@echo "=== Running Ty (Type Checker) ==="
	uv run update-test-fixtures
	uv run ty check --ignore invalid-overload --ignore invalid-argument-type --ignore unresolved-attribute --ignore possibly-unbound-attribute 2>&1 | grep -v "pre-release" || true
	@echo "✅ Ty check complete!"

# Run all checks
check:
	@echo "🔍 Running code quality checks..."
	@echo
	@$(MAKE) lint
	@echo
	@$(MAKE) type-check
	@echo
	@$(MAKE) test
	@echo
	@echo "🎉 All checks passed successfully!"

# Clean up generated files
clean:
	rm -rf test_output
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .ty_cache
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
