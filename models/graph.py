"""Undirected graph model. networkx is used only for storage / validation.

JSON form:  {"vertices": ["A","B","C"], "edges": [["A","B"],["B","C"]]}
"""
import networkx as nx

from config import MAX_EDGES, MAX_LABEL_LENGTH, MAX_NODES
from errors import (DuplicateValueError, InvalidInputError, NotFoundError,
                    SizeLimitError)


def normalize_label(raw):
    """Return a clean vertex label or raise InvalidInputError."""
    if raw is None or isinstance(raw, bool):
        raise InvalidInputError("Please enter a vertex name")
    label = str(raw).strip()
    if not label:
        raise InvalidInputError("Please enter a vertex name")
    if len(label) > MAX_LABEL_LENGTH:
        raise InvalidInputError(
            "Vertex names can have at most %d characters" % MAX_LABEL_LENGTH
        )
    return label


class Graph:
    def __init__(self):
        self._g = nx.Graph()

    # ---- (de)serialisation -------------------------------------------------
    @classmethod
    def from_dict(cls, data):
        graph = cls()
        if data is None:
            return graph
        if not isinstance(data, dict):
            raise InvalidInputError("Malformed graph state")
        vertices = data.get("vertices", [])
        edges = data.get("edges", [])
        if not isinstance(vertices, list) or not isinstance(edges, list):
            raise InvalidInputError("Malformed graph state")
        for v in vertices:
            graph.add_vertex(v)
        for edge in edges:
            if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                raise InvalidInputError("Malformed graph state: edges must be pairs")
            graph.add_edge(edge[0], edge[1])
        return graph

    def to_dict(self):
        return {
            "vertices": sorted(self._g.nodes),
            "edges": sorted([sorted(e) for e in self._g.edges]),
        }

    # ---- queries -----------------------------------------------------------
    def is_empty(self):
        return self._g.number_of_nodes() == 0

    def vertex_count(self):
        return self._g.number_of_nodes()

    def edge_count(self):
        return self._g.number_of_edges()

    def vertices(self):
        return sorted(self._g.nodes)

    def has_vertex(self, v):
        return v in self._g

    def has_edge(self, u, v):
        return self._g.has_edge(u, v)

    def neighbors(self, v):
        """Neighbours in sorted order, so BFS / DFS are deterministic."""
        if v not in self._g:
            raise NotFoundError("Vertex '%s' is not in the graph" % v)
        return sorted(self._g.neighbors(v))

    # ---- mutations ---------------------------------------------------------
    def add_vertex(self, raw):
        v = normalize_label(raw)
        if v in self._g:
            raise DuplicateValueError("Vertex '%s' already exists" % v)
        if self._g.number_of_nodes() >= MAX_NODES:
            raise SizeLimitError(
                "The graph is too large to visualise clearly (limit: %d vertices)" % MAX_NODES
            )
        self._g.add_node(v)
        return v

    def remove_vertex(self, raw):
        v = normalize_label(raw)
        if v not in self._g:
            raise NotFoundError("Vertex '%s' is not in the graph" % v)
        self._g.remove_node(v)
        return v

    def add_edge(self, raw_u, raw_v):
        u, v = normalize_label(raw_u), normalize_label(raw_v)
        for x in (u, v):
            if x not in self._g:
                raise NotFoundError("Vertex '%s' is not in the graph" % x)
        if u == v:
            raise InvalidInputError("Self-loops are not allowed in this visualiser")
        if self._g.has_edge(u, v):
            raise DuplicateValueError("Edge (%s, %s) already exists" % (u, v))
        if self._g.number_of_edges() >= MAX_EDGES:
            raise SizeLimitError(
                "The graph has too many edges to visualise clearly (limit: %d edges)" % MAX_EDGES
            )
        self._g.add_edge(u, v)
        return u, v

    def remove_edge(self, raw_u, raw_v):
        u, v = normalize_label(raw_u), normalize_label(raw_v)
        if not self._g.has_edge(u, v):
            raise NotFoundError("Edge (%s, %s) does not exist" % (u, v))
        self._g.remove_edge(u, v)
        return u, v
