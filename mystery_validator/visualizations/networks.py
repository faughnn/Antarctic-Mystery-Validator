"""Network graph visualizations for mystery relationships.

Generates interactive HTML network graphs showing killer-victim relationships,
character co-occurrences, and other connections.
"""

from typing import Dict, List, Set, Tuple
from pathlib import Path
from models import Character
import networkx as nx


def generate_killer_network(
    characters: Dict[str, Character],
    output_path: Path
) -> None:
    """Generate interactive HTML killer network graph using NetworkX.

    Shows:
    - Directed edges from killer → victim
    - Node size = number of kills (larger = serial killer)
    - Red nodes = killers, Gray nodes = pure victims, Yellow = both
    - Edge labels show cause of death and scene number

    Args:
        characters: Dict of character name to Character object
        output_path: Path to write HTML file
    """
    # Build NetworkX directed graph
    G = nx.DiGraph()

    # Add all characters as nodes
    for name in characters:
        G.add_node(name, is_killer=False, is_victim=False, killed_by=None)

    # Build edges from killer → victim relationships
    for char in characters.values():
        if char.is_dead() and char.killer and char.killer != "Accident":
            killer = char.killer
            victim = char.name

            # Only add edge if killer is in our character list
            if killer in characters:
                G.add_edge(
                    killer,
                    victim,
                    scene=char.death_scene,
                    method=char.cause_of_death
                )

                # Update node attributes
                G.nodes[killer]['is_killer'] = True
                G.nodes[victim]['is_victim'] = True
                G.nodes[victim]['killed_by'] = killer

    # Calculate kill counts for each character
    kill_counts = {node: G.out_degree(node) for node in G.nodes()}

    # Add kill count as node attribute
    nx.set_node_attributes(G, kill_counts, 'kills')

    # Calculate statistics using NetworkX
    stats = _calculate_network_stats(G)

    # Generate HTML with vis.js
    html = _generate_network_html(G, stats, characters)

    # Write to file
    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated killer network: {output_path}")
    print(f"  - Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print(f"  - Connected components: {nx.number_weakly_connected_components(G)}")
    if nx.is_directed_acyclic_graph(G):
        print(f"  - Graph is acyclic (no cycles of revenge)")
    else:
        print(f"  - Warning: Graph contains cycles (revenge chains detected)")


def _calculate_network_stats(G: nx.DiGraph) -> Dict:
    """Calculate network statistics using NetworkX."""
    # Get node data
    nodes_data = dict(G.nodes(data=True))

    # Find serial killers (kill count > 1)
    serial_killers = [(name, data['kills']) for name, data in nodes_data.items() if data['kills'] > 1]
    serial_killers.sort(key=lambda x: x[1], reverse=True)

    # Categorize characters
    pure_victims = [name for name, data in nodes_data.items() if data['is_victim'] and not data['is_killer']]
    pure_killers = [name for name, data in nodes_data.items() if data['is_killer'] and not data['is_victim']]
    both = [name for name, data in nodes_data.items() if data['is_killer'] and data['is_victim']]

    # NetworkX-specific metrics
    cycles = list(nx.simple_cycles(G))

    # Calculate centrality for most "important" characters in the killing network
    if G.number_of_edges() > 0:
        pagerank = nx.pagerank(G)
        most_central = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
    else:
        most_central = []

    return {
        'total_kills': G.number_of_edges(),
        'serial_killers': serial_killers,
        'pure_victims': len(pure_victims),
        'pure_killers': len(pure_killers),
        'killer_victims': len(both),
        'cycles': cycles,
        'most_central': most_central,
    }


def _generate_network_html(
    G: nx.DiGraph,
    stats: Dict,
    characters: Dict[str, Character]
) -> str:
    """Generate HTML with vis.js network visualization."""

    # Convert NetworkX graph nodes to vis.js format
    vis_nodes = []
    node_id = 0
    name_to_id = {}

    for name, data in G.nodes(data=True):
        # Determine node color and size
        if data['is_killer'] and data['is_victim']:
            color = '#f39c12'  # Orange - both killer and victim
            title = f"{name} (killed {data['kills']}, was killed)"
        elif data['is_killer']:
            color = '#e74c3c'  # Red - killer
            title = f"{name} (killed {data['kills']})"
        elif data['is_victim']:
            color = '#95a5a6'  # Gray - victim
            title = f"{name} (victim)"
        else:
            color = '#3498db'  # Blue - neither (survived)
            title = f"{name} (survived)"

        # Size based on kill count (min 20, max 50)
        size = 20 + (data['kills'] * 10)

        vis_nodes.append({
            'id': node_id,
            'label': name,
            'title': title,
            'color': color,
            'size': size,
        })
        name_to_id[name] = node_id
        node_id += 1

    # Convert NetworkX graph edges to vis.js format
    vis_edges = []
    for killer, victim, edge_data in G.edges(data=True):
        if killer in name_to_id and victim in name_to_id:
            scene = edge_data.get('scene', '?')
            method = edge_data.get('method', 'Unknown')
            vis_edges.append({
                'from': name_to_id[killer],
                'to': name_to_id[victim],
                'label': f"S{scene}",
                'title': f"{killer} killed {victim} in scene {scene} by {method}",
                'arrows': 'to',
            })

    # Build HTML
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Killer Network - Antarctic Mystery</title>',
        '    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>',
        '    <style>',
        _get_network_css(),
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="container">',
        '        <h1>🔪 Killer Network Graph</h1>',
        '        <p class="subtitle">Antarctic Station Alpha-7 Mystery - Who Killed Whom</p>',
        '',
        '        <div class="legend">',
        '            <h3>Legend:</h3>',
        '            <div class="legend-items">',
        '                <span class="legend-item"><span class="color-box red"></span> Pure Killers (never killed)</span>',
        '                <span class="legend-item"><span class="color-box orange"></span> Killer-Victims (killed and were killed)</span>',
        '                <span class="legend-item"><span class="color-box gray"></span> Pure Victims (never killed)</span>',
        '                <span class="legend-item"><span class="color-box blue"></span> Survivors (not involved)</span>',
        '            </div>',
        '            <p style="margin-top: 10px;"><strong>Node size</strong> = number of kills | <strong>Arrows</strong> = killer → victim</p>',
        '        </div>',
        '',
        '        <div class="stats">',
        f'            <h3>Network Statistics</h3>',
        f'            <ul>',
        f'                <li><strong>Total Murders:</strong> {stats["total_kills"]}</li>',
        f'                <li><strong>Pure Killers:</strong> {stats["pure_killers"]} (killed but never died)</li>',
        f'                <li><strong>Pure Victims:</strong> {stats["pure_victims"]} (killed but never killed anyone)</li>',
        f'                <li><strong>Killer-Victims:</strong> {stats["killer_victims"]} (killed someone AND were killed)</li>',
    ]

    if stats['serial_killers']:
        html_parts.append('                <li><strong>Serial Killers:</strong>')
        html_parts.append('                    <ul>')
        for name, kills in stats['serial_killers']:
            html_parts.append(f'                        <li>{name}: {kills} kills</li>')
        html_parts.append('                    </ul>')
        html_parts.append('                </li>')

    if stats.get('cycles'):
        html_parts.append('                <li><strong>⚠ Revenge Cycles Detected:</strong>')
        html_parts.append('                    <ul>')
        for cycle in stats['cycles'][:5]:  # Show up to 5 cycles
            cycle_str = ' → '.join(cycle) + ' → ' + cycle[0]
            html_parts.append(f'                        <li>{cycle_str}</li>')
        if len(stats['cycles']) > 5:
            html_parts.append(f'                        <li>...and {len(stats["cycles"]) - 5} more</li>')
        html_parts.append('                    </ul>')
        html_parts.append('                </li>')

    if stats.get('most_central'):
        html_parts.append('                <li><strong>Most Central Characters (PageRank):</strong>')
        html_parts.append('                    <ul>')
        for name, score in stats['most_central']:
            html_parts.append(f'                        <li>{name}: {score:.4f}</li>')
        html_parts.append('                    </ul>')
        html_parts.append('                </li>')

    html_parts.extend([
        '            </ul>',
        '        </div>',
        '',
        '        <div class="instructions">',
        '            <strong>How to use:</strong> Drag nodes to rearrange | Scroll to zoom | Click and drag background to pan | Hover over nodes/edges for details',
        '        </div>',
        '',
        '        <div id="network"></div>',
        '',
        '        <div class="footer">',
        '            <p>Generated by Antarctic Mystery Validator</p>',
        '        </div>',
        '    </div>',
        '',
        '    <script type="text/javascript">',
        '        // Network data',
        f'        var nodes = new vis.DataSet({_to_js_array(vis_nodes)});',
        f'        var edges = new vis.DataSet({_to_js_array(vis_edges)});',
        '',
        '        // Create network',
        '        var container = document.getElementById("network");',
        '        var data = { nodes: nodes, edges: edges };',
        '        var options = {',
        '            physics: {',
        '                enabled: true,',
        '                barnesHut: {',
        '                    gravitationalConstant: -8000,',
        '                    springLength: 200,',
        '                    springConstant: 0.04',
        '                },',
        '                stabilization: {',
        '                    iterations: 200',
        '                }',
        '            },',
        '            edges: {',
        '                color: { color: "#848484", highlight: "#e74c3c" },',
        '                width: 2,',
        '                font: { size: 12, color: "#333" },',
        '                smooth: { type: "cubicBezier" }',
        '            },',
        '            nodes: {',
        '                font: { size: 14, color: "#fff", face: "arial" },',
        '                borderWidth: 2,',
        '                borderWidthSelected: 4',
        '            },',
        '            interaction: {',
        '                hover: true,',
        '                tooltipDelay: 200',
        '            }',
        '        };',
        '',
        '        var network = new vis.Network(container, data, options);',
        '    </script>',
        '</body>',
        '</html>',
    ])

    return '\n'.join(html_parts)


def _get_network_css() -> str:
    """Get CSS styles for the network visualization."""
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
        }

        .container {
            max-width: 1400px;
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

        .legend-items {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            font-size: 0.95em;
        }

        .color-box {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 8px;
            border: 2px solid #333;
        }

        .color-box.red { background: #e74c3c; }
        .color-box.orange { background: #f39c12; }
        .color-box.gray { background: #95a5a6; }
        .color-box.blue { background: #3498db; }

        .stats {
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #f39c12;
        }

        .stats h3 {
            margin-bottom: 10px;
            color: #856404;
        }

        .stats ul {
            list-style: none;
            padding-left: 0;
        }

        .stats li {
            padding: 5px 0;
        }

        .stats ul ul {
            padding-left: 20px;
            list-style: disc;
        }

        .instructions {
            background: #d1ecf1;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #0c5460;
            color: #0c5460;
        }

        #network {
            width: 100%;
            height: 700px;
            border: 2px solid #ddd;
            border-radius: 5px;
            background: #fafafa;
        }

        .footer {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }
    '''


def _to_js_array(python_list: List[Dict]) -> str:
    """Convert Python list of dicts to JavaScript array literal."""
    import json
    return json.dumps(python_list, indent=8)
