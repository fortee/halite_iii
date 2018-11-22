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


# NB: No `if __name__ ...` business here to we don't have to duplicate logic in DebugMyBot.py. Should be OK since we're
# not importing this module anywhere.
game = hlt.Game()
manager = HaliteManager(game=game)
configure_logs(bot_id=game.my_id, log_level=logging.INFO)

crush = Crush(game=game, manager=manager)
crush.run()
