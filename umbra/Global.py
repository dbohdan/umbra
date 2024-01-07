# debugging flags
DEBUG = 0
FASTDAY = 0
TESTCHAR = 0  # 1=lots of cash & -hack equip, 2=only starting cash
TIMING = 0
SHOWWORLD = 0
COMBAT_DEBUG = 0
LIGHT_DEBUG = 0
BRAIN_DEBUG = 0
GZIP = 1
GZIP_LEVEL = 9
LIGHT = 1  # use light levels?
LIGHT_LOS = 1  # check LOS on light? (VERY slow!)
VISICALC = 0  # use visicalc to determine which grids to draw?
START_DEBUG = 0  # 0=town, 1=near temple, 2=near altar, 3=near ruins

VERSION = "0.11"
TITLE = "Umbra %s" % VERSION
COPYRIGHT = """(c) Copyright 2001 by Mark Hughes <kamikaze@kuoi.asui.uidaho.edu>
All Rights Reserved

Visit the web site at <http://kuoi.asui.uidaho.edu/~kamikaze/Umbra/>"""

umbra = None

# world and level size
WORLDSIZE = 64
LEVELSIZE = 64

HACK = 0
# start in town
START_LOC = (WORLDSIZE // 2, WORLDSIZE // 2, 0, LEVELSIZE - 8, LEVELSIZE // 2)
# start outside mountains temple
START_HACK = (WORLDSIZE // 2 - 1, WORLDSIZE // 2, 0, 0, 1)

# alert types
ALERT_WARNING = "warning"
ALERT_ERROR = "error"
ALERT_INFO = "info"
ALERT_YESNO = "yesno"

# brain types
B_Still = 0
B_Random = 1
B_Hunter = 2
B_Coward = 3
B_Autopilot = 4
NBRAINS = 5
BRAIN_NAMES = (
    "still",
    "random",
    "hunter",
    "coward",
    "autopilot",
)

# directories
SAVEDIR = "save"
DATABASE = "db"

# dirs
North = 0
East = 1
South = 2
West = 3
NDIRS = 4
DIR_NAMES = ("North", "East", "South", "West")
DIR_CHARS = "nesw"
MOVE_CHARS = "kljh"
DX = (
    0,
    1,
    0,
    -1,
)
DY = (
    -1,
    0,
    1,
    0,
)
# facings
Ahead = 0
Right = 1
Back = 2
Left = 3

DOOR_TOUGHNESS = 10

# friendliness values
F_Love = 3
F_Friendly = 2
F_Tolerant = 1
F_Neutral = 0
F_Dislike = -1
F_Hostile = -2
F_Enmity = -3
FRIENDLINESS_NAMES = (
    "Enmity",
    "Hostile",
    "Dislike",
    "Neutral",
    "Tolerant",
    "Friendly",
    "Love",
)

# genders
GEND_Female = 0
GEND_Male = 1
NGENDERS = 2
GENDER_NAMES = ("Female", "Male")
GENDER_KEYS = ("f", "m")

# light levels
LIGHT_NIGHT = 0
LIGHT_ECLIPSE = 1
LIGHT_TWILIGHT = 5
LIGHT_DAY = 10

# professions
P_Killer = 0
P_Sneak = 1
P_Techie = 2
P_Arcanist = 3
P_Jack = 4
NPROFS = 5
PROF_NAMES = (
    "Killer",
    "Sneak",
    "Techie",
    "Arcanist",
    "Jack of all Trades",
)
PROF_KEYS = ("k", "s", "t", "a", "j")

# redraw result codes
REDRAW = -1
NOREDRAW = 0
NEXTTURN = 1

# sector types
SECTOR_Alien_City = "A"
SECTOR_Alien_Suburb = "a"
SECTOR_Desert = "d"
SECTOR_Forest = "f"
SECTOR_Hills = "h"
SECTOR_Marsh = "m"
SECTOR_Mountains = "M"
SECTOR_Plains = "."
SECTOR_Ruins = "R"
SECTOR_Suburb = "S"
SECTOR_Town = "T"
SECTOR_Water = "~"
SECTOR_KEY = """d Desert
f Forest
h Hills
m Marsh
M Mountains
. Plains
R Downtown Ruins
S Suburb Ruins
T Town
~ Water"""

# shop types
SHOP_Cutlery = 0
SHOP_Gun = 1
SHOP_Armor = 2
SHOP_Pawn_Shop = 3
SHOP_General = 4
NSHOPS = 5
SHOP_NAMES = (
    "Cutlery",
    "Guns",
    "Armor",
    "Pawn Shop",
    "General Store",
)

# panel sides
Side_Far = 0  # the side furthest from you
Side_Right = 1  # the side to your right
Side_Near = 2  # the side closest to you
Side_Left = 3  # the side to your left
Side_Top = 4  # the top
Side_Bottom = 5  # the bottom
SIDE_CHARS = "frnltbFRNL"

NON_BLOCKING = -1
SIZE_Small = 0  # dog-sized or smaller
SIZE_Medium = 1  # human-sized
SIZE_Large = 2  # fills the grid
SIZE_Huge = 3  # fills multiple grids

SIZE_NAMES = (
    "Small",
    "Medium",
    "Large",
    "Huge",
)

# stats
Body = 0
Speed = 1
Mind = 2
Presence = 3
NPRIMES = 4
Wounds = 4
Fatigue = 5
Burnout = 6
Madness = 7
NSTATS = 8
STAT_NAMES = (
    "Body",
    "Speed",
    "Mind",
    "Presence",
    "Wounds",
    "Fatigue",
    "Burnout",
    "Madness",
)

# target modes for Umbra.selectTarget
TARGET_Ahead = 0
TARGET_Melee = 1
TARGET_Ranged = 2

TEXT3D_DIST = 4

# view menu
V_OK = 0
V_Examine_Item_or_Equip = 1
V_Use_Item = 2
V_Remove_Equip = 3
V_Move_Item = 4
V_Hand_Item = 5
V_Drop_Item = 6
V_Get_Item = 7
V_Use_Skill = 8
V_Talk_Trigger = 9
VIEW_MENU = (
    "OK",
    "Examine Item",
    "Use Item",
    "Remove Equipment",
    "Move Item to Another Character",
    "Hand Item to NPC",
    "Drop Item",
    "Get Item",
    "Use Skill",
    "Talk/Trigger",
)
VIEW_MENU_KEYS = (
    "0",
    "e",
    "u",
    "r",
    "m",
    "h",
    "d",
    "g",
    "s",
    "t",
)


class GameOverException(Exception):
    pass


def dx(facing, turn=Ahead):
    return DX[(facing + turn) % NDIRS]


def dy(facing, turn=Ahead):
    return DY[(facing + turn) % NDIRS]


def turnBack(facing):
    return (facing + Back) % NDIRS


def turnLeft(facing):
    return (facing + Left) % NDIRS


def turnRight(facing):
    return (facing + Right) % NDIRS


def setViewDist(dist):
    global VIEWDIST, VIEWSIDEDIST, VIEWSIZE
    VIEWDIST = dist
    VIEWSIDEDIST = dist // 2 + 2
    VIEWSIZE = dist * 2 + 1


setViewDist(8)


def testFacingLoop(facing):
    dist = 3
    for fb in range(dist, -1, -1):
        for lr in range(-dist, dist + 1):
            x = fb * DX[facing] + lr * -DY[facing]
            y = lr * DX[facing] + fb * DY[facing]
            print("%3d,%3d  " % (x, y), end=" ")
        print()
