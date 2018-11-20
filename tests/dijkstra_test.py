import dijkstra
import pickle
import pytest

from hlt.positionals import Position
from simple_graph import Graph


@pytest.fixture
def game_map():
    """
    Fetch pickled game_map, which was saved via a debugger while playing Halite
    :return:
    """

    with open("./resources/game_map.pickle", 'rb') as fp:
        unpickler = pickle.Unpickler(fp)
        gmap = unpickler.load()

    return gmap


@pytest.fixture
def game_graph(game_map):
    graph = game_map.to_graph()
    return graph


def test_dijkstra_simple_case():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")
    g.add_node("E")

    # A -> B -> C -> D costing 3.0
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "D", 1.0)

    # Cut through E, costing 2.0
    g.add_edge("A", "E", 1.0)
    g.add_edge("E", "D", 1.0)

    path = dijkstra.dijkstra(g, "A", "D")

    assert ["E", "D"] == path


def test_dijkstra_simple_with_dead_ends():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")
    g.add_node("E")
    g.add_node("G")
    g.add_node("H")

    # A -> B -> C -> D costing 3.0
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "D", 1.0)

    # Cut through E, costing 2.0
    g.add_edge("A", "E", 1.0)
    g.add_edge("E", "D", 1.0)

    # Some dead-ends
    g.add_edge("D", "G", 1.0)
    g.add_edge("D", "C", 1.0)
    g.add_edge("A", "H", 0.1)

    path = dijkstra.dijkstra(g, "A", "D")

    assert ["E", "D"] == path


def test_dijkstra_simple_with_negative_costs():
    # Not sure if I'll keep this, but for Halite purposes, I may be able to consider a negative cost to be a reward
    # TODO: This seems to work, can we put negative costs in the nodes of the game_map to graph function??
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")
    g.add_node("E")

    # A -> B -> C -> D costing 3.0
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", -10.0)
    g.add_edge("C", "D", 1.0)

    # Cut through E, costing 2.0
    g.add_edge("A", "E", 1.0)
    g.add_edge("E", "D", 1.0)

    path = dijkstra.dijkstra(g, "A", "D")

    assert ["B", "C", "D"] == path


def test_dijstra_halite(game_graph):
    print("Search for path start")
    path = dijkstra.dijkstra_halite(game_graph, Position(8, 16), Position(23, 4), distance_weight=1000.0)

    print(path)

