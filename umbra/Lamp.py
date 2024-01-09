import os

from . import Thing

S_Off = 0
S_On = 1
S_Always_On = 2
STATE_NAMES = ("off", "on", "always on")


class Lamp(Thing.Thing):
    # state=Int
    # on_light_level=Int
    def __init__(self, light_level, state):
        Thing.Thing.__init__(self, "a lamp", os.path.join("thing", "lamp"))
        self.on_light_level = light_level
        self.setState(state)

    def isOn(self):
        return self.state

    def setState(self, state):
        self.state = state
        if state:
            self.light_level = self.on_light_level
        elif hasattr(self, "light_level"):
            del self.light_level

    def trigger(self, who):
        if self.state == S_Always_On:
            return 0
        who.message("<click>")
        self.setState(1 - self.state)
        return 1
