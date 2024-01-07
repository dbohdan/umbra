from . import CALevel, Terrain
from . import Ammo, Cash, Door, Lamp, Level, Script, Skill
from . import Bestiary, Shop
from . import Global, util
import copy, random

SIZE = Global.LEVELSIZE
BUILDING = Terrain.Stone_Wall
CLEAR = Terrain.Road

DEBUG = 0

CULTIST_ENCOUNTERS = (
    20,
    Bestiary.S_Lunatic,
    20,
    Bestiary.S_Rat,
)


class Alien:
    def __init__(self, downtown):
        self.downtown = downtown

    def generate(self, sector):
        Global.umbra.showStatus("You enter an alien city.")
        Global.umbra.showStatus("This could take a minute or two, please wait...")
        if DEBUG:
            print("Alien.generate()")
        lvl0 = sector.level[0]

        if self.downtown:
            CALevel.CALevel(
                lvl0,
                {
                    CALevel.OPT_ITERATIONS: 20,
                    CALevel.OPT_WALL_N_MIN: 0,
                    CALevel.OPT_WALL_N_MAX: 4,
                    CALevel.OPT_CLEAR_N_MIN: 3,
                    CALevel.OPT_CLEAR_N_MAX: 4,
                    CALevel.OPT_WALL_TERRAIN: BUILDING,
                    CALevel.OPT_CLEAR_TERRAIN: CLEAR,
                },
            )
        else:  # surburban ruins
            CALevel.CALevel(
                lvl0,
                {
                    CALevel.OPT_ITERATIONS: 2,
                    CALevel.OPT_WALL_CHANCE: 50,
                    CALevel.OPT_COUNT_WALLS: 1,
                    CALevel.OPT_WALL_N_MIN: 3,
                    CALevel.OPT_WALL_N_MAX: 3,
                    CALevel.OPT_CLEAR_N_MIN: 6,
                    CALevel.OPT_CLEAR_N_MAX: 9,
                    CALevel.OPT_WALL_TERRAIN: BUILDING,
                    CALevel.OPT_CLEAR_TERRAIN: CLEAR,
                },
            )
        #        buildings = self.findBuildings(lvl0)
        #        util.expandArray(sector.level, 2)
        lvl0.drawRectangle(0, 0, SIZE - 1, SIZE - 1, CLEAR)

    #        xcoord = coord[0]; ycoord = coord[1]
    #        entrance = coord[2]
    #        Dungeon_Wall = Terrain.Dungeon_Wall
    #        Dungeon_Floor = Terrain.Dungeon_Floor
    #        # store coord in sector
    #        sector.temple = coord
    #        # place the door
    #        xdoor = entrance[0]; ydoor = entrance[1]
    #        side = entrance[2]
    #        door = Door.Door(side, Door.S_Closed)
    #        lvl.setTerrain(xdoor, ydoor, Terrain.Stone_Floor)
    #        lvl.addStuff(xdoor, ydoor, door)
    #        backside = Global.turnBack(side)
    #        xstairs0 = xcoord; ystairs0 = ycoord
    #        # put some cultists on the surface
    #        sector.makeEncounters(lvl, util.d(3, 10), CULTIST_ENCOUNTERS,
    #                Terrain.ENC_TERRAIN_OUTDOORS)
    #        # dig out the lower levels, undefined squares = None
    ##        util.expandArray(sector.level, util.d(2, 3))
    #        util.expandArray(sector.level, util.d(1, 2)+2)
    #        for i in xrange(1, len(sector.level)):
    #            sector.level[i] = Level.Level(sector=sector, levelnum=i)
    #            sector.level[i].drawRectangle(0,0, SIZE-1,SIZE-1, Dungeon_Wall)
    #
    #        # now generate levels and create stairs all the way down
    #        # the last level doesn't go down, thus the len()-1
    #        for lvlnum in xrange(len(sector.level)-1):
    #            if lvlnum == len(sector.level)-2:
    #                Global.umbra.showStatus("."*(len(sector.level)-lvlnum-1)+" - Almost done!")
    #            else:
    #                Global.umbra.showStatus("."*(len(sector.level)-lvlnum-1))
    #            lvl = sector.level[lvlnum]
    #            lvl1 = sector.level[lvlnum+1]
    #            # generate the lower level
    #            dungeon = Dungeon.Dungeon(lvl1)
    #            # choose stairway up on lower level
    #            xstairs1, ystairs1 = self.findClearLoc(lvl1)
    #            sector.makeStairsPair(lvl, xstairs0, ystairs0, side,
    #                "You descend stairs...", Terrain.Stairs_Down,
    #                lvl1, xstairs1, ystairs1, backside,
    #                "You ascend stairs...", Terrain.Stairs_Up)
    #
    #            # choose new stairway down on lower level for the next pass
    #            xstairs0, ystairs0 = self.findClearLoc(lvl1)
    #            side = util.d(1, Global.NDIRS)-1
    #            backside = Global.turnBack(side)
    #            # and fill any unused space with walls
    #            for y in xrange(SIZE):
    #                for x in xrange(SIZE):
    #                    if lvl1.getTerrain(x, y) is None:
    #                        lvl1.setTerrain(x, y, Terrain.Dungeon_Wall)
    #
    #            # scatter guardians
    #            sector.makeEncounters(lvl1, util.d(5, 10), CULTIST_ENCOUNTERS,
    #                    Terrain.ENC_TERRAIN_INDOORS)
    #            # and a sanity-blasting black altar...
    #            xaltar, yaltar = self.findClearLoc(lvl1, radius=2)
    #            lvl1.setTerrain(xaltar, yaltar, Terrain.Altar)
    #            lamp = Lamp.Lamp(5, Lamp.S_Always_On)
    #            lamp.name = "a blood-stained altar"
    #            lamp.sprite = None
    #            lvl1.addStuff(xaltar, yaltar, lamp )
    #            altarScript = Script.Script(
    #                    (Script.T, Script.SAVESTAT, Global.Presence, 0),
    #                    (Script.T, Script.SAVESKILL, Skill.Magic.name, 0,
    #                        "You magically resist the pull of the altar!"),
    #                    (Script.T, Script.ECHO,
    #                        "Your mind reels near the blood-stained altar!"),
    #                    (Script.T, Script.STAT, Global.Madness, "1 6"),
    #                )
    #            for y in xrange(yaltar-1, yaltar+2):
    #                for x in xrange(xaltar-1, xaltar+2):
    #                    lvl1.addScript(x, y, altarScript)
    #
    #            # and loot...
    #            for j in xrange(4 + util.d(lvlnum+1, 4)):
    #                xloot, yloot = self.findClearLoc(lvl1, radius=1)
    #                if util.d(1, 100) <= 50:
    #                    item = Cash.Cash(util.d(lvlnum+1, 10) * 5)
    #                else:
    #                    while 1:
    #                        shoptype = util.d(1, Global.NSHOPS)-1
    #                        products = Shop.CATALOG[shoptype]
    #                        product = random.choice(products)
    #                        if util.diceString(product[2])+lvlnum+1 > 0:
    #                            item = copy.deepcopy(product[0])
    #                            break
    #                if isinstance(item, Ammo.Ammo):
    #                    for k in xrange(util.d(1, lvlnum+1)):
    #                        lvl1.addStuff( xloot, yloot, copy.deepcopy(item) )
    #                else:
    #                    lvl1.addStuff( xloot, yloot, item )
    #                if DEBUG: print "loot %d,%d: %s" % (xloot, yloot, item)

    def findBuildings(self, lvl):
        marked = util.makeArray((SIZE, SIZE), 0)
        buildingnum = 1
        for y in range(SIZE):
            for x in range(SIZE):
                if marked[x][y] != 0:
                    continue
                if lvl.getTerrain(x, y) == BUILDING:
                    self.fillBuilding(-1, x, y, buildingnum, marked, lvl)
                    buildingnum += 1
        buildings = {}
        for y in range(SIZE):
            for x in range(SIZE):
                b = marked[x][y]
                if b != 0:
                    coord = (x, y)
                    if b in buildings:
                        buildings[b].append(coord)
                    else:
                        buildings[b] = (coord,)
        if DEBUG:
            text = ""
            for y in range(SIZE):
                for x in range(SIZE):
                    text = "%s%c" % (text, chr(32 + marked[x][y]))
                text = "%s\n" % text
            print(text)
            for key in list(buildings.keys()):
                print(key, ":", buildings[key])
            print()

    def fillBuilding(self, fromdir, x, y, buildingnum, marked, lvl):
        marked[x][y] = buildingnum
        for d in range(Global.NDIRS):
            if d == fromdir:
                continue
            x1 = x + Global.DX[d]
            y1 = y + Global.DY[d]
            if marked[x1][y1] != 0 and lvl.getTerrain(x1, y1) == BUILDING:
                self.fillBuilding(d, x1, y1, buildingnum, marked, lvl)


