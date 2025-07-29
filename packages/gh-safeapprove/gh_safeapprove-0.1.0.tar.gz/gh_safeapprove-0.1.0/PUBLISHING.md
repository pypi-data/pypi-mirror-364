# Publishing Guide for gh-safeapprove

This guide walks you through publishing gh-safeapprove to GitHub and PyPI.

## 📋 Pre-Publishing Checklist

### ✅ Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code is formatted: `black src/ tests/`
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Type checking passes: `mypy src/`

### ✅ Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG.md has latest changes
- [ ] CONTRIBUTING.md is complete
- [ ] All docstrings are complete

### ✅ Configuration
- [ ] Version is correct in `pyproject.toml`
- [ ] Author information is correct
- [ ] Dependencies are properly specified
- [ ] GitHub Actions workflows are in place

## 🚀 Publishing Steps

### Step 1: GitHub Repository

1. **Create GitHub repository** (if not exists):
   ```bash
   gh repo create gh-safeapprove --public --description "A GitHub CLI-compatible Python tool to safely auto-approve pull requests"
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial release v0.1.0"
   git push origin main
   ```

3. **Add PyPI API token to GitHub secrets**:
   - Go to https://pypi.org/manage/account/token/
   - Create API token
   - Add to GitHub repository secrets as `PYPI_API_TOKEN`

### Step 2: Test Build

1. **Run the publish script**:
   ```bash
   ./scripts/publish.sh
   ```

2. **Test upload to TestPyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

3. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ gh-safeapprove
   ```

### Step 3: PyPI Release

1. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

2. **Verify installation**:
   ```bash
   pip install gh-safeapprove
   gh-safeapprove --help
   ```

### Step 4: GitHub Release

1. **Create GitHub release**:
   ```bash
   gh release create v0.1.0 --generate-notes
   ```

2. **Verify GitHub Actions**:
   - Check that CI passes
   - Verify release workflow runs

## 🔄 Future Releases

For future releases:

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new changes
3. **Run publish script**: `./scripts/publish.sh`
4. **Upload to PyPI**: `twine upload dist/*`
5. **Create GitHub release**: `gh release create v0.2.0 --generate-notes`

## 🛠️ Troubleshooting

### Common Issues

1. **"Name already exists on PyPI"**
   - Check if package name is available: https://pypi.org/project/gh-safeapprove/

2. **Authentication errors**
   - Verify PyPI API token is correct
   - Check GitHub secrets are set

3. **Build errors**
   - Ensure all dependencies are in `pyproject.toml`
   - Check Python version compatibility

### Getting Help

- Check PyPI documentation: https://packaging.python.org/
- GitHub Actions docs: https://docs.github.com/en/actions
- PyPI upload guide: https://packaging.python.org/tutorials/packaging-projects/ 