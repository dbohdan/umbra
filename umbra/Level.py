from . import Door, Sector, Terrain, Thing, Entity
from . import Global, util
import math, os, string, time
import gzip

DEBUG_LOS = 0

SIZE = Global.LEVELSIZE


class Level:
    # sector=Sector
    # levelnum=Int
    # terrain=String[] # [y*SIZE+x] = terrain chars
    # stuff={} # (y*SIZE+x) := List of Things
    # catalog={} # (y*SIZE+x) := List of Scripts
    # zone=Zone
    def __init__(self, sector, levelnum):
        util.assertInt(levelnum, min=0)
        self.sector = sector
        self.levelnum = levelnum
        self.zone = None
        self.terrain = util.makeArray(SIZE * SIZE, None)
        self.stuff = {}
        self.catalog = {}

    def __str__(self):
        text = ""
        for y in range(0, SIZE):
            for x in range(0, SIZE):
                door = self.getDoor(x, y)
                if door:
                    if door.trap:
                        state = "^"
                    elif door.getState() == Door.S_Open:
                        state = "-"
                    elif door.getState() == Door.S_Closed:
                        state = "+"
                    else:
                        state = "&"
                    facing = Global.DIR_CHARS[door.facing]
                    char = "%c%c" % (state, facing)
                else:
                    char = self.terrain[y * SIZE + x]
                    if not char:
                        char = "XX"
                    elif not self.getTerrain(x, y).opaque:
                        stuff = self.getStuff(x, y)
                        if stuff:
                            for item in self.getStuff(x, y):
                                if isinstance(item, Entity.Entity):
                                    char = "@" + char[0]
                                elif util.endsWith(item.sprite, "sign"):
                                    char = "!" + char[0]
                text = "%s%s" % (text, char)
            text = "%s\n" % text
        return text

    def addScript(self, x, y, script):
        if not self.inBounds(x, y):
            return 0
        catalog = self.getScript(x, y)
        if catalog == None:
            catalog = []
            self.catalog[y * SIZE + x] = catalog
        catalog.append(script)
        return 1

    def addStuff(self, x, y, thing):
        if not self.inBounds(x, y):
            return 0
        stuff = self.getStuff(x, y)
        if stuff == None:
            stuff = []
            self.stuff[y * SIZE + x] = stuff
        stuff.append(thing)
        thing.setCoord(self.levelnum, x, y)
        return 1

    def blank(self):
        self.sector = None
        self.zone = None
        self.stuff.clear()
        self.terrain = None

    def checkScript(self, x, y, thing):
        catalog = self.getScript(x, y)
        if not catalog:
            return
        for script in catalog:
            script.run(None, thing)

    def clearLOS(self, x0, y0, x1, y1, rng=Global.LEVELSIZE, into=0):
        """Returns 1 if there is an unblocked line of sight between points
        x0,y0 and x1,y1, with a maximum range of rng.  If 'into' is true,
        you can see into opaque terrain."""
        #        if DEBUG_LOS: print "clearLOS(%d, %d, %d, %d, %d)" % (x0, y0, x1, y1, rng)
        if into and abs(x1 - x0) <= 1 and abs(y1 - y0) <= 1:
            return 1
        SCALE = 100
        SCALE2 = 50
        rng *= SCALE
        ix0 = x0
        iy0 = y0
        x0 = x0 * SCALE + SCALE2
        y0 = y0 * SCALE + SCALE2
        ix1 = x1
        iy1 = y1
        x1 = x1 * SCALE + SCALE2
        y1 = y1 * SCALE + SCALE2
        dx = x1 - x0
        dy = y1 - y0
        # begin inline __hypot
        xx = abs(dx)
        yy = abs(dy)
        if xx > yy:
            dist = xx + yy // 2
        else:
            dist = yy + xx // 2
        # end inline __hypot
        if dist > rng:
            #            if DEBUG_LOS: print "    %s out of range %s" % (dist, rng)
            return 0
        if dist > 0:
            #            dx = dx * SCALE / (dist * 2); dy = dy * SCALE / (dist * 2)
            dx = dx * SCALE // dist
            dy = dy * SCALE // dist
        # now run the bullet out to the target
        x = x0
        y = y0
        dist = 0
        while dist < rng:
            ix = x // SCALE
            iy = y // SCALE
            #            if DEBUG_LOS: print "    i=%d,%d, d=%d,%d" % (ix, iy, dx, dy),
            if not self.inBounds(ix, iy):
                # if DEBUG_LOS: print "out of bounds"
                return 0
            ter = self.getTerrain(ix, iy)
            # begin inline __hypot
            xx = abs(x0 - x)
            yy = abs(y0 - y)
            if xx > yy:
                dist = xx + yy // 2
            else:
                dist = yy + xx // 2
            # end inline __hypot
            # if DEBUG_LOS: print "%s %d,%d, dist=%d" % (ter, x, y, dist)
            if not into and self.getOpaque(ix, iy):
                # if DEBUG_LOS: print "opaque"
                return 0
            if ix == ix1 and iy == iy1:
                # if DEBUG_LOS: print "okay!"
                return 1
            if into and (ix != ix0 or iy != iy0) and self.getOpaque(ix, iy):
                # if DEBUG_LOS: print "opaque"
                return 0
            x += dx
            y += dy
        # if DEBUG_LOS: print "%d out of range %d" % (dist, rng)
        return 0

    def __hypot(self, x, y):
        xx = abs(x)
        yy = abs(y)
        if xx > yy:
            dist = xx + yy // 2
        else:
            dist = yy + xx // 2
        return dist

    def drawAt(self, x0, y0, text):
        y = y0
        lines = text.split("\n")
        for line in lines:
            # ignore completely blank lines - there's usually one at the start
            # of a string in the form """\n..."""
            if not line:
                continue
            x = x0
            cells = line.split()
            for t in cells:
                if not t:
                    continue
                # special case for doors
                if t[0] in ("+", "-", "*"):
                    self.setTerrain(x, y, Terrain.Stone_Floor)
                    if t[0] == "+":
                        state = Door.S_Closed
                    elif t[0] == "-":
                        state = Door.S_Open
                    else:
                        state = Door.S_Locked
                    facing = Global.DIR_CHARS.index(t[1])
                    door = Door.Door(facing, state)
                    self.addStuff(x, y, door)
                else:
                    self.setTerrain(x, y, Terrain.getTerrain(t))
                x = x + 1
            y = y + 1

    def drawRectangle(self, x0, y0, x1, y1, ter):
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        for y in range(y0, y1 + 1):
            self.setTerrain(x0, y, ter)
            self.setTerrain(x1, y, ter)
        for x in range(x0 + 1, x1):
            self.setTerrain(x, y0, ter)
            self.setTerrain(x, y1, ter)

    def fillRectangle(self, x0, y0, x1, y1, ter):
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.setTerrain(x, y, ter)

    def getAllEntities(self):
        entities = []
        for sublist in list(self.stuff.values()):
            for item in sublist:
                if isinstance(item, Entity.Entity):
                    entities.append(item)
        return entities

    def getBlocking(self, x, y, who):
        ter = self.getTerrain(x, y)
        if not ter:
            return 1
        if ter.isBlocking(who):
            return 1
        things = self.getThings(x, y)
        if not things:
            return 0
        for item in things:
            if item.isBlocking(who):
                return 1
        return 0

    def getDoor(self, x, y):
        stuff = self.getStuff(x, y)
        if not stuff:
            return None
        for item in stuff:
            if isinstance(item, Door.Door):
                return item
        return None

    def getEntities(self, x, y):
        stuff = self.getStuff(x, y)
        if not stuff:
            return None
        entities = []
        for item in stuff:
            if isinstance(item, Entity.Entity):
                entities.append(item)
        return entities

    def getLight(self, x, y):
        stuff = self.getStuff(x, y)
        if not stuff:
            return 0
        light_level = 0
        for item in stuff:
            if hasattr(item, "light_level"):
                light_level += item.light_level
        return light_level

    def getOpaque(self, x, y):
        ter = self.getTerrain(x, y)
        if not ter or ter.opaque:
            return 1
        stuff = self.getThings(x, y)
        if not stuff:
            return 0
        for item in stuff:
            if item.isOpaque():
                return 1
        return 0

    def getScript(self, x, y):
        if not self.inBounds(x, y):
            return None
        xy = y * SIZE + x
        if xy in self.catalog:
            return self.catalog[xy]
        return None

    def getStuff(self, x, y):
        if not self.inBounds(x, y):
            return None
        xy = y * SIZE + x
        if xy in self.stuff:
            return self.stuff[xy]
        return None

    def getTerrain(self, x, y):
        char = self.getTerrainChar(x, y)
        if not char:
            return None
        return Terrain.getTerrain(char)

    def getTerrainChar(self, x, y):
        if not self.inBounds(x, y):
            return None
        return self.terrain[y * SIZE + x]

    def getThings(self, x, y):
        stuff = self.getStuff(x, y)
        if not stuff:
            return None
        items = []
        for item in stuff:
            if not isinstance(item, Entity.Entity):
                items.append(item)
        return items

    def inBounds(self, x, y):
        return x >= 0 and x < SIZE and y >= 0 and y < SIZE

    def loadMap(self, filename):
        file = file.open(os.path.join(Global.SAVEDIR, filename), "rb")
        lines = file.readlines()
        file.close()
        for y in range(SIZE):
            line = lines[y]
            for x in range(SIZE):
                tchars = line[x * 3 : x * 3 + 2]
                t = Terrain.getTerrain(tchars)
                self.setTerrain(x, y, t)

    def moveStuff(self, thing, x0, y0, x1, y1):
        if not self.removeStuff(x0, y0, thing):
            return 0
        if not self.addStuff(x1, y1, thing):
            return 0
        self.checkScript(thing, x1, y1)
        return 1

    def removeScript(self, x, y, script):
        if not self.inBounds(x, y):
            return 0
        catalog = self.getScript(x, y)
        if not catalog:
            return 0
        i = util.indexOf(script, catalog)
        if i < 0:
            return 0
        if len(catalog) == 1:
            del self.catalog[y * SIZE + x]
        else:
            del catalog[i]
        return 1

    def removeStuff(self, x, y, thing):
        if not self.inBounds(x, y):
            return 0
        stuff = self.getStuff(x, y)
        if not stuff:  # stuff==None or len(stuff)==0
            return 0
        i = util.indexOf(thing, stuff)
        if i < 0:
            return 0
        if len(stuff) == 1:
            del self.stuff[y * SIZE + x]
        else:
            del stuff[i]
        thing.setCoord(Thing.VOID)
        return 1

    def setTerrain(self, x, y, ter):
        util.assertInt(x, 0, SIZE - 1)
        util.assertInt(y, 0, SIZE - 1)
        assert isinstance(ter, Terrain.Terrain), "Expected Terrain, but was (%s)%s" % (
            type(ter),
            ter,
        )
        self.terrain[y * SIZE + x] = ter.char


def gridsToString(map, x0, y0, x1, y1):
    text = ""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g = map[x][y]
            if not g:
                text = "%sXX" % text
            else:
                text = "%s%s" % (text, g)
        text = "%s\n" % text
    return text
