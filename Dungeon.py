from DungeonFeature import *
import Door, Terrain
import Global, util
import math, whrandom

DEBUG=0
SIZE=Global.LEVELSIZE

OPT_ITERATIONS = "iterations (1+)"
OPT_OPEN_DOOR_CHANCE = "open door chance (%)"
OPT_FEATURE_CHANCE_CLOSED_ROOM = "feature chance: closed room (%)"
OPT_FEATURE_CHANCE_OPEN_ROOM = "feature chance: open room (%)"
OPT_FEATURE_CHANCE_SEMI_OPEN_ROOM = "feature chance: semi-open room (%)"
OPT_FEATURE_CHANCE_DOOR_HALL = "feature chance: door hall (%)"
OPT_FEATURE_CHANCE_OPEN_HALL = "feature chance: open hall (%)"
OPT_STRIP_DEAD_DOORS = "Strip dead doors? (0/1)"
OPT_STRIP_HOOKS = "Strip hooks? (0/1)"

DEFAULT_OPTS={
	OPT_ITERATIONS:SIZE,
	OPT_OPEN_DOOR_CHANCE:0,
	OPT_FEATURE_CHANCE_CLOSED_ROOM:50,
	OPT_FEATURE_CHANCE_OPEN_ROOM:10,
	OPT_FEATURE_CHANCE_SEMI_OPEN_ROOM:10,
	OPT_FEATURE_CHANCE_DOOR_HALL:20,
	OPT_FEATURE_CHANCE_OPEN_HALL:10,
	OPT_STRIP_HOOKS:1,
	OPT_STRIP_DEAD_DOORS:1,
    }

