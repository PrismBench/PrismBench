# Contributing to PrismBench

Thank you for your interest in contributing to PrismBench! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Found a bug? Please report it with detailed reproduction steps
- **Feature Requests**: Have an idea for a new feature? Open an issue to discuss it
- **Code Contributions**: Bug fixes, new features, performance improvements
- **Documentation**: Improve existing docs or add new documentation
- **Examples**: Add example use cases or tutorials

### Before Contributing

1. Check existing [issues](../../issues) and [pull requests](../../pulls) to avoid duplication
2. For major changes, open an issue first to discuss the proposed changes
3. Read our [Code of Conduct](CODE_OF_CONDUCT.md)

## Development Setup

### Prerequisites

- Python 3.12 or higher

### Setting Up the Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PrismBench.git
   cd PrismBench
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/macOS
   # or
   .\venv\Scripts\activate   # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set Up Environment Variables**
   ```bash
   cp apis.key.example apis.key
   # Edit apis.key with your API keys
   ```
5. **Start Services**
   ```bash
   docker compose up
   ```

## Contributing Guidelines

### Branch Naming

Use descriptive branch names:
- `feature/add-new-algorithm`
- `bugfix/fix-mcts-convergence`
- `docs/update-api-documentation`
- `refactor/improve-search-performance`

### Commit Messages

Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(search): add UCB1 exploration strategy
fix(environment): resolve timeout handling bug
docs(api): update endpoint documentation
```

## Code Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Use type hints for all function signatures
- Use docstrings for all public functions and classes
- Use f-strings for string formatting

### Code Formatting

Before submitting, run:
```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy src/
```

### Documentation Style

- Use Google-style docstrings
- Include type information in docstrings
- Provide examples for public APIs

Example:
```python
def calculate_ucb1_score(node: MCTSNode, exploration_constant: float = 1.414) -> float:
    """Calculate UCB1 score for MCTS node selection.
    
    Args:
        node: The MCTS node to evaluate
        exploration_constant: Exploration parameter (typically √2)
        
    Returns:
        UCB1 score for the node
        
    Examples:
        >>> score = calculate_ucb1_score(node, 1.414)
        >>> print(f"Node score: {score}")
    """
```

## Documentation

### Types of Documentation

1. **API Documentation**: Docstrings in code
2. **User Guides**: In `docs/` directory
3. **Component READMEs**: Service-specific documentation

### Documentation Guidelines

- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Link to related documentation

## Pull Request Process

### PR Template

Use this template for pull requests:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (please describe)

## Documentation
- [ ] Documentation updated
- [ ] Docstrings added/updated
- [ ] Examples provided

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No breaking changes (or documented)
```

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one maintainer review required
3. Address all review feedback
4. Maintain clean commit history
5. Squash commits if requested

## Community Guidelines

### Getting Help

- **Documentation**: Check existing documentation first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our Discord community (link in README)

### Reporting Issues

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Reproduction Steps**: Minimal steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, dependencies
6. **Logs**: Relevant error messages or logs

Template:
```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Configure the system with '...'
2. Run the command '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots/Logs**
If applicable, add screenshots or error logs.

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.9.7]
- PrismBench Version: [e.g. 1.0.0]
```

### Feature Requests

For feature requests, include:

1. **Problem Statement**: What problem does this solve?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other solutions considered
4. **Use Cases**: Who would benefit from this feature?

## Recognition

Contributors will be:
- Added to the CONTRIBUTORS.md file
- Mentioned in release notes for significant contributions
- Eligible for contributor badges and recognition

## Questions?

Feel free to reach out:
- Open an issue for bug reports or feature requests
- Contact maintainers directly for sensitive issues

Thank you for contributing to PrismBench!