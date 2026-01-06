# CI/CD Setup Guide

This document describes the automated CI/CD pipeline for the CalcsLive Plug for Inventor project.

## Overview

The CI/CD pipeline automatically:
- ✅ Runs tests on every push
- ✅ Bumps version based on commit messages or manual trigger
- ✅ Creates Git tags
- ✅ Generates GitHub releases with changelog

## Quick Start

### Automatic Versioning (Recommended)

The pipeline automatically determines version bump type from your commit messages:

```bash
# Patch bump (1.1.1 -> 1.1.2)
git commit -m "fix: resolve parameter mapping bug"

# Minor bump (1.1.1 -> 1.2.0)
git commit -m "feat: add new API endpoint for batch updates"

# Major bump (1.1.1 -> 2.0.0)
git commit -m "breaking: redesign comment field syntax"

# Push to trigger CI/CD
git push origin main
```

**Commit Message Prefixes:**
- `fix:`, `patch:` → Patch version bump
- `feat:`, `feature:`, `minor:` → Minor version bump
- `breaking:`, `major:` → Major version bump

### Manual Version Bump

You can also trigger version bumps manually via GitHub Actions:

1. Go to **Actions** tab in GitHub
2. Select **Release and Version Management** workflow
3. Click **Run workflow**
4. Choose bump type: `patch`, `minor`, or `major`
5. Click **Run workflow**

### Local Version Bump (Without CI/CD)

For local development or testing:

```bash
# Install toml library
pip install toml

# Bump version locally
python scripts/bump_version.py patch   # 1.1.1 -> 1.1.2
python scripts/bump_version.py minor   # 1.1.1 -> 1.2.0
python scripts/bump_version.py major   # 1.1.1 -> 2.0.0

# Commit and push
git add .
git commit -m "chore: bump version to X.Y.Z"
git push origin main
```

## Architecture

### Version Management

**Single Source of Truth:** [`pyproject.toml`](pyproject.toml)

```toml
[project]
version = "1.1.1"
```