class Dungeon:
    #level=Level
    #opts={}
    #feature=DungeonFeature # set by selectFeature()
    #xSelect, ySelect, dirSelect=0 # set by selectWall()
    def __init__(self, level, **opts):
	self.level = level
        self.opts = util.dictAdd(DEFAULT_OPTS, opts)
        self.feature = None
        self.xSelect = 0
        self.ySelect = 0
        self.dirSelect = 0
        if DEBUG: print "\nGenerating level %d" % level.levelnum
        self.generate()

    def generate(self):
        self.createInitialRoom()
	closedRoom = self.opts[OPT_FEATURE_CHANCE_CLOSED_ROOM]
	openRoom = closedRoom + self.opts[OPT_FEATURE_CHANCE_OPEN_ROOM]
	semiOpenRoom = openRoom + self.opts[OPT_FEATURE_CHANCE_SEMI_OPEN_ROOM]
	doorHall = semiOpenRoom + self.opts[OPT_FEATURE_CHANCE_DOOR_HALL]
	openHall = doorHall + self.opts[OPT_FEATURE_CHANCE_OPEN_HALL]

        sub_its = int( math.sqrt(self.opts[OPT_ITERATIONS]) )

        for i in xrange( self.opts[OPT_ITERATIONS] ):
            if DEBUG: print i,
            # if there's no blank space available, stop mapping
            if not self.selectWall(): break
            for j in xrange(sub_its):
                roll = util.d(1, 100)
                if roll <= closedRoom:
                    self.feature = DungeonClosedRoom(self,
                        self.xSelect, self.ySelect, self.dirSelect)
                elif roll <= openRoom:
                    self.feature = DungeonOpenRoom(self,
                        self.xSelect, self.ySelect, self.dirSelect)
                elif roll <= semiOpenRoom:
                    self.feature = DungeonSemiOpenRoom(self,
                        self.xSelect, self.ySelect, self.dirSelect)
                elif roll <= doorHall:
                    self.feature = DungeonDoorHall(self,
                        self.xSelect, self.ySelect, self.dirSelect)
                else: #roll <= openHall:
                    self.feature = DungeonOpenHall(self,
                        self.xSelect, self.ySelect, self.dirSelect)
                if self.feature.checkSpace(): break
                self.feature = None
            # if ITERATIONS tries didn't work, you can't put anything at that
            # hook.
            if DEBUG: print "after %d tries" % j,
            if not self.feature:
                self.level.setTerrain(self.xSelect, self.ySelect,
                        Terrain.Dungeon_Wall)
                if DEBUG: print "None"
                continue
            if DEBUG: print self.feature
            self.feature.add()
        self.stripHooks()
        self.stripDeadDoors()
        self.addDoorways()

    def addDoorways(self):
        for y in xrange(SIZE):
            for x in xrange(SIZE):
                door = self.level.getDoor(x, y)
                if door:
                    self.level.setTerrain(x, y, Terrain.Dungeon_Doorway)

    def createInitialRoom(self):
        # create initial room
        roomWidth = util.d(1, 5)+1
        roomHeight = util.d(1, 5)+1
        roomx = (SIZE-roomWidth)/2
        roomy = (SIZE-roomHeight)/2
        self.feature = DungeonOpenRoom(self, roomx, roomy,
                util.d(1, Global.NDIRS)-1 )
        self.feature.width = roomWidth
        self.feature.height = roomHeight
        self.feature.add()

    def getHookDir(self, ter):
        ch = ter.name[-1]
        for d in xrange(Global.NDIRS):
            if ch == Global.DIR_CHARS[d]: return d
        return Global.North

    def isBuildableSpace(self, x, y):
        # don't build near the outside of the map
        if x <= 0 or x >= SIZE-1 or y <= 0 or y >= SIZE-1:
            return 0
        # don't overwrite anything else
        ter = self.level.getTerrain(x, y)
        if ter is None or Terrain.isHook(ter): return 1

    def randomDoorType(self, x, y, d):
        self.level.setTerrain(x, y, Terrain.Dungeon_Floor)
        roll = util.d(1, 100)
        if roll <= 10*self.level.levelnum:
            state = Door.S_Locked
        elif roll < self.opts[OPT_OPEN_DOOR_CHANCE]:
            state=Door.S_Open
        else:
            state=Door.S_Closed
        door = Door.Door(d, state)
        if state != Door.S_Open and util.d(1, 100) <= 10*self.level.levelnum:
            door.trapped()
        self.level.addStuff(x, y, door)

    def selectWall(self):
        hooks = []
        for y in xrange(SIZE):
            for x in xrange(SIZE):
                ter = self.level.getTerrain(x, y)
                if Terrain.isHook(ter):
                    hooks.append( (x, y, self.getHookDir(ter),) )
        nhooks = len(hooks)
        if nhooks == 0: return 0
        pt = whrandom.choice(hooks)
        self.xSelect, self.ySelect, self.dirSelect = pt
        return 1

    def stripDeadDoors(self):
        """Remove all doors which do not have exactly 2 bordering walls."""
        if DEBUG: print "Stripping dead doors"
        Floor = Terrain.Dungeon_Floor
        if not self.opts[OPT_STRIP_DEAD_DOORS]:
            Floor = Terrain.Hill
        for y in xrange(SIZE):
            if DEBUG: print ".",
            for x in xrange(SIZE):
                door = self.level.getDoor(x, y)
                if door:
                    self.__stripDeadDoor(x, y, Floor, door)
        if DEBUG: print

    def __stripDeadDoor(self, x, y, Floor, door):
        dirOpen = [0,]*Global.NDIRS
        for d in xrange(Global.NDIRS):
            x1 = x + Global.DX[d]; y1 = y + Global.DY[d]
            ter = self.level.getTerrain(x1, y1)
            if ter == Terrain.Dungeon_Floor or ter == Floor:
                dirOpen[d] = 1
        if dirOpen.count(1) != 2:
            self.level.setTerrain(x, y, Floor)
            self.level.removeStuff(x, y, door)
            if DEBUG:
                print "stripping door at %d,%d,f=%d: count==%d: %s" % (x, y,
                        door.facing, dirOpen.count(1), dirOpen)
            return 1
        if dirOpen[Global.North] and dirOpen[Global.South]:
            if DEBUG:
                print "not stripping door at %d,%d,f=%d: n/s: %s" % (x, y,
                        door.facing, dirOpen)
            return 0
        if dirOpen[Global.East] and dirOpen[Global.West]:
            if DEBUG:
                print "not stripping door at %d,%d,f=%d: e/w: %s" % (x, y,
                        door.facing, dirOpen)
            return 0
        else:
            self.level.setTerrain(x, y, Floor)
            self.level.removeStuff(x, y, door)
            if DEBUG:
                print "stripping door at %d,%d,f=%d: else: %s" % (x, y,
                        door.facing, dirOpen)
            return 1
        return 1

    def stripHooks(self):
        """Remove all hooks which do not have 2+ bordering hooks or floors."""
        if DEBUG: print "Stripping hooks"
        Floor = Terrain.Dungeon_Floor
        Wall = Terrain.Dungeon_Wall
        if not self.opts[OPT_STRIP_HOOKS]:
            Floor = Terrain.Grass
            Wall = Terrain.Bush
        for y in xrange(SIZE):
            for x in xrange(SIZE):
                ter = self.level.getTerrain(x, y)
                if Terrain.isHook(ter):
                    self.__stripHook(x, y, Floor, Wall)

    def __stripHook(self, x, y, Floor, Wall):
        count = 0
        for d in xrange(Global.NDIRS):
            ter = self.level.getTerrain(x+Global.DX[d], y+Global.DY[d])
            if ter == Terrain.Dungeon_Floor or Terrain.isHook(ter): count += 1
        if count <= 1:
            self.level.setTerrain(x, y, Wall)
        else:
            self.level.setTerrain(x, y, Floor)

