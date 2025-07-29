# Contributing to Hugo Speaker Generator

Thank you for your interest in contributing to the Hugo Speaker Generator! This document provides guidelines and instructions for developers.

## Development Setup

### Environment Setup Matrix

Choose the appropriate setup based on your development needs:

#### Setup Option A: Basic Installation (Recommended for most contributors)

**Use when:**
- Contributing to core functionality (data processing, file generation)
- Working on documentation or configuration
- LinkedIn image extraction is not critical for your changes

**Setup:**
```bash
git clone https://github.com/ndewijer/Communityday-hugo-speaker-generator.git
cd Communityday-hugo-speaker-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt

# Setup pre-commit hooks
pre-commit install
```

**Limitations:**
- LinkedIn image extraction uses basic HTTP requests (lower success rate)
- May fail on LinkedIn profiles with anti-scraping measures

#### Setup Option B: Enhanced Installation (For LinkedIn-focused development)

**Use when:**
- Working on LinkedIn integration features
- Testing image processing improvements
- Need high-success LinkedIn image extraction

**Setup:**
```bash
git clone https://github.com/ndewijer/Communityday-hugo-speaker-generator.git
cd Communityday-hugo-speaker-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install enhanced dependencies
pip install -r requirements.txt
pip install -r requirements-selenium.txt
pip install -r dev-requirements.txt

# Setup pre-commit hooks
pre-commit install
```

**Additional Requirements:**
- Chrome browser installed
- One-time LinkedIn login setup (see [LINKEDIN_SELENIUM_GUIDE.md](LINKEDIN_SELENIUM_GUIDE.md))
- More disk space for browser dependencies

#### Environment Verification

Test your setup:
```bash
# Verify basic functionality
python main.py --help

# Test with sample data
cp samples/responses+votes.xlsx data/
python main.py

# Verify pre-commit hooks
pre-commit run --all-files
```

#### Environment Troubleshooting

| Issue | Basic Setup | Enhanced Setup |
|-------|-------------|----------------|
| Import errors | Check `requirements.txt` installation | Check `requirements-selenium.txt` installation |
| LinkedIn failures | Expected behavior | Check Chrome installation & LinkedIn login |
| Pre-commit failures | Run `pre-commit install` | Same as basic |
| Permission errors | Check `generated_files/` permissions | Same as basic |

## Data Security & Privacy Guidelines

### Sensitive Data Handling

This project processes speaker information and LinkedIn data. Follow these security practices:

#### Development Data
- **Never commit real speaker data** to the repository
- Use sample data in `samples/` directory for testing
- Real Excel files should be placed in `data/` (gitignored)
- Clear `generated_files/` before committing if it contains real data

#### LinkedIn Integration Security
- **Personal LinkedIn credentials** are stored locally only
- Selenium session data is stored in `.selenium/` (gitignored)
- Never share or commit LinkedIn session files
- Use rate limiting to respect LinkedIn's terms of service

#### Data Sanitization for Testing
```bash
# Create sanitized test data
cp data/responses+votes.xlsx samples/test-data-sanitized.xlsx
# Manually replace real names/emails with fake data in the copy
```

#### Security Checklist Before Committing
- [ ] No real speaker names, emails, or LinkedIn profiles in committed files
- [ ] No LinkedIn session data or credentials
- [ ] Sample data uses fictional information
- [ ] Generated files directory is clean or gitignored

### GDPR & Privacy Considerations
- Speaker data should be processed with consent
- Generated files may contain personal information
- Consider data retention policies for your use case
- Implement data deletion procedures when needed

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

## Git Workflow & Branching Strategy

### Branch Naming Conventions

Use descriptive branch names with prefixes:

- `feature/description` - New features (e.g., `feature/linkedin-selenium-integration`)
- `bugfix/description` - Bug fixes (e.g., `bugfix/image-processing-error`)
- `hotfix/description` - Critical fixes for production issues
- `docs/description` - Documentation updates (e.g., `docs/update-contributing-guide`)
- `refactor/description` - Code refactoring without functional changes

### Branch Protection & Requirements

The `main` branch is protected with the following requirements:
- All changes must go through Pull Requests
- CI checks must pass (pre-commit hooks via GitHub Actions)
- At least one review required for external contributors
- Branch must be up-to-date before merging

### Pull Request Workflow

