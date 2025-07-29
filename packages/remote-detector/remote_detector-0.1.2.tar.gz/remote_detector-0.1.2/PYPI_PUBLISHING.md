# Publishing to PyPI

This document provides step-by-step instructions for publishing the remote-detector package to PyPI.

## Prerequisites

1. Create accounts on PyPI and TestPyPI:
   - PyPI: https://pypi.org/account/register/
   - TestPyPI: https://test.pypi.org/account/register/

2. Generate API tokens for each site:
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

3. Install required packages:
   ```bash
   pip install build twine
   ```

## Configuration

1. Create a `.pypirc` file in your home directory:
   ```bash
   cp .pypirc ~/.pypirc
   ```

2. Edit the file with your tokens:
   ```bash
   nano ~/.pypirc
   ```
   Replace `your_pypi_token` and `your_testpypi_token` with your actual tokens.

## Building the Package

1. Clean previous builds:
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

2. Build the package:
   ```bash
   python -m build
   ```
   This will create both source distribution (.tar.gz) and wheel (.whl) files in the dist/ directory.

## Publishing to TestPyPI (Recommended First Step)

1. Upload to TestPyPI to verify everything works:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. Test installation from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --no-deps remote-detector
   ```

3. Verify that the package works correctly:
   ```bash
   remote-detector --help
   ```

## Publishing to PyPI

Once you're confident the package works correctly:

1. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

2. Test installation from PyPI:
   ```bash
   pip install remote-detector
   ```

## Updating the Package

When you need to update the package:

1. Increment the version number in `setup.py`
2. Clean previous builds
3. Build and upload following the steps above

## Troubleshooting

- If you encounter errors during upload, check that your token is correct and has not expired.
- If the package doesn't behave as expected, check the distribution build to ensure all necessary files are included.
- For installation issues, verify dependencies are correctly specified in `setup.py`.

## Additional Resources

- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [PyPI Publishing Documentation](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/) 