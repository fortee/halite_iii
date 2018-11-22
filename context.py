from hlt import Position
from typing import List


class ShipRole:
    COLLECTOR: str = "COLLECTOR"
    SETTLER: str = "SETTLER"
    KAMIKAZE: str = "KAMIKAZE"


class ShipAssignment:
    DROPOFF: str = "DROPOFF"
    COLLECT: str = "COLLECT"


class ShipContext:
    """
    Additional context for a ship.
    """
    def __init__(self, role: ShipRole=ShipRole.COLLECTOR, assignment: ShipAssignment=ShipAssignment.COLLECT, destination: Position=None, path: List=None):
        self.role: ShipRole = role
        self.assignment: ShipAssignment = assignment
        self.destination: Position = destination
        self.path: List = path
