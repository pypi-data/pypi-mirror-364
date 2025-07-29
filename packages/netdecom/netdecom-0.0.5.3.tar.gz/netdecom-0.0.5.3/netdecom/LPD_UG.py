import networkx as nx
import igraph
from .Convex_hull_UG import * 
from collections import defaultdict

class LPD:

    def __init__(self, graph):
        """
        Initialize with a graph.
        
        :param graph: A network graph object (could be from networkx or igraph)
        """
        self.graph = graph


    def Decom_CMSA_igraph(self):
        """
        Decompose the graph using the Convex Hull method based on the maximum cardinality search.

        :return: A list of blocks representing the decomposed graph
        """
        block = []  # List to hold the blocks (decomposed parts)
        G_list = []  # List to hold the subgraphs and their associated nodes and mappings
        
        g = self.graph
        mcs = g.maximum_cardinality_search()[1]  # Get the maximum cardinality search result
        mcs_index = {node: idx for idx, node in enumerate(mcs)}  # Create an index mapping for MCS nodes
        
        # Initialize the local-to-global mapping as a one-to-one mapping (nodes are mapped to themselves initially)
        L_map = {node: node for node in range(g.vcount())}
        
        # Start by adding the full graph, the first node, and the initial mapping to G_list
        G_list.append((g.copy(), mcs[0], L_map))

        while G_list:
            sub_g, v, sub_L_map = G_list.pop(0)
            N_v = set(sub_g.neighbors(v)).union({v})
            
            # If the set of neighbors is a complete subgraph, use it as H
            if len(N_v)*(len(N_v)-1)/2 == sub_g.subgraph(N_v).ecount():
                H = N_v
            else:
                # Otherwise, find the convex hull of the nodes using the CMSA algorithm
                H = Convex_hull_UG(sub_g).CMSA_igraph(N_v)
            
            # Map the local nodes of H to global node indices
            H_global = [sub_L_map[node] for node in H]
            block.append(H_global)  # Add the global node indices of H to the block
            
            # Update the nodes that need to be processed
            update_node = list(set(range(sub_g.vcount())) - H)
            update_node.sort()  # Sort to maintain consistent order
            updata_graph = sub_g.subgraph(update_node)
            
            # Process each connected component in the subgraph
            for M in list(updata_graph.components()):
                
                # Find the indices of the nodes in M within the subgraph
                M_in_subg_idx = [update_node[idx] for idx in M]
                
                # Find the boundary nodes between the components M and H
                A = [n for n in Convex_hull_UG(sub_g).node_boundary_igraph(sub_g, M_in_subg_idx, H)] + M_in_subg_idx
                A_global = [sub_L_map[node] for node in A]
                A_global.sort()
                
                # Create the induced subgraph from A_global
                sub_A_induced = g.subgraph(A_global)
                sub_A_map = {i: A_global[i] for i in range(len(A_global))}  # Map local indices to global ones
                
                # Select the node with the smallest index in A_global according to MCS order
                v = min(A_global, key=mcs_index.get)
                v_in_sub_A_induced_idx = [key for key, val in sub_A_map.items() if val == v][0]
                
                # Add the new subgraph, the new starting node, and the new mapping to G_list
                G_list.append((sub_A_induced, v_in_sub_A_induced_idx, sub_A_map))
        
        return block
    
    def maximum_cardinality_search(self):
        """Efficient MCS implementation using bucket-based priority for Networkx graph.

        Returns
        -------
        order : list
            MCS order (perfect elimination ordering).
        """
        G = self.graph
        n = len(G)
        weights = {v: 0 for v in G.nodes}
        buckets = defaultdict(set)
        buckets[0] = set(G.nodes)
        max_weight = 0
        order = []
        used = set()

        for _ in range(n):
            # Find node with current max weight
            while max_weight >= 0 and not buckets[max_weight]:
                max_weight -= 1
            v = buckets[max_weight].pop()
            order.append(v)
            used.add(v)
            # Update neighbors
            for u in G.neighbors(v):
                if u not in used:
                    w = weights[u]
                    buckets[w].remove(u)
                    weights[u] = w + 1
                    buckets[w + 1].add(u)
                    if w + 1 > max_weight:
                        max_weight = w + 1

        return order[::-1]


    def Decom_CMSA(self):
        """
        Decompose the graph using CMSA method based on the connected components.

        :return: A list of blocks representing the decomposed graph
        """
        block = []
        G_list = []
        MCS = self.maximum_cardinality_search()
        mcs_index = {node: idx for idx, node in enumerate(MCS)}
        G_list.append((self.graph, MCS[0]))
        while G_list:
            g, v = G_list.pop(0)  
            N_v = set(g[v]).union({v})
            if len(N_v)*(len(N_v)-1)/2 == len(g.subgraph(N_v).edges):
                H = N_v
            else:
                H =  Convex_hull_UG(g).CMSA(N_v)
            block.append(H)
            for M in list(nx.connected_components(g.subgraph(set(g.nodes)-H))):
                A = {n for n in nx.node_boundary(g,M,H)}.union(M)
                G_list.append((g.subgraph(A), min(A, key=mcs_index.get)))
        return block

    def Decom_IPA(self):
        """
        Decompose the graph using IPA method based on the connected components.

        :return: A list of blocks representing the decomposed graph
        """
        block = []
        G_list = []
        MCS = self.maximum_cardinality_search()
        mcs_index = {node: idx for idx, node in enumerate(MCS)}
        G_list.append((self.graph, MCS[0]))
        while G_list:
            g, v = G_list.pop(0)  
            N_v = set(g[v]).union({v})
            if len(N_v)*(len(N_v)-1)/2 == len(g.subgraph(N_v).edges):
                H = N_v
            else:
                H =  Convex_hull_UG(g).IPA(N_v)
            block.append(H)
            for M in list(nx.connected_components(g.subgraph(set(g.nodes)-H))):
                A = {n for n in nx.node_boundary(g,M,H)}.union(M)
                G_list.append((g.subgraph(A), min(A, key=mcs_index.get)))
        return block
    
    def complete_chordal_graph(self):
        H = self.graph.copy()
        alpha = {node: 0 for node in H}
        chords = set()
        weight = {node: 0 for node in H.nodes()}
        unnumbered_nodes = list(H.nodes())
        for i in range(len(H.nodes()), 0, -1):
            # get the node in unnumbered_nodes with the maximum weight
            z = max(unnumbered_nodes, key=lambda node: weight[node])
            unnumbered_nodes.remove(z)
            alpha[z] = i
            update_nodes = []
            for y in unnumbered_nodes:
                if self.graph.has_edge(y, z):
                    update_nodes.append(y)
                else:
                    # y_weight will be bigger than node weights between y and z
                    y_weight = weight[y]
                    lower_nodes = [
                        node for node in unnumbered_nodes if weight[node] < y_weight
                    ]
                    if nx.has_path(H.subgraph(lower_nodes + [z, y]), y, z):
                        update_nodes.append(y)
                        chords.add((z, y))
            # during calculation of paths the weights should not be updated
            for node in update_nodes:
                weight[node] += 1
        H.add_edges_from(chords)
        return H, alpha,weight
    def F_t(self):
        H, alpha,weight = self.complete_chordal_graph() 
        f_t = []
        alpha_up = sorted(alpha, key=alpha.__getitem__)
        for i in range(len(list(self.graph.nodes))-1,0,-1):
            if weight[alpha_up[i-1]] <= weight[alpha_up[i]]:
                f_t.append(alpha_up[i-1])
        return H,f_t,alpha_up
    
    @staticmethod
    def is_clique(G):
        n = G.number_of_nodes()
        m = G.number_of_edges()
        return m == n * (n - 1) // 2

    def P_Decom(self):
        CH, F_a, pai_2 = self.F_t()

        
        prime_blocks = []
        g = self.graph.copy()

        for f in reversed(F_a):  # Step 2: from T to 2
            
            C_f = [v for v in CH.neighbors(f) if v in g.nodes]
            

            if len(C_f) == 0:
                prime_blocks.append([f])
                g.remove_node(f)
                continue

            C_f = [v for v in C_f if pai_2.index(v) > pai_2.index(f)]
            #print(f,C_f)
            
            
            if len(C_f) == 1:
                subgraph_nodes = [n for n in g.nodes if n not in C_f]
                comp = list(nx.node_connected_component(g.subgraph(subgraph_nodes),f))
                A = list(comp) + C_f
                B = [n for n in g.nodes if n not in comp]
                prime_blocks.append(A)
                g = g.subgraph(B).copy()
                continue

            else:
                sub_C = g.subgraph(C_f)
                if self.is_clique(sub_C):
                    subgraph_nodes = [n for n in g.nodes if n not in C_f]
                    comp = list(nx.node_connected_component(g.subgraph(subgraph_nodes),f))
                    A = list(comp) + C_f
                    B = [n for n in g.nodes if n not in comp]
                    prime_blocks.append(A)
                    g = g.subgraph(B).copy()
                    continue

        # Add remaining connected components as blocks
        for comp in nx.connected_components(g):
            prime_blocks.append(list(comp))

        return prime_blocks
    
#LPD_UG((G, mcs_sequence)).Local_decom_CMSA()
#LPD_UG((G, mcs_sequence)).Local_decom_IPA()