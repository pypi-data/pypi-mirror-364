# Packaging Guide for ByGoD (Bible Gateway Downloader)

This document outlines the packaging and distribution process for the ByGoD project using Pipfile for dependency management.

## 📦 Dependency Management

### Pipfile Structure

The project uses **Pipfile** as the single source of truth for dependencies:

```toml
[packages]
aiohttp = ">=3.8.0"
beautifulsoup4 = ">=4.11.0"
colorlog = ">=6.7.0"
pyyaml = ">=6.0"
lxml = ">=4.9.0"

[dev-packages]
pytest = "*"
black = "*"
flake8 = "*"
isort = "*"
mypy = "*"
pylint = "*"
bandit = "*"
pydocstyle = "*"
vulture = "*"
radon = "*"
safety = "*"
pre-commit = "*"
twine = "*"
build = "*"
```

### Key Benefits

- **Single Source of Truth**: All dependencies defined in Pipfile
- **Development Tools**: Comprehensive dev dependencies for code quality
- **Version Pinning**: Pipfile.lock ensures reproducible builds
- **Modern Python**: Uses pipenv for dependency resolution

## 🏗️ Build Configuration

### setup.py

The `setup.py` automatically reads dependencies from Pipfile:

```python
def read_pipfile_requirements():
    # Parses [packages] section from Pipfile
    # Returns list of dependencies for install_requires

def read_pipfile_dev_requirements():
    # Parses [dev-packages] section from Pipfile
    # Returns list of dependencies for extras_require
```

### pyproject.toml

Configured to work with setup.py:

```toml
[project]
dynamic = ["version", "dependencies", "optional-dependencies"]
# Dependencies are read from setup.py which reads from Pipfile
```

## 🚀 Development Setup

### Using Pipenv (Recommended)

1. **Install pipenv**:
   ```bash
   pip install pipenv
   ```

2. **Install dependencies**:
   ```bash
   pipenv install
   pipenv install --dev
   ```

3. **Activate virtual environment**:
   ```bash
   pipenv shell
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .
   ```

### Using pip (Alternative)

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies manually**:
   ```bash
   pip install aiohttp>=3.8.0 beautifulsoup4>=4.11.0 colorlog>=6.7.0 pyyaml>=6.0 lxml>=4.9.0
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

## 📦 Building the Package

### Automated Build

Use the build script:

```bash
python build_package.py
```

This script:
- Cleans previous builds
- Installs build dependencies
- Builds source distribution and wheel
- Validates the package

### Manual Build

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*
```

## 🧪 Testing

### Run Tests

```bash
# Using pipenv
pipenv run python tests.py

# Using pip
python tests.py
```

### Code Quality

```bash
# Format code
pipenv run black .

# Sort imports
pipenv run isort .

# Lint code
pipenv run flake8 .

# Type checking
pipenv run mypy .
```

## 📤 Distribution

### Local Installation

```bash
pip install dist/bygod-*.whl
```

### PyPI Upload

1. **TestPyPI (for testing)**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **PyPI (production)**:
   ```bash
   twine upload dist/*
   ```

## 🔧 Maintenance

### Adding Dependencies

1. **Runtime dependencies**:
   ```bash
   pipenv install package-name
   ```

2. **Development dependencies**:
   ```bash
   pipenv install --dev package-name
   ```

3. **Update Pipfile.lock**:
   ```bash
   pipenv lock
   ```

### Updating Dependencies

```bash
# Update all dependencies
pipenv update

# Update specific package
pipenv update package-name
```

### Security Checks

```bash
# Check for security vulnerabilities
pipenv run safety check
```

## 📋 File Structure

```
bible-gateway-downloader/
├── Pipfile                 # Dependency definitions
├── Pipfile.lock           # Locked dependency versions
├── setup.py               # Package configuration (reads Pipfile)
├── pyproject.toml         # Build system configuration
├── build_package.py       # Automated build script
├── release.py             # Release automation script
├── MANIFEST.in            # Package file inclusion rules
├── .gitignore             # Git ignore rules
├── bible_downloader.py    # Main package code
├── tests.py               # Test suite
└── README.md              # Project documentation
```

## 🎯 Best Practices

1. **Always use Pipfile**: Don't manually edit requirements.txt
2. **Lock dependencies**: Keep Pipfile.lock in version control
3. **Test builds**: Always test package installation before release
4. **Update documentation**: Keep README.md current with installation instructions
5. **Version bumping**: Update version in setup.py before release
6. **Security**: Regularly run safety checks on dependencies

## 🆘 Troubleshooting

### Common Issues

**Build fails with dependency errors**:
- Ensure Pipfile is up to date
- Run `pipenv lock` to regenerate Pipfile.lock
- Check that setup.py can parse Pipfile correctly

**Package installs but CLI doesn't work**:
- Verify entry_points in setup.py
- Check that bible_downloader.py has a main() function
- Test with `python -m bible_downloader`

**Development environment issues**:
- Delete and recreate virtual environment
- Run `pipenv --rm` then `pipenv install`
- Check Python version compatibility

### Getting Help

- Check the logs for detailed error messages
- Verify all dependencies are correctly specified in Pipfile
- Ensure build tools are up to date
- Test with a clean virtual environment 