"""Character-Scene Matrix visualization.

Generates an HTML matrix showing which characters appear in which scenes.
"""

from typing import Dict, List
from pathlib import Path
from models import Character, SceneEvidence


def generate_character_scene_matrix(
    characters: Dict[str, Character],
    scene_evidence: List[SceneEvidence],
    output_path: Path
) -> None:
    """Generate HTML character-scene matrix.

    Shows:
    - ● = Character appears in scene
    - ☠ = Character dies in scene
    - ✝ = Character already dead (died in earlier scene)
    - - = Character absent from scene

    Args:
        characters: Dict of character name to Character object
        scene_evidence: List of scene evidence records
        output_path: Path to write HTML file
    """
    # Organize data
    scenes_by_number = {}
    for evidence in scene_evidence:
        scene_num = evidence.scene_number
        if scene_num not in scenes_by_number:
            scenes_by_number[scene_num] = {}

        char_name = evidence.character_name
        scenes_by_number[scene_num][char_name] = evidence.dies_in_this_scene

    # Sort scenes
    sorted_scenes = sorted(scenes_by_number.keys())

    # Sort characters by name
    sorted_characters = sorted(characters.keys())

    # Calculate stats
    char_appearances = {name: 0 for name in sorted_characters}
    for scene_data in scenes_by_number.values():
        for char_name in scene_data:
            if char_name in char_appearances:
                char_appearances[char_name] += 1

    # Generate HTML
    html = _generate_html(
        sorted_characters,
        sorted_scenes,
        scenes_by_number,
        characters,
        char_appearances
    )

    # Write to file
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated character-scene matrix: {output_path}")


def _generate_html(
    sorted_characters: List[str],
    sorted_scenes: List[int],
    scenes_by_number: Dict[int, Dict[str, bool]],
    characters: Dict[str, Character],
    char_appearances: Dict[str, int]
) -> str:
    """Generate HTML content for the matrix."""

    # HTML header
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Character-Scene Matrix - Antarctic Mystery</title>',
        '    <style>',
        _get_css(),
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="container">',
        '        <h1>🧊 Character-Scene Matrix</h1>',
        '        <p class="subtitle">Antarctic Station Alpha-7 Mystery</p>',
        '',
        '        <div class="legend">',
        '            <h3>Legend:</h3>',
        '            <span class="legend-item"><span class="cell appears">●</span> Appears in scene</span>',
        '            <span class="legend-item"><span class="cell dies">☠</span> Dies in scene</span>',
        '            <span class="legend-item"><span class="cell dead">✝</span> Already dead (died in earlier scene)</span>',
        '            <span class="legend-item"><span class="cell absent">-</span> Absent from scene</span>',
        '        </div>',
        '',
        '        <div class="stats">',
        f'            <p><strong>{len(sorted_characters)} characters</strong> across <strong>{len(sorted_scenes)} scenes</strong></p>',
        '        </div>',
        '',
        '        <div class="table-wrapper">',
        '            <table>',
        '                <thead>',
        '                    <tr>',
        '                        <th class="sticky-col">Character</th>',
        '                        <th class="sticky-col">Total</th>',
    ]

    # Scene number headers
    for scene_num in sorted_scenes:
        html_parts.append(f'                        <th>S{scene_num}</th>')

    html_parts.append('                    </tr>')
    html_parts.append('                </thead>')
    html_parts.append('                <tbody>')

    # Character rows
    for char_name in sorted_characters:
        total = char_appearances[char_name]
        html_parts.append('                    <tr>')
        html_parts.append(f'                        <td class="sticky-col char-name">{char_name}</td>')
        html_parts.append(f'                        <td class="sticky-col total">{total}</td>')

        # Get death scene for this character
        char_obj = characters[char_name]
        death_scene = char_obj.death_scene if char_obj.is_dead() else None

        # Scene cells
        for scene_num in sorted_scenes:
            scene_data = scenes_by_number.get(scene_num, {})

            if char_name in scene_data:
                dies = scene_data[char_name]
                if dies:
                    html_parts.append('                        <td class="cell dies">☠</td>')
                else:
                    html_parts.append('                        <td class="cell appears">●</td>')
            else:
                # Character not in this scene - check if already dead
                if death_scene and scene_num > death_scene:
                    html_parts.append('                        <td class="cell dead">✝</td>')
                else:
                    html_parts.append('                        <td class="cell absent">-</td>')

        html_parts.append('                    </tr>')

    # HTML footer
    html_parts.extend([
        '                </tbody>',
        '            </table>',
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


def _get_css() -> str:
    """Get CSS styles for the matrix."""
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
            max-width: 100%;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 30px;
        }

        .legend {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        .legend h3 {
            margin-bottom: 10px;
            color: #2c3e50;
        }

        .legend-item {
            display: inline-block;
            margin-right: 20px;
            font-size: 0.95em;
        }

        .stats {
            margin-bottom: 20px;
            padding: 10px;
            background: #e8f4f8;
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
            padding: 8px;
            text-align: center;
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

        .sticky-col {
            position: sticky;
            left: 0;
            background: white;
            z-index: 5;
        }

        th.sticky-col {
            background: #34495e;
            z-index: 15;
        }

        .char-name {
            text-align: left;
            font-weight: 500;
            min-width: 200px;
            background: #f8f9fa;
        }

        .total {
            font-weight: 600;
            background: #e8f4f8;
            min-width: 60px;
        }

        .cell {
            font-size: 1.2em;
        }

        .appears {
            color: #27ae60;
        }

        .dies {
            color: #e74c3c;
            font-weight: bold;
        }

        .dead {
            color: #95a5a6;
            font-weight: bold;
        }

        .absent {
            color: #bdc3c7;
        }

        tr:hover td {
            background: #f0f8ff;
        }

        .footer {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }

        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .container {
                padding: 15px;
            }

            table {
                font-size: 0.8em;
            }

            th, td {
                padding: 5px;
            }

            .char-name {
                min-width: 150px;
            }
        }
    '''
