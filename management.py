import logging
import os
import time

from exceptions import HaliteTimeoutInterrupt


TURN_SEC_THRES = 1.8


class HaliteManager:
    """
    Class owning transforming state, logging state, checking time etc, maybe I'll throw business logic here too, but
    that's not what I'm intending atm.
    """
    def __init__(self):
        self._turn_tic: float = 0.0

    def mark_turn(self, turn_number: int) -> None:
        """
        Marks time, intended for the bot to mark on turn start and monitor throughout the duration of the turn
        :turn_number: int
        :return:
        """
        self._turn_tic = time.perf_counter()

        # NB: To keep timing closer to reality, this method should get called before update frame, which is the thing
        # that increments turn_number. So I'm preemptively incrementing the turn count.
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
