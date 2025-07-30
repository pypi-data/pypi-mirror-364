import argparse
import os
import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def parse_args():
    parser = argparse.ArgumentParser(description="Plot-only mode in plasmidnet for custom plots")
    parser.add_argument("--results_dir", required=True, help="Path to directory")
    parser.add_argument("--plot_k", nargs=2, type=float, metavar=('MIN_K', 'MAX_K'),
                        required=True, help="Specify minimum and maximum k values for plotting")
    parser.add_argument("--min_edge_width", type=float, default=0.2)
    parser.add_argument("--max_edge_width", type=float, default=2.0)
    parser.add_argument("--node_size", type=int, default=900)
    parser.add_argument("--node_color", type=str, default="#cccccc")
    parser.add_argument("--node_shape", type=str, default="o")
    parser.add_argument("--figsize", nargs=2, type=float, default=[25, 25])
    parser.add_argument("--iterations", type=int, default=100)
    return parser.parse_args()

def load_network_from_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return nx.cytoscape_graph(data)

def scale_edge_weights(G, min_width, max_width):
    edge_weights = nx.get_edge_attributes(G, 'weight')
    min_weight = 5
    max_weight = 100
    scaled = []
    for edge in G.edges():
        weight = edge_weights.get(edge, min_weight)
        clipped = max(min_weight, min(weight, max_weight))
        scaled_width = min_width + ((clipped - min_weight) / (max_weight - min_weight)) * (max_width - min_width)
        scaled.append(scaled_width)
    return scaled

def visualize_network(G, k, output_path, args):
    pos = nx.spring_layout(G, k=k, seed=69420, iterations=args.iterations)
    edge_widths = scale_edge_weights(G, args.min_edge_width, args.max_edge_width)

    # With labels
    fig, ax = plt.subplots(figsize=tuple(args.figsize))
    nx.draw_networkx_nodes(G, pos, node_color=args.node_color, node_size=args.node_size,
                           node_shape=args.node_shape, linewidths=1, edgecolors='black', alpha=0.85, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='grey', alpha=0.7, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path + ".pdf")
    plt.close()

    # Without labels
    fig, ax = plt.subplots(figsize=tuple(args.figsize))
    nx.draw_networkx_nodes(G, pos, node_color=args.node_color, node_size=args.node_size,
                           node_shape=args.node_shape, linewidths=1, edgecolors='black', alpha=0.85, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='grey', alpha=0.7, ax=ax)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path + "_nolabels.pdf")
    plt.close()

def visualize_network_colored_by_cluster(G, k, output_path_no_ext, cluster_mapping_file, cluster_color_file, args):
    cluster_map = {}
    with open(cluster_mapping_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                plasmid, cluster = parts
                cluster_map[plasmid] = cluster

    color_map = {}
    with open(cluster_color_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                cluster, color = parts
                color_map[cluster] = color

    node_colors = []
    for node in G.nodes():
        cluster = cluster_map.get(node)
        color = color_map.get(cluster, args.node_color)
        node_colors.append(color)

    edge_widths = scale_edge_weights(G, args.min_edge_width, args.max_edge_width)
    pos = nx.spring_layout(G, k=k, seed=69420, iterations=args.iterations)

    legend_handles = [
        mpatches.Patch(color=color, label=cluster)
        for cluster, color in sorted(color_map.items())
    ]

    # With labels
    fig, ax = plt.subplots(figsize=tuple(args.figsize))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=args.node_size, node_shape=args.node_shape,
                           linewidths=1, edgecolors='black', alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='grey', alpha=0.7, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
    ax.legend(handles=legend_handles, loc='upper right', fontsize=16, title="Clusters", title_fontsize=18,
              bbox_to_anchor=(1.02, 1.0))
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path_no_ext + "_cluster_colored.pdf")
    plt.savefig(output_path_no_ext + "_cluster_colored.svg")
    plt.close()

    # Without labels
    fig, ax = plt.subplots(figsize=tuple(args.figsize))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=args.node_size, node_shape=args.node_shape,
                           linewidths=1, edgecolors='black', alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='grey', alpha=0.7, ax=ax)
    ax.legend(handles=legend_handles, loc='upper right', fontsize=16, title="Clusters", title_fontsize=18,
              bbox_to_anchor=(1.02, 1.0))
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path_no_ext + "_cluster_colored_nolabels.pdf")
    plt.savefig(output_path_no_ext + "_cluster_colored_nolabels.svg")
    plt.close()

def run():
    args = parse_args()

    print("Generating network visualizations...")

    json_path = os.path.join(args.results_dir, "network.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"network.json not found in {args.results_dir}")

    G = load_network_from_json(json_path)

    plots_dir = os.path.join(args.results_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    cluster_mapping = os.path.join(args.results_dir, "plasmid_cluster_mapping.txt")
    cluster_colors = os.path.join(args.results_dir, "cluster_colours.txt")
    colored = os.path.exists(cluster_mapping) and os.path.exists(cluster_colors)

    k_min, k_max = args.plot_k

    for k in np.arange(k_min, k_max + 0.1, 1.0):
        output_base = os.path.join(plots_dir, f"custom_plot_k_{k}")
        visualize_network(G, k, output_base, args)

        if colored:
            visualize_network_colored_by_cluster(G, k, output_base, cluster_mapping, cluster_colors, args)

    print(f"Plots saved to: {plots_dir}")

if __name__ == "__main__":
    run()
