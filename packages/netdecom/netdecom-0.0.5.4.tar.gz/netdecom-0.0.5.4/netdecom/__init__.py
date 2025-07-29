from .Convex_hull_UG import Convex_hull_UG
from .LPD_UG import LPD
from .Convex_hull_DAG import Convex_hull_DAG
from .Graph_gererators import generator_connected_ug, generate_connected_dag, random_connected_dag, generator_connected_ig
from .examples import get_example
import networkx as nx
import igraph

__all__ = ['get_example', 'generator_connected_ug','generator_connected_ig', 'generate_connected_dag','random_connected_dag']

def CMSA(graph, r):
    """
    Perform Convex Hull CMSA method on the given NetworkX graph.

    :param graph: The NetworkX graph to perform CMSA on
    :param r: The set of nodes to perform CMSA on
    :return: The result of the CMSA decomposition
    """
    if not isinstance(graph, nx.Graph):
        raise TypeError("The graph must be a NetworkX graph.")
    
    convex_hull_ug = Convex_hull_UG(graph) 
    return convex_hull_ug.CMSA(r)

def IPA(graph, r):
    """
    Perform Convex Hull IPA method on the given NetworkX graph.

    :param graph: The NetworkX graph to perform IPA on
    :param r: The set of nodes to perform IPA on
    :return: The result of the IPA decomposition
    """
    if not isinstance(graph, nx.Graph):
        raise TypeError("The graph must be a NetworkX graph.")
    
    convex_hull_ug = Convex_hull_UG(graph) 
    return convex_hull_ug.IPA(r)

def CMSA_igraph(graph, r):
    """
    Perform Convex Hull CMSA method on the given igraph graph.

    :param graph: The igraph network graph
    :param r: The set of nodes to perform CMSA on
    :return: The result of the CMSA decomposition for igraph
    """
    if not isinstance(graph, igraph.Graph):
        raise TypeError("The graph must be an igraph graph.")
    
    convex_hull_ug = Convex_hull_UG(graph) 
    return convex_hull_ug.CMSA_igraph(r)



def CMDSA(graph, r):
    """
    Perform Convex Hull Decomposition for Directed Acyclic Graph (CMDSA).

    :param graph: The NetworkX graph to perform CMDSA on
    :param r: The set of nodes to perform CMDSA on
    :return: The result of the CMDSA decomposition
    """
    convex_hull_dag = Convex_hull_DAG(graph)
    return convex_hull_dag.CMDSA(r)

def Decom_CMSA(graph):
    """
    Decompose the NetworkX graph using the CMSA method (based on maximum cardinality search).

    :param graph: The NetworkX graph to decompose
    :return: A list of blocks representing the decomposed graph
    """
    if not isinstance(graph, nx.Graph):
        raise TypeError("The graph must be a NetworkX graph.")
    
    lpd_ug = LPD(graph)
    return lpd_ug.Decom_CMSA()


def Decom_IPA(graph):
    """
    Decompose the NetworkX graph using the IPA method.

    :param graph: The NetworkX graph to decompose
    :return: A list of blocks representing the decomposed graph
    """
    if not isinstance(graph, nx.Graph):
        raise TypeError("The graph must be a NetworkX graph.")
    
    lpd_ug = LPD(graph)
    return lpd_ug.Decom_IPA()

def Decom_CMSA_igraph(graph):
    """
    Decompose the igraph graph using the CMSA method.

    :param graph: The igraph graph to decompose
    :return: A list of blocks representing the decomposed graph
    """
    if not isinstance(graph, igraph.Graph):
        raise TypeError("The graph must be an igraph graph.")
    
    lpd_ug = LPD(graph)
    return lpd_ug.Decom_CMSA_igraph()


def P_Decom(graph):
    """
    Wrapper function to call P_Decom from Decom_xu class.
    
    :param graph: A network graph (could be NetworkX or igraph)
    :return: A list of blocks representing the decomposed graph
    """
    lpd_ug = LPD(graph)  # Create an instance of Decom_xu
    return lpd_ug.P_Decom()  

