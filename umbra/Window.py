from . import Thing
from . import Global, util
import os

class Window(Thing.Thing):
    def __init__(self, facing):
        """facing is the direction out, away from the building interior."""
        Thing.Thing.__init__(self, "a window", os.path.join("thing", "window"))
        self.facing = facing

    def isBlocking(self, who):
        return 1

