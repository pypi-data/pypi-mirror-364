#This is a convex hull algorithm that absorbs minimal separations, 
#inputs the undirected graph and sets of concerns, and obtains the convex hull.
import networkx as nx
import igraph

class Convex_hull_UG:

    def __init__(self, graph):
        """
        Initialize with a graph.
        
        :param graph: A network graph object (could be from networkx or igraph)
        """
        self.graph = graph

    def node_boundary_igraph(self, g, nbunch1, nbunch2=None):
        """
        Calculate the boundary nodes between two sets of nodes.

        :param nbunch1: The first set of nodes
        :param nbunch2: The second set of nodes (optional)
        :return: The boundary nodes
        """
        # Construct the boundary using set comprehension
        boundary = {neighbor for node in nbunch1 for neighbor in g.neighbors(node)}
        boundary -= set(nbunch1)  # Remove nodes in nbunch1
        if nbunch2 is not None:
            boundary &= nbunch2  # Keep only nodes in nbunch2
        return boundary

    def CloseSeparator_igraph(self, g_C, a, b):
        """
        Find the minimal ab-separator contained in the neighbor set of Node a

        :param g_C: The graph object
        :param a: Node a
        :param b: Node b
        :return: The separator nodes
        """
        N_A = set(g_C.neighbors(a))
        V_remove_N_A = list(set(range(g_C.vcount())) - N_A)
        V_remove_N_A.sort()
        sub_g_C = g_C.subgraph(V_remove_N_A)  # Local numbering of subgraph
        components = sub_g_C.components()
        b_idx = V_remove_N_A.index(b)  # Local index of node b in subgraph

        for component_local in components:
            if b_idx in component_local:
                component_global = [V_remove_N_A[idx] for idx in component_local]
                N_V_C = [n for n in self.node_boundary_igraph(g_C, nbunch1=component_global, nbunch2=N_A)]
                N_V_C.sort()
                return N_V_C 
            
    def CMSA_igraph(self, r):
        """
        Find the convex hull using a graph-based method (CMSA algorithm).

        :param r: A set of nodes to start with
        :return: The set of nodes in the convex hull
        """
        g = self.graph
        H = set(r)
        s = True
        while s:
            s = False
            M = list(set(range(g.vcount())) - H)
            M.sort()
            g_M = g.subgraph(M)
            M_c_local = list(g_M.components())  # Each element is a local numbering
            M_c_global = [[M[idx] for idx in comp] for comp in M_c_local]
            
            for i in range(len(M_c_global)):           
                h = self.node_boundary_igraph(g, nbunch1=M_c_global[i], nbunch2=H)
                if len(h) < 2:
                    continue
                for j in range(len(h)):
                    for k in range(j + 1, len(h)):
                        if h[j] not in g.neighbors(h[k]):
                            
                            sub_node_set = M_c_global[i].copy()
                            sub_node_set.extend([h[j], h[k]])
                            sub_node_set.sort()

                            Subgraph = g.subgraph(sub_node_set)  # Local numbering of subgraph
                            a, b = sub_node_set.index(h[j]), sub_node_set.index(h[k])  # Get local indices of h_j, h_k
                            
                            sep_a_local = self.CloseSeparator_igraph(Subgraph, a, b)  # Get local separator in subgraph
                            sep_b_local = self.CloseSeparator_igraph(Subgraph, b, a)  # Get local separator in subgraph
                            
                            sep_a_global, sep_b_global = [sub_node_set[idx] for idx in sep_a_local], [sub_node_set[idx] for idx in sep_b_local]  # Map back to global indices
                            
                            H |= (set(sep_a_global) | set(sep_b_global))
                            s = True
                            break
                    else:
                        continue
                    break    
        return H
    

    def CloseSeparator(self, g_C, a, b):
        N_A = set(g_C.adj[a])
        V_remove_N_A = set(g_C.nodes) - N_A
        N_V_C = {n for n in nx.node_boundary(g_C, nbunch1=nx.node_connected_component(nx.subgraph(g_C, V_remove_N_A), b), nbunch2=N_A)}
        return N_V_C


    def CMSA(self,r):
        g = self.graph
        s = 1 
        H=set(r)
        while s == 1:
            s = 0
            M = set(g.nodes)-H
            M_c = list(nx.connected_components(nx.subgraph(g, M))) 
            for i in range(0,len(M_c)):
                h = {n for n in nx.node_boundary(g, nbunch1=M_c[i], nbunch2=H)}           
                for a in h:
                    for b in h:
                        if a!=b and b not in g.adj[a]:
                            Subgraph = nx.subgraph(g, M | {a,b})
                            H |= self.CloseSeparator(Subgraph,a,b)
                            H |= self.CloseSeparator(Subgraph,b,a)
                            s = 1
                            break
                    else:
                        continue
                    break    
        return H
    
    def IPA(self,r):
        g = self.graph
        s = 1 
        H=set(r)
        while s == 1:
            s = 0
            M = set(g.nodes)-H
            M_c = list(nx.connected_components(nx.subgraph(g, M))) 
            for i in range(0,len(M_c)):
                h = {n for n in nx.node_boundary(g, nbunch1=M_c[i], nbunch2=H)}           
                for a in h:
                    for b in h:
                        if a!=b and b not in g.adj[a]:
                            Subgraph = nx.subgraph(g, M | {a,b})
                            H |= set(nx.shortest_path(Subgraph, a, b))
                            s = 1
                            break
                    else:
                        continue
                    break    
        return H
    

#from Convex_hull_UG import *
#hull = Convex_hull_UG(G)
#CMSA Algorithm, hull.CMSA(R)#R = list
#IPA Algorithm, hull.IPA(R)#R = list