"""Relationship network visualization showing professional, family, and killer connections.

Generates an interactive HTML network graph combining:
- Professional hierarchy (org chart structure)
- Family relationships (inferred from names)
- Nationality clustering
- Department grouping
- Killer → victim edges
"""

from typing import Dict, List, Set, Tuple
from pathlib import Path
from models import Character
import networkx as nx
from collections import defaultdict


def generate_relationship_network(
    characters: Dict[str, Character],
    output_path: Path
) -> None:
    """Generate interactive HTML relationship network.

    Args:
        characters: Dict of character name to Character object
        output_path: Path to write HTML file
    """
    # Infer relationships from data
    families = _infer_family_relationships(characters)
    hierarchy = _infer_hierarchy(characters)
    departments = _infer_departments(characters)
    nationalities = _get_nationality_groups(characters)

    # Build NetworkX graph with all relationship types
    G = _build_relationship_graph(characters, families, hierarchy, departments)

    # Calculate statistics
    stats = _calculate_relationship_stats(G, families, hierarchy, departments, nationalities)

    # Generate HTML
    html = _generate_relationship_html(G, characters, families, hierarchy, departments, stats)

    # Write to file
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated relationship network: {output_path}")
    print(f"  - Total characters: {G.number_of_nodes()}")
    print(f"  - Family connections: {len(families)} families")
    print(f"  - Departments: {len(departments)} departments")
    print(f"  - Nationalities: {len(nationalities)} nationalities")


def _infer_family_relationships(characters: Dict[str, Character]) -> Dict[str, List[str]]:
    """Infer family relationships from character names.

    Returns dict of family_name -> list of character names
    """
    families = defaultdict(list)

    for name, char in characters.items():
        # Split name into parts
        parts = name.split()

        if len(parts) >= 2:
            last_name = parts[-1]

            # Check for hyphenated names (married)
            if '-' in last_name:
                # Add to both families
                family_names = last_name.split('-')
                for family_name in family_names:
                    families[family_name].append(name)
            else:
                # Regular last name
                families[last_name].append(name)

    # Only keep families with 2+ members
    return {family: members for family, members in families.items() if len(members) > 1}


def _infer_hierarchy(characters: Dict[str, Character]) -> Dict[str, int]:
    """Infer organizational hierarchy tier from role titles.

    Returns dict of character_name -> tier (1=highest, 4=lowest)
    """
    hierarchy = {}

    for name, char in characters.items():
        role = char.role.lower()

        # Tier 1: Directors and Station Command
        if 'director' in role or 'station' in role or 'commander' in role:
            tier = 1
        # Tier 2: Department heads, Professors, Lead/Chief positions
        elif any(x in role for x in ['prof.', 'professor', 'lead', 'chief', 'head']):
            tier = 2
        # Tier 3: Doctors, Senior staff, Specialists
        elif any(x in role for x in ['dr.', 'doctor', 'senior', 'specialist']):
            tier = 3
        # Tier 4: Everyone else
        else:
            tier = 4

        hierarchy[name] = tier

    return hierarchy


def _infer_departments(characters: Dict[str, Character]) -> Dict[str, List[str]]:
    """Infer department groupings from role titles.

    Returns dict of department_name -> list of character names
    """
    departments = defaultdict(list)

    for name, char in characters.items():
        role = char.role.lower()

        # Department inference based on role keywords
        if any(x in role for x in ['medical', 'doctor', 'physician', 'nurse', 'medic']):
            dept = 'Medical'
        elif any(x in role for x in ['science', 'scientist', 'research', 'biologist', 'chemist', 'physicist']):
            dept = 'Science'
        elif any(x in role for x in ['engineer', 'technical', 'mechanic', 'maintenance']):
            dept = 'Engineering'
        elif any(x in role for x in ['security', 'guard', 'officer']):
            dept = 'Security'
        elif any(x in role for x in ['communication', 'radio', 'comms']):
            dept = 'Communications'
        elif any(x in role for x in ['logistics', 'supply', 'quartermaster']):
            dept = 'Logistics'
        elif any(x in role for x in ['director', 'station', 'administrator', 'admin']):
            dept = 'Administration'
        else:
            dept = 'Other'

        departments[dept].append(name)

    return dict(departments)


