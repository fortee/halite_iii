import heapq
import logging


def dijkstra(graph, src, dest):
    """
    Originally I started following Skiena's implementation of Dijkstra's algorithm, but it wasn't quite what I wanted.

    I'm not sure if this technically is still Dijkstra, but it seems to be doing what I want.

    Note: Works for non-negative weights only!
    """
    nodes = graph.get_nodes()
    path_heap = [_Path([src], 0.0)]
    heapq.heapify(path_heap)

    completed_path_heap = []
    heapq.heapify(completed_path_heap)
    i = 0
    while path_heap:
        logging.debug(f"i={i}")
        i += 1
        path = heapq.heappop(path_heap)
        if completed_path_heap:
            logging.debug(f"Current best path={completed_path_heap[0]}")
        else:
            logging.debug(f"Still seeking first completed path...")
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


def dijkstra_halite(graph, src, dest, distance_weight):
    """
    Halite-specific variant of dijkstra, general didn't work, since it spent a bunch fo time searching paths completely
    in the wrong direction.

    Note: Works for non-negative weights only!
    """
    nodes = graph.get_nodes()
    initial_distance_cost = src.distance_to(dest) * distance_weight
    path_heap = [_HalitePath(nodes=[src], game_cost=0.0, distance_cost=initial_distance_cost)]
    heapq.heapify(path_heap)

    completed_path_heap = []
    heapq.heapify(completed_path_heap)
    i = 0
    while path_heap:
        logging.debug(f"i={i}")
        i += 1
        path = heapq.heappop(path_heap)
        if completed_path_heap:
            logging.debug(f"Current best path={completed_path_heap[0]}")
        else:
            logging.debug(f"Still seeking first completed path...")
        current = path.nodes[-1]
        if current == dest:
            heapq.heappush(completed_path_heap, path)
            if len(completed_path_heap) > 100:
                break
        current_node = nodes[current]
        neighbors = current_node.get_neighbors()

        for neighbor in neighbors:
            if neighbor in path.nodes:  # TODO: Is `in` on Python Lists O(n)???
                continue
            new_nodes = path.nodes + [neighbor]
            distance_cost = distance_weight * dest.distance_to(new_nodes[-1])
            new_cost = path.game_cost + current_node.get_weight(neighbor)
            new_path = _HalitePath(nodes=new_nodes, game_cost=new_cost, distance_cost=distance_cost)
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

    def __repr__(self):
        return self.nodes.__repr__() + self.cost.__repr__()


class _HalitePath:
    """
    class to keep track of a path on a heapq. Only the cost is considered when placing on the heap
    """
    def __init__(self, nodes, game_cost, distance_cost):
        self.nodes = nodes
        self.game_cost = game_cost
        self.distance_cost = distance_cost

    def __gt__(self, other):
        return self.game_cost + self.distance_cost > other.game_cost + other.distance_cost

    def __lt__(self, other):
        return self.game_cost + self.distance_cost < other.game_cost + other.distance_cost

    def __eq__(self, other):
        return self.game_cost + self.distance_cost == other.game_cost + other.distance_cost

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.nodes.__repr__() + (self.game_cost + self.distance_cost).__repr__()
