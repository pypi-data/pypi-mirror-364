# Developer Guide

## Development Setup

```shell
# Clone the repository
git clone https://github.com/your-org/sdk-python.git
cd sdk-python

# Install in development mode with all dependencies
pip install -e ".[dev]"
# This installs: linting, testing, and aws extras

# Check linting issues
ruff format --preview --check src tests
ruff check src tests

# Fix linting issues
ruff format --preview src tests
ruff check --fix --preview src tests

# Run tests
pytest
```

## Development Guidelines

> [!WARNING]  
> When introducing a new `.py` file, make sure to add it in the appropriate `__init__.py` file, otherwise it will not be made available in the published package.

## Publishing

### Recommended: GitHub Actions

1. **Merge your changes** to the main branch

2. **Create Release** using GitHub UI:
   - Go to "Releases" → "Draft a new release"
   - Choose tag → Enter "v1.2.0" → "Create new tag"
   - Click "Generate release notes"
   - Click "Publish release"

3. **Automatic publication**: GitHub Actions automatically publishes to PyPI using the version from the git tag

> [!NOTE]
> No version updates needed in `pyproject.toml`! The version is automatically extracted from the git tag during the build process.

### Verify Build

When introducing a new file, ensure the file will be made available in the published package.

```shell
python -m build
mkdir -p wheel_extract
# Extract the wheel (it's just a zip file)
unzip dist/baresquare_sdk-*.whl -d wheel_extract
# View the contents
ls -la wheel_extract
# Specifically check for your Python files
find wheel_extract -name "*.py"
```