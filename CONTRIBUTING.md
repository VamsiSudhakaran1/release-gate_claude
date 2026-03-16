# Contributing to release-gate

Thanks for your interest in contributing to release-gate! We welcome contributions of all kinds.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Questions?](#questions)

---

## Code of Conduct

Please be respectful and inclusive. We're building a community around safe AI deployment.

**Principles:**
- Be respectful of different viewpoints
- Welcome feedback and criticism
- Focus on the problem, not the person
- Include diverse perspectives

---

## How to Contribute

### Report Bugs

Found a bug? Open an issue with:
1. Clear title
2. Steps to reproduce
3. Expected vs actual behavior
4. Your environment (Python version, OS, etc.)

**Example:**
```
Title: INPUT_CONTRACT fails with empty schema

Steps:
1. Create config with empty schema: {}
2. Run: python cli.py run --config release-gate.yaml
3. Expected: Error message about missing schema
4. Actual: Crashes with AttributeError
```

### Suggest Features

Have an idea? Open an issue with:
1. Use case
2. Why it matters
3. How it might work

**Example:**
```
Title: Add ACTION_BUDGET_DECLARED check

Use case: Prevent resource exhaustion attacks
Relevance: Prevents Agents of Chaos cases #4, #5
Implementation: Validate max_tokens, max_retries, timeout_seconds
```

### Submit Code

See [Making Changes](#making-changes) below.

### Improve Documentation

Documentation improvements are always welcome:
- Fix typos
- Clarify examples
- Add use cases
- Update guides

---

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/release_gate.git
cd release_gate
git remote add upstream https://github.com/VamsiSudhakaran1/release_gate.git
```

### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation
- `refactor/` for refactoring

### 3. Install Dependencies

```bash
pip install pyyaml jsonschema
```

### 4. Make Your Changes

See [Making Changes](#making-changes) below.

---

## Making Changes

### Code Structure

```
release_gate/
├── cli.py              # Main CLI tool
├── requirements.txt    # Dependencies
├── tests/              # Test suite (coming)
└── docs/               # Documentation
```

### What to Change

**Good first issues:**
- [ ] Add test for exit codes
- [ ] Add test for INPUT_CONTRACT logic
- [ ] Add test for FALLBACK_DECLARED logic
- [ ] Improve error messages
- [ ] Add example configurations
- [ ] Fix documentation typos
- [ ] Add docstrings to functions

**Medium complexity:**
- [ ] Implement ACTION_BUDGET_DECLARED check
- [ ] Improve JSON report format
- [ ] Add custom check support
- [ ] Add language wrapper (Go, Rust, etc.)

**Complex features:**
- [ ] Runtime agent testing (v0.2)
- [ ] Formal verification layer (v0.3)
- [ ] Web dashboard (v1.0)

### Example: Adding a Check

To add a new check like `ACTION_BUDGET_DECLARED`:

1. **Create the check function** in `cli.py`:

```python
def _check_action_budget_declared(config):
    """
    Validate ACTION_BUDGET_DECLARED check.
    
    Tests:
    1. max_retries is defined
    2. max_tokens_per_call is defined
    3. timeout_seconds is defined
    """
    budget_check = config.get("checks", {}).get("action_budget_declared", {})
    
    if not budget_check.get("enabled", True):
        return {
            "name": "action_budget_declared",
            "result": "PASS",
            "evidence": {"status": "check disabled"}
        }
    
    missing = []
    if not budget_check.get("max_retries"):
        missing.append("max_retries")
    if not budget_check.get("max_tokens_per_call"):
        missing.append("max_tokens_per_call")
    if not budget_check.get("timeout_seconds"):
        missing.append("timeout_seconds")
    
    evidence = {
        "max_retries_defined": budget_check.get("max_retries") is not None,
        "max_tokens_defined": budget_check.get("max_tokens_per_call") is not None,
        "timeout_defined": budget_check.get("timeout_seconds") is not None,
    }
    
    if missing:
        return {
            "name": "action_budget_declared",
            "result": "FAIL",
            "evidence": {**evidence, "missing_fields": missing},
            "suggestion": f"Define: {', '.join(missing)}"
        }
    else:
        return {
            "name": "action_budget_declared",
            "result": "PASS",
            "evidence": evidence
        }
```

2. **Add to run_gate()** in `cli.py`:

```python
# In the run_gate() function, add:
budget_check_result = _check_action_budget_declared(config)
results["checks"].append(budget_check_result)
if budget_check_result["result"] == "FAIL":
    results["overall"] = "FAIL"
results["summary"]["counts"][budget_check_result["result"].lower()] += 1
```

3. **Test it** (see Testing section below)

4. **Update documentation**:
   - Update README.md to mention the new check
   - Add example config
   - Update roadmap if needed

---

## Testing

### Manual Testing

```bash
# Test initialization
python cli.py init --project test

# Test with valid config
python cli.py run --config release-gate.yaml --format text

# Test with JSON output
python cli.py run --config release-gate.yaml --format json

# Test exit codes
python cli.py run --config release-gate.yaml
echo $?  # Should be 0, 1, or 10
```

### Automated Tests (Coming v0.2)

When we add test suite:

```bash
python -m pytest tests/
```

---

## Submitting Changes

### 1. Commit

```bash
# Make meaningful commits
git commit -m "Add: ACTION_BUDGET_DECLARED check

- Validates max_retries, max_tokens_per_call, timeout_seconds
- Returns FAIL if any missing
- Provides helpful suggestions"
```

**Commit message format:**
```
Type: Short description (50 chars)

Longer description (wrap at 72 chars):
- What changed
- Why it changed
- Any side effects

Fixes #123
```

**Types:**
- `Add:` - New feature
- `Fix:` - Bug fix
- `Docs:` - Documentation
- `Refactor:` - Code reorganization
- `Test:` - Test improvements

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

On GitHub:
1. Click "New Pull Request"
2. Select your branch
3. Fill in title and description
4. Submit!

**PR Template:**
```markdown
## What does this PR do?
Brief description

## Why?
Motivation and context

## How was this tested?
Steps to verify

## Checklist
- [ ] Code follows style guide
- [ ] Added/updated documentation
- [ ] Added tests (if applicable)
- [ ] Verified exit codes work
```

---

## Code Style

### Python Style

- **PEP 8** - Follow Python style guide
- **Line length** - 88 characters max
- **Naming** - snake_case for functions, CamelCase for classes
- **Docstrings** - Include for all functions

**Example:**

```python
def _check_input_contract(config, config_dir, jsonschema):
    """
    Validate INPUT_CONTRACT check.
    
    Loads valid and invalid samples, tests them against schema.
    Returns PASS if all tests pass, FAIL or WARN otherwise.
    
    Args:
        config: Loaded YAML configuration dict
        config_dir: Directory containing config file
        jsonschema: jsonschema module for validation
        
    Returns:
        Dict with check result and evidence
    """
    # Implementation...
    pass
```

### Documentation Style

- **Markdown** - Use markdown for documentation
- **Headers** - Use `#` for h1, `##` for h2, etc.
- **Code blocks** - Use triple backticks with language
- **Examples** - Include real examples

---

## Questions?

- 📖 Read the [README.md](README.md)
- 📚 Read the [EXTENDED_README.md](EXTENDED_README.md)
- 💬 Open a discussion on GitHub
- 📝 Open an issue

---

## Roadmap

See [CHANGELOG.md](CHANGELOG.md) for the roadmap.

### v0.2 (Next)
- [ ] BUDGET_GUARDRAILS check
- [ ] LATENCY_GATE check
- [ ] Test suite
- [ ] Golden regression testing

### v0.3 (Future)
- [ ] Formal verification
- [ ] Neuro-symbolic layer
- [ ] Runtime monitoring

### v1.0 (Later)
- [ ] Web dashboard
- [ ] Enterprise features
- [ ] Multi-agent orchestration

---

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- GitHub contributors page
- Release notes

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to release-gate!** 🙌

Together we're making autonomous agents safer.
