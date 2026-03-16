# 🏗️ Release-Gate Architecture

## Overview

release-gate is a **pre-deployment governance gate** for AI agents. It validates request contracts and enforces operational readiness before deployment.

```
┌─────────────────────────────────────┐
│  Developer/CI/CD Pipeline           │
└────────────┬────────────────────────┘
             │
             │ python cli.py run
             │ --config release-gate.yaml
             ↓
┌─────────────────────────────────────┐
│     release-gate CLI                │
│  ┌──────────────────────────────────┤
│  │ 1. Load YAML config              │
│  │ 2. Parse schema                  │
│  │ 3. Run checks                    │
│  │ 4. Generate report               │
│  └──────────────────────────────────┤
└────────┬────────────────────────────┘
         │
         ├─→ INPUT_CONTRACT Check
         │   ├─ Load valid_requests.jsonl
         │   ├─ Load invalid_requests.jsonl
         │   ├─ Test schema syntax
         │   ├─ Test valid samples pass
         │   └─ Test invalid samples fail
         │
         └─→ FALLBACK_DECLARED Check
             ├─ Check kill_switch
             ├─ Check fallback mode
             ├─ Check ownership
             └─ Check runbook URL
             
         ↓
┌─────────────────────────────────────┐
│    Report Generation                │
│  ├─ JSON format (machine readable)  │
│  ├─ Text format (human readable)    │
│  └─ Exit codes (0, 10, 1)           │
└────────┬────────────────────────────┘
         │
         ├─→ JSON Report
         │   └─ readiness_report.json
         │
         ├─→ Text Output
         │   └─ Console display
         │
         └─→ Exit Code
             ├─ 0 = PASS (deploy)
             ├─ 10 = WARN (review)
             └─ 1 = FAIL (block)
```

---

## Code Structure

### cli.py (Main File)

```python
# Core Functions

def init_project(project_name)
  Create: release-gate.yaml, valid_requests.jsonl, invalid_requests.jsonl

def run_gate(config_path, env, output_format, output_file)
  Main function that orchestrates all checks
  Returns: exit code (0, 10, or 1)

def _check_input_contract(config, config_dir, jsonschema)
  Validates INPUT_CONTRACT check
  Tests valid and invalid samples
  Returns: {"result": "PASS|WARN|FAIL", "evidence": {...}}

def _check_fallback_declared(config)
  Validates FALLBACK_DECLARED check
  Checks all required fields
  Returns: {"result": "PASS|WARN|FAIL", "evidence": {...}}

def _load_jsonl_file(file_path)
  Helper: Load JSONL file line by line
  Returns: List of parsed JSON objects

def _display_text_report(results)
  Helper: Format and print text output
```

---

## Data Flow

### 1. Initialization
```
User: python cli.py init --project my-system
       ↓
create release-gate.yaml (template)
create valid_requests.jsonl (samples)
create invalid_requests.jsonl (samples)
```

### 2. Configuration
```
release-gate.yaml structure:

project:
  name: my-system
  version: 1.0.0

checks:
  input_contract:
    enabled: true
    schema: {...}
    samples:
      valid_path: valid_requests.jsonl
      invalid_path: invalid_requests.jsonl

  fallback_declared:
    enabled: true
    kill_switch: {...}
    fallback: {...}
    ownership: {...}
    runbook_url: {...}
```

### 3. Validation
```
Load config
  ↓
Validate INPUT_CONTRACT
  ├─ Load schema
  ├─ Load valid samples
  ├─ Load invalid samples
  ├─ Test valid samples pass
  └─ Test invalid samples fail
  ↓
Validate FALLBACK_DECLARED
  ├─ Check kill_switch
  ├─ Check fallback
  ├─ Check ownership
  └─ Check runbook
  ↓
Aggregate results
  ├─ FAIL if any check fails
  ├─ WARN if any check warns
  └─ PASS if all pass
```

### 4. Reporting
```
Generate report:
  ├─ timestamp
  ├─ environment (staging/prod)
  ├─ project info
  ├─ summary counts
  └─ checks details
        └─ name, result, evidence

Output:
  ├─ JSON: machine readable
  ├─ Text: human readable
  └─ File: custom location
```

