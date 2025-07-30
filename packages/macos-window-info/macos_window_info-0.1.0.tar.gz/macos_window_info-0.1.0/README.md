# macos-window-info

A Python project to find the process ID (PID) of a window by its title or other attributes.

[![Build and Test](https://github.com/bsamartins/macos-window-info/actions/workflows/build.yml/badge.svg)](https://github.com/bsamartins/macos-window-info/actions/workflows/build.yml)
[![Code Quality](https://github.com/bsamartins/macos-window-info/actions/workflows/code-quality.yml/badge.svg)](https://github.com/bsamartins/macos-window-info/actions/workflows/code-quality.yml)
[![PyPI version](https://badge.fury.io/py/macos-window-info.svg)](https://badge.fury.io/py/macos-window-info)

## Requirements
- Python 3.13 or higher
- macOS (uses Quartz framework)

## Installation

### From PyPI
```bash
pip install macos-window-info
```

### From source
This project uses [Poetry](https://python-poetry.org/) for dependency management.

```bash
poetry install
```

## Usage
Run the main script:

```bash
python macos-window-info.py
```

Or if installed via pip:

```bash
macos-window-info
```

## Development

### Setting up development environment
```bash
# Clone the repository
git clone https://github.com/bsamartins/macos-window-info.git
cd macos-window-info

# Install with development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run code formatting
poetry run black src/

# Run linting
poetry run flake8 src/
```

### CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **Build and Test**: Runs on every push and pull request, testing across multiple OS and Python versions
- **Code Quality**: Runs code formatting, linting, and security checks
- **Publish**: Automatically publishes to PyPI when a new release is created

#### Setting up PyPI publishing

To enable automatic publishing to PyPI, you need to set up the following secrets in your GitHub repository:

1. `PYPI_API_TOKEN`: Your PyPI API token for publishing to the main PyPI
2. `TEST_PYPI_API_TOKEN`: Your Test PyPI API token for testing releases

You can create these tokens at:
- PyPI: https://pypi.org/manage/account/token/
- Test PyPI: https://test.pypi.org/manage/account/token/

#### Manual publishing

You can also manually trigger publishing to Test PyPI using the workflow dispatch feature in GitHub Actions.

## Author
Bernardo Martins (<bsamartins@gmail.com>)

