.PHONY: test lint format check clean help coverage

## Development Targets

test:
	@echo "Running tests with pytest..."
	pytest -v
	@echo "✅ All tests passed"

coverage:
	@echo "Running tests with coverage..."
	coverage run -m pytest -v
	@echo ""
	@echo "Coverage Report:"
	coverage report
	@echo ""
	@echo "Generating HTML coverage report..."
	coverage html
	@echo "✅ Coverage report generated (htmlcov/index.html)"

lint:
	@echo "Running type-checker..."
	mypy braxis.py --strict
	@echo "✅ Type-checking passed"
	@echo ""
	@echo "Running linter..."
	ruff check braxis.py
	@echo "✅ Linting passed"
	@echo ""
	@echo "Checking formatting..."
	ruff format braxis.py --check
	@echo "✅ Formatting check passed"

format:
	@echo "Formatting code..."
	ruff format braxis.py
	@echo "✅ Code formatted"

check: test lint
	@echo "✅ All checks passed (tests + lint)"

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ .mypy_cache .ruff_cache *.pyc
	find . -type d -name '__pycache__' -exec rm -rf {} +
	@echo "✅ Cleaned"

help:
	@echo "Braxis Development Targets:"
	@echo ""
	@echo "  make test       Run unit tests with pytest"
	@echo "  make coverage   Run tests with coverage reporting"
	@echo "  make lint       Run type-checker + linter + format check"
	@echo "  make format     Auto-format code with ruff"
	@echo "  make check      Run tests + lint (comprehensive check)"
	@echo "  make clean      Remove cache and temporary files"
	@echo "  make help       Show this help message"
	@echo ""
	@echo "Recommended workflow:"
	@echo "  1. make check       # Verify everything passes"
	@echo "  2. make coverage    # Check test coverage"
	@echo "  3. git commit       # Commit changes"
	@echo "  4. git push         # Push to remote"
