from . import Sprite
from . import Global, util
import os

TERRAINS = {}

TERRAIN_KEY = ""

TRANSPARENT = 0
OPAQUE = 1

Non_Blocking = Global.NON_BLOCKING
Small = Global.SIZE_Small
Medium = Global.SIZE_Medium


class Terrain:
    # char=2-char string
    # name=String
    # blocking=Int # minimum Global.SIZE blocked
    # opaque=Boolean # does it block vision?
    # sprite=String
    # toughness=Int # 0=invulnerable, 1+=damage needed in a single attack to
    #           transform to self.damaged
    # damaged=char # terrain type of what it changes into when destroyed
    def __init__(self, char, name, blocking, opaque, toughness=0, damaged=None):
        self.char = char
        self.name = name
        self.sprite = os.path.join("terrain", util.purifyName(self.name))
        self.blocking = blocking
        self.opaque = opaque
        self.toughness = toughness
        self.damaged = damaged
        TERRAINS[char] = self
        if not isHook(self):
            global TERRAIN_KEY
            TERRAIN_KEY = "%s%2s %s\n" % (TERRAIN_KEY, char, name)

    def __str__(self):
        return self.char

    def damage(self, level, x, y):
        level.setTerrain(x, y, getTerrain(self.damaged))

    def draw(self, canvas, nx, ny, facing, light):
        if self.sprite is None:
            return
        spr = Sprite.getSprite(self.sprite)
        if spr:
            spr.draw(self, canvas, nx, ny, facing, light, Global.North)
            return
        else:
            canvas.drawPanel3D(Global.Side_Bottom, nx, ny, "#ff0000", "#000000")

    def isBlocking(self, who):
        if who.player:
            vehicle = Global.umbra.game.vehicle
            if vehicle:
                return self.char not in vehicle.okayTerrains
        if self.blocking == Non_Blocking:
            return 0
        return who.size >= self.blocking


def getTerrain(char):
    return TERRAINS[char]


def hookForDir(d):
    return TERRAINS["*%c" % Global.DIR_CHARS[d]]


def isHook(ter):
    if ter is None:
        return 0
    return ter.char[0] == "*"


Altar = Terrain("AA", "Altar", Small, TRANSPARENT, 10, "__")
Bush = Terrain("%%", "Bush", Non_Blocking, TRANSPARENT, 3, "..")
Counter = Terrain("#c", "Counter", Small, TRANSPARENT, 8, "_S")
Dock = Terrain("dk", "Dock", Non_Blocking, TRANSPARENT, 12, "~~")
Doorway = Terrain("++", "Doorway", Non_Blocking, TRANSPARENT)
Dungeon_Doorway = Terrain("DD", "Dungeon Doorway", Non_Blocking, TRANSPARENT)
Dungeon_Floor = Terrain("__", "Dungeon Floor", Non_Blocking, TRANSPARENT)
Dungeon_Hook_N = Terrain("*n", "hook n", Non_Blocking, TRANSPARENT)
Dungeon_Hook_E = Terrain("*e", "hook e", Non_Blocking, TRANSPARENT)
Dungeon_Hook_S = Terrain("*s", "hook s", Non_Blocking, TRANSPARENT)
Dungeon_Hook_W = Terrain("*w", "hook w", Non_Blocking, TRANSPARENT)
Dungeon_Wall = Terrain("##", "Dungeon Wall", Small, OPAQUE)
Grass = Terrain("..", "Grass", Non_Blocking, TRANSPARENT)
Hill = Terrain("hh", "Hill", Non_Blocking, TRANSPARENT)
Marsh = Terrain("mm", "Marsh", Non_Blocking, TRANSPARENT)
Mountain = Terrain("MM", "Mountain", Small, OPAQUE)
Road = Terrain("==", "Road", Non_Blocking, TRANSPARENT)
Rough = Terrain("rr", "Rough", Non_Blocking, TRANSPARENT)
Sand = Terrain("ss", "Sand", Non_Blocking, TRANSPARENT)
Scrub = Terrain("sc", "Scrub", Non_Blocking, TRANSPARENT, 4, "sc")
Skyscraper = Terrain("YY", "Skyscraper", Small, OPAQUE)
Sky_Doorway = Terrain("YD", "Sky Doorway", Non_Blocking, TRANSPARENT)
Stairs_Up = Terrain("D<", "Stairs Up", Non_Blocking, TRANSPARENT)
Stairs_Down = Terrain("D>", "Stairs Down", Non_Blocking, TRANSPARENT)
Stone_Floor = Terrain("_S", "Stone Floor", Non_Blocking, TRANSPARENT)
Stone_Wall = Terrain("#S", "Stone Wall", Small, OPAQUE)
Tree = Terrain("tt", "Tree", Medium, OPAQUE, 8, "ts")
Tree_Stump = Terrain("ts", "Tree Stump", Non_Blocking, OPAQUE, 10, "rr")
Unknown = Terrain("--", "Unknown", Small, OPAQUE)
Unknown.sprite = None
Water = Terrain("~~", "Water", Small, TRANSPARENT)

ENC_TERRAIN_OUTDOORS = (Grass, Sand, Rough, Bush, Scrub)
ENC_TERRAIN_INDOORS = (Dungeon_Floor, Stone_Floor)
