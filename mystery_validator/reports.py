from typing import Dict, Tuple, List
from pathlib import Path


def generate_simple_report(validation_results: Dict[str, Tuple[bool, str]]) -> None:
    """Generate a simple text report from validation results."""
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print()

    passed_count = 0
    failed_count = 0

    for validation_name, (passed, details) in validation_results.items():
        status = "✓ PASS" if passed else "✗ FAIL"

        print(f"{status} - {validation_name}")

        if details:
            # Indent details for readability
            for line in details.split('\n'):
                if line.strip():
                    print(f"      {line}")

        print()

        if passed:
            passed_count += 1
        else:
            failed_count += 1

    print("=" * 80)
    print(f"Summary: {passed_count} passed, {failed_count} failed")
    print("=" * 80)


def generate_html_report(
    validation_results: Dict[str, Tuple[bool, str]],
    difficulty_groups: Dict[str, List[str]],
    clue_analysis: Dict,
    appearance_analysis: Dict,
    scene_complexity: Dict,
    total_characters: int,
    total_scenes: int,
    output_path: Path
) -> None:
    """Generate comprehensive HTML validation report.

    Args:
        validation_results: Dict of validation name to (passed, details)
        difficulty_groups: Dict of difficulty level to list of character names
        clue_analysis: Dict of character name to clue data
        appearance_analysis: Dict of character name to scene count
        scene_complexity: Dict of scene number to complexity data
        total_characters: Total number of characters
        total_scenes: Total number of scenes
        output_path: Path to write HTML file
    """
    # Calculate summary stats
    passed_count = sum(1 for passed, _ in validation_results.values() if passed)
    failed_count = len(validation_results) - passed_count

    # Build character details table data
    char_details = []
    for char_name in sorted(clue_analysis.keys()):
        char_data = clue_analysis[char_name]
        scenes = appearance_analysis[char_name]
        clue_types = char_data['clue_types']

        char_details.append({
            'name': char_name,
            'difficulty': char_data['difficulty'],
            'total_clues': char_data['total_clues'],
            'scenes': scenes,
            'visual': clue_types['visual'],
            'dialogue': clue_types['dialogue'],
            'contextual': clue_types['contextual'],
            'relationship': clue_types['relationship'],
            'role': clue_types['role']
        })

    # Sort by difficulty
    difficulty_order = {'VERY HARD': 0, 'HARD': 1, 'MEDIUM': 2, 'EASY': 3, 'VERY EASY': 4}
    char_details.sort(key=lambda x: (difficulty_order[x['difficulty']], x['total_clues'], x['name']))

    # Calculate scene complexity distribution
    from collections import Counter
    complexity_counts = Counter(info['complexity_rating'] for info in scene_complexity.values())

    # Generate HTML
    html = _generate_validation_html(
        validation_results,
        passed_count,
        failed_count,
        difficulty_groups,
        char_details,
        complexity_counts,
        total_characters,
        total_scenes,
        appearance_analysis
    )

    # Write to file
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated validation report: {output_path}")


