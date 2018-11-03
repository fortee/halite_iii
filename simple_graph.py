import logging
import sys


class Graph:
    def __init__(self):
        self._nodes = {}
        self._node_count = 0

    def __repr__(self):
        return repr([node for _, node in self._nodes.items()]

    def add_node(self, value):  # Does this prevent me from having the same value on a node???
        node = _Node(value)
        self._nodes[value] = node
        self._node_count += 1
        return node

    def add_edge(self, src, dest, weight):
        if src not in self._nodes or dest not in self._nodes:
            raise SimpleGraphException(f"adding edge from src={src} to dest={dest} required both to exist in graph!")

        self._nodes[src].add_neighbor(self._nodes[dest], weight)
        logging.info(f"Directed edge from src={src} to dest={dest} with weight={weight} added to graph.")

    def get_nodes(self):
        return self._nodes

    def get_node(self, value):
        if value not in self._nodes.keys():
            raise SimpleGraphException(f"value={value} not in graph!")


class _Node:
    def __init__(self, value):
        self._value = value
        self._neighbors = {}

    def __repr__(self):
        return f"{self._value}: {self.get_neighbors()}"

    def add_neighbor(self, neighbor, weight=0):
        self._neighbors[neighbor] = weight

    def get_neighbors(self):
        return self._neighbors.keys()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]


class SimpleGraphException(Exception):
    pass


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    g = Graph()
    g.add_node("A")
    g.add_node("B")

    g.add_edge("B", "A", 1.0)
    g.add_edge("A", "B", 1.0)

    logging.info(g)

