from . import CALevel, MapGenerator, Terrain
from . import Ammo, Cash, Door, Lamp, Level, Script, Skill
from . import Bestiary, Shop
from . import Global, util
import copy, random

DEBUG=0

SIZE=Global.LEVELSIZE
BUILDING = Terrain.Skyscraper
WALL = Terrain.Stone_Wall
DOOR = Terrain.Skyscraper
ROAD = Terrain.Road
#STREETS = (0, 12, 24, 38, 50, 62)
STREETS = (0, 15, 31, 47, 62)

NFLOORS = 11
GROUND = 0
SEWER = 1
GARAGE = 2
BASEMENT = 3
TOWER = 4

RUINS_ENCOUNTERS=(
    40, Bestiary.S_Rat,
    10, Bestiary.S_Jumping_Arantula,
     5, Bestiary.S_Harvestman,
    10, Bestiary.S_Phantom,
     5, Bestiary.S_Ghost,
     2, Bestiary.S_Spectre,
    )

class Ruins(MapGenerator.MapGenerator):
    def __init__(self, downtown):
        self.downtown = downtown

    def generate(self, sector):
        Global.umbra.showStatus("You enter the ruins of a once-great human city.")
        Global.umbra.showStatus("This could take a minute or two, please wait...")
        if DEBUG: print("Ruins.generate()")
        lvl0 = sector.level[0]

        if self.downtown:
            self.makeCity(sector)
        else: # surburban ruins
            self.makeSuburb(sector)

    def makeCity(self, sector):
        lvl0 = sector.level[0]
        util.expandArray(sector.level, NFLOORS)
        for lvlnum in range(1, NFLOORS):
            sector.level[lvlnum] = Level.Level(sector=sector, levelnum=lvlnum)
            sector.level[lvlnum].fillRectangle(0, 0, SIZE-1, SIZE-1,
                    Terrain.Dungeon_Wall)
        xstreets = STREETS #self.makeStreets()
        ystreets = STREETS #self.makeStreets()
        for y0 in ystreets:
            lvl0.fillRectangle(0, y0, SIZE-1, y0+1, ROAD)
        for x0 in xstreets:
            lvl0.fillRectangle(x0, 0, x0+1, SIZE-1, ROAD)
        count = (len(xstreets)-1) * (len(ystreets)-1)
        for y0 in range(SIZE):
            for x0 in range(SIZE):
                if lvl0.getTerrain(x0, y0): continue
                # else it's the top-left of a building
                for x1 in range(x0+1, SIZE):
                    if lvl0.getTerrain(x1, y0): break
                else:
                    assert 0, "no end to a building at %d,%d?\n%s"%(x0,y0,lvl0)
                x1 -= 1
                for y1 in range(y0+1, SIZE):
                    if lvl0.getTerrain(x0, y1): break
                else:
                    assert 0, "no end to a building at %d,%d?\n%s"%(x0,y0,lvl0)
                y1 -= 1
                self.makeSkyscraper(sector, x0, y0, x1, y1)
                count -= 1
                if count == 0: Global.umbra.showStatus("Almost done!")
                else: Global.umbra.showStatus("."*count)
        lvl0.drawRectangle(0, 0, SIZE-1, SIZE-1, ROAD)
        sector.makeEncounters(lvl0, util.d(8, 10), RUINS_ENCOUNTERS, (ROAD,) )

    def makeStreets(self):
        streets = []
        x = 0
        while x < SIZE-2:
            streets.append(x)
            x += util.d(2, 7)+6
        streets.append( SIZE-2 )
        return streets

    def makeSkyscraper(self, sector, x0, y0, x1, y1):
        lvl0 = sector.level[GROUND]
        lvl0.fillRectangle(x0, y0, x1, y1, BUILDING)
        if DEBUG: print("makeSkyscraper %d,%d-%d,%d\n%s" % (x0,y0, x1,y1, lvl0))
        sector.level[GROUND].fillRectangle(x0, y0, x1, y1, BUILDING)
        for lvlnum in range(1, NFLOORS):
            sector.level[lvlnum].fillRectangle(x0, y0, x1, y1, Terrain.Dungeon_Floor)
        w = x1 - x0 + 1; h = y1 - y0 + 1
        self.makeSkyscraperDoors(sector, x0, y0, x1, y1, w, h)
        self.makeSkyscraperStairs(sector, x0, y0, x1, y1, w, h)
        self.makeSkyscraperContents(sector, x0, y0, x1, y1, w, h)

    def makeSkyscraperDoors(self, sector, x0, y0, x1, y1, w, h):
        if DEBUG: print("makeSkyscraperDoors %d,%d-%d,%d" % (x0,y0, x1,y1))
        for d in range(Global.NDIRS):
            while 1:
                if d == Global.North:
                    x = x0 + util.d(1, w-2)
                    y = y0
                elif d == Global.East:
                    x = x1
                    y = y0 + util.d(1, h-2)
                elif d == Global.South:
                    x = x0 + util.d(1, w-2)
                    y = y1
                elif d == Global.West:
                    x = x0
                    y = y0 + util.d(1, h-2)
                dx = x + Global.DX[d]; dy = y + Global.DY[d]
                if sector.level[TOWER].getTerrain(dx+Global.DX[d],
                        dy+Global.DY[d]) == Terrain.Dungeon_Wall:
                    break
            if util.d(1, 2) == 1: state = Door.S_Closed
            else: state = Door.S_Locked
            sector.makeDoorPair(sector.level[0], x, y, d,
                    "You enter the building.",
                    sector.level[TOWER], dx, dy, Global.turnBack(d),
                    "You exit the building.",
                    state)
            sector.level[0].setTerrain(x, y, Terrain.Sky_Doorway)

    def makeSkyscraperStairs(self, sector, x0, y0, x1, y1, w, h):
        if DEBUG: print("makeSkyscraperStairs %d,%d-%d,%d" % (x0,y0, x1,y1))
        # run stairs up and down the building
        for lvlnum in range(1, NFLOORS):
            if lvlnum == NFLOORS-1: fup = 0
            else: fup = lvlnum + 1
            if fup:
                xstairs, ystairs, facing = self.findStairs(sector.level[lvlnum],
                        sector.level[fup], x0, y0, x1, y1)
                sector.makeStairsPair(sector.level[lvlnum], xstairs, ystairs,
                        facing, "You ascend stairs...", Terrain.Stairs_Up,
                        sector.level[fup], xstairs, ystairs, facing,
                        "You descend stairs...", Terrain.Stairs_Down)

    def findStairs(self, lvl0, lvl1, x0, y0, x1, y1):
        okayterrain = (Terrain.Dungeon_Floor, Terrain.Dungeon_Wall)
        w = x1-x0+1; h = y1-y0+1
        while 1:
            facing = util.d(1, Global.NDIRS)-1
            if facing == Global.North:
                xstairs = x0 + util.d(1, w-2)
                ystairs = y0 + h
            elif facing == Global.East:
                xstairs = x0-1
                ystairs = y0 + util.d(1, h-2)
            elif facing == Global.South:
                xstairs = x0 + util.d(1, w-2)
                ystairs = y0-1
            elif facing == Global.West:
                xstairs = x0 + w
                ystairs = y0 + util.d(1, h-2)
            ter0 = lvl0.getTerrain(xstairs, ystairs)
            ter1 = lvl1.getTerrain(xstairs, ystairs)
            if ter0 not in okayterrain or ter1 not in okayterrain:
                continue
            okay = 1
            for d in range(Global.NDIRS):
                if d == facing: goodterrain = (Terrain.Dungeon_Floor,)
                else: goodterrain = okayterrain
                dx = xstairs + Global.DX[d]; dy = ystairs + Global.DY[d]
                ter0 = lvl0.getTerrain(dx, dy)
                ter1 = lvl1.getTerrain(dx, dy)
                if ter0 not in goodterrain or ter1 not in goodterrain:
                    okay = 0
                    break
            if okay:
                return xstairs, ystairs, facing

    def makeSkyscraperContents(self, sector, x0, y0, x1, y1, w, h):
        if DEBUG: print("makeSkyscraperContents %d,%d-%d,%d" % (x0,y0, x1,y1))
        # fill in the building interior
        for lvlnum in range(1, NFLOORS):
            lvl = sector.level[lvlnum]
            for y in range(y0+1, y1):
                for x in range(x0+1, x1):
                    self.makeOneSkyscraperContent(sector, lvl, x, y)
                    if x % 4 == 0 and y % 4 == 0:
                        lvl.addStuff(x, y, Lamp.Lamp(5, Lamp.S_On))

    def makeOneSkyscraperContent(self, sector, lvl, x, y):
        lvlnum = lvl.levelnum
        depth = abs(lvlnum - TOWER) + 4
        n = util.d(1, 20) - depth//2
        if n <= 1:
            who = sector.makeOneEncounter(lvl, depth, x, y, RUINS_ENCOUNTERS)
        elif n <= 3:
            item = Cash.Cash(util.d(depth, 10) * 5)
            lvl.addStuff(x, y, item)
        elif n <= 5:
            if lvlnum >= TOWER and (x % 4 != 0 or y % 4 != 0):
                lvl.setTerrain(x, y, Terrain.Dungeon_Wall)
        elif n <= 7:
            shoptype = util.d(1, Global.NSHOPS)-1
            products = Shop.CATALOG[shoptype]
            product = random.choice(products)
            if util.diceString(product[2])+depth > 0:
                item = copy.deepcopy(product[0])
                lvl.addStuff(x, y, item)
        elif n <= 8:
            if lvlnum >= TOWER:
                lvl.setTerrain(x, y, Terrain.Counter)

    def makeSuburb(self, sector):
        lvl0 = sector.level[0]
        CALevel.CALevel(lvl0,
            { CALevel.OPT_ITERATIONS:2,
            CALevel.OPT_WALL_CHANCE:50,
            CALevel.OPT_COUNT_WALLS:1,
            CALevel.OPT_WALL_N_MIN:3,
            CALevel.OPT_WALL_N_MAX:3,
            CALevel.OPT_CLEAR_N_MIN:6,
            CALevel.OPT_CLEAR_N_MAX:9,
            CALevel.OPT_WALL_TERRAIN:WALL,
            CALevel.OPT_CLEAR_TERRAIN:ROAD, } )
        lvl0.drawRectangle(0, 0, SIZE-1, SIZE-1, ROAD)
        Global.umbra.showStatus("Almost done...")
        self.makeSuburbIndoors(sector)
        sector.makeEncounters(lvl0, util.d(4, 10), RUINS_ENCOUNTERS, (ROAD,) )

    def makeSuburbIndoors(self, sector):
        lvl0 = sector.level[0]
        util.expandArray(sector.level, 2)
        lvl1 = sector.level[1] = Level.Level(sector=sector, levelnum=1)
        lvl1.fillRectangle(0, 0, SIZE-1, SIZE-1, Terrain.Dungeon_Wall)
        buildings = self.findBuildings(lvl0)
        for building in list(buildings.values()):
            if len(building) < 8: continue
            doors = self.findSuburbDoors(lvl0, lvl1, building)
            # not terribly likely, but it could happen.
            if not doors: continue
            self.makeSuburbDoor(sector, lvl0, lvl1, random.choice(doors))
            for coord in building:
                x, y = coord
                self.makeOneSuburbContent(sector, lvl1, x, y)

    def findBuildings(self, level):
        if DEBUG: print("findBuildings\n%s\n" % level)
        marked = util.makeArray( (SIZE*SIZE), 0 )
        index = 1
        for y in range(SIZE):
            for x in range(SIZE):
                xy = x+y*SIZE
                if marked[xy]: continue
                ter = level.getTerrain(x, y)
                if ter == WALL:
                    self.flood(level, marked, index, x, y)
                    index += 1
                else:
                    marked[xy] = -1
        # scan marked, building[index] = list of (x,y)
        if DEBUG: print()
        buildings = {}
        for y in range(SIZE):
            text = ""
            for x in range(SIZE):
                xy = x+y*SIZE
                index = marked[xy]
                if DEBUG:
                    if index < 0: text = "%s   " % text
                    else: text = "%s%3d" % (text, index)
                if index <= 0: continue
                if index in buildings:
                    gridlist = buildings[index]
                else:
                    gridlist = []
                    buildings[index] = gridlist
                gridlist.append( (x, y) )
            if DEBUG: print(text)
        return buildings

    def flood(self, level, marked, index, x, y):
        flood = [ (x,y) ]
        marked[x+y*SIZE] = index
        while flood:
            if DEBUG: print(flood)
            flood2 = []
            for coord in flood:
                x, y = coord
                for d in range(Global.NDIRS):
                    x1 = x+Global.DX[d]
                    y1 = y+Global.DY[d]
                    if x1 <= 0 or x1 >= SIZE-1 or y1 <= 0 or y1 >= SIZE-1:
                        continue
                    xy1 = x1+y1*SIZE
                    if level.getTerrain(x1, y1) == WALL:
                        if not marked[xy1]:
                            marked[xy1] = index
                            flood2.append( (x1, y1) )
                    else:
                        marked[xy1] = -1
            flood = flood2

    def findSuburbDoors(self, lvl0, lvl1, building):
        doors = []
        for coord in building:
            x, y = coord
            lvl1.setTerrain(x, y, Terrain.Dungeon_Floor)
            roadcount = 0
            roaddir = -1
            for d in range(Global.NDIRS):
                x1 = x+Global.DX[d]
                y1 = y+Global.DY[d]
                if lvl0.getTerrain(x1, y1) == ROAD:
                    roadcount += 1
                    roaddir = d
            if roadcount == 1:
                doors.append( (x, y, roaddir) )
        return doors

    def makeSuburbDoor(self, sector, lvl0, lvl1, door):
        x, y, d = door
        dx = x+Global.DX[d]
        dy = y+Global.DY[d]
        if util.d(1, 2) == 1: state = Door.S_Closed
        else: state = Door.S_Locked
        sector.makeDoorPair(lvl0, x, y, d, "You enter the building.",
                lvl1, dx, dy, Global.turnBack(d), "You exit the building.",
                state)

    def makeOneSuburbContent(self, sector, lvl, x, y):
        depth = 5
        n = util.d(1, 10)
        if n == 1:
            shoptype = util.d(1, Global.NSHOPS)-1
            products = Shop.CATALOG[shoptype]
            product = random.choice(products)
            if util.diceString(product[2])+depth > 0:
                item = copy.deepcopy(product[0])
                lvl.addStuff(x, y, item)
        elif n == 2:
            item = Cash.Cash(util.d(depth, 10) * 10)
            lvl.addStuff(x, y, item)
        elif n == 3:
            who = sector.makeOneEncounter(lvl, depth, x, y, RUINS_ENCOUNTERS)
        elif n == 4:
            lvl.addStuff(x, y, Lamp.Lamp(5, Lamp.S_Off))

