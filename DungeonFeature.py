import Door, Terrain
import Global, util

SIZE = Global.LEVELSIZE
DX = Global.DX
DY = Global.DY

class DungeonFeature:
    def __init__(self, dungeon, xloc, yloc, facing):
        self.dungeon = dungeon
        # set by selectWall()
        self.xloc = xloc
        self.yloc = yloc
        self.facing = facing
        # set by selectFeature()
        self.width = self.height = 0
        # set by computeSelectedBounds(); these are the bounds of the feature,
        # not counting the 1x1 connecting piece at xSelect, ySelect.
        self.x0 = self.y0 = self.x1 = self.y1 = 0

    def __str__(self):
        return "%s %d,%d %c %dx%d" % (str(self.__class__),
            self.xloc, self.yloc, Global.DIR_CHARS[self.facing],
            self.width, self.height)

    def add(self):
        """override me!"""
        pass

    def addTail(self):
        x = self.xloc + self.width * DX[self.facing]
        y = self.yloc + self.height * DY[self.facing]
        level = self.dungeon.level
        for d in xrange(Global.NDIRS):
            # don't put a tail inside the feature
            if d == (self.facing+2) % Global.NDIRS:
                continue
            xx = x + DX[d]; yy = y + DY[d]
            if self.dungeon.isBuildableSpace(xx, yy):
                level.setTerrain(xx, yy, Terrain.hookForDir(d))

    def checkSpace(self):
        for y in xrange(self.y0-1, self.y1+1):
            for x in xrange(self.x0-1, self.x1+1):
                if not self.dungeon.isBuildableSpace(x, y): return 0
        return 1

    def computeBounds(self):
        if self.facing == Global.North:
            self.x0 = self.xloc
            self.y0 = self.yloc - self.height
        elif self.facing == Global.East:
            self.x0 = self.xloc +1
            self.y0 = self.yloc
        elif self.facing == Global.South:
            self.x0 = self.xloc
            self.y0 = self.yloc +1
        elif self.facing == Global.West:
            self.x0 = self.xloc - self.width
            self.y0 = self.yloc
        self.x1 = self.x0 + self.width - 1
        self.y1 = self.y0 + self.height - 1

#________________________________________
class DungeonAbstractRoom(DungeonFeature):
    def __init__(self, dungeon, xloc, yloc, facing):
        DungeonFeature.__init__(self, dungeon, xloc, yloc, facing)
        self.width = util.d(2, 6)+1
        self.height = util.d(2, 6)+1
        self.computeBounds()

    def add(self):
        level = self.dungeon.level
        for y in xrange(self.y0+1, self.y1):
            for x in xrange(self.x0+1, self.x1):
                level.setTerrain(x, y, Terrain.Dungeon_Floor)

    def outline(self):
        level = self.dungeon.level
        for y in xrange(self.y0, self.y1+1):
            level.setTerrain(self.x0, y, Terrain.Dungeon_Floor)
            level.setTerrain(self.x1, y, Terrain.Dungeon_Floor)
        for x in xrange(self.x0, self.x1+1):
            level.setTerrain(x, self.y0, Terrain.Dungeon_Floor)
            level.setTerrain(x, self.y1, Terrain.Dungeon_Floor)

#________________________________________
class DungeonClosedRoom(DungeonAbstractRoom):
    def add(self):
        DungeonAbstractRoom.add(self)
        self.outline()
        level = self.dungeon.level
        for outdir in xrange(Global.NDIRS):
            if outdir == Global.North:
                x = self.x0 + util.d(1, self.width-2)
                y = self.y0
            elif outdir == Global.East:
                x = self.x1
                y = self.y0 + util.d(1, self.height-2)
            elif outdir == Global.South:
                x = self.x0 + util.d(1, self.width-2)
                y = self.y1
            elif outdir == Global.West:
                x = self.x0
                y = self.y0 + util.d(1, self.height-2)
            self.dungeon.randomDoorType(x, y, outdir)
            x += DX[outdir]
            y += DY[outdir]
            if self.dungeon.isBuildableSpace(x, y):
                level.setTerrain(x, y, Terrain.hookForDir(outdir))
        back = Global.turnBack(self.facing)
        self.dungeon.randomDoorType(self.xloc, self.yloc, back)
        x = self.xloc+DX[back]; y = self.yloc+DY[back]
        if self.dungeon.isBuildableSpace(x, y):
            level.setTerrain(x, y, Terrain.hookForDir(back))

