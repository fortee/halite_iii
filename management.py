import logging
import time

from exceptions import HaliteTimeoutInterrupt


TURN_SEC_THRES = 1.8


class HaliteManager:
    """
    Class owning transforming state, logging state, checking time etc, maybe I'll throw business logic here too, but
    that's not what I'm intending atm.
    """
    @staticmethod
    def clock_check(turn_tic):
        dt = time.perf_counter() - turn_tic
        logging.info(f"Clock check: time spent on turn so far dt={dt} seconds")
        if dt >= TURN_SEC_THRES:
            logging.warning(f"dt greater than threshold of {TURN_SEC_THRES} seconds! Aborting turn!")
            raise HaliteTimeoutInterrupt()
