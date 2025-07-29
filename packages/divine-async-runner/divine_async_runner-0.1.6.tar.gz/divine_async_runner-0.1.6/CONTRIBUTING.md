# Contributing to divine-async-runner

## Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/divinescreener/divine-async-runner.git
cd async-runner
```

### 2. Install Poetry (if not already installed)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install dependencies
```bash
poetry install --with dev
```

### 4. Set up pre-commit hooks
```bash
# Run the setup script
./setup-pre-commit.sh

# Or manually:
poetry run pre-commit install
```

## Code Style

This project uses automated code formatting and linting:

- **ruff**: For code formatting and linting
- **mypy**: For type checking
- **bandit**: For security scanning
- **pre-commit**: Automatically runs formatters before each commit

### Manual formatting
```bash
# Format all files
poetry run pre-commit run --all-files

# Or individual tools
poetry run ruff format .
poetry run ruff check --fix .
poetry run mypy src/
```

### Commit hooks
When you commit, pre-commit will automatically:
1. Format your code with `ruff format`
2. Fix linting issues with `ruff check --fix`
3. Run mypy type checking
4. Run bandit security scanning
5. Remove trailing whitespace
6. Ensure files end with a newline
7. Check YAML/JSON/TOML syntax
8. Detect potential secrets

If any files are modified by the hooks, the commit will fail and you'll need to:
1. Review the changes
2. Stage them with `git add`
3. Commit again

### Bypassing hooks (not recommended)
```bash
git commit --no-verify
```

## Running Tests

```bash
# Run all tests with coverage
poetry run pytest

# Run specific test file
poetry run pytest tests/test_core.py

# Run with verbose output
poetry run pytest -v

# Generate coverage report
poetry run pytest --cov-report html
```

## Making Changes

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Ensure tests pass: `poetry run pytest`
4. Ensure 100% coverage: `poetry run coverage report --fail-under=100`
5. Commit your changes (pre-commit will format automatically)
6. Push and create a pull request

## Code Quality Standards

- Maintain 100% test coverage
- All functions should have type hints
- Follow the existing code style (enforced by ruff)
- Add tests for new functionality
- Update documentation as needed
- Pass all security scans (bandit)

## Testing Guidelines

- Use descriptive test names that explain what is being tested
- Test both success and failure scenarios
- Mock external dependencies (like `anyio.open_process`)
- Test edge cases (empty output, decode errors, cancellation)
- Maintain comprehensive coverage of all code paths

## Pull Request Guidelines

- Include a clear description of the changes
- Reference any related issues
- Ensure all CI checks pass
- Update documentation if needed
- Add tests for new features or bug fixes

## Security

- Never commit secrets or API keys
- Run `poetry run bandit -r src/` before submitting
- Follow secure coding practices
- Report security issues privately via email to security@divine.sh

## Documentation

- Keep README.md up to date
- Update API documentation for any interface changes
- Include practical examples in the `examples/` directory
- Use clear, concise language

Thank you for contributing to divine-async-runner!