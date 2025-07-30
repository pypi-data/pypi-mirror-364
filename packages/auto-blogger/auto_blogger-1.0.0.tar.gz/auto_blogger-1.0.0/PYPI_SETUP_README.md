# 📦 PyPI Setup Guide for AUTO-blogger

This guide explains how to set up and publish the AUTO-blogger package to PyPI so users can install it with `pip install auto-blogger`.

## 🏗️ Package Structure

The project has been restructured for PyPI compatibility:

```
AUTO-blogger/
├── auto_blogger/              # Main package directory
│   ├── __init__.py           # Package initialization
│   ├── gui_blogger.py        # Main GUI application
│   ├── automation_engine.py  # Core automation logic
│   ├── log_manager.py        # Logging system
│   ├── css_selector_extractor.py
│   └── configs/              # Configuration files
├── setup.py                  # Setup script (legacy)
├── pyproject.toml           # Modern Python packaging
├── MANIFEST.in              # Include non-Python files
├── build_and_upload.py      # Build and upload script
├── requirements.txt         # Dependencies
├── README.md               # Project documentation
└── LICENSE                 # License file
```

## 🚀 Quick Setup

### 1. Install Build Tools

```bash
pip install --upgrade pip setuptools wheel build twine
```

### 2. Build and Test Package

```bash
# Clean, build, and test everything
python build_and_upload.py --all

# Or step by step:
python build_and_upload.py --clean   # Clean previous builds
python build_and_upload.py --build   # Build package
python build_and_upload.py --test    # Test installation
```

### 3. Upload to Test PyPI (Recommended First)

```bash
# Upload to Test PyPI for testing
python build_and_upload.py --upload-test

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ auto-blogger
```

### 4. Upload to PyPI

```bash
# Upload to production PyPI
python build_and_upload.py --upload
```

## 📋 Prerequisites

### 1. PyPI Account Setup

1. **Create PyPI Account**: [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **Create Test PyPI Account**: [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
3. **Generate API Tokens**:
   - PyPI: [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
   - Test PyPI: [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)

### 2. Configure Twine

Create `~/.pypirc` file:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## 🔧 Manual Build Process

If you prefer manual control:

### 1. Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info/
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### 2. Build Package

```bash
# Modern build method (recommended)
python -m build

# Legacy method (for compatibility)
python setup.py sdist bdist_wheel
```

### 3. Check Package

```bash
twine check dist/*
```

### 4. Test Installation

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from wheel
pip install dist/auto_blogger-1.0.0-py3-none-any.whl

# Test import
python -c "import auto_blogger; print(auto_blogger.__version__)"

# Test CLI
autoblog --help
auto-blogger --help

# Cleanup
deactivate
rm -rf test_env
```

### 5. Upload

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## 📦 Package Features

### Console Scripts

After installation, users can run:

```bash
# Primary command
autoblog

# Alternative command
auto-blogger
```

### Python Import

```python
# Import main components
from auto_blogger import BlogAutomationGUI, BlogAutomationEngine, main

# Run GUI
main()

# Or create GUI instance
import tkinter as tk
root = tk.Tk()
app = BlogAutomationGUI(root)
root.mainloop()
```

### Package Data

The package includes:
- Configuration files (`configs/*.json`)
- Documentation (`docs/**/*`)
- Website assets (`website/**/*`)
- Scripts (`scripts/**/*`)
- Icons and images (`*.png`, `*.ico`, `*.svg`)

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   ```

2. **Missing Files in Package**:
   - Check `MANIFEST.in` includes all necessary files
   - Verify `package_data` in `setup.py` and `pyproject.toml`

3. **Build Errors**:
   ```bash
   # Update build tools
   pip install --upgrade setuptools wheel build
   ```

4. **Upload Errors**:
   - Verify API tokens in `~/.pypirc`
   - Check package name availability on PyPI
   - Ensure version number is incremented

### Version Management

To release a new version:

1. Update version in:
   - `auto_blogger/__init__.py`
   - `setup.py`
   - `pyproject.toml`

2. Update changelog/release notes
3. Build and upload new version

## 📝 User Installation

Once published, users can install with:

```bash
# Install latest version
pip install auto-blogger

# Install with development dependencies
pip install auto-blogger[dev]

# Install specific version
pip install auto-blogger==1.0.0

# Upgrade to latest
pip install --upgrade auto-blogger
```

## 🎯 Usage After Installation

```bash
# Launch GUI application
autoblog

# Or use alternative command
auto-blogger

# Python usage
python -c "from auto_blogger import main; main()"
```

## 📊 Package Statistics

After publishing, monitor your package:

- **PyPI Page**: `https://pypi.org/project/auto-blogger/`
- **Download Stats**: Available on PyPI project page
- **Dependencies**: Automatically managed by pip

## 🔄 Continuous Integration

For automated publishing, you can integrate with GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## ✅ Final Checklist

Before publishing:

- [ ] Package builds without errors
- [ ] All tests pass
- [ ] Documentation is complete
- [ ] Version number is updated
- [ ] License is included
- [ ] README is comprehensive
- [ ] Dependencies are correctly specified
- [ ] Console scripts work
- [ ] Package installs and imports correctly
- [ ] Tested on Test PyPI first

---

**Copyright © 2025 AryanVBW**  
**GitHub**: [https://github.com/AryanVBW/AUTO-blogger](https://github.com/AryanVBW/AUTO-blogger)