1. **Create Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes & Commit**
   ```bash
   # Make your changes
   git add .
   git commit -m "feat: add your feature description"

   # Push to your branch
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Use descriptive PR titles following conventional commits
   - Fill out the PR template with:
     - Description of changes
     - Testing performed
     - Screenshots (if UI changes)
     - Breaking changes (if any)

4. **Address Review Feedback**
   ```bash
   # Make requested changes
   git add .
   git commit -m "fix: address review feedback"
   git push origin feature/your-feature-name
   ```

5. **Merge Strategy**
   - Use "Squash and merge" for feature branches
   - Use "Merge commit" for release branches
   - Delete branch after successful merge

### Commit Message Conventions

Follow conventional commits format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Issue Management & Triage

### Current Labels

The repository uses these labels for issue categorization:

#### Type Labels
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `question` - Further information is requested

#### Status Labels
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `duplicate` - This issue or pull request already exists
- `invalid` - This doesn't seem right
- `wontfix` - This will not be worked on

#### Component Labels
- `component:excel-processing` - Issues related to Excel data processing
- `component:image-processing` - Issues related to image downloading/processing
- `component:linkedin-integration` - Issues related to LinkedIn functionality
- `component:hugo-generation` - Issues related to Hugo file generation

#### Priority Labels
- `priority:high` - High priority issues
- `priority:medium` - Medium priority issues
- `priority:low` - Low priority issues

#### Environment Labels
- `env:selenium` - Issues specific to Selenium setup
- `env:basic` - Issues with basic installation

#### Special Labels
- `dependencies` - Dependency updates (used by Dependabot)

### Issue Triage Process

#### For New Issues:
1. **Add type label** (`bug`, `enhancement`, `documentation`, `question`)
2. **Add component label** if applicable
3. **Add priority label** based on impact
4. **Add environment label** if setup-specific
5. **Add `good first issue`** for newcomer-friendly tasks

#### For Bug Reports:
- Require environment details (basic vs enhanced setup)
- Ask for sample data or steps to reproduce
- Label with affected component
- Set priority based on severity

#### For Feature Requests:
- Discuss scope and implementation approach
- Label with affected components
- Consider breaking large features into smaller issues
- Add `help wanted` if community contribution is welcome

## Dependency Management with Dependabot

### Automated Dependency Updates

This project uses Dependabot for automated dependency management:

#### Python Dependencies
- **Schedule**: Monthly updates
- **Grouping**: Minor and patch updates are grouped together
- **Limit**: Maximum 10 open PRs at once
- **Labels**: Automatically tagged with `dependencies`
- **Reviewer**: @ndewijer assigned for review

#### GitHub Actions Dependencies
- **Schedule**: Monthly updates for workflow actions
- **Labels**: Tagged with `dependencies` and `ci`

### Handling Dependabot PRs

#### For Maintainers:
1. **Review the changes**: Check changelog and breaking changes
2. **Test locally**:
   ```bash
   git checkout dependabot/pip/python-packages-{date}
   pip install -r requirements.txt -r dev-requirements.txt
   python main.py  # Test with sample data
   pre-commit run --all-files
   ```
3. **Merge strategy**: Use "Squash and merge" for dependency updates
4. **Monitor**: Watch for issues after merging grouped updates

#### For Contributors:
- Dependabot PRs don't require contributor action
- If your PR conflicts with dependency updates:
  ```bash
  git checkout main
  git pull origin main
  git checkout your-feature-branch
  git rebase main
  ```

### Dependency Update Policy

#### Auto-merge Criteria:
- Patch version updates (e.g., 1.0.1 → 1.0.2)
- CI passes successfully
- No breaking changes in changelog

#### Manual Review Required:
- Minor version updates (e.g., 1.0.0 → 1.1.0)
- Major version updates (e.g., 1.0.0 → 2.0.0)
- Security updates (always prioritized)
- Updates affecting core dependencies (pandas, requests, selenium)

### Managing Dependency Conflicts

If dependency updates cause issues:

1. **Identify the problematic package**:
   ```bash
   pip list | grep {package-name}
   ```

2. **Pin the version temporarily**:
   ```bash
   # In requirements.txt or dev-requirements.txt
   problematic-package==1.2.3  # Pin to last working version
   ```

3. **Create an issue** with `dependencies` label to track the problem

4. **Update Dependabot config** if needed to exclude problematic packages:
   ```yaml
   # In .github/dependabot.yml
   ignore:
     - dependency-name: "problematic-package"
       versions: ["2.x"]
   ```

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
│   ├── linkedin_selenium_extractor.py  # LinkedIn integration
│   └── utils.py                 # Utility functions
├── .github/workflows/           # GitHub Actions CI/CD
├── .pre-commit-config.yaml      # Pre-commit configuration
├── dev-requirements.txt         # Development dependencies
├── requirements.txt             # Runtime dependencies
├── requirements-selenium.txt    # Enhanced dependencies
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
- Write clear commit messages following conventional commits
- Add docstrings for new functions/classes
- Update documentation if needed
- Follow data security guidelines
- Test with both basic and enhanced setups if applicable

### For Reviewers

- Check that CI passes
- Verify code follows project conventions
- Ensure new features have appropriate error handling
- Confirm documentation is updated
- Verify no sensitive data is committed
- Check appropriate labels are applied to PRs

## Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub discussions for questions
- **Code Style**: Refer to this document and existing code examples
- **LinkedIn Setup**: See [LINKEDIN_SELENIUM_GUIDE.md](LINKEDIN_SELENIUM_GUIDE.md) for detailed instructions

## Release Process

1. Update version numbers if applicable
2. Update CHANGELOG.md (if exists)
3. Create release branch
4. Ensure all tests pass
5. Create GitHub release with appropriate tags

---

Thank you for contributing to Hugo Speaker Generator! 🚀
