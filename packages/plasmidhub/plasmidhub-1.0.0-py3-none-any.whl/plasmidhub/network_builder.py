import numpy as np
import networkx as nx
import pandas as pd
import community.community_louvain as community_louvain
from itertools import combinations
import json
import random
import os
import logging
logger = logging.getLogger(__name__)

def load_and_process_fastani_data(file_path, results_dir):
    """Load and process FastANI data to create a similarity matrix."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    if lines[0].startswith('Query'):
        lines = lines[1:]

    from io import StringIO
    data = StringIO(''.join(lines))
    df = pd.read_csv(data, sep="\t", header=None)

    df.columns = ['Query', 'Reference', 'ANI', 'Matching_Frags_Query', 'Matching_Frags_Ref',
                  'Query_size', 'Reference_size', 'Matching_Frags_Query_bp', 'Matching_Frags_Ref_bp']

    df = df[['Query', 'Reference', 'ANI', 'Matching_Frags_Query', 'Matching_Frags_Ref']]

    df['ANI'] = pd.to_numeric(df['ANI'], errors='coerce')
    df['Matching_Frags_Query'] = pd.to_numeric(df['Matching_Frags_Query'], errors='coerce')
    df['Matching_Frags_Ref'] = pd.to_numeric(df['Matching_Frags_Ref'], errors='coerce')

    labels = pd.concat([df['Query'], df['Reference']]).unique()
    similarity_matrix = pd.DataFrame(0, index=labels, columns=labels, dtype=float)

    for _, row in df.iterrows():
        query = row['Query']
        reference = row['Reference']
        ani = row['ANI']
        if pd.notna(ani) and pd.notna(row['Matching_Frags_Query']) and pd.notna(row['Matching_Frags_Ref']):
            match_frac = min(row['Matching_Frags_Query'] / row['Matching_Frags_Ref'],
                             row['Matching_Frags_Ref'] / row['Matching_Frags_Query'])

            # Use both ANI and matching fragment ratio to determine the weight
            weight = ani * match_frac

            # Use the lower value if a weight is already present
            existing_weight = similarity_matrix.loc[query, reference]
            if existing_weight > 0:
                weight = min(weight, existing_weight)

            # Populate similarity matrix
            similarity_matrix.loc[query, reference] = weight
            similarity_matrix.loc[reference, query] = weight

    np.fill_diagonal(similarity_matrix.values, 1)
    similarity_matrix.to_csv(os.path.join(results_dir, "similarity_matrix.csv"), index=True)

    return labels, similarity_matrix.values

def create_network(labels, similarity_matrix, plasmid_list_path, results_dir):
    G = nx.Graph()

    for label in labels:
        if label not in G:
            G.add_node(label)

    n = len(labels)
    for i in range(n):
        for j in range(i + 1, n):
            similarity = similarity_matrix[i, j]
            if similarity > 5 and similarity <= 100:
                weight = similarity
                if not G.has_edge(labels[i], labels[j]):
                    G.add_edge(labels[i], labels[j], weight=weight)

    # Save edge list after edges are added
    nx.write_weighted_edgelist(G, os.path.join(results_dir, "network_edges.txt"))

    with open(plasmid_list_path, 'r') as f:
        all_plasmids = [line.strip() for line in f.readlines()]

    for plasmid in all_plasmids:
        if plasmid not in G.nodes:
            G.add_node(plasmid, type='singleton')

    singleton_positions = {}
    for plasmid in all_plasmids:
        if plasmid not in G.nodes:
            singleton_positions[plasmid] = (random.uniform(-1, 1), random.uniform(-1, 1))

    logger.info("Total nodes in the network: %d", len(G.nodes()))
    logger.info("Total edges in the network: %d", G.number_of_edges())

    nodes_to_remove = [node for node in G.nodes() if node not in all_plasmids]
    G.remove_nodes_from(nodes_to_remove)

    nx.write_gml(G, os.path.join(results_dir, "network.gml"))

    G_json = nx.cytoscape_data(G)
    with open(os.path.join(results_dir, "network.json"), "w") as f:
        json.dump(G_json, f)

    return G

def detect_communities(G):
    partition = community_louvain.best_partition(G, weight='weight')
    return partition

def calculate_subcluster_distances(G, partition, results_dir):
    subcluster_combinations = list(combinations(set(partition.values()), 2))
    results = []
    
    for cluster1, cluster2 in subcluster_combinations:
        edges_between_clusters = []
        for node1, node2 in combinations(G.nodes(), 2):
            if partition[node1] == cluster1 and partition[node2] == cluster2 and G.has_edge(node1, node2):
                edges_between_clusters.append(G[node1][node2]['weight'])

        mean_distance = np.mean(edges_between_clusters) if edges_between_clusters else np.nan
        median_distance = np.median(edges_between_clusters) if edges_between_clusters else np.nan
        results.append((cluster1, cluster2, mean_distance, median_distance))
    
    df_results = pd.DataFrame(results, columns=["Subcluster1", "Subcluster2", "Mean Distance", "Median Distance"])
    df_results.to_csv(os.path.join(results_dir, "subcluster_distances.tsv"), sep="\t", index=False)
    return df_results

def save_plasmids_by_subcluster(partition, results_dir):
    subcluster_plasmids = {cluster: [] for cluster in set(partition.values())}
    for node, cluster in partition.items():
        subcluster_plasmids[cluster].append(node)

    for cluster, plasmids in subcluster_plasmids.items():
        with open(os.path.join(results_dir, f"subcluster_{cluster}_plasmids.txt"), "w") as f:
            f.write("\n".join(plasmids))

def calculate_network_metrics(G, partition):
    num_edges = G.number_of_edges()
    num_nodes = G.number_of_nodes()
    num_possible_edges = num_nodes * (num_nodes - 1) / 2
    connectance = num_edges / num_possible_edges
    modularity = community_louvain.modularity(partition, G, weight='weight')

    def calculate_nestedness():
        adj_matrix = nx.to_numpy_array(G)
        nestedness_value = 0
        count = 0
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if adj_matrix[i, j] > 0:
                    ki = np.sum(adj_matrix[i, :])
                    kj = np.sum(adj_matrix[j, :])
                    nestedness_value += 1 / min(ki, kj)
                    count += 1
        return nestedness_value / count if count > 0 else np.nan

    nestedness = calculate_nestedness()
    return connectance, modularity, nestedness

def calculate_node_degrees(G, results_dir):
    degrees = dict(G.degree(weight='weight'))
    df_degrees = pd.DataFrame(list(degrees.items()), columns=["Node", "Degree"])
    df_degrees.to_csv(os.path.join(results_dir, "node_degrees.csv"), index=False)
    return df_degrees

def calculate_betweenness_centrality(G, results_dir):
    betweenness = nx.betweenness_centrality(G, weight='weight', normalized=True)
    df_betweenness = pd.DataFrame(list(betweenness.items()), columns=["Node", "Betweenness Centrality"])
    df_betweenness.to_csv(os.path.join(results_dir, "betweenness_centrality.csv"), index=False)
    return df_betweenness

def calculate_degree_centrality(G, results_dir):
    degree_centrality = nx.degree_centrality(G)
    df_degree_centrality = pd.DataFrame(list(degree_centrality.items()), columns=["Node", "Degree Centrality"])
    df_degree_centrality.to_csv(os.path.join(results_dir, "degree_centrality.csv"), index=False)
    return df_degree_centrality

def build_network(file_path="ANI_results_final.tsv", plasmid_list_path="Plasmid_list.txt", results_dir="results"):
    os.makedirs(results_dir, exist_ok=True)

    labels, similarity_matrix = load_and_process_fastani_data(file_path, results_dir)
    G = create_network(labels, similarity_matrix, plasmid_list_path, results_dir)
    partition = detect_communities(G)
    df_results = calculate_subcluster_distances(G, partition, results_dir)
    save_plasmids_by_subcluster(partition, results_dir)

    connectance, modularity, nestedness = calculate_network_metrics(G, partition)
    metrics = {
        "Connectance": [connectance],
        "Modularity": [modularity],
        "Nestedness": [nestedness]
    }

    df_metrics = pd.DataFrame(metrics)
    df_metrics.to_csv(os.path.join(results_dir, "network_metrics.csv"), index=False)

    df_degrees = calculate_node_degrees(G, results_dir)
    df_betweenness = calculate_betweenness_centrality(G, results_dir)
    df_degree_centrality = calculate_degree_centrality(G, results_dir)

    with open(os.path.join(results_dir, "community_partition.json"), "w") as f:
        json.dump(partition, f)
