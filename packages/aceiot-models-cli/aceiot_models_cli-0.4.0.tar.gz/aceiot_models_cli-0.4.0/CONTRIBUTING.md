# Contributing to ACE IoT Models CLI

We welcome contributions to the ACE IoT Models CLI! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setting up your development environment

1. Clone the repository:
```bash
git clone https://github.com/ACE-IoT-Solutions/aceiot-models-cli.git
cd aceiot-models-cli
```

2. Install the package in development mode with dev dependencies:
```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

## Testing

We test against multiple Python versions to ensure compatibility. All code must pass tests on Python 3.10, 3.11, 3.12, and 3.13.

### Running tests locally

#### Using pytest directly:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aceiot_models_cli --cov-report=term-missing

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v
```

#### Using tox for multi-version testing:
```bash
# Install tox if not already installed
uv pip install tox tox-uv

# Run tests on all Python versions
tox

# Run tests on specific Python version
tox -e py310

# Run only linting
tox -e lint

# Run only type checking
tox -e type

# Run formatting
tox -e format
```

### Code Quality

Before submitting a pull request, ensure your code meets our quality standards:

1. **Formatting**: Code must be formatted with ruff
```bash
ruff format src tests
```

2. **Linting**: Code must pass ruff checks
```bash
ruff check src tests
```

3. **Type Checking**: Code must pass pyright type checks
```bash
pyright src
```

4. **Tests**: All tests must pass
```bash
pytest
```

You can run all checks at once using tox:
```bash
tox
```

## Pull Request Process

1. Fork the repository and create your branch from `main`
2. Make your changes and add tests for new functionality
3. Ensure all tests pass on all supported Python versions
4. Update documentation as needed
5. Submit a pull request with a clear description of your changes

### CI/CD

Our GitHub Actions workflow will automatically:
- Run tests on Python 3.10, 3.11, 3.12, and 3.13
- Check code formatting with ruff
- Run type checking with pyright
- Generate coverage reports

All checks must pass before a PR can be merged.

## Release Process

Releases are managed through GitHub releases and automatically published to PyPI. Only maintainers can create releases.

### Creating a Release

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Commit changes: `git commit -m "chore: bump version to X.Y.Z"`
4. Create and push tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
5. Create GitHub release
6. GitHub Actions will automatically run tests and publish to PyPI

## Questions?

If you have questions, please open an issue on GitHub.