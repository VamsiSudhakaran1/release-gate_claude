# release-gate v0.1.0

Deployment readiness gate for autonomous AI agents.

## What is it?

release-gate prevents AI agents from being deployed without operational safeguards.

It answers: **Is this agent safe to run unsupervised?**

## The Problem

AI agents fail in ways traditional QA can't catch:

- **Non-owner access** - Anyone executes commands (Agents of Chaos, Case #2)
- **Self-destruction** - Agents delete their own infrastructure (Case #1)
- **Resource exhaustion** - Infinite loops consume tokens (Cases #4, #5)
- **Identity spoofing** - Governance bypassed via usernames (Case #8)
- **Manipulation** - Agents exploited into harmful behavior (Case #7)

**Traditional QA tests:** Does it work?
**release-gate tests:** Is it safe to run?

These are different questions.

## Quick Start

### 1. Install dependencies

```bash
pip install pyyaml jsonschema
```

### 2. Initialize a project

```bash
python cli.py init --project my-system
```

Creates:
- `release-gate.yaml` - Configuration template
- `valid_requests.jsonl` - Example valid requests
- `invalid_requests.jsonl` - Example invalid requests

### 3. Run the gate

```bash
python cli.py run --config release-gate.yaml --format text
```

Expected output:

```
Overall: ✓ PASS
```

## Features

### Check 1: INPUT_CONTRACT

Validates that your agent's request contract is well-defined and tested.

**What it checks:**
- Schema is defined in YAML
- Valid sample requests pass the schema
- Invalid sample requests fail the schema
- Schema has no syntax errors

**Prevents:** Non-owner requests, resource exhaustion, unexpected behavior

**Configuration:**

```yaml
input_contract:
  enabled: true
  schema:
    type: object
    required: [prompt, duration]
    properties:
      prompt:
        type: string
        minLength: 1
      duration:
        type: number
        minimum: 1
        maximum: 60
  samples:
    valid_path: valid_requests.jsonl
    invalid_path: invalid_requests.jsonl
```

### Check 2: FALLBACK_DECLARED

Validates that operational safety mechanisms are declared.

**What it checks:**
- Kill switch declared (how to disable the agent)
- Fallback mode specified (what happens if it fails)
- Ownership assigned (who's responsible)
- Runbook available (incident response guide)

**Prevents:** Unmanaged deployments, unclear responsibility, no recovery path

**Configuration:**

```yaml
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

## Complete Example

```yaml
project:
  name: video-gen-api
  version: 1.0.0
  description: Video generation service with autonomous agent

gate:
  policy: default-v0.1

checks:
  input_contract:
    enabled: true
    schema:
      type: object
      required: [prompt, duration_sec, resolution]
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
      description: Static video returned on failure
    ownership:
      team: platform-team
      oncall: oncall-platform
    runbook_url: https://wiki.internal/runbooks/video-gen
```

## Sample Files

### valid_requests.jsonl

```json
{"prompt":"A cat playing guitar","duration_sec":5,"resolution":"720p"}
{"prompt":"A dog dancing","duration_sec":10,"resolution":"1080p"}
{"prompt":"Ocean waves","duration_sec":30,"resolution":"480p"}
```

### invalid_requests.jsonl

```json
{"prompt":"","duration_sec":5,"resolution":"720p"}
{"prompt":"Test","duration_sec":120,"resolution":"720p"}
{"duration_sec":5,"resolution":"720p"}
```

## Commands

### Initialize

```bash
python cli.py init --project my-system
```

Creates config file and sample files.

### Run

```bash
python cli.py run --config release-gate.yaml [--env ENV] [--format FORMAT]
```

**Options:**
- `--config FILE` - Path to release-gate.yaml (required)
- `--env {staging,prod}` - Environment (default: staging)
- `--format {json,text}` - Output format (default: json)

## Exit Codes

- `0` = PASS - Deployment is safe
- `10` = WARN - Deployment has warnings
- `1` = FAIL - Deployment is blocked

## Output Formats

### Text Output

Human-readable report:

```
==================================================================
  release-gate v0.1.0 - Deployment Readiness Report
==================================================================

Project: video-gen-api
Environment: staging
Timestamp: 2026-03-10T15:30:45Z

------------------------------------------------------------------
Check Results:
------------------------------------------------------------------

input_contract
  Status: ✓ PASS
  schema_valid: True

fallback_declared
  Status: ✓ PASS
  all_declared: True

==================================================================
Summary: 2 passed, 0 warned, 0 failed
Overall: ✓ PASS
==================================================================
```

### JSON Output

Machine-readable report (saved to readiness_report.json):

```json
{
  "overall": "PASS",
  "timestamp": "2026-03-10T15:30:45Z",
  "environment": "staging",
  "project": {
    "name": "video-gen-api"
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
        "checked": "syntax"
      }
    },
    {
      "name": "fallback_declared",
      "result": "PASS",
      "evidence": {
        "all_declared": true
      }
    }
  ]
}
```

## Use Cases

### CI/CD Integration

```bash
# In GitHub Actions, GitLab CI, Jenkins, etc.
python cli.py run --config release-gate.yaml --env staging

# Check exit code
if [ $? -ne 0 ]; then
  echo "Deployment blocked"
  exit 1
fi
```

### Pre-Deployment Audit

```bash
python cli.py run --config release-gate.yaml --env prod --format json
```

### Compliance Reporting

```bash
python cli.py run --config release-gate.yaml --format json > audit_report.json
```

## Design Philosophy

**1. Governance vs Functionality**

QA tests functionality (does it work).
release-gate tests governance (is it safe).

**2. Inspired by Agents of Chaos**

Research paper documenting 11 ways autonomous agents fail in production.
release-gate prevents 9 of those 11.

**3. CLI-First**

No backend servers, no data transmission, runs locally in your CI/CD.

**4. Simple Configuration**

YAML-based, easy to understand and review.

## Roadmap

### v0.1 (Current)
- INPUT_CONTRACT check
- FALLBACK_DECLARED check
- CLI init and run
- JSON/text output
- Exit codes

### v0.2 (Future)
- BUDGET_GUARDRAILS check
- Formal verification layer
- Custom check support

### v1.0 (Future)
- Full neuro-symbolic verification
- Runtime monitoring
- Distributed agent management

## Technology Stack

- **Language:** Python 3.7+
- **Dependencies:** PyYAML, jsonschema (2 packages)
- **License:** MIT
- **Infrastructure:** None required - runs locally

## References

- Agents of Chaos: https://arxiv.org/abs/2602.20021
- DARPA ANSR: Assured Neuro-Symbolic Research
- Neuro-Symbolic AI: Future of reliable autonomous systems

## Support

**Stuck?**

1. Run `python cli.py init --project test` to see defaults
2. Check the example config in this file
3. Review the sample JSONL files
4. Look at error messages (they're helpful)

## License

MIT License - Use freely, modify as needed

---

**release-gate: Making autonomous agents deterministically reliable.** 🚀
