import json
import numpy as np
import networkx as nx
import tqdm
from sys import argv
import os
import yaml

######################################################################################
#                                INIT
######################################################################################
input_name = argv[1]
output_dir = argv[2]

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"'{output_dir}' created.")
else:
    print(
        f"'{output_dir}' already exists. Will add switch configs there...")

# read topo data
with open(input_name, 'r') as f:
    data = json.load(f)

# get nodes and egdes
nodes, edges = data['nodeList'], data['edgeList']
NUM_NODES, NUM_EDGES = len(nodes), len(edges)

# creating some usefull maps to get information regarding the nodes
new_to_old = {}
for node in nodes:
    new_to_old[node['id']] = node['old_id']

id_to_node = {}
for node in nodes:
    id_to_node[node['id']] = node

port_map = {}
for node in nodes:
    port_map[node['id']] = {}
    for port in node['portList']:
        port_map[node['id']][port['id']] = port

######################################################################################
#                                PARSING
######################################################################################

print('Parsing data and creating graph...')

# the topology adj. matrix
adj = np.zeros((NUM_NODES, NUM_NODES))
# connection details for topology
connection_info = {node['id']: {} for node in nodes}

# for each node find all edges that start from that node and add them to the adj. matrix
for node in nodes:
    for edge in edges:
        if node['id'] == edge['srcNode']:
            src, src_port, dest, dest_port = node['id'], edge['srcPort'], edge['destNode'], edge['destPort']
            if adj[src, dest] == 0:  # NOTE: FOR NOW, IGNORING DUPLICATE EDGES CONNECTIONS
                adj[src, dest] = 1  # adj. matrix
                # Getting src node port info
                for p in id_to_node[src]['portList']:
                    if p['id'] == src_port:
                        connection_info[src][dest] = p

######################################################################################
#                                CREATING GRAPHS
######################################################################################

# Create a undirected graph from the dictionary
g = nx.from_numpy_array(adj, create_using=nx.DiGraph)

# get the nodes of the subgraphs in the topology
subgraphs = list(nx.strongly_connected_components(g))

for idx, cc in enumerate(subgraphs):
    print(f'subgraph index: {idx}: nodes in subgraph {len(cc)}')

index = int(input("Choose subgraph: "))

# get the topology of selected subgraph
g = g.subgraph(subgraphs[index])

######################################################################################
#                            GENERATING THE SWITCH CONFIGS
######################################################################################

shortest_paths = nx.all_pairs_shortest_path(g)  # using Floyd-Warshall
'''
    returns list of tuples: [(source, {dest1: path, dest2: path ...})]
'''
for paths in tqdm.tqdm(shortest_paths, desc=f"creating routing tables", unit="iteration"):
    source = paths[0]  # getting the source node

    # initialising the switch infro struct
    switch_info = {
        'qos': None,
        'terminals': None,
        'type': id_to_node[source]['deviceLevel'],
        'ports': {x['id']: x['bw'] for x in port_map[source].values()},
        'routing': {}
    }

    # adding the routing information for all possible destinations
    for dest, path in paths[1].items():
        if source != dest:
            next_hop = path[1]
            switch_info['routing'][dest] = {
                'next_hop': next_hop, 'port': connection_info[source][next_hop]['id']}

    # writting the yaml switch file
    with open(f'{output_dir}/{source}.yaml', 'w') as f:
        yaml.dump(switch_info, f)
