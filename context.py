from hlt import Position
from typing import List


class ShipRole:
    COLLECTOR: str = "COLLECTOR"
    SETTLER: str = "SETTLER"
    KAMIKAZE: str = "KAMIKAZE"


class ShipAssignment:
    UNASSIGNED: str = "UNASSIGNED"
    DROPOFF: str = "DROPOFF"
    COLLECT: str = "COLLECT"


class ShipContext:
    """
    Additional context for a ship.

    TODO:
     - Do we want to pull everything we know about a ship here and on the beginnging of each turn map the Ship objs
       to this context? Might make life a little easier, but may also have a time cost...
    """
    def __init__(self, role: ShipRole=ShipRole.COLLECTOR, assignment: ShipAssignment=ShipAssignment.UNASSIGNED, destination: Position=None, path: List=None):
        self.role: ShipRole = role
        self.assignment: ShipAssignment = assignment
        self.destination: Position = destination
        self.path: List = path


class ResourceFocus:
    """
    Current focus of resources, to prioritize decisions.

    spawn ships - spend any available resources on spawning new ships
    plant dropoff - spend any available resources on having settler(s) build a new dropoff location
    stockpile - don't spend any resources
    """
    SPAWN_SHIPS: str = "SPAWN_SHIPS"
    BUILD_DROPOFF: str = "BUILD_DROPOFF"
    STOCKPILE: str = "STOCKPILE"
