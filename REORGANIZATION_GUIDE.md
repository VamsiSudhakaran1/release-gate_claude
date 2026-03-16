# 📋 Repository Reorganization Guide

Follow these steps to reorganize your repository into a clean, professional structure.

---

## Step 1: Create Folder Structure

```powershell
cd C:\Vamsi\release-gate

# Create folders
mkdir docs
mkdir examples
mkdir tests
mkdir .github\workflows
```

---

## Step 2: Move Files to docs/

Files that go to `docs/` folder:

```powershell
# Documentation files
move QUICKSTART.md docs\
move EXTENDED_README.md docs\
move CHANGELOG.md docs\
move CONTRIBUTING.md docs\
move ARCHITECTURE.md docs\
move DEVELOPMENT.md docs\
```

Create `docs/README.md`:

```markdown
# 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start
- **[EXTENDED_README.md](EXTENDED_README.md)** - Comprehensive guide
- **[CHANGELOG.md](CHANGELOG.md)** - Features and roadmap
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - How it works
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup
```

---

## Step 3: Move Files to examples/

Files that go to `examples/` folder:

```powershell
# Example configuration files
move example-config.yaml examples\
move valid_requests.jsonl examples\
move invalid_requests.jsonl examples\
```

Create `examples/README.md`:

```markdown
# 📋 Examples

## Files

- **example-config.yaml** - Sample configuration file
- **valid_requests.jsonl** - Valid request examples
- **invalid_requests.jsonl** - Invalid request examples

## Usage

```bash
# Initialize project
python cli.py init --project my-system

# This creates release-gate.yaml based on the template here

# Customize your configuration
cp examples/example-config.yaml release-gate.yaml
# Edit as needed

# Run the gate
python cli.py run --config release-gate.yaml --format text
```

## Configuration Structure

```yaml
project:
  name: my-system
  version: 1.0.0

checks:
  input_contract:
    enabled: true
    schema:
      type: object
      properties:
        # Your schema here
    samples:
      valid_path: valid_requests.jsonl
      invalid_path: invalid_requests.jsonl

  fallback_declared:
    enabled: true
    kill_switch:
      type: feature_flag
      name: disable_my_system
    fallback:
      mode: static_placeholder
    ownership:
      team: platform-team
      oncall: oncall-platform
    runbook_url: https://wiki.internal/runbooks/my-system
```
```

---

## Step 4: Move Files to tests/

Files that go to `tests/` folder:

```powershell
# Test files
move test_release_gate.py tests\
```

Create `tests/README.md`:

```markdown
# 🧪 Tests

## Running Tests

```bash
python tests/test_release_gate.py
```

## Test Coverage

The test suite includes 10 tests:

### Core Tests (6)
1. Initialization creates files
2. PASS returns exit code 0
3. FAIL returns exit code 1
4. JSON output is valid
5. Custom output file is created
6. Sample validation works

### WARN Tests (4)
7. WARN when invalid samples pass schema
8. WARN returns exit code 10
9. WARN appears in summary counts
10. FAIL takes precedence over WARN

## Expected Output

```
Results: 10 passed, 0 failed
✅ All tests passed! release-gate is working correctly.
```

## Writing New Tests

See `docs/DEVELOPMENT.md` for how to add new tests.
```

---

## Step 5: Create .gitignore

Create `.gitignore` at root:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Test/Coverage
.pytest_cache/
.coverage
htmlcov/

# Generated files
readiness_report.json
release-gate.yaml
valid_requests.jsonl
invalid_requests.jsonl

