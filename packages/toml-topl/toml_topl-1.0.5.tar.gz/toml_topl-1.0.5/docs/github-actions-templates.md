# GitHub Actions Workflow Templates

Due to GitHub App permission restrictions, the workflow files must be created manually. Here are the recommended templates:

## CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: uv sync --all-extras
    
    - name: Run linting
      run: |
        uv run ruff check .
        uv run ruff format --check .
    
    - name: Run type checking
      run: uv run mypy src tests
    
    - name: Run tests
      run: uv run pytest --cov=topl --cov-report=xml --cov-report=term-missing
    
    - name: Run security scan
      run: uv run bandit -r src/
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

## Release Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: read
  id-token: write  # For trusted publishing to PyPI

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Fetch full history for proper versioning
    
    - name: Install uv
      uses: astral-sh/setup-uv@v4
    
    - name: Set up Python
      run: uv python install 3.11
    
    - name: Install dependencies
      run: uv sync --dev
    
    - name: Run tests
      run: uv run pytest
    
    - name: Build package
      run: uv build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        packages-dir: dist/

  github-release:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/
    
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v2
      with:
        files: dist/*
        generate_release_notes: true
        draft: false
        prerelease: false
```

## Setup Instructions

1. Create the `.github/workflows/` directory in your repository
2. Copy the above templates into the respective files
3. Commit and push the workflow files
4. Configure any required secrets (for PyPI publishing, etc.)
5. Set up branch protection rules as needed

## Additional Recommendations

- Configure Dependabot for automated dependency updates
- Set up CodeCov for test coverage reporting
- Configure branch protection rules for the main branch
- Enable GitHub's security features (vulnerability alerts, etc.)