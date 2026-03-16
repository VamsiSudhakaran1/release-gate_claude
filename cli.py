#!/usr/bin/env python3
"""release-gate CLI - Deployment readiness gate for AI systems"""

import sys
import json
from pathlib import Path
from datetime import datetime

def init_project(project_name, output_dir="."):
    """Initialize a new release-gate project"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create config file
    config_content = f"""project:
  name: {project_name}
  version: 1.0.0
  description: AI system deployment gate

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

  fallback_declared:
    enabled: true
    kill_switch:
      type: feature_flag
      name: disable_{project_name.replace('-', '_')}
    fallback:
      mode: static_placeholder
    ownership:
      team: platform-team
      oncall: oncall-platform
    runbook_url: https://wiki.internal/runbooks/{project_name}
"""
    
    # Write config
    config_path = output_path / "release-gate.yaml"
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"✓ Created: {config_path}")
    
    # Create valid samples
    valid_content = """{"prompt":"Test prompt 1","duration_sec":5}
{"prompt":"Test prompt 2","duration_sec":10}
{"prompt":"Another test","duration_sec":30}
"""
    valid_path = output_path / "valid_requests.jsonl"
    with open(valid_path, 'w') as f:
        f.write(valid_content)
    print(f"✓ Created: {valid_path}")
    
    # Create invalid samples
    invalid_content = """{"prompt":"","duration_sec":5}
{"prompt":"Test","duration_sec":120}
{"duration_sec":5}
"""
    invalid_path = output_path / "invalid_requests.jsonl"
    with open(invalid_path, 'w') as f:
        f.write(invalid_content)
    print(f"✓ Created: {invalid_path}")
    
    print("\n✨ Initialization complete!")

def run_gate(config_path, env="staging", output_format="json"):
    """Run the deployment gate checks"""
    try:
        import yaml
    except ImportError:
        print("ERROR: pyyaml not installed. Run: pip install pyyaml jsonschema")
        return 1
    
    try:
        import jsonschema
    except ImportError:
        print("ERROR: jsonschema not installed. Run: pip install pyyaml jsonschema")
        return 1
    
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return 1
    
    # Load config
    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}")
        return 1
    
    # Initialize results
    results = {
        "overall": "PASS",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": env,
        "project": config.get("project", {}),
        "summary": {"counts": {"pass": 0, "warn": 0, "fail": 0}},
        "checks": []
    }
    
    # INPUT_CONTRACT check
    input_check = config.get("checks", {}).get("input_contract", {})
    if input_check.get("enabled", True):
        schema = input_check.get("schema")
        if not schema:
            results["checks"].append({
                "name": "input_contract",
                "result": "FAIL",
                "evidence": {"error": "No schema defined"}
            })
            results["overall"] = "FAIL"
            results["summary"]["counts"]["fail"] += 1
        else:
            try:
                jsonschema.Draft7Validator.check_schema(schema)
                results["checks"].append({
                    "name": "input_contract",
                    "result": "PASS",
                    "evidence": {"schema_valid": True, "checked": "syntax"}
                })
                results["summary"]["counts"]["pass"] += 1
            except Exception as e:
                results["checks"].append({
                    "name": "input_contract",
                    "result": "FAIL",
                    "evidence": {"error": f"Invalid schema: {str(e)}"}
                })
                results["overall"] = "FAIL"
                results["summary"]["counts"]["fail"] += 1
    
    # FALLBACK_DECLARED check
    fallback_check = config.get("checks", {}).get("fallback_declared", {})
    if fallback_check.get("enabled", True):
        missing = []
        if not fallback_check.get("kill_switch"):
            missing.append("kill_switch")
        if not fallback_check.get("fallback"):
            missing.append("fallback")
        if not fallback_check.get("ownership"):
            missing.append("ownership")
        if not fallback_check.get("runbook_url"):
            missing.append("runbook_url")
        
        if missing:
            results["checks"].append({
                "name": "fallback_declared",
                "result": "FAIL",
                "evidence": {"missing_fields": missing}
            })
            if results["overall"] == "PASS":
                results["overall"] = "FAIL"
            results["summary"]["counts"]["fail"] += 1
        else:
            results["checks"].append({
                "name": "fallback_declared",
                "result": "PASS",
                "evidence": {"all_declared": True}
            })
            results["summary"]["counts"]["pass"] += 1
    
    # Write report
    with open("readiness_report.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display
    if output_format == "text":
        print("\n" + "="*70)
        print("  release-gate v0.1.0 - Deployment Readiness Report")
        print("="*70)
        print(f"\nProject: {config.get('project', {}).get('name', 'unknown')}")
        print(f"Environment: {env}")
        print(f"Timestamp: {results['timestamp']}")
        print("\n" + "-"*70)
        print("Check Results:")
        print("-"*70)
        
        for check in results["checks"]:
            if check["result"] == "PASS":
                status = "✓ PASS"
            elif check["result"] == "FAIL":
                status = "✗ FAIL"
            else:
                status = "⚠ WARN"
            
            print(f"\n{check['name']}")
            print(f"  Status: {status}")
            for key, value in check.get("evidence", {}).items():
                if isinstance(value, list):
                    print(f"  {key}: {', '.join(value)}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n" + "="*70)
        summary = results["summary"]["counts"]
        print(f"Summary: {summary['pass']} passed, {summary['warn']} warned, {summary['fail']} failed")
        overall = results['overall']
        if overall == "PASS":
            print(f"Overall: ✓ PASS")
        elif overall == "WARN":
            print(f"Overall: ⚠ WARN")
        else:
            print(f"Overall: ✗ FAIL")
        print("="*70 + "\n")
    else:
        print(json.dumps(results, indent=2))
    
    # Return exit code
    exit_codes = {"PASS": 0, "WARN": 10, "FAIL": 1}
    return exit_codes.get(results["overall"], 1)

def main():
    if len(sys.argv) < 2:
        print("release-gate v0.1.0 - Deployment Readiness Gate for AI Systems")
        print("\nUsage:")
        print("  python cli.py init --project NAME")
        print("  python cli.py run --config CONFIG [--env ENV] [--format FORMAT]")
        print("\nExample:")
        print("  python cli.py init --project my-system")
        print("  python cli.py run --config release-gate.yaml --format text")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "init":
        project = "my-system"
        if "--project" in sys.argv:
            idx = sys.argv.index("--project")
            if idx + 1 < len(sys.argv):
                project = sys.argv[idx + 1]
        init_project(project)
        sys.exit(0)
    
    elif command == "run":
        config = None
        env = "staging"
        fmt = "json"
        
        if "--config" in sys.argv:
            idx = sys.argv.index("--config")
            if idx + 1 < len(sys.argv):
                config = sys.argv[idx + 1]
        
        if "--env" in sys.argv:
            idx = sys.argv.index("--env")
            if idx + 1 < len(sys.argv):
                env = sys.argv[idx + 1]
        
        if "--format" in sys.argv:
            idx = sys.argv.index("--format")
            if idx + 1 < len(sys.argv):
                fmt = sys.argv[idx + 1]
        
        if not config:
            print("ERROR: --config is required")
            print("Usage: python cli.py run --config release-gate.yaml")
            sys.exit(1)
        
        sys.exit(run_gate(config, env, fmt))
    
    else:
        print(f"Unknown command: {command}")
        print("\nUsage:")
        print("  python cli.py init --project NAME")
        print("  python cli.py run --config CONFIG")
        sys.exit(1)

if __name__ == "__main__":
    main()
