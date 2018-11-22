import dijkstra
import logging
import random
import time

from context import ShipAssignment, ShipContext
from exceptions import HaliteTimeoutInterrupt
from hlt import constants, Game, Position
from hlt.game_map import GameMap
from hlt.entity import Ship
from management import HaliteManager
from simple_graph import Graph
from typing import Dict, List


NAME = "Crush-v0.4"
DISTANCE_WEIGHT = 500.0


class Crush:
    """
    Named after one of my favorite characters, Crush from Finding Nemo. This is my first family of Halite III bots.
    """
    def __init__(self,
                 game: Game,
                 manager: HaliteManager,
                 name: str = NAME,
                 distance_weight: float = DISTANCE_WEIGHT
                 ):
        self._game: Game = game
        self._manager: HaliteManager = manager
        self._name: str = name
        self._distance_weight: float = distance_weight

        self._ships_context: Dict[int, ShipContext] = {}

    def run(self) -> None:
        self._initialize()
        self._mark_ready()

        while True:
            self._turn()

    @staticmethod
    def _game_map_to_graph(game_map: GameMap) -> Graph:
        """
        Translate game_map cells to a Graph, where the weight represent the cost of stepping from
        the node to the neighbor.

        NB: This method bothers me a bit since we're "reaching into" the private field `_cells` of the `game_map` obj,
        but I opt'ed to leave the `hlt` package code alone

        :return: simple_graph.Graph
        """
        g = Graph()

        # NB: We're iterating through twice, as simple_graph.Graph requires src and dest nodes to already exist
        # when appending an edge.
        for r, _ in enumerate(game_map._cells):
            for c, cell in enumerate(game_map._cells[r]):
                g.add_node(cell.position)

        for r, _ in enumerate(game_map._cells):
            for c, cell in enumerate(game_map._cells[r]):
                src = Position(c, r)
                cost = cell.halite_amount / 10.0
                # c-1, r+0
                if c-1 >= 0 and c-1 < game_map.height:
                    g.add_edge(src, Position(c-1, r), cost)
                # c+0, r+1
                if r+1 >= 0 and r+1 < game_map.width:
                    g.add_edge(src, Position(c, r+1), cost)
                # c+1, r+0
                if c+1 >= 0 and c+1 < game_map.height:
                    g.add_edge(src, Position(c+1, r), cost)
                # c+0, r-1
                if r-1 >= 0 and r-1 < game_map.width:
                    g.add_edge(src, Position(c, r-1), cost)

        return g

    @staticmethod
    def _should_step(game_map: GameMap, ship: Ship, path: List[Position]):
        if ship.is_full:
            return True

        reward_stay = 0.25 * game_map[ship.position].halite_amount
        reward_step = (0.25 * game_map[path[0]].halite_amount) - (0.10 * game_map[ship.position].halite_amount)
        if reward_step >= reward_stay:
            return True

        return False

    @staticmethod
    def _assign_target(game_map: GameMap) -> Position:
        x = random.randint(0, game_map.width)
        y = random.randint(0, game_map.height)

        return Position(x=x, y=y)

    def _initialize(self) -> None:
        logging.info("Crush initializing!")
        random.seed(int(time.time()))

    def _mark_ready(self) -> None:
        logging.info("Crush reporting as ready!")
        self._game.ready(self._name)

    def _turn(self):
        self._manager.mark_turn(turn_number=self._game.turn_number)
        command_queue: List = []

        try:
            self._game.update_frame()
            me = self._game.me
            game_map = self._game.game_map
            game_graph = self._game_map_to_graph(game_map)
            my_ships = me.get_ships()
            shipyard = me.shipyard
            self._manager.clock_check(checkpoint_name="turn initialization complete")

            # NB: For now all ships are COLLECTORS
            for ship in my_ships:
                self._manager.clock_check(checkpoint_name=f"begin ship={ship.id}")

                if ship.id not in self._ships_context:
                    logging.info(f"Initializing ship context for ship={ship.id}")
                    self._ships_context[ship.id] = ShipContext()

                ship_context = self._ships_context[ship.id]

                # Give assignement to unassigned ships
                if ship_context.assignment == ShipAssignment.UNASSIGNED:
                    ship_context.assignment = ShipAssignment.COLLECT
                    ship_context.destination = self._assign_target(self._game.game_map)

                # If we're full, change assignment
                if ship.is_full:
                    ship_context.assignment = ShipAssignment.DROPOFF
                    ship_context.destination = shipyard.position

                # If we're currenting COLLECTING and we've reached our destination, change
                if ship_context.assignment == ShipAssignment.COLLECT and ship.position == ship_context.destination:
                    ship_context.assignment = ShipAssignment.DROPOFF
                    ship_context.destination = shipyard.position

                # If we're currenting dropping off, and we've reached our destination, give new assignment
                if ship_context.assignment == ShipAssignment.DROPOFF and ship.position == ship_context.destination:
                    ship_context.assignment = ShipAssignment.COLLECT
                    ship_context.destination = self._assign_target(self._game.game_map)

                path = dijkstra.dijkstra_halite(
                    graph=game_graph, src=ship.position, dest=ship_context.destination, distance_weight=self._distance_weight
                )

                if self._should_step(game_map=game_map, ship=ship, path=path):
                    direction = self._game.game_map.safe_step(
                        ship=ship, path=path, game_graph=game_graph
                    )
                    command_queue.append(ship.move(direction))
                else:
                    command_queue.append(ship.stay_still())

            # If the game is in the first 200 turns and you have enough halite, spawn a ship.
            # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
            if self._game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[
                me.shipyard].is_occupied:
                command_queue.append(me.shipyard.spawn())

        except HaliteTimeoutInterrupt as timeout_ex:
            logging.warning(f"HaliteTimeoutInterrupt caught! exception={timeout_ex}")

        finally:
            self._manager.clock_check(checkpoint_name="submit command queue")
            self._game.end_turn(command_queue)