---

## Check Details

### INPUT_CONTRACT

**Purpose:** Validate request schema and test samples

**Logic:**
1. Load schema from config
2. Validate schema syntax (JSON Schema)
3. Load valid_requests.jsonl
4. Load invalid_requests.jsonl
5. Test each valid sample against schema
   - Must pass ✅
   - If fails → FAIL
6. Test each invalid sample against schema
   - Must fail ✅
   - If passes → WARN

**Evidence:**
```json
{
  "schema_valid": true,
  "valid_samples_tested": 3,
  "valid_samples_passed": 3,
  "valid_samples_failed": 0,
  "invalid_samples_tested": 3,
  "invalid_samples_rejected": 3,
  "invalid_samples_accepted": 0
}
```

### FALLBACK_DECLARED

**Purpose:** Ensure operational safeguards are declared

**Checks:**
1. kill_switch exists and has type + name
2. fallback exists and has mode
3. ownership exists and has team + oncall
4. runbook_url exists and is valid HTTP/HTTPS URL

**Evidence:**
```json
{
  "kill_switch_declared": true,
  "fallback_declared": true,
  "ownership_assigned": true,
  "runbook_provided": true
}
```

---

## Decision Logic

### Result Aggregation

```
Overall = PASS (default)

For each check:
  if result == FAIL:
    Overall = FAIL (and stop checking)
  elif result == WARN and Overall != FAIL:
    Overall = WARN

Precedence: FAIL > WARN > PASS
```

### Exit Codes

```
Overall PASS → exit code 0 (deploy)
Overall WARN → exit code 10 (review needed)
Overall FAIL → exit code 1 (deployment blocked)
```

### CI/CD Integration

```bash
python cli.py run --config release-gate.yaml

if [ $? -eq 0 ]; then
  # PASS: deploy
  deploy_to_production
elif [ $? -eq 10 ]; then
  # WARN: require approval
  send_for_approval
else
  # FAIL: block
  exit 1
fi
```

---

## Dependencies

### Required
- **pyyaml** (>= 6.0) - Parse YAML config
- **jsonschema** (>= 4.0) - Validate JSON Schema

### Optional (for development)
- **pytest** - Run test suite

---

## Error Handling

### Config Errors
- Missing config file → Error message + exit code 1
- Invalid YAML syntax → Error message + exit code 1
- Missing required fields → Check fails

### Sample Errors
- Missing sample file → Error message + exit code 1
- Invalid JSON in samples → Error message + exit code 1
- Schema not found → Check fails

### Graceful Degradation
- Missing sample file → Error (can't validate)
- Invalid schema syntax → Fails (schema required)
- Empty sample files → PASS (no samples to test)

---

## Extensions (Future)

### Phase 2: Runtime Testing
- GOLDEN_REGRESSION check
- ACTION_BUDGET_DECLARED check
- LATENCY_GATE check

### Phase 3: Formal Verification
- Neuro-symbolic verification
- CSL-Core guardrails
- Valori-style state replay

### Phase 4+: Runtime Monitoring
- Continuous governance verification
- Anomaly detection
- Dashboard integration

---

## Design Principles

1. **Configuration-as-Code** - Safety defined in YAML
2. **Local-First** - No backend services
3. **CI/CD Friendly** - Exit codes for pipelines
4. **Evidence-Based** - Detailed reports
5. **Fail-Safe** - Errs on the side of caution
6. **Transparent** - Clear pass/warn/fail decisions

---

## Performance

- **Initialization:** < 100ms
- **Single check:** < 50ms
- **Full gate run:** < 200ms
- **Typical JSON report:** < 5KB

---

## Security Considerations

- No external API calls
- No data transmission
- No credentials stored
- Configuration-only data
- Local file processing only

---

## Testing

See `tests/README.md` for complete test documentation.

Quick test:
```bash
python -m pytest tests/test_release_gate.py -v
```

---

## Support

For questions about architecture:
1. Read `EXTENDED_README.md` for complete guide
2. Check `CONTRIBUTING.md` for development info
3. Review examples in `examples/`
4. Run tests for working examples

