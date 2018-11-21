#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import dijkstra
import hlt
import logging
import random
import time

from hlt import constants
from hlt.positionals import Direction, Position
from random import randint

""" <<<Game Begin>>> """

# This game object contains the initial game state.
random.seed(int(time.time()))
game = hlt.Game(log_level=logging.INFO)

# Do pre-processing here.
game_map = game.game_map
me = game.me

# Ready starts the 2 second clock
game.ready("Crush_v0.4")


# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

TURN_SEC_THRES = 1.8


class HaliteTimeoutInterrupt(Exception):
    pass


class ShipContext:
    def __init__(self, role="COLLECTOR", assignment="COLLECT", destination=None, path=None):
        self.role = role
        self.assignment = assignment
        self.destination = destination
        self.path = path


def log_state(me, game_map):
    logging.info(f"halite_amount={me.halite_amount}")
    ships = me.get_ships()
    for ship in ships:
        logging.info({ship})


def compute_ship_target(game_map):

    x, y = randint(0, game_map.height), randint(0, game_map.width)
    return Position(x, y)


# TODO: R. Sokolowski
# Is there a way to have this context part of the Ship object? The _generate method tramples any fields I add to the
# Ship class, though I didn't try hard to find a better way.
ship_values = {}


def compute_path_to_target():
    pass


def should_ship_step(game_map, ship, path):
    if ship.is_full:
        return True

    # If cost of leaving is less than reward for staying, we should step
    if (0.10 * game_map[ship.position].halite_amount) <= (0.25 * game_map[path[0]].halite_amount):
        return True

    return False


def clock_check(turn_tic):
    dt = time.perf_counter() - turn_tic
    logging.info(f"Clock check: time spent on turn so far dt={dt} seconds")
    if dt >= TURN_SEC_THRES:
        logging.warning(f"dt greater than threshold of {TURN_SEC_THRES} seconds! Aborting turn!")
        raise HaliteTimeoutInterrupt()


command_queue = []
ships_context = {}

while True:
    try:
        turn_tic = time.perf_counter()
        game.update_frame()
        me = game.me
        game_map = game.game_map
        game_graph = game_map.to_graph()
        my_ships = me.get_ships()
        shipyard = me.shipyard
        toc = time.perf_counter()
        logging.info(f"Turn initialization took {toc-turn_tic} seconds")
        clock_check(turn_tic=turn_tic)

        for ship in my_ships:
            clock_check(turn_tic=turn_tic)

            if ship.id not in ships_context:
                logging.info(f"Initializing ship context for ship={ship.id}")
                ships_context[ship.id] = ShipContext()

            ship_context = ships_context[ship.id]
            ship_context = None

            if ship.is_full and not ship_values[ship.id]['seeking_home']:
                # This ship is now seeking the shipyard and will continue to do so despite the cost!
                ship_values[ship.id]['seeking_home'] = True
                logging.info(f"ship {ship.id} is full, now set to seeking shipyard at {shipyard.position}")
                path = dijkstra.dijkstra_halite(game_graph, ship.position, shipyard.position, distance_weight=1000)
                direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
                command_queue.append(ship.move(direction))
            elif not ship_values[ship.id]['seeking_home'] and ship.position == ship_values[ship.id]["target"]:
                logging.info(f"ship {ship.id} reached target!, now seeking home")
                ship_values[ship.id]['seeking_home'] = True
                path = dijkstra.dijkstra_halite(game_graph, ship.position, shipyard.position, distance_weight=1000)
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
                path = dijkstra.dijkstra_halite(game_graph, ship.position, shipyard.position, distance_weight=1000)
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
        if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
            command_queue.append(me.shipyard.spawn())

    except HaliteTimeoutInterrupt as timeout_ex:
        logging.warning(f"HaliteTimeoutInterrupt caught!")

    finally:
        game.end_turn(command_queue)