def _generate_validation_html(
    validation_results: Dict[str, Tuple[bool, str]],
    passed_count: int,
    failed_count: int,
    difficulty_groups: Dict[str, List[str]],
    char_details: List[Dict],
    complexity_counts: Dict,
    total_characters: int,
    total_scenes: int,
    appearance_analysis: Dict
) -> str:
    """Generate the HTML content for validation report."""

    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Validation Report - Antarctic Mystery</title>',
        '    <style>',
        _get_validation_css(),
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="container">',
        '        <h1>🧊 Antarctic Mystery Validator</h1>',
        '        <p class="subtitle">Antarctic Station Alpha-7 - Validation Report</p>',
        '',
        '        <!-- Summary -->',
        '        <div class="summary">',
        f'            <div class="summary-card {"passed" if failed_count == 0 else "failed"}">',
        f'                <div class="summary-number">{passed_count}/{len(validation_results)}</div>',
        f'                <div class="summary-label">Checks Passed</div>',
        '            </div>',
        '            <div class="summary-card info">',
        f'                <div class="summary-number">{total_characters}</div>',
        f'                <div class="summary-label">Characters</div>',
        '            </div>',
        '            <div class="summary-card info">',
        f'                <div class="summary-number">{total_scenes}</div>',
        f'                <div class="summary-label">Scenes</div>',
        '            </div>',
        '        </div>',
        '',
        '        <!-- Validation Results -->',
        '        <h2>📋 Validation Results</h2>',
        '        <div class="validation-list">',
    ]

    # Add validation results
    for validation_name, (passed, details) in validation_results.items():
        status_class = "pass" if passed else "fail"
        status_icon = "✓" if passed else "✗"

        html_parts.append(f'            <div class="validation-item {status_class}">')
        html_parts.append(f'                <div class="validation-header">')
        html_parts.append(f'                    <span class="status-icon">{status_icon}</span>')
        html_parts.append(f'                    <span class="validation-name">{validation_name}</span>')
        html_parts.append(f'                </div>')

        if details:
            html_parts.append(f'                <div class="validation-details">')
            for line in details.split('\n'):
                if line.strip():
                    html_parts.append(f'                    <div>{line}</div>')
            html_parts.append(f'                </div>')

        html_parts.append(f'            </div>')

    html_parts.extend([
        '        </div>',
        '',
        '        <!-- Game Balance Analysis -->',
        '        <h2>📊 Game Balance Analysis</h2>',
        '',
        '        <div class="analysis-section">',
        '            <h3>Difficulty Distribution</h3>',
        '            <p class="explanation">More clues = easier to identify | Fewer clues = harder to identify</p>',
        '            <div class="difficulty-bars">',
    ])

    # Add difficulty distribution bars
    for difficulty in ['VERY HARD', 'HARD', 'MEDIUM', 'EASY', 'VERY EASY']:
        count = len(difficulty_groups[difficulty])
        percentage = (count / total_characters) * 100
        html_parts.append(f'                <div class="difficulty-row">')
        html_parts.append(f'                    <div class="difficulty-label">{difficulty}</div>')
        html_parts.append(f'                    <div class="difficulty-bar-container">')
        html_parts.append(f'                        <div class="difficulty-bar" style="width: {percentage}%"></div>')
        html_parts.append(f'                    </div>')
        html_parts.append(f'                    <div class="difficulty-count">{count} ({percentage:.1f}%)</div>')
        html_parts.append(f'                </div>')

    # Scene complexity
    html_parts.extend([
        '            </div>',
        '        </div>',
        '',
        '        <div class="analysis-section">',
        '            <h3>Scene Complexity</h3>',
        '            <div class="complexity-grid">',
        f'                <div class="complexity-item"><strong>SIMPLE:</strong> {complexity_counts.get("SIMPLE", 0)} scenes (1-2 characters)</div>',
        f'                <div class="complexity-item"><strong>BALANCED:</strong> {complexity_counts.get("BALANCED", 0)} scenes (3-6 characters)</div>',
        f'                <div class="complexity-item"><strong>COMPLEX:</strong> {complexity_counts.get("COMPLEX", 0)} scenes (7-10 characters)</div>',
        f'                <div class="complexity-item"><strong>OVERWHELMING:</strong> {complexity_counts.get("OVERWHELMING", 0)} scenes (11+ characters)</div>',
        '            </div>',
        '        </div>',
        '',
        '        <!-- Character Breakdown -->',
        '        <h2>👥 Detailed Character Breakdown</h2>',
        '        <div class="table-wrapper">',
        '            <table>',
        '                <thead>',
        '                    <tr>',
        '                        <th>Character</th>',
        '                        <th>Difficulty</th>',
        '                        <th>Clues</th>',
        '                        <th>Scenes</th>',
        '                        <th>Vis</th>',
        '                        <th>Dlg</th>',
        '                        <th>Ctx</th>',
        '                        <th>Rel</th>',
        '                        <th>Role</th>',
        '                    </tr>',
        '                </thead>',
        '                <tbody>',
    ])

    # Add character rows
    for char in char_details:
        difficulty_class = char['difficulty'].lower().replace(' ', '-')
        html_parts.append('                    <tr>')
        html_parts.append(f'                        <td class="char-name">{char["name"]}</td>')
        html_parts.append(f'                        <td class="difficulty {difficulty_class}">{char["difficulty"]}</td>')
        html_parts.append(f'                        <td>{char["total_clues"]}</td>')
        html_parts.append(f'                        <td>{char["scenes"]}</td>')
        html_parts.append(f'                        <td>{char["visual"]}</td>')
        html_parts.append(f'                        <td>{char["dialogue"]}</td>')
        html_parts.append(f'                        <td>{char["contextual"]}</td>')
        html_parts.append(f'                        <td>{char["relationship"]}</td>')
        html_parts.append(f'                        <td>{char["role"]}</td>')
        html_parts.append('                    </tr>')

    # Footer
    html_parts.extend([
        '                </tbody>',
        '            </table>',
        '        </div>',
        '',
        '        <div class="legend-box">',
        '            <h3>Legend</h3>',
        '            <ul>',
        '                <li><strong>Diff:</strong> Difficulty rating (percentile-based, ~12 characters per bucket)</li>',
        '                <li><strong>Clues:</strong> Total identifying clues</li>',
        '                <li><strong>Scenes:</strong> Number of scenes character appears in</li>',
        '                <li><strong>Vis:</strong> Visual clues (uniform, items, features, body position)</li>',
        '                <li><strong>Dlg:</strong> Dialogue clues (accent, name mentions)</li>',
        '                <li><strong>Ctx:</strong> Contextual clues (environment, spatial relationships)</li>',
        '                <li><strong>Rel:</strong> Relationship clues</li>',
        '                <li><strong>Role:</strong> Role clues (mentioned, behavior)</li>',
        '            </ul>',
        '            <p class="note">Note: A single clue doesn\'t identify a character - players must combine multiple clues to deduce WHO they are, HOW they died, and WHO killed them.</p>',
        '        </div>',
        '',
        '        <div class="footer">',
        '            <p>Generated by Antarctic Mystery Validator</p>',
        '        </div>',
        '    </div>',
        '</body>',
        '</html>',
    ])

    return '\n'.join(html_parts)


