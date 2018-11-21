import dijkstra
import logging
import time

from context import ShipContext
from exceptions import HaliteTimeoutInterrupt
from hlt import constants, Game
from management import HaliteManager


NAME = "Crush-v0.4"


class Crush:
    """
    Named after one of my favorite characters, Crush from Finding Nemo. This is my first family of Halite III bots.
    """
    def __init__(self,
                 game: Game,
                 manager: HaliteManager,
                 name: str = NAME,
                 ):
        self._game = game
        self._manager = manager
        self._name = name

    def run(self):
        self._initialize()
        self._mark_ready()
        while True:
            self._turn()

    def _initialize(self):
        logging.info("Crush initializing!")

    def _mark_ready(self):
        logging.info("Crush reporting ready!")
        self._game.ready(self._name)

    def _turn(self):
        self._manager.mark_turn()
        command_queue = []
        ships_context = {}

        try:
            turn_tic = time.perf_counter()
            self._game.update_frame()
            me = self._game.me
            game_map = self._game.game_map
            game_graph = game_map.to_graph()
            my_ships = me.get_ships()
            shipyard = me.shipyard
            toc = time.perf_counter()
            logging.info(f"Turn initialization took {toc-turn_tic} seconds")
            self._manager.clock_check()

            for ship in my_ships:
                self._manager.clock_check()

                if ship.id not in ships_context:
                    logging.info(f"Initializing ship context for ship={ship.id}")
                    ships_context[ship.id] = ShipContext()

                ship_context = ships_context[ship.id]
                ship_context = None

                if ship.is_full and not ship_values[ship.id]['seeking_home']:
                    # This ship is now seeking the shipyard and will continue to do so despite the cost!
                    ship_values[ship.id]['seeking_home'] = True
                    logging.info(f"ship {ship.id} is full, now set to seeking shipyard at {shipyard.position}")
                    path = dijkstra.dijkstra_halite(game_graph, ship.position, shipyard.position,
                                                    distance_weight=1000)
                    direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
                    command_queue.append(ship.move(direction))
                elif not ship_values[ship.id]['seeking_home'] and ship.position == ship_values[ship.id]["target"]:
                    logging.info(f"ship {ship.id} reached target!, now seeking home")
                    ship_values[ship.id]['seeking_home'] = True
                    path = dijkstra.dijkstra_halite(game_graph, ship.position, shipyard.position,
                                                    distance_weight=1000)
                    direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
                    command_queue.append(ship.move(direction))
                elif ship_values[ship.id]['seeking_home'] and ship.position == shipyard.position:
                    logging.info(f"ship {ship.id} has reached the shipyard. No longer seeking it")
                    ship_values[ship.id]['seeking_home'] = False
                    ship_values[ship.id]['target'] = assign_target(game_map=game_map)
                    logging.info(f"ship {ship.id} seeking target of {ship_values[ship.id]['target']}")
                    path = dijkstra.dijkstra_halite(game_graph, ship.position, ship_values[ship.id]["target"],
                                                    distance_weight=1000)
                    direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
                    command_queue.append(ship.move(direction))
                elif ship_values[ship.id]['seeking_home']:
                    logging.info(f"ship {ship.id} is continuing to seek shipyard at {shipyard.position}")
                    path = dijkstra.dijkstra_halite(game_graph, ship.position, shipyard.position,
                                                    distance_weight=1000)
                    direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
                    command_queue.append(ship.move(direction))
                elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
                    logging.info(f"ship {ship.id} seeking target of {ship_values[ship.id]['target']}")
                    path = dijkstra.dijkstra_halite(game_graph, ship.position, ship_values[ship.id]["target"],
                                                    distance_weight=1000)
                    direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
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
            self._game.end_turn(command_queue)