# Development
*.egg-info/
dist/
build/
.tmp/
```

---

## Step 6: Delete Old Reference Files

These files were for guidance during development - delete them:

```powershell
# Delete reference files
del FINAL_COMPLETE_SUMMARY.md
del FINAL_SUMMARY.md
del ACTION_CHECKLIST.md
del FINAL_COPY_LIST.md
del COMPLETE_FILE_LIST.md
del COMPLETE.md
del VERIFICATION_REPORT.md
del PM_RESPONSE.md
del WARN_TEST_SCENARIOS.md
del TEST_FIXES.md
del REPO_STRUCTURE.md
del test_cli.py
```

Keep only:
- `cli.py`
- `README.md`
- `requirements.txt`
- `LICENSE`
- `.gitignore`

---

## Step 7: Update Links in Documentation

### In README.md
Replace:
```markdown
[QUICKSTART.md](QUICKSTART.md)
[CHANGELOG.md](CHANGELOG.md)
```

With:
```markdown
[Quick Start](docs/QUICKSTART.md)
[Changelog](docs/CHANGELOG.md)
```

### In docs/README.md (new file)
Links to other docs:
```markdown
- [Quick Start](QUICKSTART.md)
- [Comprehensive Guide](EXTENDED_README.md)
- [API Reference](API.md)
```

---

## Step 8: Create GitHub Actions Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.7', '3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python tests/test_release_gate.py
```

---

## Step 9: Test Everything

```powershell
# Verify structure
dir /s

# Should show:
# .github\workflows\tests.yml
# docs\README.md
# docs\QUICKSTART.md
# docs\EXTENDED_README.md
# docs\CHANGELOG.md
# docs\CONTRIBUTING.md
# docs\ARCHITECTURE.md
# docs\DEVELOPMENT.md
# examples\README.md
# examples\example-config.yaml
# examples\valid_requests.jsonl
# examples\invalid_requests.jsonl
# tests\README.md
# tests\test_release_gate.py
# .gitignore
# cli.py
# README.md
# requirements.txt
# LICENSE

# Test that code still works
python cli.py init --project test
python cli.py run --config release-gate.yaml --format text

# Run tests
python tests/test_release_gate.py
```

---

## Step 10: Commit and Push

```powershell
cd C:\Vamsi\release-gate

git add .

git commit -m "refactor: Reorganize repository structure

- Move docs to docs/ folder
- Move examples to examples/ folder
- Move tests to tests/ folder
- Add .github/workflows for CI/CD
- Create folder README files
- Add ARCHITECTURE.md
- Add DEVELOPMENT.md
- Delete reference/guide files

Repository structure:
- docs/ - All documentation
- examples/ - Configuration examples
- tests/ - Test suite
- .github/ - GitHub workflows
- cli.py - Main application

Much cleaner and more professional!"

git push origin main
```

---

## Final Structure

After reorganization:

```
release-gate/
├── README.md                    Main entry point
├── LICENSE                      MIT License
├── .gitignore                   Git ignore rules
├── requirements.txt             Dependencies
├── cli.py                       Main application
│
├── docs/                        📖 Documentation
│   ├── README.md                Docs index
│   ├── QUICKSTART.md
│   ├── EXTENDED_README.md
│   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md
│   ├── ARCHITECTURE.md
│   └── DEVELOPMENT.md
│
├── examples/                    📋 Examples
│   ├── README.md
│   ├── example-config.yaml
│   ├── valid_requests.jsonl
│   └── invalid_requests.jsonl
│
├── tests/                       🧪 Tests
│   ├── README.md
│   └── test_release_gate.py
│
└── .github/                     🔧 GitHub
    └── workflows/
        └── tests.yml
```

---

## GitHub will Show

**Before:** Cluttered with 16+ files at root
**After:** Clean, organized, professional

```
release-gate
  📄 README.md
  📄 LICENSE
  📄 .gitignore
  📄 requirements.txt
  📄 cli.py
  📁 docs/
  📁 examples/
  📁 tests/
  📁 .github/
```

Much better! ✨

---

## Benefits

✅ Professional appearance
✅ Easy to navigate
✅ Clear organization
✅ GitHub-friendly
✅ Scalable structure
✅ Prepared for growth

---

## Next Steps

1. Follow all 10 steps above
2. Test everything works
3. Commit and push
4. View on GitHub
5. Celebrate! 🎉

