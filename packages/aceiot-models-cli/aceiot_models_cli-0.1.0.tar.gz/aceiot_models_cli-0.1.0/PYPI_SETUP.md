# PyPI Publishing Setup Guide

This guide explains how to set up OpenID Connect (OIDC) for publishing `aceiot-models-cli` to PyPI and TestPyPI using GitHub Actions.

## Prerequisites

1. PyPI account: https://pypi.org/account/register/
2. TestPyPI account: https://test.pypi.org/account/register/
3. GitHub repository with admin access

## Setup Steps

### 1. Configure PyPI OIDC Trust

#### For TestPyPI:
1. Log in to https://test.pypi.org/
2. Go to your account settings
3. Navigate to "Publishing" → "Add a new pending publisher"
4. Enter these details:
   - PyPI Project Name: `aceiot-models-cli`
   - Owner: `ACE-IoT-Solutions`
   - Repository name: `aceiot-models-cli`
   - Workflow name: `publish.yml`
   - Environment name: `testpypi`

#### For PyPI:
1. Log in to https://pypi.org/
2. Go to your account settings
3. Navigate to "Publishing" → "Add a new pending publisher"
4. Enter these details:
   - PyPI Project Name: `aceiot-models-cli`
   - Owner: `ACE-IoT-Solutions`
   - Repository name: `aceiot-models-cli`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`

### 2. Configure GitHub Environments

1. Go to GitHub repository settings
2. Navigate to "Environments"
3. Create two environments:
   - `testpypi` - for test releases
   - `pypi` - for production releases
4. Optionally add protection rules (e.g., require reviews for production)

### 3. Test Publishing to TestPyPI

1. Run the workflow manually:
   ```bash
   gh workflow run publish.yml -f publish_to_testpypi=true -f publish_to_pypi=false
   ```

2. Or use GitHub UI:
   - Go to Actions tab
   - Select "Publish to PyPI" workflow
   - Click "Run workflow"
   - Check "Publish to TestPyPI"
   - Uncheck "Publish to PyPI"

3. Verify package at: https://test.pypi.org/project/aceiot-models-cli/

4. Test installation:
   ```bash
   pip install -i https://test.pypi.org/simple/ aceiot-models-cli
   ```

### 4. Publish to Production PyPI

Once tested, you can publish to production PyPI:

1. Create a git tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. The workflow will automatically trigger and publish to PyPI

3. Or manually trigger:
   ```bash
   gh workflow run publish.yml -f publish_to_testpypi=false -f publish_to_pypi=true
   ```

### 5. Verify Installation

After publishing, users can install:
```bash
pip install aceiot-models-cli
```

## Troubleshooting

### OIDC Trust Issues
- Ensure the workflow name matches exactly: `publish.yml`
- Verify the environment names match: `testpypi` and `pypi`
- Check that the repository owner and name are correct

### Build Issues
- Run `uv run python -m build` locally to test the build
- Check `twine check dist/*` for package issues

### Version Conflicts
- Ensure version in `pyproject.toml` is incremented
- Delete old builds: `rm -rf dist/ build/`

## Version Management

1. Update version in `pyproject.toml`
2. Commit changes
3. Create and push tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

## Security Notes

- Never store PyPI tokens in the repository
- OIDC eliminates the need for tokens
- GitHub environments provide additional security controls