#    def findAlien(self, sector, ter):
#        """Finds a place for a temple entrance in deep terrain."""
#        import random
#        lvl = sector.level[0]
#        temples = []
#        # first locate all possible temples
#        for y in xrange(2, SIZE-4):
#            for x in xrange(2, SIZE-4):
#                walls = 0
#                for h in xrange(-1, 2):
#                    for w in xrange(-1, 2):
#                        if lvl.getTerrain(x+w, y+h) == ter: walls += 1
#                if walls != 9: continue
#                entrances = []
#                for d in xrange(Global.NDIRS):
#                    x1 = x + Global.DX[d]; y1 = y + Global.DY[d]
#                    x2 = x1 + Global.DX[d]; y2 = y1 + Global.DY[d]
#                    if lvl.getTerrain(x2, y2) in Terrain.ENC_TERRAIN_OUTDOORS:
#                        entrances.append( (x1, y1, d) )
#                if not entrances: continue
#                temples.append( (x, y, random.choice(entrances)) )
#        if not temples:
#            x = util.d(1, SIZE-4)+1; y = util.d(1, SIZE-4)+1
#            d = util.d(1, Global.NDIRS)-1
#            return (x, y, (x+Global.DX[d], y+Global.DY[d], d))
#        # now select a location
#        temple = random.choice(temples)
#        return temple
#
#    def findClearLoc(self, lvl, radius=2):
#        size = SIZE-radius-radius
#        while 1:
#            xtry = util.d(1, size)+1; ytry = util.d(1, size)+1
#            okay=1
#            for y in xrange(ytry-radius, ytry+radius+1):
#                for x in xrange(xtry-radius, xtry+radius+1):
#                    if lvl.getTerrain(x, y) != Terrain.Dungeon_Floor:
#                        okay=0
#            if okay: break
#        return xtry, ytry
