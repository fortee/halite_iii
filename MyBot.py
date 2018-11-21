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
game.ready("Crush_v0.3")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

TURN_SEC_THRES = 1.8


def log_state(me, game_map):
    logging.info(f"halite_amount={me.halite_amount}")
    ships = me.get_ships()
    for ship in ships:
        logging.info({ship})


def assign_target(game_map):
    x, y = randint(0, game_map.height), randint(0, game_map.width)
    return Position(x, y)


def randomize_local_path(path, random_chance=20):
    if randint(0, 100) < random_chance:
        pass
    else:
        return path[0]

# TODO: R. Sokolowski
# Is there a way to have this context part of the Ship object? The _generate method tramples any fields I add to the
# Ship class, though I didn't try hard to find a better way.
ship_values = {}

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().

    turn_tic = time.perf_counter()
    command_queue = []
    game.update_frame()
    me = game.me
    game_map = game.game_map
    game_graph = game_map.to_graph()
    my_ships = me.get_ships()
    shipyard = me.shipyard
    toc = time.perf_counter()
    logging.info(f"Turn initialization took {toc-turn_tic} seconds")

    log_state(me=me, game_map=game_map)

    for ship in my_ships:
        dt = toc - turn_tic
        logging.info(f"Time spent on turn so far dt={dt} seconds")
        if dt >= TURN_SEC_THRES:
            logging.warning(f"Aborting turn prematurely to avoid timeout")
            break
        if ship.id not in ship_values:
            ship_values[ship.id] = {
                'seeking_home': False,
                'target': assign_target(game_map=game_map)
            }

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
            path = dijkstra.dijkstra_halite(game_graph, ship.position, ship_values[ship.id]["target"], distance_weight=1000)
            direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
            command_queue.append(ship.move(direction))
        elif ship_values[ship.id]['seeking_home']:
            logging.info(f"ship {ship.id} is continuing to seek shipyard at {shipyard.position}")
            path = dijkstra.dijkstra_halite(game_graph, ship.position, shipyard.position, distance_weight=1000)
            direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
            command_queue.append(ship.move(direction))
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
            logging.info(f"ship {ship.id} seeking target of {ship_values[ship.id]['target']}")
            path = dijkstra.dijkstra_halite(game_graph, ship.position, ship_values[ship.id]["target"], distance_weight=1000)
            direction = game_map.safe_step(ship=ship, path=path, game_graph=game_graph)
            command_queue.append(ship.move(direction))
        else:
            command_queue.append(ship.stay_still())

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
