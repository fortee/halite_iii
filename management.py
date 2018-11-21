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

    def mark_turn(self):
        """
        Marks time, intended for the bot to mark on turn start and monitor throughout the duration of the turn
        :return:
        """
        self._turn_tic = time.time()

    def clock_check(self):
        """
        Checks in to see if we're getting close to timing out.
        :return:
        """
        dt = time.perf_counter() - self._turn_tic
        logging.info(f"Clock check: time since last mark turn: dt={dt} seconds")
        if dt >= TURN_SEC_THRES:
            logging.warning(f"dt greater than threshold of {TURN_SEC_THRES} seconds! Raising timeout interrupt!")
            raise HaliteTimeoutInterrupt()
