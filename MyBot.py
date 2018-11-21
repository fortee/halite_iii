#!/usr/bin/env python3
# Python 3.6

import hlt
import logging
import os

from crush import Crush
from management import HaliteManager


def configure_logs(bot_id, log_level=logging.INFO):
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging.basicConfig(
        filename="logs/bot-{}.log".format(bot_id),
        filemode="w",
        level=log_level,
    )


# NB: I normally do the usual `if __name__ == '__main__'` thing here but that would make DebugMyBot.py a little bit
# cumbersome, so we just can't import MyBot.py anywhere, which should be OK.
game = hlt.Game()
manager = HaliteManager()
configure_logs(bot_id=game.my_id, log_level=logging.INFO)

crush = Crush(game=game, manager=manager)
crush.run()
