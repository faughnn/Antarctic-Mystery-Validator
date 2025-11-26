"""Character Analysis Table - Sortable/filterable character difficulty analysis."""

from typing import Dict
from pathlib import Path
import json


def generate_character_analysis(
    clue_analysis: Dict[str, Dict],
    appearance_analysis: Dict[str, int],
    output_path: Path
) -> None:
    """Generate HTML character analysis table.

    Args:
        clue_analysis: Dict from analyze_clues_per_character
        appearance_analysis: Dict from analyze_character_appearances
        output_path: Path to write HTML file
    """
    # Combine data into table rows
    table_data = []
    for char_name in sorted(clue_analysis.keys()):
        char_data = clue_analysis[char_name]
        clue_types = char_data['clue_types']

        table_data.append({
            'name': char_name,
            'difficulty': char_data['difficulty'],
            'total_clues': char_data['total_clues'],
            'scenes': appearance_analysis[char_name],
            'visual': clue_types['visual'],
            'dialogue': clue_types['dialogue'],
            'contextual': clue_types['contextual'],
            'relationship': clue_types['relationship'],
            'role': clue_types['role']
        })

    # Generate HTML
    html = _generate_analysis_html(table_data)

    # Write to file
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated character analysis: {output_path}")


def _generate_analysis_html(table_data: list) -> str:
    """Generate HTML for character analysis table."""

    table_data_json = json.dumps(table_data)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Character Analysis - Antarctic Mystery</title>
    <style>
{_get_analysis_css()}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Character Analysis</h1>
        <p class="subtitle">Difficulty Ratings & Clue Distribution</p>

        <!-- Filters -->
        <div class="controls">
            <div class="filter-group">
                <label>Filter by Difficulty:</label>
                <select id="difficultyFilter">
                    <option value="all">All Characters</option>
                    <option value="VERY HARD">Very Hard</option>
                    <option value="HARD">Hard</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="EASY">Easy</option>
                    <option value="VERY EASY">Very Easy</option>
                </select>
            </div>

            <div class="filter-group">
                <label>Search:</label>
                <input type="text" id="searchBox" placeholder="Search by name...">
            </div>
        </div>

        <!-- Table -->
        <div class="table-container">
            <table id="characterTable">
                <thead>
                    <tr>
                        <th data-sort="name">Character <span class="sort-arrow">↕</span></th>
                        <th data-sort="difficulty">Difficulty <span class="sort-arrow">↕</span></th>
                        <th data-sort="total_clues">Total Clues <span class="sort-arrow">↕</span></th>
                        <th data-sort="scenes">Scenes <span class="sort-arrow">↕</span></th>
                        <th data-sort="visual">Visual <span class="sort-arrow">↕</span></th>
                        <th data-sort="dialogue">Dialogue <span class="sort-arrow">↕</span></th>
                        <th data-sort="contextual">Context <span class="sort-arrow">↕</span></th>
                        <th data-sort="relationship">Relations <span class="sort-arrow">↕</span></th>
                        <th data-sort="role">Role <span class="sort-arrow">↕</span></th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    <!-- Populated by JavaScript -->
                </tbody>
            </table>
        </div>

        <!-- Legend -->
        <div class="legend">
            <h3>Legend</h3>
            <div class="legend-grid">
                <div><strong>Difficulty:</strong> Based on total clue count (fewer clues = harder to identify)</div>
                <div><strong>Total Clues:</strong> Sum of all identifying clues across all scenes</div>
                <div><strong>Scenes:</strong> Number of scenes this character appears in</div>
                <div><strong>Visual:</strong> Uniform, items, features, body position</div>
                <div><strong>Dialogue:</strong> Accent, name mentions</div>
                <div><strong>Context:</strong> Environment, spatial relationships</div>
                <div><strong>Relations:</strong> Relationships mentioned</div>
                <div><strong>Role:</strong> Role mentioned or behavior visible</div>
            </div>
            <p style="margin-top: 15px; font-style: italic; color: #7f8c8d;">
                Note: Players must combine multiple clues to deduce WHO they are, HOW they died, and WHO killed them.
            </p>
        </div>

        <!-- Back Link -->
        <div class="footer">
            <a href="index.html" class="back-link">← Back to Home</a>
        </div>
    </div>

    <script>
        // Data
        const tableData = {table_data_json};

        // Difficulty order for sorting
        const difficultyOrder = {{
            'VERY HARD': 0,
            'HARD': 1,
            'MEDIUM': 2,
            'EASY': 3,
            'VERY EASY': 4
        }};

        // Difficulty colors
        const difficultyColors = {{
            'VERY HARD': '#e74c3c',
            'HARD': '#e67e22',
            'MEDIUM': '#f39c12',
            'EASY': '#3498db',
            'VERY EASY': '#2ecc71'
        }};

        // Current sort state
        let currentSort = {{ column: 'difficulty', ascending: true }};

        // Render table
        function renderTable(data) {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            data.forEach(row => {{
                const tr = document.createElement('tr');
                const diffColor = difficultyColors[row.difficulty];

                tr.innerHTML = `
                    <td class="char-name">${{row.name}}</td>
                    <td><span class="difficulty-badge" style="background: ${{diffColor}}">${{row.difficulty}}</span></td>
                    <td class="number">${{row.total_clues}}</td>
                    <td class="number">${{row.scenes}}</td>
                    <td class="number">${{row.visual}}</td>
                    <td class="number">${{row.dialogue}}</td>
                    <td class="number">${{row.contextual}}</td>
                    <td class="number">${{row.relationship}}</td>
                    <td class="number">${{row.role}}</td>
                `;

                tbody.appendChild(tr);
            }});
        }}

        // Sort data
        function sortData(column) {{
            const ascending = currentSort.column === column ? !currentSort.ascending : true;
            currentSort = {{ column, ascending }};

            const sorted = [...tableData].sort((a, b) => {{
                let valA = a[column];
                let valB = b[column];

                // Special handling for difficulty
                if (column === 'difficulty') {{
                    valA = difficultyOrder[valA];
                    valB = difficultyOrder[valB];
                }}

                if (valA < valB) return ascending ? -1 : 1;
                if (valA > valB) return ascending ? 1 : -1;
                return 0;
            }});

            renderTable(filtered(sorted));
            updateSortArrows();
        }}

        // Filter data
        function filtered(data) {{
            const diffFilter = document.getElementById('difficultyFilter').value;
            const searchText = document.getElementById('searchBox').value.toLowerCase();

            return data.filter(row => {{
                const matchesDiff = diffFilter === 'all' || row.difficulty === diffFilter;
                const matchesSearch = row.name.toLowerCase().includes(searchText);
                return matchesDiff && matchesSearch;
            }});
        }}

        // Update sort arrows
        function updateSortArrows() {{
            document.querySelectorAll('th .sort-arrow').forEach(arrow => {{
                arrow.textContent = '↕';
                arrow.style.opacity = '0.3';
            }});

            const activeHeader = document.querySelector(`th[data-sort="${{currentSort.column}}"] .sort-arrow`);
            if (activeHeader) {{
                activeHeader.textContent = currentSort.ascending ? '↑' : '↓';
                activeHeader.style.opacity = '1';
            }}
        }}

        // Event listeners
        document.querySelectorAll('th[data-sort]').forEach(th => {{
            th.style.cursor = 'pointer';
            th.addEventListener('click', () => {{
                sortData(th.dataset.sort);
            }});
        }});

        document.getElementById('difficultyFilter').addEventListener('change', () => {{
            renderTable(filtered(tableData));
        }});

        document.getElementById('searchBox').addEventListener('input', () => {{
            renderTable(filtered(tableData));
        }});

        // Initial render
        sortData('difficulty');
    </script>