def _get_nationality_groups(characters: Dict[str, Character]) -> Dict[str, List[str]]:
    """Group characters by nationality.

    Returns dict of nationality -> list of character names
    """
    nationalities = defaultdict(list)

    for name, char in characters.items():
        nationalities[char.nationality].append(name)

    return dict(nationalities)


def _build_relationship_graph(
    characters: Dict[str, Character],
    families: Dict[str, List[str]],
    hierarchy: Dict[str, int],
    departments: Dict[str, List[str]]
) -> nx.Graph:
    """Build multi-layer NetworkX graph with all relationship types."""
    G = nx.Graph()

    # Add all characters as nodes with attributes
    for name, char in characters.items():
        G.add_node(
            name,
            role=char.role,
            nationality=char.nationality,
            tier=hierarchy.get(name, 4),
            is_dead=char.is_dead(),
            death_scene=char.death_scene if char.is_dead() else None,
            cause_of_death=char.cause_of_death if char.is_dead() else None,
            killer=char.killer if char.is_dead() else None,
            department=_get_character_department(name, departments)
        )

    # Add family edges
    for family_name, members in families.items():
        for i, member1 in enumerate(members):
            for member2 in members[i+1:]:
                if member1 in G and member2 in G:
                    G.add_edge(member1, member2, relationship='family', family=family_name)

    # Add professional hierarchy edges (boss → subordinate)
    for name, tier in hierarchy.items():
        if tier < 4:  # Not lowest tier
            # Find potential subordinates in same department
            char_dept = G.nodes[name].get('department')
            for other_name, other_tier in hierarchy.items():
                if other_name != name and other_tier == tier + 1:
                    other_dept = G.nodes[other_name].get('department')
                    # Connect if same department or if this is a director
                    if char_dept == other_dept or tier == 1:
                        G.add_edge(name, other_name, relationship='professional')

    # Add killer edges (directed, but stored in undirected graph with metadata)
    for name, char in characters.items():
        if char.is_dead() and char.killer and char.killer != "Accident":
            if char.killer in G:
                G.add_edge(
                    char.killer,
                    name,
                    relationship='killer',
                    scene=char.death_scene,
                    method=char.cause_of_death
                )

    return G


def _get_character_department(name: str, departments: Dict[str, List[str]]) -> str:
    """Get department for a character."""
    for dept, members in departments.items():
        if name in members:
            return dept
    return 'Other'


