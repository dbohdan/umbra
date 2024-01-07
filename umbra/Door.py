from . import Item, Script, Sprite, Thing
from . import Global, util
import os

DEBUG = 0

S_Open = 0
S_Closed = 1
S_Locked = 2
STATE_NAMES = ("open", "closed", "locked")


class Door(Thing.Thing):
    # __state=Int
    # trap=Script
    # linkedTo=(x,y,levelnum)
    # stateSprites=[open, closed]
    def __init__(self, facing, state):
        """facing is the direction out, away from the building interior."""
        Thing.Thing.__init__(self, "a door", None)
        self.stateSprites = (
            os.path.join("thing", "door_open"),
            os.path.join("thing", "door_closed"),
        )
        self.setState(state)
        self.facing = facing
        self.trap = None
        self.linkedTo = None

    def __str__(self):
        return "Door %x at %d,%d,%d, state=%d, facing=%d, linkedTo=%s" % (
            id(self),
            self.x(),
            self.y(),
            self.levelnum(),
            self.__state,
            self.facing,
            self.linkedTo,
        )

    def getState(self):
        return self.__state

    def isBlocking(self, who):
        return self.__state != S_Open

    def isOpaque(self):
        return self.__state != S_Open

    def isOpen(self):
        return self.__state == S_Open

    def setState(self, state):
        self.__state = state
        self.sprite = self.stateSprites[state != S_Open]

    def trapped(self, dmg="1 6"):
        self.trap = Script.Script(
            (
                Script.T,
                Script.SAVESTAT,
                Global.Speed,
                0,
                "You barely pull away as a trap fires!",
            ),
            (Script.T, Script.ECHO, "You triggered a poisoned needle trap!"),
            (Script.T, Script.STAT, Global.Wounds, dmg),
        )

    def trigger(self, who):
        if Global.DEBUG:
            print("%s.trigger(%s)" % (self, who.name))
        # not only does it hurt, you don't open it.
        if self.trap:
            self.trap.run(self, who)
            return 1
        s = self.__state
        if s == S_Open:
            self.setState(S_Closed)
            who.message("You close the door.")
        elif s == S_Closed:
            self.setState(S_Open)
            who.message("You open the door.")
        elif s == S_Locked:
            who.message("It's locked - try Locksmith skill!")
        else:
            assert 0, "Unknown door state %d" % s
        self.updateLink()
        return 1

    def updateLink(self):
        if not self.linkedTo:
            return
        if DEBUG:
            print(self)
        otherlevel = Global.umbra.game.getLevel(self.linkedTo[2])
        door = otherlevel.getDoor(self.linkedTo[0], self.linkedTo[1])
        if DEBUG:
            print("    linkedTo door=%s" % door)
        if door:
            door.setState(self.__state)
        if DEBUG:
            print("    after, linkedTo door=%s" % door)
