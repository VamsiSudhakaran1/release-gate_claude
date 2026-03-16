# release-gate v0.1.0

**Pre-deployment governance gate for AI agents that validates request contracts and operational readiness.**

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.7+-blue)
![Status](https://img.shields.io/badge/status-v0.1-brightgreen)

---

## What is release-gate?

release-gate prevents autonomous AI agents from being deployed without operational safeguards.

It answers: **Is this agent safe to run unsupervised?**

### The Key Insight

> **Traditional QA tests: "Does it work?"**
>
> **release-gate tests: "Is it safe to run?"**

These are fundamentally different questions that require different tools.

---

## The Problem

Autonomous AI agents fail in production in ways traditional testing can't catch:

- **Non-owner access** (Agents of Chaos #2) - Anyone can execute commands
- **Self-destruction** (Agents of Chaos #1) - Agent deletes its own infrastructure
- **Resource exhaustion** (Agents of Chaos #4, #5) - Infinite loops consume tokens
- **Identity spoofing** (Agents of Chaos #8) - Governance bypassed via usernames
- **Manipulation** (Agents of Chaos #7) - Agents exploited into harmful behavior

These aren't bugs. They're **governance failures**.

**Reference:** [Agents of Chaos: Red-Teaming of Autonomous AI Agents](https://arxiv.org/abs/2602.20021)

---

## What release-gate Does (v0.1)

### ✅ Validates INPUT_CONTRACT

Ensures your agent's request format is well-defined and tested.

**Checks:**
- ✅ Schema is defined and syntactically valid
- ✅ All valid test samples pass the schema
- ✅ All invalid test samples fail the schema

**Example:**
```yaml
input_contract:
  enabled: true
  schema:
    type: object
    required: [prompt, duration_sec]
    properties:
      prompt:
        type: string
        minLength: 1
        maxLength: 1000
      duration_sec:
        type: number
        minimum: 1
        maximum: 60
  samples:
    valid_path: valid_requests.jsonl
    invalid_path: invalid_requests.jsonl
```

### ✅ Validates FALLBACK_DECLARED

Ensures operational safety mechanisms are documented.

**Checks:**
- ✅ Kill switch is declared (how to disable)
- ✅ Fallback mode is specified (what happens if it fails)
- ✅ Ownership is assigned (who's responsible)
- ✅ Runbook URL is provided (incident response)

**Example:**
```yaml
fallback_declared:
  enabled: true
  kill_switch:
    type: feature_flag
    name: disable_my_agent
  fallback:
    mode: static_placeholder
  ownership:
    team: platform-team
    oncall: oncall-platform
  runbook_url: https://wiki.internal/runbooks/my-agent
```

---

## What release-gate Does NOT Do (v0.1)

These features are planned for future versions:

❌ **Runtime behavior testing** - Doesn't execute the agent
❌ **Output validation** - Doesn't test actual outputs or model behavior
❌ **Formal verification** - Doesn't mathematically verify behavior
❌ **Runtime monitoring** - Doesn't continuously verify at runtime

See [CHANGELOG.md](CHANGELOG.md) for complete roadmap.

---

## Quick Start

### 1. Install

```bash
pip install pyyaml jsonschema
```

### 2. Initialize

```bash
python cli.py init --project my-system
```

Creates:
- `release-gate.yaml` - Configuration template
- `valid_requests.jsonl` - Valid request examples
- `invalid_requests.jsonl` - Invalid request examples

### 3. Run

```bash
python cli.py run --config release-gate.yaml --format text
```

Expected output:
```
input_contract
  Status: ✓ PASS
  valid_samples_tested: 3
  valid_samples_passed: 3
  invalid_samples_tested: 3
  invalid_samples_rejected: 3

fallback_declared
  Status: ✓ PASS
  kill_switch_declared: True
  fallback_declared: True
  ownership_assigned: True
  runbook_provided: True

Overall Decision: ✓ PASS
```

---

## Usage

### Initialize a Project

```bash
python cli.py init --project my-system
```

### Run Governance Gate

```bash
# Text output (human-readable)
python cli.py run --config release-gate.yaml --format text

# JSON output (machine-readable, saved to readiness_report.json)
python cli.py run --config release-gate.yaml --format json

# Custom output file
python cli.py run --config release-gate.yaml --output my-report.json

# Specify environment
python cli.py run --config release-gate.yaml --env prod
```

### Exit Codes

| Code | Status | Meaning |
|------|--------|---------|
| 0 | PASS | All checks passed, safe to deploy |
| 10 | WARN | Warnings found (invalid samples accepted) |
| 1 | FAIL | Critical failures, deployment blocked |

**CI/CD Example:**
```bash
python cli.py run --config release-gate.yaml
exit_code=$?

if [ $exit_code -eq 0 ]; then
  echo "✓ Deploying..."
  deploy_to_production
elif [ $exit_code -eq 10 ]; then
  echo "⚠ Requires review..."
  send_for_approval
else
  echo "✗ Blocked"
  exit 1
fi
```

---

## Complete Configuration Example

```yaml
project:
  name: video-generation-api
  version: 1.0.0
  description: AI video generation with autonomous agent

gate:
  policy: default-v0.1

checks:
  input_contract:
    enabled: true
    schema:
      type: object
      required:
        - prompt
        - duration_sec
        - resolution
      properties:
        prompt:
          type: string
          minLength: 1
          maxLength: 1000
        duration_sec:
          type: number
          minimum: 1
          maximum: 60
        resolution:
          type: string
          enum: ["480p", "720p", "1080p"]
    samples:
      valid_path: valid_requests.jsonl
      invalid_path: invalid_requests.jsonl

  fallback_declared:
    enabled: true
    kill_switch:
      type: feature_flag
      name: disable_video_generation
    fallback:
      mode: static_placeholder
      description: Return static placeholder video on failure
    ownership:
      team: platform-team
      oncall: oncall-platform
    runbook_url: https://wiki.internal/runbooks/video-generation
```

---

## Sample Files

### valid_requests.jsonl
```json
{"prompt":"A cat playing guitar","duration_sec":5,"resolution":"720p"}
{"prompt":"A dog dancing in rain","duration_sec":10,"resolution":"1080p"}
{"prompt":"Ocean waves at sunset","duration_sec":30,"resolution":"480p"}
```

### invalid_requests.jsonl
```json
{"prompt":"","duration_sec":5,"resolution":"720p"}
{"prompt":"Test","duration_sec":120,"resolution":"720p"}
{"duration_sec":5,"resolution":"720p"}
```

---

## Output Examples

### Text Output

```
======================================================================
  release-gate v0.1.0 - Deployment Readiness Report
======================================================================

Project: video-generation-api
Environment: staging
Timestamp: 2026-03-16T10:30:45Z

----------------------------------------------------------------------
Check Results:
----------------------------------------------------------------------

input_contract
  Status: ✓ PASS
  schema_valid: True
  valid_samples_tested: 3
  valid_samples_passed: 3
  valid_samples_failed: 0
  invalid_samples_tested: 3
  invalid_samples_rejected: 3
  invalid_samples_accepted: 0

fallback_declared
  Status: ✓ PASS
  kill_switch_declared: True
  fallback_declared: True
  ownership_assigned: True
  runbook_provided: True

======================================================================
Summary: 2 passed, 0 warned, 0 failed
Overall Decision: ✓ PASS
======================================================================
```

### JSON Output

```json
{
  "overall": "PASS",
  "timestamp": "2026-03-16T10:30:45Z",
  "environment": "staging",
  "project": {
    "name": "video-generation-api",
    "version": "1.0.0"
  },
  "summary": {
    "counts": {
      "pass": 2,
      "warn": 0,
      "fail": 0
    }
  },
  "checks": [
    {
      "name": "input_contract",
      "result": "PASS",
      "evidence": {
        "schema_valid": true,
        "valid_samples_tested": 3,
        "valid_samples_passed": 3,
        "valid_samples_failed": 0,
        "invalid_samples_tested": 3,
        "invalid_samples_rejected": 3,
        "invalid_samples_accepted": 0
      }
    },
    {
      "name": "fallback_declared",
      "result": "PASS",
      "evidence": {
        "kill_switch_declared": true,
        "fallback_declared": true,
        "ownership_assigned": true,
        "runbook_provided": true
      }
    }
  ]
}
```

---

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start
- **[EXTENDED_README.md](EXTENDED_README.md)** - Complete guide (8,000+ words)
- **[CHANGELOG.md](CHANGELOG.md)** - Features and roadmap
- **[COMPLETE.md](COMPLETE.md)** - Project overview
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Governance Gate
  run: |
    pip install pyyaml jsonschema
    python cli.py run --config release-gate.yaml
    
- name: Upload Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: readiness-report
    path: readiness_report.json
```

### GitLab CI

```yaml
governance:
  script:
    - pip install pyyaml jsonschema
    - python cli.py run --config release-gate.yaml
  artifacts:
    paths:
      - readiness_report.json
```

### Jenkins

```groovy
stage('Governance') {
  steps {
    sh '''
      pip install pyyaml jsonschema
      python cli.py run --config release-gate.yaml
    '''
  }
}
```

---

## Design Philosophy

### 1. Governance ≠ Testing

Testing asks: "Does it work?"
Governance asks: "Is it safe to run?"

release-gate focuses on governance.

### 2. Configuration-as-Safety

Safety requirements are declared in YAML and validated before deployment.

### 3. Local-First

No external services, no data transmission, no back-end infrastructure.

### 4. Automation Over Checklists

Checklists can be skipped. CI/CD gates cannot.

---

## Current Capabilities (v0.1)

✅ Schema syntax validation  
✅ Sample test validation  
✅ Governance declaration enforcement  
✅ JSON and text output  
✅ Exit codes for CI/CD  
✅ No external dependencies (just YAML + JSON Schema)

## Planned Capabilities (v0.2+)

🔜 Runtime agent execution testing  
🔜 Action budget verification  
🔜 Performance validation  
🔜 Formal verification layer  
🔜 Runtime monitoring integration  

See [CHANGELOG.md](CHANGELOG.md) for complete roadmap.

---

## Requirements

- Python 3.7+
- pyyaml >= 6.0
- jsonschema >= 4.0

That's it. No heavy frameworks, no external services.

---

## License

MIT License - Use freely and modify as needed.

---

## References

- **Agents of Chaos** - https://arxiv.org/abs/2602.20021
- **DARPA ANSR** - Assured Neuro-Symbolic Research
- **Responsible AI** - Safety as a first-class concern

---

## Support

**Questions or issues?**

- 📖 Read [QUICKSTART.md](QUICKSTART.md) for common questions
- 📚 Read [EXTENDED_README.md](EXTENDED_README.md) for deep dive
- 🐛 Open an issue on GitHub
- 💬 Start a discussion on GitHub

---

**release-gate: Governance enforcement for autonomous AI agents.** 🚀

*Making autonomous agents deterministically reliable.*
