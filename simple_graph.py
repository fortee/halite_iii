import logging


class Graph:
    def __init__(self):
        self._nodes = {}
        self._node_count = 0

    def __repr__(self):
        # return repr(self._nodes["A"])
        s = f"Graph object:\n"
        for nid, node in self._nodes.items():
            s += f"\t{nid}: {[n for n in node.get_neighbors()]}\n"

        return s

    def __eq__(self, other):
        if isinstance(other, Graph):
            return self._node_count == other._node_count and self._nodes == other._nodes

        return False

    def add_node(self, value):  # Does this prevent me from having the same value on a node???
        node = _Node(value)
        self._nodes[value] = node
        self._node_count += 1

        return node

    def add_edge(self, src, dest, weight):
        if src not in self._nodes or dest not in self._nodes:
            raise SimpleGraphException(f"adding edge from src={src} to dest={dest} required both to exist in graph!")

        self._nodes[src].add_neighbor(self._nodes[dest], weight)
        logging.debug(f"Directed edge from src={src} to dest={dest} with weight={weight} added to graph.")

    def get_nodes(self):
        return self._nodes

    def get_node(self, value):
        if value not in self._nodes.keys():
            raise SimpleGraphException(f"value={value} not in graph!")

        return self._nodes[value]

    def get_node_count(self):
        return self._node_count


class _Node:
    """
    A node container for a value with meta data about it's neighbors and weights.
    """
    def __init__(self, value):
        self.value = value
        self._neighbors = {}

    def __repr__(self):
        return f"{self.value}: {self.get_neighbors()}"

    def add_neighbor(self, neighbor_node, weight):
        self._neighbors[neighbor_node.value] = weight

    def get_neighbors(self):
        return self._neighbors

    def get_weight(self, neighbor):
        return self._neighbors[neighbor]

    def __eq__(self, other):
        if isinstance(other, _Node):
            return self.value == other.value and self._neighbors == other._neighbors

        return False


class SimpleGraphException(Exception):
    pass
