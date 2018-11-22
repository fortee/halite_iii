import logging
import time

from exceptions import HaliteTimeoutInterrupt
from hlt import Game


TURN_SEC_THRES = 1.8


class HaliteManager:
    """
    Class owning transforming state, logging state, checking time etc, maybe I'll throw business logic here too, but
    that's not what I'm intending atm.
    """
    def __init__(self, game: Game):
        self._turn_tic: float = 0.0

        N = game.game_map.height
        # According to AlanTuring (somehow I doubt it's him) in the Forums
        # total turns = 300+25*N/8 turns in a game on NxN board
        self.total_turns = int(300 + (25 * N / 8))

    def mark_turn(self, turn_number: int) -> None:
        """
        Marks time, intended for the bot to mark on turn start and monitor throughout the duration of the turn
        :turn_number: int
        :return:
        """
        self._turn_tic = time.perf_counter()

        # NB: To keep timing closer to reality, this method should get called before update frame, which is the thing
        # that increments turn_number. So I'm preemptively incrementing the turn count, so the logs are more readable.
        logging.info(f"Clock check: turn_number={turn_number+1} marked.")

    def clock_check(self, checkpoint_name: str=None) -> None:
        """

        :param checkpoint_name: Optional, for logging purposes only, name this check
        :return:
        """
        dt = time.perf_counter() - self._turn_tic
        logging.info(f"Clock check - {checkpoint_name}: Time since last marked turn: dt={dt} seconds")
        if dt >= TURN_SEC_THRES:
            logging.warning(f"dt greater than threshold of {TURN_SEC_THRES} seconds! Raising timeout interrupt!")
            raise HaliteTimeoutInterrupt()

    @staticmethod
    def log_stats(game: Game) -> None:
        halite = game.me.halite_amount
        turn = game.turn_number
        n_ships = len(game.me.get_ships())
        n_dropoffs = len(game.me.get_dropoffs())

        mean_halite_per_turn = halite / turn if turn > 0 else 0.0
        mean_halite_per_turn_per_ship = (halite / turn) / n_ships if turn > 0 and n_ships > 0 else 0.0

        logging.info(f"""
            Stats for turn={turn}:
            halite={halite}
            n_ships={n_ships}
            n_dropoffs={n_dropoffs}
            mean halite per turn = {mean_halite_per_turn}
            mean halite per turn per ship = {mean_halite_per_turn_per_ship}
        """)
