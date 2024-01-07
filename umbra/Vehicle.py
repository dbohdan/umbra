from . import Sprite, Terrain, Thing
from . import Global, util
import os


class Vehicle(Thing.Thing):
    # boardedSprite=Sprite
    # boarded=Boolean
    # okayTerrains=String[] := Terrain.char
    def __init__(self, name, sprite, boardedSprite, okayTerrains):
        Thing.Thing.__init__(self, name, os.path.join("thing", sprite))
        self.boardedSprite = os.path.join("thing", boardedSprite)
        self.boarded = 0
        self.okayTerrains = okayTerrains

    def draw(self, canvas, nx, ny, facing, light):
        if self.boarded:
            sprname = self.boardedSprite
        else:
            sprname = self.sprite
        spr = Sprite.getSprite(sprname)
        if spr:
            spr.draw(self, canvas, nx, ny, facing, light, self.facing)
        else:
            canvas.drawBlock3D(nx, ny, "#ff0000", "#000000", height=0.5)


def makeBoat(facing):
    boat = Vehicle(
        "rowboat",
        "boat",
        "boat",
        (Terrain.Water.char, Terrain.Dock.char, Terrain.Sand.char),
    )
    boat.facing = facing
    return boat
