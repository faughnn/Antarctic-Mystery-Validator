"""Organizational chart visualization showing hierarchy and reporting structure.

Generates an interactive HTML org chart with:
- Horizontal bands for each tier level (Leadership → Staff)
- Department grouping with colored backgrounds
- Clear reporting relationships (boss → subordinate)
- Top-to-bottom hierarchical layout
"""

from typing import Dict, List
from pathlib import Path
from models import Character
from collections import defaultdict
import json


def generate_org_chart(
    characters: Dict[str, Character],
    output_path: Path
) -> None:
    """Generate interactive HTML organizational chart.

    Args:
        characters: Dict of character name to Character object
        output_path: Path to write HTML file
    """
    # Infer hierarchy and departments
    hierarchy = _infer_hierarchy(characters)
    departments = _infer_departments(characters)

    # Build org chart data
    nodes = _build_nodes(characters, hierarchy, departments)

    # Generate HTML (no edges - tier bands and department boxes show structure)
    html = _generate_org_chart_html(nodes, departments, hierarchy)

    # Write to file
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated org chart: {output_path}")


def _infer_hierarchy(characters: Dict[str, Character]) -> Dict[str, int]:
    """Infer organizational hierarchy tier from role titles and names.

    Returns dict of character_name -> tier (1=highest, 4=lowest)
    """
    hierarchy = {}

    for name, char in characters.items():
        role = char.role.lower()
        name_lower = name.lower()

        # Tier 1: Directors and Station Command
        if 'director' in role or 'station manager' in role or 'commander' in role:
            tier = 1
        # Tier 2: Department heads, Professors, Lead/Chief positions
        elif any(x in role for x in ['lead', 'chief', 'head']) or name_lower.startswith('prof.'):
            tier = 2
        # Tier 3: Doctors, Senior staff, Specialists
        elif any(x in role for x in ['dr.', 'doctor', 'senior', 'specialist']) or name_lower.startswith('dr.'):
            tier = 3
        # Tier 4: Everyone else
        else:
            tier = 4

        hierarchy[name] = tier

    return hierarchy


def _infer_departments(characters: Dict[str, Character]) -> Dict[str, List[str]]:
    """Infer department groupings from role titles.

    Returns dict of department_name -> list of character names
    Each person is assigned to exactly ONE department.
    """
    departments = defaultdict(list)

    for name, char in characters.items():
        role = char.role.lower()

        # Department inference based on role keywords (order matters - most specific first)
        # Check specific department keywords before generic ones
        if any(x in role for x in ['communication', 'radio', 'comms']):
            dept = 'Communications'
        elif any(x in role for x in ['medical', 'doctor', 'physician', 'nurse', 'medic']):
            dept = 'Medical'
        elif any(x in role for x in ['science', 'scientist', 'research', 'biologist', 'chemist', 'physicist']):
            dept = 'Science'
        elif any(x in role for x in ['engineer', 'technical', 'mechanic', 'maintenance']):
            dept = 'Engineering'
        elif any(x in role for x in ['logistics', 'supply', 'quartermaster']):
            dept = 'Logistics'
        elif any(x in role for x in ['director', 'station manager', 'administrator', 'admin']):
            dept = 'Administration'
        elif any(x in role for x in ['security', 'guard', 'officer']):
            # Generic "officer" comes after specific department officers
            dept = 'Security'
        else:
            dept = 'Other'

        departments[dept].append(name)

    return dict(departments)


def _get_character_department(name: str, departments: Dict[str, List[str]]) -> str:
    """Get department for a character."""
    for dept, members in departments.items():
        if name in members:
            return dept
    return 'Other'


def _get_department_colors() -> Dict[str, str]:
    """Get color mapping for departments."""
    return {
        'Medical': '#2ecc71',
        'Science': '#3498db',
        'Engineering': '#e67e22',
        'Security': '#e74c3c',
        'Communications': '#9b59b6',
        'Logistics': '#f39c12',
        'Administration': '#34495e',
        'Other': '#95a5a6'
    }