#________________________________________
class DungeonOpenRoom(DungeonAbstractRoom):
    def add(self):
        DungeonAbstractRoom.add(self)
        self.outline()
        level = self.dungeon.level
        for y in xrange(self.y0+1, self.y1):
            x = self.x0-1
            if self.dungeon.isBuildableSpace(x, y):
                level.setTerrain(x, y, Terrain.Dungeon_Hook_W)
            x = self.x1+1
            if self.dungeon.isBuildableSpace(x, y):
                level.setTerrain(x, y, Terrain.Dungeon_Hook_E)
        for x in xrange(self.x0+1, self.x1):
            y = self.y0-1
            if self.dungeon.isBuildableSpace(x, y):
                level.setTerrain(x, y, Terrain.Dungeon_Hook_N)
            y = self.y1+1
            if self.dungeon.isBuildableSpace(x, y):
                level.setTerrain(x, y, Terrain.Dungeon_Hook_S)
        level.setTerrain(self.xloc, self.yloc, Terrain.Dungeon_Floor)
        back = Global.turnBack(self.facing)
        level.setTerrain(self.xloc+DX[back], self.yloc+DY[back],
                Terrain.Dungeon_Floor)

#________________________________________
class DungeonSemiOpenRoom(DungeonAbstractRoom):
    def add(self):
        DungeonAbstractRoom.add(self)
#        self.outline()
        level = self.dungeon.level
        nhooks = util.d(1, (self.width + self.height)*2 )
        for h in xrange(nhooks):
            outdir = util.d(1, Global.NDIRS)-1
            if outdir == Global.North:
                x = self.x0 + util.d(1, self.width-2)
                y = self.y0
            elif outdir == Global.East:
                x = self.x1
                y = self.y0 + util.d(1, self.height-2)
            elif outdir == Global.South:
                x = self.x0 + util.d(1, self.width-2)
                y = self.y1
            elif outdir == Global.West:
                x = self.x0
                y = self.y0 + util.d(1, self.height-2)
            if self.dungeon.isBuildableSpace(x, y):
                level.setTerrain(x, y, Terrain.hookForDir(outdir))
        level.setTerrain(self.xloc, self.yloc, Terrain.Dungeon_Floor)
        x = self.xloc + DX[self.facing]; y = self.yloc + DY[self.facing]
        level.setTerrain(x, y, Terrain.Dungeon_Floor)
        x += DX[self.facing]; y += DY[self.facing]
        level.setTerrain(x, y, Terrain.Dungeon_Floor)
        back = Global.turnBack(self.facing)
        x = self.xloc + DX[back]; y = self.yloc + DY[back]
        level.setTerrain(x, y, Terrain.Dungeon_Floor)
        x += DX[back]; y += DY[back]
        level.setTerrain(x, y, Terrain.Dungeon_Floor)

#________________________________________
class DungeonDoorHall(DungeonFeature):
    def __init__(self, dungeon, xloc, yloc, facing):
        DungeonFeature.__init__(self, dungeon, xloc, yloc, facing)
        if facing == Global.North or facing == Global.South:
            self.width = 1
            self.height = util.d(2, 3) + 2
        else:
            self.width = util.d(2, 3) + 2
            self.height = 1
        self.computeBounds()

    def add(self):
        level = self.dungeon.level
        for y in xrange(self.y0, self.y1+1):
            for x in xrange(self.x0, self.x1+1):
                level.setTerrain(x, y, Terrain.Dungeon_Floor)
        self.dungeon.randomDoorType(self.xloc, self.yloc, self.facing)
        self.addTail()

#________________________________________
class DungeonOpenHall(DungeonFeature):
    def __init__(self, dungeon, xloc, yloc, facing):
        DungeonFeature.__init__(self, dungeon, xloc, yloc, facing)
        if facing == Global.North or facing == Global.South:
            self.width = 1
            self.height = util.d(1, 6) + 2
        else:
            self.width = util.d(1, 6) + 2
            self.height = 1
        self.computeBounds()

    def add(self):
        level = self.dungeon.level
        for y in xrange(self.y0, self.y1+1):
            for x in xrange(self.x0, self.x1+1):
                level.setTerrain(x, y, Terrain.Dungeon_Floor)
        level.setTerrain(self.xloc, self.yloc, Terrain.Dungeon_Floor)
        back = Global.turnBack(self.facing)
        x = self.xloc + DX[back]; y = self.yloc + DY[back]
        if self.dungeon.isBuildableSpace(x, y):
            level.setTerrain(x, y, Terrain.Dungeon_Floor)
        self.addTail()

