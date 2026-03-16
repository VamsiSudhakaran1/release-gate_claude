# 🧪 Tests

This folder contains the automated test suite for release-gate.

---

## Running Tests

### Basic Test Run

```bash
cd C:\Vamsi\release-gate

python tests/test_release_gate.py
```

### Expected Output

```
======================================================================
  release-gate Automated Smoke Test Suite
======================================================================

✓ Test 1: Initialization - PASSED
✓ Test 2: PASS case (exit 0) - PASSED
✓ Test 3: FAIL case (exit 1) - PASSED
✓ Test 4: JSON output - PASSED
✓ Test 5: Custom output file - PASSED
✓ Test 6: Sample validation - PASSED
✓ Test 7: WARN case (invalid samples accepted) - PASSED
✓ Test 8: WARN exit code (10) - PASSED
✓ Test 9: WARN in summary counts - PASSED
✓ Test 10: FAIL precedence over WARN - PASSED

======================================================================
Results: 10 passed, 0 failed
======================================================================

✅ All tests passed! release-gate is working correctly.
```

---

## Test Files

### test_release_gate.py

The main test suite with 10 comprehensive tests.

**Tests included:**

#### Core Tests (6)

1. **Initialization**
   - Creates release-gate.yaml
   - Creates valid_requests.jsonl
   - Creates invalid_requests.jsonl

2. **PASS Case**
   - Valid config returns exit code 0
   - Report shows PASS status

3. **FAIL Case**
   - Invalid config returns exit code 1
   - Report shows FAIL status

4. **JSON Output**
   - JSON output is valid and parseable
   - Contains required fields (overall, checks, timestamp)

5. **Custom Output File**
   - `--output` flag works correctly
   - Creates file at specified path
   - File contains valid JSON

6. **Sample Validation**
   - INPUT_CONTRACT loads valid samples
   - INPUT_CONTRACT loads invalid samples
   - Evidence includes sample counts

#### WARN Tests (4)

7. **WARN on Invalid Samples**
   - When invalid samples incorrectly pass schema
   - Overall result is WARN
   - Evidence shows invalid_samples_accepted > 0

8. **WARN Exit Code**
   - WARN returns exit code 10 (not 0 or 1)
   - Correct for CI/CD integration

9. **WARN in Summary**
   - WARN count appears in summary
   - summary["counts"]["warn"] > 0

10. **FAIL Precedence**
    - If one check fails and one warns, overall is FAIL
    - FAIL always takes precedence over WARN

---

## Test Coverage

| Component | Tested | How |
|-----------|--------|-----|
| Initialization | ✅ | Test 1 |
| Run command | ✅ | Tests 2-6 |
| PASS case | ✅ | Test 2 |
| FAIL case | ✅ | Test 3 |
| WARN case | ✅ | Tests 7-10 |
| JSON output | ✅ | Test 4 |
| Custom output | ✅ | Test 5 |
| Sample validation | ✅ | Test 6 |
| Exit codes | ✅ | Tests 2, 3, 8 |
| Result aggregation | ✅ | Test 10 |

---

## How Tests Work

### Test Structure

Each test follows this pattern:

```python
def test_something():
    """Test description"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Copy cli.py to temp directory
        import shutil as sh
        sh.copy("cli.py", tmpdir / "cli.py")
        
        # Run CLI command
        code, stdout, stderr = run_cli("init", "--project", "test", cwd=tmpdir)
        
        # Assert expectations
        assert code == 0
        assert (tmpdir / "release-gate.yaml").exists()
```

### Why Temporary Directories?

Each test uses a fresh temporary directory to:
- Isolate tests from each other
- Prevent file conflicts
- Clean up automatically after test
- Test in a clean environment

---

## Writing New Tests

### Add a New Test

Edit `tests/test_release_gate.py`:

```python
def test_my_new_feature():
    """Test description"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        import shutil as sh
        sh.copy("cli.py", tmpdir / "cli.py")
        
        # Run CLI command
        code, stdout, stderr = run_cli("init", "--project", "test", cwd=tmpdir)
        
        # Assert expectations
        assert code == 0, f"Expected success, got {code}"
        
        print("✓ Test: My new feature - PASSED")
```

### Register the Test

Add to the `tests` list in `main()`:

```python
tests = [
    ("Initialization", test_init),
    ("PASS case", test_pass_case),
    # ... other tests ...
    ("My new feature", test_my_new_feature),  # ← Add here
]
```

---

## Troubleshooting Tests

### Tests Fail with "cli.py not found"

Make sure you're running from the repo root:

```bash
cd C:\Vamsi\release-gate
python tests/test_release_gate.py
```

### Unicode Character Errors

If you see charset errors, ensure cli.py uses ASCII-safe characters:
- Use `[OK]` instead of `✓`
- Use `[DONE]` instead of `✨`

### Python Version Issues

Tests require Python 3.7+:

```bash
python --version
# Should be 3.7 or higher
```

---

## Manual Testing

If automated tests fail, test manually:

```bash
# 1. Initialize
python cli.py init --project manual-test

# Should create:
# - release-gate.yaml
# - valid_requests.jsonl
# - invalid_requests.jsonl

# 2. Run gate
python cli.py run --config release-gate.yaml --format text

# Should show: ✓ PASS

# 3. Check exit code
echo %ERRORLEVEL%

# Should be: 0
```

---

## Continuous Integration

### GitHub Actions

Tests run automatically on every push:

```yaml
# .github/workflows/tests.yml
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python tests/test_release_gate.py
```

---

## Test Metrics

- **Total tests:** 10
- **Core tests:** 6
- **WARN tests:** 4
- **Typical runtime:** < 10 seconds
- **Coverage:** Main functionality and edge cases

---

## What's Not Tested

- External API calls (none made)
- Network connectivity (not required)
- Database operations (not used)
- Production deployment (out of scope)

Tests focus on local CLI functionality.

---

## Contributing Tests

When adding new features:

1. Write tests for the feature
2. Make sure tests pass
3. Include in pull request
4. Update this README if needed

---

## Resources

- **Python unittest:** https://docs.python.org/3/library/unittest.html
- **pytest:** https://docs.pytest.org/
- **Testing best practices:** See DEVELOPMENT.md

---

**All tests passing = You're good to deploy! ✅**
