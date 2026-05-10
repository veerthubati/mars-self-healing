# Contributing to MARS

Thank you for your interest in contributing to the MARS self-healing framework. This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature suggestion:

1. Check existing issues to avoid duplicates
2. Open a new issue with a clear title and description
3. Include steps to reproduce (for bugs)
4. Tag the issue appropriately (bug, enhancement, documentation)

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes following the code style guidelines below
4. Add tests for new functionality
5. Run the test suite (`make test`)
6. Submit a pull request with a clear description of changes

## Code Style

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Write docstrings for all public classes and methods
- Keep functions focused and under 50 lines where practical
- Use descriptive variable names

## Development Setup

```bash
git clone https://github.com/veerthubati/mars-self-healing.git
cd mars-self-healing
pip install -e ".[dev]"
make test
```

## Testing

- Write unit tests for new agents and components
- Integration tests should use the fault injection framework
- Target 80% code coverage for new contributions

## Code of Conduct

All contributors are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Open a discussion issue or reach out to the maintainers.
