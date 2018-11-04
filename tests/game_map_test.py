import pytest

from hlt.game_map import GameMap, MapCell, Position


@pytest.fixture
def game_map(mocker):
    cells = [
        [MapCell(Position(0, 0), 10), MapCell(Position(0, 1), 15), MapCell(Position(0, 2), 20)],
        [MapCell(Position(1, 0), 5), MapCell(Position(1, 1), 100), MapCell(Position(1, 2), 18)],
        [MapCell(Position(2, 0), 25), MapCell(Position(2, 1), 23), MapCell(Position(2, 2), 29)],
        [MapCell(Position(3, 0), 17), MapCell(Position(3, 1), 31), MapCell(Position(3, 2), 35)],
    ]
    map = GameMap(cells=cells, width=len(cells[0]), height=len(cells))

    return map


def test_this(game_map):
    cell = game_map[Position(2,3)]

    print(cell)
