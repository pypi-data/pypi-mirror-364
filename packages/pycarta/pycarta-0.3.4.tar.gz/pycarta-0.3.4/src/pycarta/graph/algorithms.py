import logging
import networkx as nx
from pycarta.graph.graph import Graph
from pycarta.graph.vertex import Vertex

logger = logging.getLogger(__name__)


numeric = int | float


def minimal_spanning_tree(graph: Graph) -> Graph:
    """
    Returns the minimal spanning tree of the graph.

    Parameters
    ----------
    graph : Graph
        The graph from which to find the minimal spanning tree.

    Returns
    -------
    Graph
        The minimal spanning tree of the graph.
    """
    result = Graph()
    result.add_edges_from(nx.minimum_spanning_tree(nx.Graph(graph)).edges)
    return result


def color(graph: Graph, strategy: str="connected_sequential_dfs") -> dict[Vertex, int] | None:
    """
    Returns the coloring of the graph.

    Parameters
    ----------
    graph : Graph
        The graph to color.

    Returns
    -------
    dict[Vertex, int] | None
        The coloring of the graph, or None if the graph is not
        bipartite.
    """
    return nx.greedy_color(nx.Graph(graph), strategy=strategy)


def percolation_centrality(graph: Graph, *, states: None | dict[Vertex, numeric]=None) -> dict[Vertex, float]:
    """
    Returns the percolation centrality of the graph.

    Parameters
    ----------
    graph : Graph
        The graph whose percolation centrality is to be calculated.

    states : dict[Vertex, numeric]
        The state of each node. Default: equal weight for all nodes.

    Returns
    -------
    dict[Vertex, float]
        The percolation centrality of the graph.
    """
    states_ = states or {k:1.0 for k in graph.nodes}
    return nx.percolation_centrality(graph, states=states_) # type: ignore