def _calculate_relationship_stats(
    G: nx.Graph,
    families: Dict[str, List[str]],
    hierarchy: Dict[str, int],
    departments: Dict[str, List[str]],
    nationalities: Dict[str, List[str]]
) -> Dict:
    """Calculate network statistics."""

    # Count edge types
    edge_counts = defaultdict(int)
    for u, v, data in G.edges(data=True):
        edge_counts[data.get('relationship', 'unknown')] += 1

    # Count by tier
    tier_counts = defaultdict(int)
    for name, tier in hierarchy.items():
        tier_counts[tier] += 1

    # Largest families
    largest_families = sorted(
        [(family, len(members)) for family, members in families.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    # Department sizes
    dept_sizes = sorted(
        [(dept, len(members)) for dept, members in departments.items()],
        key=lambda x: x[1],
        reverse=True
    )

    # Nationality distribution
    nationality_dist = sorted(
        [(nat, len(members)) for nat, members in nationalities.items()],
        key=lambda x: x[1],
        reverse=True
    )

    return {
        'edge_counts': dict(edge_counts),
        'tier_counts': dict(tier_counts),
        'largest_families': largest_families,
        'dept_sizes': dept_sizes,
        'nationality_dist': nationality_dist,
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
    }


def _generate_relationship_html(
    G: nx.Graph,
    characters: Dict[str, Character],
    families: Dict[str, List[str]],
    hierarchy: Dict[str, int],
    departments: Dict[str, List[str]],
    stats: Dict
) -> str:
    """Generate HTML with vis.js interactive network."""

    # Get nationality color mapping
    nationality_colors = _get_nationality_colors(characters)
    department_colors = _get_department_colors()

    # Convert graph to vis.js format
    vis_nodes = []
    node_id_map = {}

    for i, (name, data) in enumerate(G.nodes(data=True)):
        node_id_map[name] = i

        # Node color based on nationality
        color = nationality_colors.get(data['nationality'], '#95a5a6')

        # Node size based on hierarchy tier (higher tier = larger)
        size = 40 - (data['tier'] * 8)  # Tier 1=32, Tier 4=8

        # Node shape based on tier (leadership gets boxes)
        shape = 'box' if data['tier'] <= 1 else 'dot'

        # Border color shows department (not death status since everyone dies)
        dept_colors = _get_department_colors()
        dept = data['department']
        border_color = dept_colors.get(dept, '#95a5a6')
        border_width = 3

        # Build title (tooltip)
        title = f"{name}\n{data['role']}\nTier {data['tier']} - {data['department']}\nNationality: {data['nationality']}"
        if data['is_dead']:
            title += f"\n☠ Died in scene {data['death_scene']}"

        vis_nodes.append({
            'id': i,
            'label': name,
            'title': title,
            'color': {
                'background': color,
                'border': border_color
            },
            'size': size,
            'shape': shape,
            'borderWidth': border_width,
            'font': {'size': 12},
            'group': dept,  # Group nodes by department for visual clustering
            'level': data['tier'],  # Explicit hierarchy level for better layout
        })

    # Convert edges to vis.js format
    vis_edges = []
    for u, v, data in G.edges(data=True):
        rel_type = data.get('relationship', 'unknown')

        if rel_type == 'family':
            # Family edges: thick red/pink
            edge = {
                'from': node_id_map[u],
                'to': node_id_map[v],
                'color': {'color': '#e74c3c', 'opacity': 0.6},
                'width': 3,
                'title': f"Family: {data.get('family', 'Unknown')}",
                'group': 'family'
            }
        elif rel_type == 'professional':
            # Professional edges: blue lines
            edge = {
                'from': node_id_map[u],
                'to': node_id_map[v],
                'color': {'color': '#3498db', 'opacity': 0.4},
                'width': 2,
                'dashes': False,
                'title': 'Professional relationship',
                'group': 'professional'
            }
        elif rel_type == 'killer':
            # Killer edges: red dashed with arrow
            edge = {
                'from': node_id_map[u],
                'to': node_id_map[v],
                'color': {'color': '#c0392b'},
                'width': 3,
                'dashes': [5, 5],
                'arrows': {'to': {'enabled': True, 'scaleFactor': 1.2}},
                'title': f"Killed in scene {data.get('scene', '?')} - {data.get('method', 'Unknown')}",
                'group': 'killer'
            }
        else:
            continue

        vis_edges.append(edge)

    # Build HTML
    html = _build_html_template(
        vis_nodes,
        vis_edges,
        stats,
        nationality_colors,
        department_colors,
        G,
        characters
    )

    return html


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


def _build_html_template(
    vis_nodes: List[Dict],
    vis_edges: List[Dict],
    stats: Dict,
    nationality_colors: Dict[str, str],
    department_colors: Dict[str, str],
    G: nx.Graph,
    characters: Dict[str, Character]
) -> str:
    """Build complete HTML document."""

    import json

    nodes_json = json.dumps(vis_nodes)
    edges_json = json.dumps(vis_edges)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relationship Network - Antarctic Mystery</title>
    <script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <style>
{_get_relationship_css()}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Relationship Network</h1>
        <p class="subtitle">Antarctic Station Alpha-7 - Professional, Family & Killer Connections</p>

        <!-- View Mode Controls -->
        <div class="controls">
            <h3>View Mode:</h3>
            <div class="button-group">
                <button id="viewAll" class="btn active">📊 Full View</button>
                <button id="viewOrg" class="btn">🏢 Org Chart</button>
                <button id="viewFamily" class="btn">👨‍👩‍👧 Family</button>
                <button id="viewDept" class="btn">🏭 Departments</button>
                <button id="viewNationality" class="btn">🌍 Nationality</button>
                <button id="viewKiller" class="btn">💀 Killers</button>
            </div>

            <h3>Show/Hide Edges:</h3>
            <div class="checkbox-group">
                <label><input type="checkbox" id="showProfessional" checked> Reporting (boss→subordinate)</label>
                <label><input type="checkbox" id="showFamily" checked> Family</label>
                <label><input type="checkbox" id="showKiller" checked> Killer</label>
            </div>
        </div>

        <!-- Network Visualization -->
        <div id="network"></div>

        <!-- Statistics Panel -->
        <div class="stats-panel">
            <h3>Network Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">{stats['total_nodes']}</div>
                    <div class="stat-label">Characters</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{stats['edge_counts'].get('family', 0)}</div>
                    <div class="stat-label">Family Connections</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{stats['edge_counts'].get('professional', 0)}</div>
                    <div class="stat-label">Professional Links</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{stats['edge_counts'].get('killer', 0)}</div>
                    <div class="stat-label">Murders</div>
                </div>
            </div>

            <h4>Departments</h4>
            <div class="dept-list">
'''

    for dept, count in stats['dept_sizes']:
        color = department_colors.get(dept, '#95a5a6')
        html += f'                <div class="dept-item"><span class="color-box" style="background:{color}"></span>{dept}: {count}</div>\n'

    html += '''            </div>

            <h4>Hierarchy Tiers</h4>
            <ul>
                <li>Tier 1 (Leadership): ''' + str(stats['tier_counts'].get(1, 0)) + '''</li>
                <li>Tier 2 (Department Heads): ''' + str(stats['tier_counts'].get(2, 0)) + '''</li>
                <li>Tier 3 (Senior Staff): ''' + str(stats['tier_counts'].get(3, 0)) + '''</li>
                <li>Tier 4 (Staff): ''' + str(stats['tier_counts'].get(4, 0)) + '''</li>
            </ul>
'''

    if stats['largest_families']:
        html += '            <h4>Families</h4>\n            <ul>\n'
        for family, count in stats['largest_families']:
            html += f'                <li>{family}: {count} members</li>\n'
        html += '            </ul>\n'

    html += '''        </div>

        <!-- Legend -->
        <div class="legend">
            <h3>Legend</h3>
            <div class="legend-section">
                <h4>Node Colors (Nationality)</h4>
                <div class="legend-grid">
'''

    for nat, color in sorted(nationality_colors.items()):
        html += f'                    <div><span class="color-box" style="background:{color}"></span>{nat}</div>\n'

    html += '''                </div>
            </div>

            <div class="legend-section">
                <h4>Node Borders (Department)</h4>
                <div><span class="color-box" style="background:#2ecc71"></span>Medical</div>
                <div><span class="color-box" style="background:#3498db"></span>Science</div>
                <div><span class="color-box" style="background:#e67e22"></span>Engineering</div>
                <div><span class="color-box" style="background:#e74c3c"></span>Security</div>
                <div><span class="color-box" style="background:#9b59b6"></span>Communications</div>
                <div><span class="color-box" style="background:#34495e"></span>Administration</div>
                <div><span class="color-box" style="background:#95a5a6"></span>Other</div>
            </div>

            <div class="legend-section">
                <h4>Hierarchy (Size & Shape)</h4>
                <div>■ Large Box = Station Leadership (Tier 1)</div>
                <div>● Large Circle = Dept Heads/Professors (Tier 2)</div>
                <div>● Medium Circle = Doctors/Specialists (Tier 3)</div>
                <div>● Small Circle = General Staff (Tier 4)</div>
                <p style="margin-top:8px; font-size:0.9em; font-style:italic;">In Org Chart view: Leadership at top → Staff below</p>
            </div>

            <div class="legend-section">
                <h4>Edge Types</h4>
                <div><span style="color:#e74c3c;">—</span> Family Connection</div>
                <div><span style="color:#3498db;">—</span> Reporting Relationship (boss → subordinate)</div>
                <div><span style="color:#c0392b;">⤍</span> Killer → Victim</div>
            </div>
        </div>
    </div>

    <script>
        // Network data
        const nodes = new vis.DataSet(''' + nodes_json + ''');
        const edges = new vis.DataSet(''' + edges_json + ''');

        // Create network
        const container = document.getElementById('network');
        const data = { nodes: nodes, edges: edges };
        const options = {
            physics: {
                enabled: true,
                hierarchicalRepulsion: {
                    nodeDistance: 150,
                    centralGravity: 0.2,
                },
                solver: 'hierarchicalRepulsion',
            },
            layout: {
                improvedLayout: true,
                hierarchical: {
                    enabled: false,
                    direction: 'UD',  // Up-down (leadership at top)
                    sortMethod: 'directed',
                    nodeSpacing: 350,  // Increased horizontal spacing to prevent overlap
                    levelSeparation: 250,  // Vertical spacing between tiers
                    treeSpacing: 400,  // Spacing between separate department trees
                    blockShifting: true,  // Better department separation
                    edgeMinimization: true,  // Cleaner edge routing
                    parentCentralization: false,  // Allow separate trees per department
                    shakeTowards: 'leaves',  // Push nodes toward leaves (downward)
                }
            },
            interaction: {
                hover: true,
                navigationButtons: true,
                keyboard: true,
            },
            nodes: {
                font: {
                    size: 14,
                    color: '#2c3e50'
                }
            }
        };

        const network = new vis.Network(container, data, options);

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

        let orgChartMode = false;

        // Custom rendering for department backgrounds in org chart mode
        network.on('beforeDrawing', function(ctx) {
            if (!orgChartMode) return;

            // Get positions of all nodes grouped by department
            const departmentGroups = {};
            nodes.forEach(node => {
                const dept = node.group || 'Other';
                if (!departmentGroups[dept]) {
                    departmentGroups[dept] = [];
                }
                const pos = network.getPositions([node.id])[node.id];
                if (pos) {
                    departmentGroups[dept].push({
                        x: pos.x,
                        y: pos.y,
                        size: node.size || 20
                    });
                }
            });

            // Draw background rectangles for each department
            Object.keys(departmentGroups).forEach(dept => {
                const positions = departmentGroups[dept];
                if (positions.length === 0) return;

                // Calculate bounding box for this department
                const padding = 60;
                const xs = positions.map(p => p.x);
                const ys = positions.map(p => p.y);
                const minX = Math.min(...xs) - padding;
                const maxX = Math.max(...xs) + padding;
                const minY = Math.min(...ys) - padding;
                const maxY = Math.max(...ys) + padding;

                // Draw rounded rectangle background
                ctx.fillStyle = departmentColors[dept] || 'rgba(200, 200, 200, 0.15)';
                ctx.strokeStyle = departmentColors[dept].replace('0.15', '0.4') || 'rgba(200, 200, 200, 0.4)';
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

                // Draw department label at top of bounding box
                ctx.fillStyle = departmentColors[dept].replace('0.15', '0.8') || 'rgba(52, 73, 94, 0.8)';
                ctx.font = 'bold 18px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(dept, (minX + maxX) / 2, minY - 20);
            });
        });

        // View mode switching
        document.getElementById('viewAll').addEventListener('click', function() {
            setActiveButton(this);
            showAllEdges();
            orgChartMode = false;
            options.layout.hierarchical.enabled = false;
            network.setOptions(options);
            network.redraw();
        });

        document.getElementById('viewOrg').addEventListener('click', function() {
            setActiveButton(this);
            hideEdgeGroup('family');
            hideEdgeGroup('killer');
            showEdgeGroup('professional');
            orgChartMode = true;
            options.layout.hierarchical.enabled = true;
            network.setOptions(options);
            network.redraw();
        });

        document.getElementById('viewFamily').addEventListener('click', function() {
            setActiveButton(this);
            hideEdgeGroup('professional');
            hideEdgeGroup('killer');
            showEdgeGroup('family');
            orgChartMode = false;
            options.layout.hierarchical.enabled = false;
            network.setOptions(options);
            network.redraw();
        });

        document.getElementById('viewDept').addEventListener('click', function() {
            setActiveButton(this);
            showEdgeGroup('professional');
            hideEdgeGroup('family');
            hideEdgeGroup('killer');
            orgChartMode = true;
            options.layout.hierarchical.enabled = true;
            network.setOptions(options);
            network.redraw();
        });

        document.getElementById('viewNationality').addEventListener('click', function() {
            setActiveButton(this);
            hideAllEdges();
            orgChartMode = false;
            options.layout.hierarchical.enabled = false;
            network.setOptions(options);
            network.redraw();
        });

        document.getElementById('viewKiller').addEventListener('click', function() {
            setActiveButton(this);
            hideEdgeGroup('professional');
            hideEdgeGroup('family');
            showEdgeGroup('killer');
            orgChartMode = false;
            options.layout.hierarchical.enabled = false;
            network.setOptions(options);
            network.redraw();
        });

        // Edge toggle checkboxes
        document.getElementById('showProfessional').addEventListener('change', function() {
            if (this.checked) showEdgeGroup('professional');
            else hideEdgeGroup('professional');
        });

        document.getElementById('showFamily').addEventListener('change', function() {
            if (this.checked) showEdgeGroup('family');
            else hideEdgeGroup('family');
        });

        document.getElementById('showKiller').addEventListener('change', function() {
            if (this.checked) showEdgeGroup('killer');
            else hideEdgeGroup('killer');
        });

        // Helper functions
        function setActiveButton(button) {
            document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
            button.classList.add('active');
        }

        function showAllEdges() {
            edges.forEach(edge => edges.update({id: edge.id, hidden: false}));
        }

        function hideAllEdges() {
            edges.forEach(edge => edges.update({id: edge.id, hidden: true}));
        }

        function showEdgeGroup(group) {
            edges.forEach(edge => {
                if (edge.group === group) {
                    edges.update({id: edge.id, hidden: false});
                }
            });
        }

        function hideEdgeGroup(group) {
            edges.forEach(edge => {
                if (edge.group === group) {
                    edges.update({id: edge.id, hidden: true});
                }
            });
        }
    </script>
</body>
</html>'''

    return html


def _get_relationship_css() -> str:
    """Get CSS styles for relationship network."""
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
            max-width: 1600px;
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

        .controls {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }

        .btn {
            padding: 10px 20px;
            border: 2px solid #3498db;
            background: white;
            color: #3498db;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            transition: all 0.2s;
        }

        .btn:hover {
            background: #3498db;
            color: white;
        }

        .btn.active {
            background: #3498db;
            color: white;
        }

        .checkbox-group {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .checkbox-group label {
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
        }

        #network {
            width: 100%;
            height: 700px;
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

        .legend-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 8px;
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
                height: 500px;
            }

            .button-group {
                flex-direction: column;
            }

            .btn {
                width: 100%;
            }
        }
    '''
