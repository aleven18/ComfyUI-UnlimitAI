# Contributing to ComfyUI-UnlimitAI

First off, thank you for considering contributing to ComfyUI-UnlimitAI! It's people like you that make this project great.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. By participating, you are expected to:

- Be respectful and inclusive
- Be patient and welcoming
- Be collaborative
- Be careful with words and actions

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

**Bug Report Template**:

```markdown
**Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
- OS: [e.g. macOS, Windows, Linux]
- Python Version: [e.g. 3.10.0]
- ComfyUI Version: [e.g. latest]
- Plugin Version: [e.g. 1.0.0]

**Additional Context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

**Feature Request Template**:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional Context**
Add any other context or screenshots about the feature request.
```

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the coding standards
- Include tests for new features
- Update documentation for changes

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/ComfyUI-UnlimitAI.git
cd ComfyUI-UnlimitAI

# Add upstream remote
git remote add upstream https://github.com/original-owner/ComfyUI-UnlimitAI.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Set Up Pre-commit Hooks

```bash
# Install pre-commit
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### 5. Create Branch

```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

```python
# Line length: 100 characters (not 79)
# Use 4 spaces for indentation (no tabs)

# Good
def function_with_long_name(parameter_one, parameter_two,
                           parameter_three):
    """Function description."""
    return parameter_one + parameter_two


# Bad
def function_with_long_name(parameter_one, parameter_two, parameter_three):
    return parameter_one + parameter_two
```

### Code Formatting

We use **Black** for code formatting:

```bash
# Format code
black .

# Format specific file
black path/to/file.py
```

### Import Sorting

We use **isort** for import sorting:

```bash
# Sort imports
isort .

# Sort imports in specific file
isort path/to/file.py
```

### Type Annotations

We use type annotations for better code clarity:

```python
# Good
def generate_image(
    prompt: str,
    model: str = "flux.1-schnell",
    size: str = "1024x1024"
) -> str:
    """Generate image from prompt."""
    pass


# Bad
def generate_image(prompt, model="flux.1-schnell", size="1024x1024"):
    pass
```

### Documentation

Use docstrings for all public modules, functions, classes, and methods:

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    A brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is empty
        APIError: When API call fails
    
    Examples:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

### Logging

Use our logging system instead of print statements:

```python
from utils.logger import get_logger

logger = get_logger(__name__)

# Good
logger.info("Processing started")
logger.error(f"Failed to process: {e}", exc_info=True)

# Bad
print("Processing started")
print(f"Failed to process: {e}")
```

### Testing

Write tests for new features:

```python
import pytest

class TestNewFeature:
    """Tests for new feature."""
    
    def test_success_case(self):
        """Test successful scenario."""
        result = new_feature()
        assert result is not None
    
    def test_failure_case(self):
        """Test failure scenario."""
        with pytest.raises(ValueError):
            new_feature(invalid_param=True)
```

---

## Commit Guidelines

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools

### Examples

```bash
# Feature
feat(api): add support for new video model

# Bug fix
fix(nodes): correct image size validation

# Documentation
docs(readme): update installation instructions

# Refactoring
refactor(utils): simplify delay calculation logic

# Test
test(character): add tests for character consistency

# Chore
chore(deps): update dependencies to latest versions
```

### Commit Best Practices

- Use the imperative mood in the subject line
- Capitalize the subject line
- Do not end the subject line with a period
- Limit the subject line to 72 characters
- Separate subject from body with a blank line
- Use the body to explain what and why vs. how

---

## Pull Request Process

### 1. Before Submitting

- ✅ Update documentation
- ✅ Add tests for new features
- ✅ Ensure all tests pass
- ✅ Run linters (black, isort, flake8)
- ✅ Run type checker (mypy)
- ✅ Update CHANGELOG.md

### 2. Submitting

1. Push your changes to your fork
2. Create a Pull Request from your branch to `main`
3. Fill in the PR template
4. Request review from maintainers

### 3. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
Description of tests

## Checklist:
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests
- [ ] New and existing unit tests pass
- [ ] Any dependent changes have been merged

## Screenshots (if applicable)
```

### 4. Review Process

- PRs require at least one approval
- Address all review comments
- Maintain a clean commit history
- Squash commits if requested

### 5. After Approval

- A maintainer will merge your PR
- Your contribution will be added to CHANGELOG.md
- Thank you! 🎉

---

## Testing

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test file
pytest tests/test_utils.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Test Coverage

We aim for at least 80% test coverage. To check coverage:

```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Additional Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)

---

## Questions?

Feel free to open an issue or reach out to the maintainers if you have any questions!

---

Thank you for contributing! ❤️
