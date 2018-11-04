import pytest

from hlt.game_map import GameMap, MapCell, Position
from simple_graph import Graph


@pytest.fixture
def game_map():
    cells = [
        [MapCell(Position(0, 0), 10), MapCell(Position(0, 1), 15), MapCell(Position(0, 2), 20)],
        [MapCell(Position(1, 0), 5), MapCell(Position(1, 1), 100), MapCell(Position(1, 2), 18)],
        [MapCell(Position(2, 0), 25), MapCell(Position(2, 1), 23), MapCell(Position(2, 2), 29)],
    ]
    map = GameMap(cells=cells, width=len(cells[0]), height=len(cells))

    return map


def test_game_map_to_graph(game_map):
    g = Graph()

    g.add_node(Position(0, 0))
    g.add_node(Position(0, 1))
    g.add_node(Position(0, 2))
    g.add_node(Position(1, 0))
    g.add_node(Position(1, 1))
    g.add_node(Position(1, 2))
    g.add_node(Position(2, 0))
    g.add_node(Position(2, 1))
    g.add_node(Position(2, 2))

    # NB:
    # - Cost is 10% of the halite in the origin cell
    # - Only cardinal directions are considered.
    # TODO: - Is there rounding on this cost???
    g.add_edge(Position(0, 0), Position(0, 1), 1.0)
    g.add_edge(Position(0, 0), Position(1, 0), 1.0)

    g.add_edge(Position(0, 1), Position(0, 2), 1.5)
    g.add_edge(Position(0, 1), Position(1, 1), 1.5)
    g.add_edge(Position(0, 1), Position(0, 0), 1.5)

    g.add_edge(Position(0, 2), Position(1, 2), 2.0)
    g.add_edge(Position(0, 2), Position(0, 2), 2.0)

    g.add_edge(Position(1, 0), Position(0, 0), 0.5)
    g.add_edge(Position(1, 0), Position(1, 1), 0.5)
    g.add_edge(Position(1, 0), Position(2, 0), 0.5)

    g.add_edge(Position(1, 1), Position(0, 1), 10.0)
    g.add_edge(Position(1, 1), Position(1, 2), 10.0)
    g.add_edge(Position(1, 1), Position(2, 1), 10.0)
    g.add_edge(Position(1, 1), Position(1, 0), 10.0)

    g.add_edge(Position(1, 2), Position(0, 2), 1.8)
    g.add_edge(Position(1, 2), Position(2, 2), 1.8)
    g.add_edge(Position(1, 2), Position(1, 1), 1.8)

    g.add_edge(Position(2, 0), Position(1, 0), 2.5)
    g.add_edge(Position(2, 0), Position(2, 1), 2.5)

    g.add_edge(Position(2, 1), Position(1, 1), 2.3)
    g.add_edge(Position(2, 1), Position(2, 2), 2.3)
    g.add_edge(Position(2, 1), Position(2, 0), 2.3)

    g.add_edge(Position(2, 2), Position(1, 2), 2.9)
    g.add_edge(Position(2, 2), Position(2, 1), 2.9)

    game_graph = game_map.to_graph()

    assert g == game_map
