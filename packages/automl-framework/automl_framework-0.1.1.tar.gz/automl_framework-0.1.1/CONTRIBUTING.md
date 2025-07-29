# Contributing to AutoML Framework

## 🌟 Welcome Contributors!

We're thrilled that you're interested in contributing to the AutoML Framework! This document provides guidelines and instructions for contributing to our project.

## 🎯 Our Mission

The AutoML Framework aims to democratize machine learning by providing an intelligent, easy-to-use solution for automated model selection, optimization, and evaluation.

## 🤝 Ways to Contribute

### 1. Code Contributions
- Fix bugs
- Implement new features
- Improve existing functionality
- Enhance documentation

### 2. Non-Code Contributions
- Report bugs
- Suggest features
- Improve documentation
- Write tutorials
- Share use cases

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- GitHub account

### Setup Development Environment
```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/your-username/automl-framework.git
cd automl-framework

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# 4. Install development dependencies
pip install -e .[dev]

# 5. Install pre-commit hooks
pre-commit install
```

## 💻 Development Workflow

### Code Contribution Steps
1. Create a new branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

2. Make your changes
- Follow PEP 8 style guide
- Write clear, concise code
- Add type hints
- Include docstrings

3. Run tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=automl tests/

# Run linters
black .
flake8 .
mypy .
```

4. Commit your changes
```bash
# Conventional commit messages recommended
git add .
git commit -m "feat: add new feature description"
# or
git commit -m "fix: resolve specific bug"
```

5. Push to your fork
```bash
git push origin feature/your-feature-name
```

6. Open a Pull Request
- Provide a clear title and description
- Reference related issues
- Describe the motivation for the changes

## 🧪 Contribution Guidelines

### Code Quality
- Write clean, readable code
- Follow Python best practices
- Include type hints
- Write comprehensive docstrings
- Add unit tests for new functionality

### Documentation
- Update documentation for any changes
- Add examples where appropriate
- Ensure clarity and conciseness

### Testing
- Add unit tests for new features
- Ensure 90%+ test coverage
- Test across different Python versions
- Include edge case testing

## 🔍 Review Process

### Pull Request Checklist
- [ ] Code follows project style guidelines
- [ ] Tests have been added/updated
- [ ] Documentation has been updated
- [ ] Commits are well-documented
- [ ] All tests pass

### Code Review Process
1. Automated checks run
2. Maintainers review the PR
3. Feedback and discussions
4. Approved and merged or request changes

## 🏆 Contribution Recognition

Contributors will be recognized:
- In the project's README
- In the CONTRIBUTORS.md file
- Potentially in release notes

## 🛡️ Code of Conduct

### Our Pledge
- Welcoming and inclusive environment
- Harassment-free experience
- Respectful interactions
- Constructive feedback

### Unacceptable Behavior
- Discriminatory comments
- Personal attacks
- Trolling
- Public or private harassment

## 💬 Communication Channels
- GitHub Issues
- GitHub Discussions
- Project Email: nandarizky52@gmail.com

## 📚 Additional Resources
- [Project Documentation](https://automl-framework.readthedocs.io)
- [GitHub Repository](https://github.com/nandarizkika/automl-framework)
- [Issue Tracker](https://github.com/nandarizkika/automl-framework/issues)

## 🎉 Final Thoughts

Your contributions, no matter the size, are valuable and appreciated. Whether it's a tiny bug fix or a significant feature, we welcome your help in making the AutoML Framework better!

---

<div align="center">
🚀 **Together, We Build Intelligent Machine Learning** 🤖

*Every contribution moves us forward*
</div>
