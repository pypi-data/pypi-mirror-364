import networkx as nx


class Graph(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
# Graph = nx.DiGraph
