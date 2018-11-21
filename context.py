

class ShipContext:
    """
    Additional context for a ship.
    """
    def __init__(self, role="COLLECTOR", assignment="COLLECT", destination=None, path=None):
        self.role = role
        self.assignment = assignment
        self.destination = destination
        self.path = path


class ShipRole:
    COLLECTOR = "COLLECTOR"
    SETTLER = "SETTLER"
    KAMIKAZE = "KAMIKAZE"


class Assignment:
    DROPOFF = "DROPOFF"
    COLLECT = "COLLECT"
