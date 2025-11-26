"""Game Balance Visualization - Overall game metrics and statistics."""

from typing import Dict, List
from pathlib import Path
from collections import Counter
import json


def generate_game_balance(
    difficulty_groups: Dict[str, List[str]],
    clue_analysis: Dict[str, Dict],
    scene_complexity: Dict[int, Dict],
    appearance_analysis: Dict[str, int],
    total_characters: int,
    total_scenes: int,
    output_path: Path
) -> None:
    """Generate HTML game balance visualization.

    Args:
        difficulty_groups: Dict from analyze_character_difficulty
        clue_analysis: Dict from analyze_clues_per_character
        scene_complexity: Dict from analyze_scene_complexity
        appearance_analysis: Dict from analyze_character_appearances
        total_characters: Total number of characters
        total_scenes: Total number of scenes
        output_path: Path to write HTML file
    """
    # Calculate statistics
    stats = _calculate_balance_stats(
        difficulty_groups,
        clue_analysis,
        scene_complexity,
        appearance_analysis,
        total_characters,
        total_scenes
    )

    # Generate HTML
    html = _generate_balance_html(stats)

    # Write to file
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated game balance report: {output_path}")


def _calculate_balance_stats(
    difficulty_groups: Dict[str, List[str]],
    clue_analysis: Dict[str, Dict],
    scene_complexity: Dict[int, Dict],
    appearance_analysis: Dict[str, int],
    total_characters: int,
    total_scenes: int
) -> Dict:
    """Calculate statistics for game balance visualization."""

    # Difficulty distribution
    difficulty_dist = {
        diff: len(chars) for diff, chars in difficulty_groups.items()
    }

    # Clue type totals
    clue_totals = {
        'visual': 0,
        'dialogue': 0,
        'contextual': 0,
        'relationship': 0,
        'role': 0
    }
    for char_data in clue_analysis.values():
        for clue_type, count in char_data['clue_types'].items():
            clue_totals[clue_type] += count

    total_clues = sum(clue_totals.values())
    clue_averages = {
        clue_type: count / total_characters
        for clue_type, count in clue_totals.items()
    }

    # Scene complexity distribution
    complexity_counts = Counter(
        info['complexity_rating'] for info in scene_complexity.values()
    )

    # Appearance statistics
    appearances = list(appearance_analysis.values())
    min_appearances = min(appearances)
    max_appearances = max(appearances)
    avg_appearances = sum(appearances) / len(appearances)

    # Character with min/max appearances
    min_char = [name for name, count in appearance_analysis.items() if count == min_appearances][0]
    max_char = [name for name, count in appearance_analysis.items() if count == max_appearances][0]

    # Clue count statistics
    clue_counts = [data['total_clues'] for data in clue_analysis.values()]
    min_clues = min(clue_counts)
    max_clues = max(clue_counts)
    avg_clues = sum(clue_counts) / len(clue_counts)

    return {
        'total_characters': total_characters,
        'total_scenes': total_scenes,
        'total_clues': total_clues,
        'difficulty_dist': difficulty_dist,
        'clue_totals': clue_totals,
        'clue_averages': clue_averages,
        'complexity_counts': dict(complexity_counts),
        'min_appearances': min_appearances,
        'max_appearances': max_appearances,
        'avg_appearances': avg_appearances,
        'min_char': min_char,
        'max_char': max_char,
        'min_clues': min_clues,
        'max_clues': max_clues,
        'avg_clues': avg_clues
    }


