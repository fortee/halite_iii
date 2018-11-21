import queue
import logging
import random
import time

from . import constants
from .entity import Entity, Shipyard, Ship, Dropoff
from .player import Player
from .positionals import Direction, Position
from .common import read_input
from simple_graph import Graph


class MapCell:
    """A cell on the game map."""
    def __init__(self, position, halite_amount):
        self.position = position
        self.halite_amount = halite_amount
        self.ship = None
        self.structure = None

    @property
    def is_empty(self):
        """
        :return: Whether this cell has no ships or structures
        """
        return self.ship is None and self.structure is None

    @property
    def is_occupied(self):
        """
        :return: Whether this cell has any ships
        """
        return self.ship is not None

    @property
    def has_structure(self):
        """
        :return: Whether this cell has any structures
        """
        return self.structure is not None

    @property
    def structure_type(self):
        """
        :return: What is the structure type in this cell
        """
        return None if not self.structure else type(self.structure)

    def mark_unsafe(self, ship):
        """
        Mark this cell as unsafe (occupied) for navigation.

        Use in conjunction with GameMap.naive_navigate.
        """
        self.ship = ship

    def __eq__(self, other):
        return self.position == other.position

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'MapCell({}, halite={})'.format(self.position, self.halite_amount)


class GameMap:
    """
    The game map.

    Can be indexed by a position, or by a contained entity.
    Coordinates start at 0. Coordinates are normalized for you
    """
    def __init__(self, cells, width, height):
        self.width = width
        self.height = height
        self._cells = cells

        self._graph = None

    def __getitem__(self, location):
        """
        Getter for position object or entity objects within the game map
        :param location: the position or entity to access in this map
        :return: the contents housing that cell or entity
        """
        if isinstance(location, Position):
            location = self.normalize(location)
            return self._cells[location.y][location.x]
        elif isinstance(location, Entity):
            return self._cells[location.position.y][location.position.x]
        return None

    def calculate_distance(self, source, target):
        """
        Compute the Manhattan distance between two locations.
        Accounts for wrap-around.
        :param source: The source from where to calculate
        :param target: The target to where calculate
        :return: The distance between these items
        """
        source = self.normalize(source)
        target = self.normalize(target)
        resulting_position = abs(source - target)
        return min(resulting_position.x, self.width - resulting_position.x) + \
            min(resulting_position.y, self.height - resulting_position.y)

    def normalize(self, position):
        """
        Normalized the position within the bounds of the toroidal map.
        i.e.: Takes a point which may or may not be within width and
        height bounds, and places it within those bounds considering
        wraparound.
        :param position: A position object.
        :return: A normalized position object fitting within the bounds of the map
        """
        return Position(position.x % self.width, position.y % self.height)

    @staticmethod
    def _get_target_direction(source, target):
        """
        Returns where in the cardinality spectrum the target is from source. e.g.: North, East; South, West; etc.
        NOTE: Ignores toroid
        :param source: The source position
        :param target: The target position
        :return: A tuple containing the target Direction. A tuple item (or both) could be None if within same coords
        """
        if target.y > source.y:
            y_dir = 1 # down / south
        elif target.y < source.y:
            y_dir = -1 # up / north
        else:
            y_dir = 0 # no y component of movement

        if target.x > source.x:
            x_dir = 1 # right / east
        elif target.x < source.x:
            x_dir = -1 # left / I thought you said "weast"!
        else:
            x_dir = 0 # noxy component of movement

        return (x_dir, y_dir)

    def safe_step(self, ship, path, game_graph):
        """
        takes a "safe step" along the defined path.

        TODO:
         - Should this be part of the hlt code?
         - Do we need to keep additional context in
        :param ship:
        :param path:
        :param game_graph:
        :return:
        """
        # First try the path[0], if it's occupied, pick a random neighbor
        preferred_direction = self._get_target_direction(ship.position, path[0])
        directions = [Direction.North, Direction.South, Direction.East, Direction.West]
        random.shuffle(directions)
        directions = [preferred_direction] + directions  # TODO: R. Sokoloski - Remove dupe
        for direction in directions:
            target_pos = ship.position.directional_offset(direction)
            if not self[target_pos].is_occupied:
                self[target_pos].mark_unsafe(ship)
                return direction

        logging.info(f"safe_step for ship {ship.id} as exhaused all directions, staying still")
        return Direction.Still

    @staticmethod
    def _generate():
        """
        Creates a map object from the input given by the game engine
        :return: The map object
        """
        map_width, map_height = map(int, read_input().split())
        game_map = [[None for _ in range(map_width)] for _ in range(map_height)]
        for y_position in range(map_height):
            cells = read_input().split()
            for x_position in range(map_width):
                game_map[y_position][x_position] = MapCell(Position(x_position, y_position),
                                                           int(cells[x_position]))
        return GameMap(game_map, map_width, map_height)

    def _update(self):
        """
        Updates this map object from the input given by the game engine
        :return: nothing
        """
        # Mark cells as safe for navigation (will re-mark unsafe cells
        # later)
        for y in range(self.height):
            for x in range(self.width):
                self[Position(x, y)].ship = None

        for _ in range(int(read_input())):
            cell_x, cell_y, cell_energy = map(int, read_input().split())
            self[Position(cell_x, cell_y)].halite_amount = cell_energy

    def to_graph(self):
        """
        Translate game_map cells to a Graph, where the weight represent the cost of stepping from
        the node to the neighbor.

        :return: simple_graph.Graph
        """
        tic = time.perf_counter()
        g = Graph()

        # NB: We're iterating through twice, as simple_graph.Graph requires src and dest nodes to already exist
        # when appending an edge.
        for r, _ in enumerate(self._cells):
            for c, cell in enumerate(self._cells[r]):
                g.add_node(cell.position)

        for r, _ in enumerate(self._cells):
            for c, cell in enumerate(self._cells[r]):
                src = Position(c, r)
                cost = cell.halite_amount / 10.0
                # c-1, r+0
                if c-1 >= 0 and c-1 < self.height:
                    g.add_edge(src, Position(c-1, r), cost)
                # c+0, r+1
                if r+1 >= 0 and r+1 < self.width:
                    g.add_edge(src, Position(c, r+1), cost)
                # c+1, r+0
                if c+1 >= 0 and c+1 < self.height:
                    g.add_edge(src, Position(c+1, r), cost)
                # c+0, r-1
                if r-1 >= 0 and r-1 < self.width:
                    g.add_edge(src, Position(c, r-1), cost)

        toc = time.perf_counter()
        logging.info(f"Translating game_map to graph took dt={toc-tic} seconds.")
        self._graph = g
        return g

    def get_cheapest_path(self, src, destination):
        """

        :param src:
        :param destination:
        :return:
        """
        pass