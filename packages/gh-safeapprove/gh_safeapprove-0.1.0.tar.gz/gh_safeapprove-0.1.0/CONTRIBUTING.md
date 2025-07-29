# Contributing to gh-safeapprove

Thank you for your interest in contributing to gh-safeapprove! This document provides guidelines for contributing to this project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/danielmeint/gh-safeapprove.git
   cd gh-safeapprove
   ```

2. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## Code Style

This project uses:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

Run these before submitting a PR:
```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Testing

- Add tests for new functionality
- Ensure all tests pass: `pytest tests/ -v`
- Test with both regular GitHub and Enterprise URLs

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Run the test suite
6. Submit a pull request

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a GitHub release
4. PyPI upload will be automated via GitHub Actions

## Questions?

Feel free to open an issue for questions or discussions! 