</body>
</html>'''

    return html


def _get_analysis_css() -> str:
    """Get CSS styles for character analysis."""
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

        h3 {
            color: #34495e;
            margin-bottom: 15px;
        }

        .subtitle {
            text-align: center;
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 30px;
        }

        .controls {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: #ecf0f1;
            border-radius: 8px;
            flex-wrap: wrap;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .filter-group label {
            font-weight: 600;
            color: #34495e;
            font-size: 0.9em;
        }

        .filter-group select,
        .filter-group input {
            padding: 10px;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            font-size: 1em;
            min-width: 200px;
        }

        .filter-group select:focus,
        .filter-group input:focus {
            outline: none;
            border-color: #3498db;
        }

        .table-container {
            overflow-x: auto;
            margin-bottom: 30px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        thead {
            background: #34495e;
            color: white;
        }

        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            position: relative;
            user-select: none;
        }

        th:hover {
            background: #2c3e50;
        }

        .sort-arrow {
            margin-left: 5px;
            opacity: 0.3;
            font-size: 0.8em;
        }

        tbody tr {
            border-bottom: 1px solid #ecf0f1;
            transition: background 0.2s;
        }

        tbody tr:hover {
            background: #f8f9fa;
        }

        td {
            padding: 12px 15px;
            color: #2c3e50;
        }

        .char-name {
            font-weight: 600;
            color: #2c3e50;
        }

        .number {
            text-align: center;
            font-family: 'Courier New', monospace;
        }

        .difficulty-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            color: white;
            font-size: 0.85em;
            font-weight: 600;
            text-align: center;
            min-width: 100px;
        }

        .legend {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .legend-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 10px;
            color: #34495e;
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

            .controls {
                flex-direction: column;
            }

            .filter-group select,
            .filter-group input {
                width: 100%;
            }

            table {
                font-size: 0.9em;
            }

            th, td {
                padding: 8px;
            }
        }
    '''
