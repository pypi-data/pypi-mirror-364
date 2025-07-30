import networkx as nx
from abc import ABC, abstractmethod
from pycarta.graph.graph import Graph
from pycarta.graph.util import as_list
from pycarta.graph.vertex import Vertex


class NodeIterator(ABC):
    """
    Base class for iterating through nodes. All iterators require a graph over
    which to iterate and an optional source, or list of sources, from which the
    iteration should start. If no source is provided the graph is iterated
    in a non-deterministic order.
    """
    def __init__(self, graph: Graph, *, source: None | Vertex | list[Vertex]=None):
        self._graph__ = graph
        if isinstance(source, Vertex):
            self._sources__ = [source]
        else:
            self._sources__ = source

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError(f"GraphIterator subclass must define __iter__.")
    
    @property
    def graph(self):
        return self._graph__
    
    @property
    def sources(self):
        return self._sources__


class DfsGraphIterator(NodeIterator):
    """
    Base class for a depth first iterator through a graph. Extends
    "NodeIterator" in its default sources. If not specified, the graph is
    traversed starting from all root nodes, e.g. nodes with in-degree equal
    to 0.
    """
    def __init__(self, graph: Graph, *, source: None | Vertex | list[Vertex]=None):
        super().__init__(graph, source=source)
        self._sources__ = (
            self._sources__ or
            [v for v in self._graph__.nodes if self._graph__.in_degree(v) == 0]
        )


class PreorderIterator(DfsGraphIterator):
    """
    Iterate through a graph in a preorder fashion: root-left-right.
    """
    def __iter__(self):
        for source in self.sources: # type: ignore
            for vertex in nx.dfs_preorder_nodes(self.graph, source):
                yield vertex


class PostorderIterator(DfsGraphIterator):
    """
    Iterate through a graph in a postorder fashion: left-right-root.
    """
    def __iter__(self):
        for source in self.sources: # type: ignore
            for vertex in nx.dfs_postorder_nodes(self.graph, source):
                yield vertex


class TopologicalSortIterator(NodeIterator):
    """
    Iterate through a graph in topological order.
    """
    def __iter__(self):
        for vertex in nx.topological_sort(self.graph):
            yield vertex