**Version Reading:** [main.py:12-19](main.py#L12-L19)

```python
def get_version():
    try:
        import toml
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
            return data["project"]["version"]
    except:
        return "1.1.1"  # Fallback version
```

**Version Bump Script:** [`scripts/bump_version.py`](scripts/bump_version.py)

Semantic versioning utility:
- Reads current version from `pyproject.toml`
- Increments based on bump type
- Updates `pyproject.toml` in-place

### GitHub Actions Workflow

**Workflow File:** [`.github/workflows/release.yml`](.github/workflows/release.yml)

**Triggers:**
- Push to `main` branch (excluding documentation changes)
- Manual workflow dispatch with version bump selection

**Jobs:**

#### 1. Test Job
- Runs on `windows-latest` (required for `pywin32`)
- Installs dependencies
- Executes `pytest test_comment_parser.py -v`

#### 2. Version and Release Job
- Runs on `ubuntu-latest` after tests pass
- Auto-detects bump type from commit messages (or uses manual input)
- Bumps version using `scripts/bump_version.py`
- Commits updated `pyproject.toml`
- Creates Git tag (e.g., `v1.2.0`)
- Generates release notes from commit history
- Creates GitHub Release

## Workflow Details

### Automatic Bump Type Detection

The workflow analyzes the last 10 commit messages:

```yaml
if echo "$COMMITS" | grep -qiE "^(breaking|major):"; then
  # Major bump
elif echo "$COMMITS" | grep -qiE "^(feat|feature|minor):"; then
  # Minor bump
else
  # Patch bump (default)
fi
```

### Release Notes Generation

Automatically generates changelog comparing:
- **First release:** Last 20 commits
- **Subsequent releases:** All commits since previous tag

Format:
```markdown
## What's Changed

- feat: add batch parameter update endpoint (abc1234)
- fix: resolve COM exception in text parameter creation (def5678)

**Full Changelog**: https://github.com/CalcsLive/calcslive-plug-4-inventor/compare/v1.1.0...v1.2.0
```

## Dependencies

### Runtime
- `fastapi>=0.100.0`
- `uvicorn[standard]>=0.22.0`
- `pywin32>=306`
- `toml>=0.10.2` ← **Required for version reading**

### Development
- `pytest>=7.0.0`
- `toml>=0.10.2`

## File Structure

```
calcslive-plug-4-inventor/
├── .github/
│   └── workflows/
│       └── release.yml          # GitHub Actions workflow
├── scripts/
│   └── bump_version.py          # Version bump utility
├── pyproject.toml               # Version source of truth
├── main.py                      # Reads version from pyproject.toml
├── requirements.txt             # Includes toml library
└── CI_CD_SETUP.md              # This file
```

## Usage Examples

### Example 1: Bug Fix Release

```bash
# Make changes
git add .
git commit -m "fix: correct unit conversion for density parameters"
git push origin main

# CI/CD automatically:
# 1. Runs tests
# 2. Detects "fix:" prefix → patch bump
# 3. Updates version: 1.1.1 -> 1.1.2
# 4. Creates tag: v1.1.2
# 5. Creates GitHub release
```

### Example 2: New Feature Release

```bash
git commit -m "feat: add support for multi-article namespace (CA1, CA2)"
git push origin main

# CI/CD automatically:
# 1.1.2 -> 1.2.0 (minor bump)
# Tag: v1.2.0
```

### Example 3: Breaking Change Release

```bash
git commit -m "breaking: change comment field syntax to support nested symbols"
git push origin main

# CI/CD automatically:
# 1.2.0 -> 2.0.0 (major bump)
# Tag: v2.0.0
```

### Example 4: Manual Trigger

1. Go to GitHub Actions
2. Select **Release and Version Management**
3. Click **Run workflow**
4. Choose `minor` (1.2.0 -> 1.3.0)
5. Click **Run workflow**

## Troubleshooting

### Tests Failing on Push

**Issue:** CI/CD blocked because tests failed

**Solution:**
```bash
# Run tests locally before pushing
pytest test_comment_parser.py -v

# Fix issues, then push
git push origin main
```

### Version Not Updated in main.py

**Issue:** API still returns old version after release

**Solution:**
- Ensure `toml` is installed: `pip install toml`
- Restart FastAPI server to reload version
- Check `pyproject.toml` was updated correctly

### Release Not Created

**Issue:** Tag created but no GitHub release

**Check:**
1. GitHub Actions permissions (Settings → Actions → General → Workflow permissions → Read and write)
2. Workflow logs for errors in "Create GitHub Release" step

### Manual Version Bump Conflicts

**Issue:** Local bump conflicts with CI/CD bump

**Solution:**
```bash
# Always pull before manual bumps
git pull origin main

# Then bump and push
python scripts/bump_version.py patch
git add .
git commit -m "chore: bump version to X.Y.Z"
git push origin main
```

## Best Practices

1. **Use Conventional Commits:** Prefix commits with `fix:`, `feat:`, or `breaking:` for automatic versioning
2. **Test Before Pushing:** Run `pytest` locally to avoid CI/CD failures
3. **Pull Before Bumping:** Always `git pull` before manual version bumps
4. **Review Release Notes:** Check GitHub releases after each deployment
5. **Document Breaking Changes:** Add migration notes to release descriptions for major versions

## Disabling CI/CD

To temporarily disable automatic versioning:

1. **For specific push:**
   ```bash
   git commit -m "docs: update README [skip ci]"
   ```

2. **For all pushes:**
   - Go to GitHub → Settings → Actions → Disable workflows
   - Or delete `.github/workflows/release.yml`

## Future Enhancements

Potential improvements:
- [ ] Add Docker image building and publishing
- [ ] Deploy to PyPI for `pip install calcslive-plug-inventor`
- [ ] Add code coverage reporting
- [ ] Automatic CHANGELOG.md generation
- [ ] Slack/Discord notifications for releases
- [ ] Pre-release tags for beta versions

---

**Last Updated:** 2026-01-06
**Current Version:** 1.1.1
**Pipeline Status:** ✅ Active