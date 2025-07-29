
# netdecom Documentation

## Overview
netdecom is a Python package for advanced graph analysis, providing algorithms for convex subgraph extraction and recursive decomposition of both undirected graphs (UGs) and directed acyclic graphs (DAGs). Built on NetworkX, it offers efficient implementations of three core functionalities.

## Installation

```pycon
>>> pip install netdecom
```

## Core Functionalities

### 1. Convex Hull Identification in Undirected Graphs
Finds the minimal convex subgraph containing a given node set R:

```pycon
>>> import netdecom as nd
>>> import networkx as nx
>>> G = nx.Graph([(1, 2), (2, 3), (3, 4)])
>>> nd.IPA(G, [1, 3])  # Inducing Path Absorbing Algorithm for NetworkX graph
>>> nd.CMSA(G, [1, 3])  # Close Minimal Separator Absorbing Algorithm for NetworkX graph
>>> G = ig.Graph([(0, 1), (1, 2), (2, 3)])
>>> nd.CMSA_igraph(G, [1, 3])  # Close Minimal Separator Absorbing Algorithm for igraph graph
```

### 2. Recursive Graph Decomposition
Decomposes graphs into atoms using MCS ordering:

```pycon
>>> nd.Decom_CMSA(G)  # CMSA-based decomposition for NetworkX graph
>>> nd.Decom_IPA(G)  # IPA-based decomposition for NetworkX graph
>>> nd.P_Decom(G)  # Xu and Guo method decomposition for NetworkX graph
>>> nd.Decom_CMSA_igraph(G)  # CMSA-based decomposition for igraph graph
```

### 3. Directed Convex Hull Identification in Directed Acyclic Graphs
Finds the minimal d-convex subgraph containing a given node set R:

```pycon
>>> G = nx.DiGraph([(1, 2), (2, 3), (3, 4)])
>>> nd.CMDSA(G, {1, 3})  # Close Minimal D-Separator Absorbing Algorithm
```

### 4. Random Graph Generation
Generates random connected graphs, including UGs and DAGs, with specified parameters for node count and edge probability.

#### `generator_connected_ug(n, p)`
#### `generate_connected_dag(n, p, max_parents=3)`
#### Parameters:
- `n` (int): The number of nodes in the graph.
- `p` (float): The probability of adding an edge between any pair of nodes (for UG) or from a parent node to a child node (for DAG). The value should be between 0 and 1.
- `max_parents` (int, optional): The maximum number of parent nodes for each node in the DAG. Defaults to 3.

#### Returns:
- A connected graph (`networkx.Graph` for UG or `networkx.DiGraph` for DAG).

#### Example:

```pycon
>>> ug = nd.generator_connected_ug(10, 0.3)  # Generates a random connected NetworkX graph with 10 nodes and a probability 0.3 of adding edges.
>>> dag = nd.generate_connected_dag(10, 0.3, max_parents=3)  # Generate a connected Directed Acyclic Graph (DAG) with 10 nodes, edge probability 0.3, and maximum 3 parents per node.
>>> ug = nd.generator_connected_ig(10, 0.3)  # Generates a random connected igraph graph with 10 nodes and a probability 0.3 of adding edges.
>>> dag = nd.random_connected_dag(10, 0.3)  # Generate a random Directed Acyclic Graph (DAG) with 10 nodes and edge probability 0.3.
```

### 5. Load Example Graphs

#### `get_example(file_name)`
Reads the specified example file from the library and returns the corresponding undirected graph object (either `NetworkX` or `igraph`):

#### Parameters:
- `file_name` (str): The name of the example file to be read. The following example files are available:

| File Name                                     | Nodes | Edges   | Connected Components | Largest Component Size |
|-----------------------------------------------|-------|---------|----------------------|------------------------|
| mammalia-voles-rob-trapping-22.txt            | 103   | 151     | 15                   | 59                     |
| Animal-Network.txt                            | 445   | 1332    | 22                   | 117                    |
| bio-CE-GT.txt                                 | 924   | 3239    | 13                   | 878                    |
| bio-CE-GN.txt                                 | 2220  | 53683   | 3                    | 2215                   |
| bio-DR-CX.txt                                 | 3289  | 84940   | 2                    | 3287                   |
| DD6.txt                                       | 4152  | 10320   | 1                    | 4152                   |
| as20000102.txt                                | 6474  | 12572   | 1                    | 6474                   |
| rec-movielens-user-movies-10m.txt             | 7601  | 55384   | 1                    | 7601                   |
| CA-HepTh.txt                                  | 9875  | 25973   | 427                  | 8638                   |
| rec-movielens-tag-movies-10m.txt              | 16528 | 71067   | 1                    | 16528                  |
| CA-CondMat.txt                                | 23133 | 93439   | 567                  | 21363                  |
| Email-Enron.txt                               | 36692 | 183831  | 1065                 | 33696                  |
| rec-yelp-user-business.txt                    | 50394 | 229572  | 19                   | 50319                  |
| rec-eachmovie.txt                             | 61989 | 2811458 | 1                    | 61989                  |
| rec-movielens.txt                             | 70155 | 9991339 | 1                    | 70155                  |
| rec-amazon.txt                                | 91813 | 125704  | 1                    | 91813                  |


#### Returns:
- A NetworkX UG object corresponding to the specified example file.

#### Example:

```pycon
>>> G = nd.get_example("Animal-Network.txt", class_type="nx")  # Reads the example file and returns a NetworkX graph.
>>> G = nd.get_example("Animal-Network.txt", class_type="ig")  # Reads the example file and returns an igraph graph.
```

## Notes
- All input graphs must be NetworkX Graph/DiGraph objects.
- MCS ordering should follow graph topology.
- DAG decomposition features are under development.