def _get_nationality_colors(characters: Dict[str, Character]) -> Dict[str, str]:
    """Generate color mapping for nationalities."""
    unique_nationalities = sorted(set(char.nationality for char in characters.values()))

    # Predefined color palette
    colors = [
        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
        '#1abc9c', '#e67e22', '#34495e', '#16a085', '#27ae60',
        '#2980b9', '#8e44ad', '#2c3e50', '#f1c40f', '#d35400',
        '#c0392b', '#7f8c8d', '#bdc3c7', '#95a5a6', '#ecf0f1'
    ]

    return {nat: colors[i % len(colors)] for i, nat in enumerate(unique_nationalities)}


def _build_nodes(
    characters: Dict[str, Character],
    hierarchy: Dict[str, int],
    departments: Dict[str, List[str]]
) -> List[Dict]:
    """Build node data for org chart."""
    nodes = []
    nationality_colors = _get_nationality_colors(characters)
    dept_colors = _get_department_colors()

    for i, (name, char) in enumerate(characters.items()):
        tier = hierarchy.get(name, 4)
        dept = _get_character_department(name, departments)

        node = {
            'id': i,
            'name': name,
            'role': char.role,
            'tier': tier,
            'department': dept,
            'nationality': char.nationality,
            'color': nationality_colors.get(char.nationality, '#95a5a6'),
            'border_color': dept_colors.get(dept, '#95a5a6'),
            'is_dead': char.is_dead(),
            'death_scene': char.death_scene if char.is_dead() else None
        }
        nodes.append(node)

    return nodes


def _generate_org_chart_html(
    nodes: List[Dict],
    departments: Dict[str, List[str]],
    hierarchy: Dict[str, int]
) -> str:
    """Generate HTML for org chart visualization."""

    nodes_json = json.dumps(nodes)
    dept_colors = _get_department_colors()

    # Count by tier
    tier_counts = defaultdict(int)
    for name, tier in hierarchy.items():
        tier_counts[tier] += 1

    # Department sizes
    dept_sizes = sorted(
        [(dept, len(members)) for dept, members in departments.items()],
        key=lambda x: x[1],
        reverse=True
    )

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organizational Chart - Antarctic Mystery</title>
    <script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <style>
{_get_org_chart_css()}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 Organizational Chart</h1>
        <p class="subtitle">Antarctic Station Alpha-7 - Hierarchical Structure by Tier & Department</p>

        <!-- Network Visualization -->
        <div id="network"></div>

        <!-- Statistics Panel -->
        <div class="stats-panel">
            <h3>Organization Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">{len(nodes)}</div>
                    <div class="stat-label">Total Staff</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(departments)}</div>
                    <div class="stat-label">Departments</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">4</div>
                    <div class="stat-label">Hierarchy Levels</div>
                </div>
            </div>

            <h4>Hierarchy Tiers</h4>
            <ul>
                <li>Tier 1 (Station Leadership): {tier_counts.get(1, 0)} people</li>
                <li>Tier 2 (Department Heads): {tier_counts.get(2, 0)} people</li>
                <li>Tier 3 (Senior Staff): {tier_counts.get(3, 0)} people</li>
                <li>Tier 4 (General Staff): {tier_counts.get(4, 0)} people</li>
            </ul>

            <h4>Departments</h4>
            <div class="dept-list">
