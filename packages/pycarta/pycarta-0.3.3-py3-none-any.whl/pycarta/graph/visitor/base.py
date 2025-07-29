from __future__ import annotations

from abc import ABC, abstractmethod
from pycarta.graph.graph import Graph
from pycarta.graph.iterator import PreorderIterator, PostorderIterator
from pycarta.graph.vertex import Vertex
from typing import Callable


class Visitor(ABC):
    def __init__(self, fn: Callable):
        self.fn = fn
    
    @abstractmethod
    def __call__(self, *args, **kwds):
        return self.fn(*args, **kwds)
    

# Preserve for future use.
# class UnaryVisitor(Visitor):
#     def __call__(self, x, **kwds):
#         return super().__call__(x, **kwds)
    

class BinaryVisitor(Visitor):
    def __call__(self, lhs, rhs, **kwds):
        return super().__call__(lhs, rhs, **kwds)


class Aggregator(BinaryVisitor):
    """
    Exposes the "Visitor Pattern" to aggregate data from child-to-parent
    through the connections present in a graph. Function calls are made as

        f(parent, child)

    An Aggregator may be constructed with an optional binary function that
    accepts two Vertex objects. Any return value is discarded.
    
    By default, the fields from the child Vertex are joined with the fields in
    the parent Vertex and flattened. The parent holds the resulting data. This
    is roughly equal to:

        f(parent, const child)

    where "parent" is updated in place.

    Methods
    -------
    recurse:
        The visitor function is applied recursively to all pairs, e.g.
        f(f(...f(first, second), third)..., last).

    adjacent: The visitor function is applied to each pair, e.g.
        f : f(first, second), f(second, third), ..., f(pentultimate, last)
    """
    def __init__(self, fn: Callable):
        super().__init__(fn)

    def recurse(self, graph: Graph, *, source: None | Vertex | list[Vertex]=None) -> None:
        """
        Each Vertex is populated with fields from all descendents.

        Parameters
        ----------
        graph : Graph
            The directed graph to traverse when aggregating fields.
        source : (optional) Vertex | list[Vertex]
            A Vertex or list of Vertexes from where to start the graph
            traversal. Default: All roots (in-degree of 0).
        """
        # aggregation updates the parent
        for child in PostorderIterator(graph, source=source):
            for parent in graph.predecessors(child):
                self(parent, child)
    
    def adjacent(self, graph: Graph, *, source: None | Vertex | list[Vertex]=None) -> None:
        """
        Each Vertex is populated with fields from its immediate descendent.

        Parameters
        ----------
        graph : Graph
            The directed graph to traverse when aggregating fields.
        source : (optional) Vertex | list[Vertex]
            A Vertex or list of Vertexes from where to start the graph
            traversal. Default: All roots (in-degree of 0).
        """
        # aggregation updates the parent
        for child in PreorderIterator(graph, source=source):
            for parent in graph.predecessors(child):
                self(parent, child)


class Propagator(BinaryVisitor):
    """
    Exposes the "Visitor Pattern" to propagate data from parent-to-child
    through the connections present in a directed graph, e.g.

        f(child, parent)

    A Propagator may be constructed with an optional binary function that
    accepts two Vertex objects. Any return value is discarded.
    
    By default, the fields from the child Vertex are joined with the fields in
    the parent Vertex and flattened. Fields already present in the child Vertex
    are  excluded. The child Vertex holds the resulting set of data. This is
    equivalent to:

        f(child, const parent)

    where "child" is modified in place.

    Methods
    -------
    recurse:
        The visitor function is applied recursively to all pair, e.g.
        f(f(...f(first, second), third)..., last).

    adjacent: The visitor function is applied to each pair, e.g.
        f : f(first, second), f(second, third), ..., f(pentultimate, last)
    """    
    def __init__(self, fn: Callable):
        super().__init__(fn)

    def recurse(self, graph: Graph, *, source: None | Vertex | list[Vertex]=None) -> None:
        """
        Each Vertex is populated with fields from all predecessors.

        Parameters
        ----------
        graph : Graph
            The directed graph to traverse when propagating fields.
        source : (optional) Vertex | list[Vertex]
            A Vertex or list of Vertexes from where to start the graph
            traversal. Default: All roots (in-degree of 0).
        """
        # propagation updates the child
        for parent in PreorderIterator(graph, source=source):
            for child in graph.successors(parent):
                self(child, parent)

    def adjacent(self, graph: Graph, *, source: None | Vertex | list[Vertex]=None) -> None:
        """
        Each Vertex is populated with fields from its immediate predecessor.

        Parameters
        ----------
        graph : Graph
            The directed graph to traverse when propagating fields.
        source : (optional) Vertex | list[Vertex]
            A Vertex or list of Vertexes from where to start the graph
            traversal. Default: All roots (in-degree of 0).
        """
        # propagation updates the child
        for parent in PostorderIterator(graph, source=source):
            for child in graph.successors(parent):
                self(child, parent)