def _get_validation_css() -> str:
    """Get CSS styles for validation report."""
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
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        h2 {
            color: #2c3e50;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }

        h3 {
            color: #34495e;
            margin-bottom: 15px;
        }

        .subtitle {
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 30px;
        }

        .summary {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .summary-card {
            flex: 1;
            min-width: 150px;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .summary-card.passed {
            background: #d4edda;
            border: 2px solid #28a745;
        }

        .summary-card.failed {
            background: #f8d7da;
            border: 2px solid #dc3545;
        }

        .summary-card.info {
            background: #e8f4f8;
            border: 2px solid #3498db;
        }

        .summary-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
        }

        .summary-label {
            font-size: 1em;
            color: #7f8c8d;
            margin-top: 5px;
        }

        .validation-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .validation-item {
            border-radius: 8px;
            padding: 15px 20px;
            border-left: 5px solid;
        }

        .validation-item.pass {
            background: #d4edda;
            border-color: #28a745;
        }

        .validation-item.fail {
            background: #f8d7da;
            border-color: #dc3545;
        }

        .validation-header {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            font-size: 1.1em;
        }

        .status-icon {
            font-size: 1.3em;
        }

        .validation-item.pass .status-icon {
            color: #28a745;
        }

        .validation-item.fail .status-icon {
            color: #dc3545;
        }

        .validation-details {
            margin-top: 10px;
            padding-left: 35px;
            font-size: 0.95em;
            color: #495057;
        }

        .analysis-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .explanation {
            color: #6c757d;
            font-style: italic;
            margin-bottom: 15px;
        }

        .difficulty-bars {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .difficulty-row {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .difficulty-label {
            min-width: 100px;
            font-weight: 600;
            color: #495057;
        }

        .difficulty-bar-container {
            flex: 1;
            height: 25px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }

        .difficulty-bar {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2980b9);
            border-radius: 4px;
        }

        .difficulty-count {
            min-width: 100px;
            text-align: right;
            color: #495057;
        }

        .complexity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .complexity-item {
            padding: 15px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }

        .table-wrapper {
            overflow-x: auto;
            margin-bottom: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }

        th, td {
            padding: 12px 8px;
            text-align: left;
            border: 1px solid #ddd;
        }

        th {
            background: #34495e;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .char-name {
            font-weight: 500;
        }

        .difficulty {
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            text-align: center;
        }

        .difficulty.very-hard {
            background: #e74c3c;
            color: white;
        }

        .difficulty.hard {
            background: #e67e22;
            color: white;
        }

        .difficulty.medium {
            background: #f39c12;
            color: white;
        }

        .difficulty.easy {
            background: #2ecc71;
            color: white;
        }

        .difficulty.very-easy {
            background: #27ae60;
            color: white;
        }

        tr:hover {
            background: #f0f8ff;
        }

        .legend-box {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
        }

        .legend-box ul {
            list-style: none;
            padding-left: 0;
        }

        .legend-box li {
            margin-bottom: 8px;
            color: #495057;
        }

        .note {
            margin-top: 15px;
            padding: 10px;
            background: #d1ecf1;
            border-left: 4px solid #0c5460;
            color: #0c5460;
            font-style: italic;
        }

        .footer {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }

        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .container {
                padding: 20px;
            }

            h1 {
                font-size: 2em;
            }

            .summary {
                flex-direction: column;
            }

            .difficulty-row {
                flex-direction: column;
                align-items: flex-start;
            }

            .difficulty-bar-container {
                width: 100%;
            }

            table {
                font-size: 0.8em;
            }

            th, td {
                padding: 8px 5px;
            }
        }
    '''
