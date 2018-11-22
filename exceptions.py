class HaliteTimeoutInterrupt(Exception):
    """
    Exception used to interrupt game loop and take sub-optimal action to avoid the forfeiting the game.
    """
    pass