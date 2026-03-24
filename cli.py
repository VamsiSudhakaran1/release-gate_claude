"""
Updated CLI for release-gate with ALL 4 CHECKS
File: release_gate/cli.py

This integrates ACTION_BUDGET (new) with existing 3 checks
All 4 checks run together, completely compatible
"""

import click
import yaml
import json
from pathlib import Path
from datetime import datetime


def load_config(config_path):
    """Load YAML configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


@click.group()
def cli():
    """release-gate: Governance enforcement for AI agents"""
    pass


@cli.command()
@click.option('--config', required=True, help='Path to governance.yaml')
@click.option('--output', default='text', type=click.Choice(['text', 'json', 'yaml']))
def check(config, output):
    """Run ALL 4 governance checks on agent configuration"""
    
    try:
        # Load configuration
        config_data = load_config(config)
        
        # Import all 4 checks
        from release_gate.checks.action_budget import ActionBudgetCheck
        from release_gate.checks.input_contract import InputContractCheck
        from release_gate.checks.fallback_declared import FallbackDeclaredCheck
        from release_gate.checks.identity_boundary import IdentityBoundaryCheck
        
        # Run all 4 checks (in order)
        results = {}
        
        # 1. ACTION_BUDGET (NEW) - validates costs
        try:
            action_budget = ActionBudgetCheck()
            results['ACTION_BUDGET'] = action_budget.evaluate(config_data)
        except Exception as e:
            results['ACTION_BUDGET'] = {
                'status': 'ERROR',
                'title': 'ACTION_BUDGET: Error',
                'details': str(e)
            }
        
        # 2. INPUT_CONTRACT (EXISTING) - validates request schema
        try:
            input_contract = InputContractCheck()
            results['INPUT_CONTRACT'] = input_contract.evaluate(config_data)
        except Exception as e:
            results['INPUT_CONTRACT'] = {
                'status': 'ERROR',
                'title': 'INPUT_CONTRACT: Error',
                'details': str(e)
            }
        
        # 3. FALLBACK_DECLARED (EXISTING) - validates kill switch
        try:
            fallback = FallbackDeclaredCheck()
            results['FALLBACK_DECLARED'] = fallback.evaluate(config_data)
        except Exception as e:
            results['FALLBACK_DECLARED'] = {
                'status': 'ERROR',
                'title': 'FALLBACK_DECLARED: Error',
                'details': str(e)
            }
        
        # 4. IDENTITY_BOUNDARY (EXISTING) - validates access control
        try:
            identity = IdentityBoundaryCheck()
            results['IDENTITY_BOUNDARY'] = identity.evaluate(config_data)
        except Exception as e:
            results['IDENTITY_BOUNDARY'] = {
                'status': 'ERROR',
                'title': 'IDENTITY_BOUNDARY: Error',
                'details': str(e)
            }
        
        # Determine overall decision
        # Logic: If ANY check fails → FAIL, else if ANY warns → WARN, else PASS
        decision = _determine_decision(results)
        exit_code = _get_exit_code(decision)
        
        # Prepare output
        final_output = {
            'decision': decision,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': results,
            'exit_code': exit_code
        }
        
        # Format and display output
        if output == 'json':
            click.echo(json.dumps(final_output, indent=2))
        elif output == 'yaml':
            click.echo(yaml.dump(final_output, default_flow_style=False))
        else:  # text (human-readable)
            _display_text_output(results, decision)
        
        exit(exit_code)
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


def _determine_decision(results):
    """
    Determine overall decision from all 4 checks
    
    Decision tree:
    - If ANY check FAILS → FAIL (deployment blocked)
    - Else if ANY check WARNS → WARN (manual review needed)
    - Else → PASS (all good)
    """
    
    for check_name, result in results.items():
        if result.get('status') == 'FAIL':
            return 'FAIL'
    
    for check_name, result in results.items():
        if result.get('status') == 'WARN':
            return 'WARN'
    
    return 'PASS'


def _get_exit_code(decision):
    """Get exit code from decision"""
    if decision == 'PASS':
        return 0
    elif decision == 'WARN':
        return 10
    else:  # FAIL or ERROR
        return 1


def _display_text_output(results, decision):
    """Display results in human-readable text format"""
    
    click.echo()
    click.echo("┌─────────────────────────────────────────────────────────────┐")
    click.echo("│ 🚪 release-gate: Governance Validation (All 4 Checks)       │")
    click.echo("├─────────────────────────────────────────────────────────────┤")
    click.echo()
    
    # Display each check result
    check_order = ['ACTION_BUDGET', 'INPUT_CONTRACT', 'FALLBACK_DECLARED', 'IDENTITY_BOUNDARY']
    icons = {
        'ACTION_BUDGET': '💰',
        'INPUT_CONTRACT': '📋',
        'FALLBACK_DECLARED': '⏹',
        'IDENTITY_BOUNDARY': '🔐'
    }
    
    for check_name in check_order:
        if check_name not in results:
            continue
        
        result = results[check_name]
        status = result.get('status', 'UNKNOWN')
        icon = icons.get(check_name, '✓')
        
        # Status indicator
        if status == 'PASS':
            status_icon = '✓'
        elif status == 'WARN':
            status_icon = '⚠'
        else:
            status_icon = '✗'
        
        # Display check
        click.echo(f"{icon} {check_name}: {status_icon} {status}")
        click.echo(f"   {result.get('title', '')}")
        click.echo(f"   {result.get('details', '')}")
        click.echo()
    
    # Final decision
    click.echo()
    if decision == 'PASS':
        click.echo("✅ FINAL DECISION: PASS (Safe to deploy)")
        click.echo("   All 4 checks passed")
    elif decision == 'WARN':
        click.echo("⚠️ FINAL DECISION: WARN (Manual review recommended)")
        click.echo("   One or more checks require review")
    else:
        click.echo("❌ FINAL DECISION: FAIL (Deployment blocked)")
        click.echo("   One or more checks failed")
    
    click.echo()
    click.echo("└─────────────────────────────────────────────────────────────┘")
    click.echo()


if __name__ == '__main__':
    cli()