def _generate_balance_html(stats: Dict) -> str:
    """Generate HTML for game balance visualization."""

    stats_json = json.dumps(stats)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Balance - Antarctic Mystery</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
{_get_balance_css()}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Game Balance Analysis</h1>
        <p class="subtitle">Overall Statistics & Distribution Metrics</p>

        <!-- Key Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-number">{stats['total_characters']}</div>
                <div class="metric-label">Characters</div>
            </div>
            <div class="metric-card">
                <div class="metric-number">{stats['total_scenes']}</div>
                <div class="metric-label">Scenes</div>
            </div>
            <div class="metric-card">
                <div class="metric-number">{stats['total_clues']}</div>
                <div class="metric-label">Total Clues</div>
            </div>
            <div class="metric-card">
                <div class="metric-number">{stats['avg_clues']:.1f}</div>
                <div class="metric-label">Avg Clues/Character</div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
            <!-- Difficulty Distribution -->
            <div class="chart-card">
                <h3>Difficulty Distribution</h3>
                <canvas id="difficultyChart"></canvas>
                <div class="chart-note">
                    Based on total clue count per character
                </div>
            </div>

            <!-- Clue Type Distribution -->
            <div class="chart-card">
                <h3>Clue Type Distribution</h3>
                <canvas id="clueTypeChart"></canvas>
                <div class="chart-note">
                    Total clues across all characters by type
                </div>
            </div>

            <!-- Scene Complexity -->
            <div class="chart-card">
                <h3>Scene Complexity</h3>
                <canvas id="complexityChart"></canvas>
                <div class="chart-note">
                    Number of characters per scene
                </div>
            </div>

            <!-- Clue Averages -->
            <div class="chart-card">
                <h3>Average Clues per Character</h3>
                <canvas id="averagesChart"></canvas>
                <div class="chart-note">
                    Average number of each clue type
                </div>
            </div>
        </div>

        <!-- Statistics -->
        <div class="stats-section">
            <h2>Detailed Statistics</h2>

            <div class="stat-group">
                <h3>Character Appearances</h3>
                <ul>
                    <li><strong>Minimum:</strong> {stats['min_appearances']} scenes - {stats['min_char']}</li>
                    <li><strong>Maximum:</strong> {stats['max_appearances']} scenes - {stats['max_char']}</li>
                    <li><strong>Average:</strong> {stats['avg_appearances']:.1f} scenes per character</li>
                </ul>
            </div>

            <div class="stat-group">
                <h3>Clue Distribution</h3>
                <ul>
                    <li><strong>Minimum:</strong> {stats['min_clues']} clues (hardest character)</li>
                    <li><strong>Maximum:</strong> {stats['max_clues']} clues (easiest character)</li>
                    <li><strong>Average:</strong> {stats['avg_clues']:.1f} clues per character</li>
                    <li><strong>Total:</strong> {stats['total_clues']} clues across all characters</li>
                </ul>
            </div>

            <div class="stat-group">
                <h3>Design Notes</h3>
                <ul>
                    <li>More clues = easier to identify (more information to work with)</li>
                    <li>Fewer clues = harder to identify (requires deduction with limited information)</li>
                    <li>Players must combine multiple clues to deduce WHO, HOW, and WHO KILLED</li>
                    <li>Single clues don't solve the puzzle - cross-referencing is required</li>
                </ul>
            </div>
        </div>

        <!-- Back Link -->
        <div class="footer">
            <a href="index.html" class="back-link">← Back to Home</a>
        </div>
    </div>

    <script>
        const stats = {stats_json};

        // Difficulty Distribution Chart
        new Chart(document.getElementById('difficultyChart'), {{
            type: 'bar',
            data: {{
                labels: ['Very Hard', 'Hard', 'Medium', 'Easy', 'Very Easy'],
                datasets: [{{
                    label: 'Number of Characters',
                    data: [
                        stats.difficulty_dist['VERY HARD'],
                        stats.difficulty_dist['HARD'],
                        stats.difficulty_dist['MEDIUM'],
                        stats.difficulty_dist['EASY'],
                        stats.difficulty_dist['VERY EASY']
                    ],
                    backgroundColor: ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#2ecc71']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ stepSize: 2 }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});

        // Clue Type Distribution Chart
        new Chart(document.getElementById('clueTypeChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Visual', 'Dialogue', 'Contextual', 'Relationship', 'Role'],
                datasets: [{{
                    data: [
                        stats.clue_totals.visual,
                        stats.clue_totals.dialogue,
                        stats.clue_totals.contextual,
                        stats.clue_totals.relationship,
                        stats.clue_totals.role
                    ],
                    backgroundColor: ['#3498db', '#9b59b6', '#e67e22', '#e74c3c', '#2ecc71']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});

        // Scene Complexity Chart
        new Chart(document.getElementById('complexityChart'), {{
            type: 'bar',
            data: {{
                labels: ['Simple\\n(1-2)', 'Balanced\\n(3-6)', 'Complex\\n(7-10)', 'Overwhelming\\n(11+)'],
                datasets: [{{
                    label: 'Number of Scenes',
                    data: [
                        stats.complexity_counts['SIMPLE'] || 0,
                        stats.complexity_counts['BALANCED'] || 0,
                        stats.complexity_counts['COMPLEX'] || 0,
                        stats.complexity_counts['OVERWHELMING'] || 0
                    ],
                    backgroundColor: ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ stepSize: 5 }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});

        // Clue Averages Chart
        new Chart(document.getElementById('averagesChart'), {{
            type: 'bar',
            data: {{
                labels: ['Visual', 'Dialogue', 'Context', 'Relations', 'Role'],
                datasets: [{{
                    label: 'Average per Character',
                    data: [
                        stats.clue_averages.visual,
                        stats.clue_averages.dialogue,
                        stats.clue_averages.contextual,
                        stats.clue_averages.relationship,
                        stats.clue_averages.role
                    ],
                    backgroundColor: '#3498db'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

    return html


def _get_balance_css() -> str:
    """Get CSS styles for game balance."""
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
            margin: 40px 0 20px 0;
            font-size: 1.8em;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }

        h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

        .subtitle {
            text-align: center;
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 40px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .metric-number {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .metric-label {
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.9;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }

        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .chart-card h3 {
            margin-bottom: 20px;
            text-align: center;
        }

        .chart-note {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 15px;
            font-style: italic;
        }

        .stats-section {
            background: #ecf0f1;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 40px;
        }

        .stat-group {
            margin-bottom: 30px;
        }

        .stat-group:last-child {
            margin-bottom: 0;
        }

        .stat-group h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .stat-group ul {
            list-style: none;
            padding-left: 0;
        }

        .stat-group li {
            padding: 8px 0;
            color: #34495e;
            font-size: 1.05em;
        }

        .stat-group li strong {
            color: #2c3e50;
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

            .charts-grid {
                grid-template-columns: 1fr;
            }

            .metric-card {
                padding: 20px;
            }

            .metric-number {
                font-size: 2em;
            }
        }
    '''
