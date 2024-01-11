import json

in_name = 'resultData_fixed.json'
out_name = 'resultData_fixed_ids.json'

# read topo data
with open(in_name, 'r') as f:
    data = json.load(f)

# get nodes and egdes
nodes, edges = data['nodeList'], data['edgeList']

# removing nodes that are never a source in the edges (to prevent generation of a discnonnected graph)
removed_nodes = set()  # so we can remove edges that refer to them as dest nodes later

cleaned_nodes = []
while nodes:
    # get node
    node = nodes.pop()
    # if node has no ports - remove node
    if not node['portList']:
        print("HAS NO PORTS:", node)
        removed_nodes.add(node['id'])
    else:
        # check if node is part of the topology
        is_src = False
        for edge in edges:
            if edge['srcNode'] == node['id']:
                is_src = True
                break
        # if the node conncets to another as a src node keep it
        if is_src:
            cleaned_nodes.append(node)

print(f'removed: {len(removed_nodes)}')
nodes = cleaned_nodes

# remove edges that contain removed nodes as destNodes
# removed nodes cannot be src nodes as they are the nodes that never appear as a src in the edgeList
cleaned_edges = []
while edges:
    edge = edges.pop()
    # keeping only dest nodes that are at appear as source at least once
    if not edge['destNode'] in removed_nodes:
        cleaned_edges.append(edge)
    else:
        print(f'removed edge: {edge}')

edges = cleaned_edges

# adding a index to each node that is to be used as the main id
# (old id is stored as old_id for each node in case that is useful for iding the nodes later for QoS etc..)
old_to_new_map = {}
for idx, node in enumerate(nodes):
    node['old_id'] = node['id']
    node['id'] = idx
    old_to_new_map[node['old_id']] = idx

# changing the old id to new id in edgeList
for idx, edge in enumerate(edges):
    edge['srcNode'] = old_to_new_map[edge['srcNode']]
    edge['destNode'] = old_to_new_map[edge['destNode']]
    edge['id'] = idx

cleaned_data = {'nodeList': nodes, 'edgeList': edges}

with open(out_name, 'w') as f:
    json.dump(cleaned_data, f, indent=4)