'''

    for dept, count in dept_sizes:
        color = dept_colors.get(dept, '#95a5a6')
        html += f'                <div class="dept-item"><span class="color-box" style="background:{color}"></span>{dept}: {count}</div>\n'

    html += '''            </div>
        </div>

        <!-- Legend -->
        <div class="legend">
            <h3>Legend</h3>

            <div class="legend-section">
                <h4>Hierarchy Levels (Horizontal Bands)</h4>
                <div><strong>Tier 1</strong> - Station Leadership (Directors, Commanders)</div>
                <div><strong>Tier 2</strong> - Department Heads (Professors, Chief Officers)</div>
                <div><strong>Tier 3</strong> - Senior Staff (Doctors, Specialists)</div>
                <div><strong>Tier 4</strong> - General Staff</div>
            </div>

            <div class="legend-section">
                <h4>Departments (Vertical Grouping)</h4>
                <div><span class="color-box" style="background:#2ecc71"></span>Medical</div>
                <div><span class="color-box" style="background:#3498db"></span>Science</div>
                <div><span class="color-box" style="background:#e67e22"></span>Engineering</div>
                <div><span class="color-box" style="background:#e74c3c"></span>Security</div>
                <div><span class="color-box" style="background:#9b59b6"></span>Communications</div>
                <div><span class="color-box" style="background:#f39c12"></span>Logistics</div>
                <div><span class="color-box" style="background:#34495e"></span>Administration</div>
                <div><span class="color-box" style="background:#95a5a6"></span>Other</div>
            </div>

            <div class="legend-section">
                <h4>Visual Elements</h4>
                <div>■ <strong>Box Shape</strong> = Station Leadership (Tier 1)</div>
                <div>● <strong>Circle Shape</strong> = All other staff</div>
                <div><strong>Border Color</strong> = Department</div>
                <div><strong>Fill Color</strong> = Nationality</div>
                <div><strong>Horizontal Bands</strong> = Hierarchy tiers (top to bottom)</div>
                <div><strong>Colored Boxes</strong> = Department grouping</div>
            </div>
        </div>
    </div>

    <script>
        // Network data
        const nodesData = ''' + nodes_json + ''';

        // Convert to vis.js format
        const visNodes = nodesData.map(node => ({
            id: node.id,
            label: node.name,
            title: `${node.name}\\n${node.role}\\nTier ${node.tier} - ${node.department}\\nNationality: ${node.nationality}` +
                   (node.is_dead ? `\\n☠ Died in scene ${node.death_scene}` : ''),
            color: {
                background: node.color,
                border: node.border_color
            },
            size: 40 - (node.tier * 8),  // Tier 1=32, Tier 4=8
            shape: node.tier === 1 ? 'box' : 'dot',
            borderWidth: 3,
            font: { size: 12 },
            level: node.tier,  // Explicit level for hierarchical layout
            group: node.department
        }));

        const nodes = new vis.DataSet(visNodes);

        // Create network (no edges - structure shown by tier bands and department boxes)
        const container = document.getElementById('network');
        const data = { nodes: nodes };
        const options = {
            layout: {
                hierarchical: {
                    enabled: false  // Disabled - we position nodes manually
                }
            },
            physics: {
                enabled: false  // Disable physics for manual positioning
            },
            interaction: {
                hover: true,
                navigationButtons: true,
                keyboard: true,
                zoomView: true,
                dragView: true
            },
            nodes: {
                font: {
                    size: 14,
                    color: '#2c3e50'
                }
            }
        };

        const network = new vis.Network(container, data, options);

        // Manually position nodes by tier and department to prevent overlap
        const departmentOrder = ['Administration', 'Medical', 'Science', 'Engineering', 'Security', 'Communications', 'Logistics', 'Other'];
        const tierY = {
            1: -300,  // Top
            2: -100,
            3: 100,
            4: 300    // Bottom
        };
        const nodeSpacing = 100;   // Spacing between nodes in same dept/tier

        // First pass: Calculate how many nodes each department has in each tier
        const deptTierCounts = {};
        const deptTierGroups = {};
        nodes.forEach(node => {
            const dept = node.group;
            const tier = node.level;
            const key = `${dept}_${tier}`;
            if (!deptTierGroups[key]) {
                deptTierGroups[key] = [];
            }
            deptTierGroups[key].push(node);

            if (!deptTierCounts[dept]) {
                deptTierCounts[dept] = 0;
            }
            // Track max nodes in any single tier for this department
            deptTierCounts[dept] = Math.max(deptTierCounts[dept], deptTierGroups[key].length);
        });

        // Calculate required width for each department
        const deptWidths = {};
        departmentOrder.forEach(dept => {
            const maxNodesInTier = deptTierCounts[dept] || 1;
            // Width = nodes * spacing + padding on both sides
            const requiredWidth = maxNodesInTier * nodeSpacing + 80;
            deptWidths[dept] = requiredWidth;
        });

        // Calculate department X positions ensuring no overlap
        const deptBaseX = {};
        let currentX = 0;
        departmentOrder.forEach(dept => {
            deptBaseX[dept] = currentX;
            currentX += deptWidths[dept] + 60; // Add 60px gap between departments
        });

        // Center the entire chart
        const totalWidth = currentX - 60; // Subtract last gap
        const offset = -totalWidth / 2;
        Object.keys(deptBaseX).forEach(dept => {
            deptBaseX[dept] += offset + deptWidths[dept] / 2; // Center of department
        });

        // Position each node within its department
        nodes.forEach(node => {
            const dept = node.group;
            const tier = node.level;
            const key = `${dept}_${tier}`;
            const groupNodes = deptTierGroups[key];
            const indexInGroup = groupNodes.indexOf(node);
            const groupSize = groupNodes.length;

            // X position: centered within department, spread horizontally
            const offsetX = (indexInGroup - (groupSize - 1) / 2) * nodeSpacing;
            const x = deptBaseX[dept] + offsetX;

            // Y position: based on tier
            const y = tierY[tier];

            // Update node position
            network.moveNode(node.id, x, y);
        });

        // Department clustering configuration
        const departmentColors = {
            'Medical': 'rgba(46, 204, 113, 0.15)',
            'Science': 'rgba(52, 152, 219, 0.15)',
            'Engineering': 'rgba(230, 126, 34, 0.15)',
            'Security': 'rgba(231, 76, 60, 0.15)',
            'Communications': 'rgba(155, 89, 182, 0.15)',
            'Logistics': 'rgba(243, 156, 18, 0.15)',
            'Administration': 'rgba(52, 73, 94, 0.15)',
            'Other': 'rgba(149, 165, 166, 0.15)'
        };

        // Tier band colors
        const tierBandColors = [
            'rgba(230, 126, 34, 0.08)',  // Tier 1 - Orange tint
            'rgba(52, 152, 219, 0.08)',  // Tier 2 - Blue tint
            'rgba(46, 204, 113, 0.08)',  // Tier 3 - Green tint
            'rgba(149, 165, 166, 0.08)'  // Tier 4 - Gray tint
        ];

        let networkReady = false;

        // Wait for network to be ready before enabling custom drawing
        network.once('afterDrawing', function() {
            networkReady = true;
            network.redraw();
        });

        // Custom rendering for tier bands and department backgrounds
        network.on('beforeDrawing', function(ctx) {
            if (!networkReady) return;
            // Get canvas dimensions
            const canvasWidth = ctx.canvas.width;

            // Group nodes by tier and department
            const tierGroups = { 1: [], 2: [], 3: [], 4: [] };
            const departmentGroups = {};
            const allPositions = []; // Track all positions for calculating overall bounds

            nodes.forEach(node => {
                const pos = network.getPositions([node.id])[node.id];
                if (pos) {
                    const nodeData = {
                        x: pos.x,
                        y: pos.y,
                        tier: node.level,
                        dept: node.group,
                        size: node.size || 20
                    };

                    allPositions.push(nodeData);

                    // Add to tier group
                    if (tierGroups[node.level]) {
                        tierGroups[node.level].push(nodeData);
                    }

                    // Add to department group
                    if (!departmentGroups[node.group]) {
                        departmentGroups[node.group] = [];
                    }
                    departmentGroups[node.group].push(nodeData);
                }
            });

            // Calculate overall X boundaries for all tier bands (so they align)
            const allXs = allPositions.map(p => p.x);
            const overallMinX = Math.min(...allXs) - 200;
            const overallMaxX = Math.max(...allXs) + 200;

            // Draw horizontal bands for each tier (all with same X boundaries)
            Object.keys(tierGroups).forEach(tier => {
                const positions = tierGroups[tier];
                if (positions.length === 0) return;

                const tierNum = parseInt(tier);
                const ys = positions.map(p => p.y);
                const minY = Math.min(...ys) - 80;
                const maxY = Math.max(...ys) + 80;

                // Use overall X boundaries so all tier bands are left-aligned
                const minX = overallMinX;
                const maxX = overallMaxX;

                // Draw full-width horizontal band
                ctx.fillStyle = tierBandColors[tierNum - 1];
                ctx.fillRect(minX, minY, maxX - minX, maxY - minY);

                // Draw tier label on left side
                ctx.fillStyle = 'rgba(44, 62, 80, 0.7)';
                ctx.font = 'bold 16px Arial';
                ctx.textAlign = 'right';
                ctx.textBaseline = 'middle';
                const tierLabels = ['Tier 1: Leadership', 'Tier 2: Dept Heads', 'Tier 3: Senior Staff', 'Tier 4: General Staff'];
                ctx.fillText(tierLabels[tierNum - 1], minX - 10, (minY + maxY) / 2);
            });

            // Draw department backgrounds (on top of tier bands)
            // Use dynamic widths that fit all nodes, ensuring no overlap
            const departmentOrder = ['Administration', 'Medical', 'Science', 'Engineering', 'Security', 'Communications', 'Logistics', 'Other'];

            departmentOrder.forEach((dept) => {
                // Check if this department has any people
                if (!departmentGroups[dept] || departmentGroups[dept].length === 0) return;

                const positions = departmentGroups[dept];

                // Get actual bounding box from node positions (with generous padding)
                const xs = positions.map(p => p.x);
                const ys = positions.map(p => p.y);
                const padding = 50;
                const minX = Math.min(...xs) - padding;
                const maxX = Math.max(...xs) + padding;
                const minY = Math.min(...ys) - 60;
                const maxY = Math.max(...ys) + 60;

                // Draw rounded rectangle background
                ctx.fillStyle = departmentColors[dept] || 'rgba(200, 200, 200, 0.15)';
                ctx.strokeStyle = departmentColors[dept].replace('0.15', '0.5') || 'rgba(200, 200, 200, 0.5)';
                ctx.lineWidth = 2;

                const radius = 15;
                ctx.beginPath();
                ctx.moveTo(minX + radius, minY);
                ctx.lineTo(maxX - radius, minY);
                ctx.quadraticCurveTo(maxX, minY, maxX, minY + radius);
                ctx.lineTo(maxX, maxY - radius);
                ctx.quadraticCurveTo(maxX, maxY, maxX - radius, maxY);
                ctx.lineTo(minX + radius, maxY);
                ctx.quadraticCurveTo(minX, maxY, minX, maxY - radius);
                ctx.lineTo(minX, minY + radius);
                ctx.quadraticCurveTo(minX, minY, minX + radius, minY);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Draw department label at top center of box
                ctx.fillStyle = departmentColors[dept].replace('0.15', '0.9') || 'rgba(52, 73, 94, 0.9)';
                ctx.font = 'bold 18px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';
                ctx.fillText(dept, (minX + maxX) / 2, minY - 10);
            });
        });

        // Fit to view after initial render (physics disabled, no stabilization needed)
        setTimeout(function() {
            network.fit({ animation: { duration: 1000 } });
        }, 100);
    </script>
</body>
</html>'''

    return html


def _get_org_chart_css() -> str:
    """Get CSS styles for org chart."""
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
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2em;
        }

        h3 {
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 10px;
        }

        h4 {
            color: #7f8c8d;
            margin-top: 15px;
            margin-bottom: 8px;
            font-size: 0.9em;
        }

        .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 20px;
        }

        #network {
            width: 100%;
            height: 800px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            margin-bottom: 20px;
            background: #fafafa;
        }

        .stats-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid #3498db;
        }

        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }

        .stat-label {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }

        .dept-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }

        .dept-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            background: white;
            border-radius: 4px;
        }

        .legend {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
        }

        .legend-section {
            margin-bottom: 15px;
        }

        .color-box {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 1px solid #333;
            border-radius: 3px;
            margin-right: 8px;
            vertical-align: middle;
        }

        ul {
            list-style: none;
            padding-left: 0;
        }

        ul li {
            padding: 5px 0;
            color: #495057;
        }

        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            #network {
                height: 600px;
            }
        }
    '''
