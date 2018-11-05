import heapq


def dijkstra(graph, src, dest):
    """
    Originally I started following Skiena's implementation of Dijkstra's algorithm, but it wasn't quite what I wanted.

    I'm not sure if this technically is still Dijkstra, but it seems to be doing what I want.

    Note: Works for non-negative wieghts only!
    """
    nodes = graph.get_nodes()
    path_heap = [_Path([src], 0.0)]
    heapq.heapify(path_heap)

    completed_path_heap = []
    heapq.heapify(completed_path_heap)

    while path_heap:
        path = heapq.heappop(path_heap)
        current = path.nodes[-1]
        if current == dest:
            heapq.heappush(completed_path_heap, path)
        current_node = nodes[current]
        neighbors = current_node.get_neighbors()

        for neighbor in neighbors:
            if neighbor in path.nodes:  # TODO: Is `in` on Python Lists O(n)???
                continue
            new_nodes = path.nodes + [neighbor]
            new_cost = path.cost + current_node.get_weight(neighbor)
            new_path = _Path(nodes=new_nodes, cost=new_cost)
            heapq.heappush(path_heap, new_path)

    best_path = heapq.heappop(completed_path_heap)
    return best_path.nodes[1:]


class _Path:
    """
    class to keep track of a path on a heapq. Only the cost is considered when placing on the heap
    """
    def __init__(self, nodes, cost):
        self.nodes = nodes
        self.cost = cost

    def __gt__(self, other):
        return self.cost > other.cost

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return self.cost == other.cost

    def __ne__(self, other):
        return not self.__eq__(other)
