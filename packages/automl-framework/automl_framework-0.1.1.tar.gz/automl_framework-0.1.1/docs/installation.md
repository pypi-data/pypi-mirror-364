# Installation Guide for AutoML Framework

## Prerequisites

### System Requirements
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Required Dependencies
- scikit-learn
- numpy
- pandas
- matplotlib
- seaborn

## Installation Methods

### 1. Standard Installation (Recommended)
```bash
# Install latest stable version
pip install automl-framework
```

### 2. Development Version
```bash
# Install from GitHub (latest development)
pip install git+https://github.com/nandarizkika/automl-framework.git
```

### 3. Local Development Setup
```bash
# Clone the repository
git clone https://github.com/nandarizkika/automl-framework.git
cd automl-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install in editable mode
pip install -e .
```

## Installation Options

### Minimal Install
```bash
pip install automl-framework
```

### Full Installation (Recommended)
```bash
# Install with all optional dependencies
pip install automl-framework[all]
```

### Specific Feature Installations
```bash
# Visualization tools
pip install automl-framework[visualization]

# Advanced hyperparameter tuning
pip install automl-framework[tuning]

# Deep learning extensions
pip install automl-framework[deep-learning]
```

## Verification

### Check Installation
```bash
# Verify installation
python -c "import automl; print(automl.__version__)"
```

## Troubleshooting

### Common Installation Issues
- Ensure you have the latest pip: `pip install --upgrade pip`
- Check Python version compatibility
- Install system-level dependencies if required

### Dependency Conflicts
If you encounter dependency conflicts:
1. Use a virtual environment
2. Check package versions
3. Consider using `conda` for environment management

## System-Specific Notes

### Windows
- Ensure you have Visual C++ build tools
- Use Anaconda or Python from the Microsoft Store for easier setup

### macOS
- Install Python via Homebrew or official Python.org installer
- May require Xcode command-line tools

### Linux
- Use system package manager to install Python development tools
- Most distributions come with pip pre-installed

## Optional Dependencies

| Feature Group | Packages Included |
|--------------|-------------------|
| Visualization | matplotlib, seaborn, plotly |
| Tuning | scikit-optimize, hyperopt |
| Deep Learning | tensorflow, keras, torch |

## Reporting Installation Issues

If you encounter any problems:
- Check [GitHub Issues](https://github.com/nandarizkika/automl-framework/issues)
- Open a new issue with detailed error logs
- Include:
  - Python version
  - Operating system
  - Full error traceback
  - Installation method used

## Next Steps
- [Quick Start Guide](quickstart.md)
- [Basic Usage Examples](examples/basic_usage.md)

---

<div align="center">
🚀 Happy Machine Learning! 🤖
</div>
