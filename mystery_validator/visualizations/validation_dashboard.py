"""Validation Dashboard - Visual summary of all validation checks."""

from typing import Dict, Tuple
from pathlib import Path
import json


def generate_validation_dashboard(
    validation_results: Dict[str, Tuple[bool, str]],
    output_path: Path
) -> None:
    """Generate HTML validation dashboard with all checks.

    Args:
        validation_results: Dict of check_name -> (passed: bool, details: str)
        output_path: Path to write HTML file
    """
    # Count passing/failing checks
    total_checks = len(validation_results)
    passing_checks = sum(1 for passed, _ in validation_results.values() if passed)
    failing_checks = total_checks - passing_checks

    # Generate HTML
    html = _generate_dashboard_html(validation_results, total_checks, passing_checks, failing_checks)

    # Write to file
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated validation dashboard: {output_path}")


def _generate_dashboard_html(
    validation_results: Dict[str, Tuple[bool, str]],
    total_checks: int,
    passing_checks: int,
    failing_checks: int
) -> str:
    """Generate HTML for validation dashboard."""

    # Build check cards HTML
    checks_html = ""
    for check_name, (passed, details) in validation_results.items():
        status_class = "check-pass" if passed else "check-fail"
        status_icon = "✓" if passed else "✗"
        status_text = "PASS" if passed else "FAIL"

        # Handle multi-line details
        detail_lines = details.strip().split('\n')
        if len(detail_lines) == 1:
            details_html = f"<p>{detail_lines[0]}</p>"
        else:
            # First line is summary, rest are details
            details_html = f"<p>{detail_lines[0]}</p>"
            if len(detail_lines) > 1:
                error_list = "<ul>" + "".join(f"<li>{line}</li>" for line in detail_lines[1:]) + "</ul>"
                details_html += f'<details class="error-details"><summary>Show {len(detail_lines) - 1} errors</summary>{error_list}</details>'

        checks_html += f'''
            <div class="check-card {status_class}">
                <div class="check-header">
                    <span class="check-icon">{status_icon}</span>
                    <span class="check-name">{check_name}</span>
                    <span class="check-status">{status_text}</span>
                </div>
                <div class="check-details">
                    {details_html}
                </div>
            </div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validation Dashboard - Antarctic Mystery</title>
    <style>
{_get_dashboard_css()}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Validation Dashboard</h1>
        <p class="subtitle">Antarctic Station Alpha-7 - Data Integrity Checks</p>

        <!-- Summary Cards -->
        <div class="summary-grid">
            <div class="summary-card summary-total">
                <div class="summary-number">{total_checks}</div>
                <div class="summary-label">Total Checks</div>
            </div>
            <div class="summary-card summary-pass">
                <div class="summary-number">{passing_checks}</div>
                <div class="summary-label">Passing</div>
            </div>
            <div class="summary-card summary-fail">
                <div class="summary-number">{failing_checks}</div>
                <div class="summary-label">Failing</div>
            </div>
            <div class="summary-card summary-percentage">
                <div class="summary-number">{(passing_checks/total_checks*100):.0f}%</div>
                <div class="summary-label">Success Rate</div>
            </div>
        </div>

        <!-- Validation Checks -->
        <div class="checks-container">
            <h2>Validation Results</h2>
            {checks_html}
        </div>

        <!-- Back Link -->
        <div class="footer">
            <a href="index.html" class="back-link">← Back to Home</a>
        </div>
    </div>
</body>
</html>'''

    return html


def _get_dashboard_css() -> str:
    """Get CSS styles for validation dashboard."""
    return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }

        h2 {
            color: #34495e;
            margin: 30px 0 20px 0;
            font-size: 1.5em;
        }

        .subtitle {
            text-align: center;
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 40px;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .summary-card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            border: 3px solid;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .summary-total {
            border-color: #3498db;
        }

        .summary-pass {
            border-color: #2ecc71;
        }

        .summary-fail {
            border-color: #e74c3c;
        }

        .summary-percentage {
            border-color: #9b59b6;
        }

        .summary-number {
            font-size: 3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .summary-label {
            color: #7f8c8d;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .checks-container {
            margin-bottom: 40px;
        }

        .check-card {
            background: white;
            border-left: 6px solid;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: box-shadow 0.2s;
        }

        .check-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .check-pass {
            border-left-color: #2ecc71;
            background: linear-gradient(to right, rgba(46, 204, 113, 0.05), white);
        }

        .check-fail {
            border-left-color: #e74c3c;
            background: linear-gradient(to right, rgba(231, 76, 60, 0.05), white);
        }

        .check-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }

        .check-icon {
            font-size: 1.5em;
            font-weight: bold;
        }

        .check-pass .check-icon {
            color: #2ecc71;
        }

        .check-fail .check-icon {
            color: #e74c3c;
        }

        .check-name {
            flex: 1;
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
        }

        .check-status {
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }

        .check-pass .check-status {
            background: #2ecc71;
            color: white;
        }

        .check-fail .check-status {
            background: #e74c3c;
            color: white;
        }

        .check-details {
            color: #34495e;
            line-height: 1.6;
        }

        .check-details p {
            margin: 10px 0;
        }

        .error-details {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0,0,0,0.02);
            border-radius: 4px;
            border: 1px solid rgba(0,0,0,0.1);
        }

        .error-details summary {
            cursor: pointer;
            font-weight: 600;
            color: #e74c3c;
            user-select: none;
        }

        .error-details summary:hover {
            color: #c0392b;
        }

        .error-details ul {
            margin-top: 15px;
            padding-left: 20px;
        }

        .error-details li {
            margin: 8px 0;
            color: #555;
            font-size: 0.95em;
        }

        .footer {
            text-align: center;
            padding-top: 30px;
            border-top: 1px solid #ecf0f1;
        }

        .back-link {
            display: inline-block;
            padding: 12px 30px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            transition: background 0.3s;
        }

        .back-link:hover {
            background: #2980b9;
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }

            .summary-grid {
                grid-template-columns: 1fr;
            }

            .check-header {
                flex-wrap: wrap;
            }
        }
    '''
