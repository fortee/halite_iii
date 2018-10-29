#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging


""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()

# Do pre-processing here.
game_map = game.game_map
me = game.me


# Ready starts the 2 second clock
game.ready("Crush_v0.1")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))


def log_state(me, game_map):
    logging.info(f"halite_amount={me.halite_amount}")
    ships = me.get_ships()
    for ship in ships:
        logging.info({ship})

ship_values = {}

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    command_queue = []
    game.update_frame()
    me = game.me
    game_map = game.game_map
    my_ships = me.get_ships()
    shipyard = me.shipyard

    log_state(me=me, game_map=game_map)

    for ship in my_ships:
        if ship.id not in ship_values:
            ship_values[ship.id] = {'seeking_home': False}
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if ship.is_full and not ship_values[ship.id]['seeking_home']:
            # This ship is now seeking the shipyard and will continue to do so despite the cost!
            ship_values[ship.id]['seeking_home'] = True
            logging.info(f"ship {ship.id} is full, now set to seeking shipyard at {shipyard.position}")
            direction = game_map.naive_navigate(ship, shipyard.position)
            command_queue.append(ship.move(direction))
        elif ship_values[ship.id]['seeking_home'] and ship.position == shipyard.position:
            logging.info(f"ship {ship.id} has reached the shipyard. No longer seeking it")
            ship_values[ship.id]['seeking_home'] = False
            # Move in a random dir
            command_queue.append(ship.move(random.choice([Direction.North, Direction.South, Direction.East, Direction.West])))
        elif ship_values[ship.id]['seeking_home']:
            logging.info(f"ship {ship.id} is continuing to seek shipyard at {shipyard.position}")
            direction = game_map.naive_navigate(ship, shipyard.position)
            command_queue.append(ship.move(direction))
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
            # Move in a random dir
            command_queue.append(ship.move(random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])))
        else:
            command_queue.append(ship.stay_still())

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
