# Contributing to Hugo Speaker Generator

Thank you for your interest in contributing to the Hugo Speaker Generator! This document provides guidelines and instructions for developers.

## Development Setup

### 1. Clone and Setup Environment

```bash
git clone https://github.com/ndewijer/Communityday-hugo-speaker-generator.git
cd Communityday-hugo-speaker-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies (includes pre-commit, black, flake8)
pip install -r dev-requirements.txt
```

### 3. Setup Pre-commit Hooks

Pre-commit hooks ensure code quality and consistency. They run automatically before each commit.

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files (optional, but recommended)
pre-commit run --all-files
```

## Code Quality Standards

This project uses several tools to maintain code quality:

### Pre-commit Hooks

The following hooks run automatically on every commit:

- **Trailing Whitespace**: Removes trailing whitespace from files
- **End of File Fixer**: Ensures files end with a newline
- **Large File Check**: Prevents accidentally committing large files
- **Black**: Code formatting (Python 3.13 compatible)
- **Flake8**: Linting with Google docstring conventions

### Manual Code Quality Checks

You can run these tools manually:

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run individual tools
black .                    # Format code
flake8 .                   # Lint code
```

### Code Style Guidelines

- **Line Length**: Maximum 100 characters
- **Docstrings**: Google style docstrings required for all functions and classes
- **Type Hints**: Use type hints for function parameters and return values
- **Import Organization**: Follow PEP 8 import ordering

### Flake8 Configuration

The project uses these flake8 settings:
- `--docstring-convention=google`: Google-style docstrings
- `--max-line-length=100`: 100 character line limit
- `--extend-ignore=D202,D212,D400,D403,F541`: Specific rule exceptions

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the style guidelines
- Add/update docstrings for new functions and classes
- Add type hints where appropriate

### 3. Test Your Changes

```bash
# Run the application
python main.py

# Run code quality checks
pre-commit run --all-files
```

### 4. Commit Changes

Pre-commit hooks will run automatically:

```bash
git add .
git commit -m "feat: add your feature description"
```

If pre-commit hooks fail:
- Fix the issues reported
- Stage the changes again
- Commit again

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Continuous Integration

The project uses GitHub Actions for CI/CD:

### CI Pipeline

The CI pipeline (`.github/workflows/python-ci.yml`) runs:
1. Python 3.13 setup
2. Dependency installation (runtime + development)
3. All pre-commit hooks via `pre-commit run --all-files`

### Local vs CI Consistency

The CI pipeline uses the exact same tools and versions as local development:
- Same pre-commit configuration
- Same tool versions from `dev-requirements.txt`
- Same flake8 rules and settings

## Project Structure

```
├── src/                          # Source code modules
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration and constants
│   ├── data_processor.py        # Excel data processing
│   ├── speaker_generator.py     # Speaker page generation
│   ├── session_generator.py     # Session page generation
│   ├── image_processor.py       # Image processing
│   └── utils.py                 # Utility functions
├── .github/workflows/           # GitHub Actions CI/CD
├── .pre-commit-config.yaml      # Pre-commit configuration
├── dev-requirements.txt         # Development dependencies
├── requirements.txt             # Runtime dependencies
└── main.py                      # Application entry point
```

## Common Development Tasks

### Adding New Features

1. **New Modules**: Add to `src/` directory with proper docstrings
2. **Configuration**: Update `src/config.py` for new settings
3. **Dependencies**: Add to `requirements.txt` (runtime) or `dev-requirements.txt` (development)

### Updating Dependencies

```bash
# Update development dependencies
pip install --upgrade pre-commit black flake8 flake8-docstrings
pip freeze | grep -E "(pre-commit|black|flake8)" > temp_versions.txt
# Update dev-requirements.txt with new versions
```

### Debugging Pre-commit Issues

```bash
# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify -m "temporary commit"

# Update pre-commit hooks
pre-commit autoupdate
```

## Code Review Guidelines

### For Contributors

- Ensure all pre-commit hooks pass
- Write clear commit messages
- Add docstrings for new functions/classes
- Update documentation if needed

### For Reviewers

- Check that CI passes
- Verify code follows project conventions
- Ensure new features have appropriate error handling
- Confirm documentation is updated

## Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub discussions for questions
- **Code Style**: Refer to this document and existing code examples

## Release Process

1. Update version numbers if applicable
2. Update CHANGELOG.md (if exists)
3. Create release branch
4. Ensure all tests pass
5. Create GitHub release with appropriate tags

---

Thank you for contributing to Hugo Speaker Generator! 🚀
