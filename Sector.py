import Bestiary, Door, Entity, Level, Script, Terrain
import Generators, Ruins, Temple, Town
import Global, util
import cPickle, time, whrandom
import gzip

DEBUG=0
SIZE=Global.LEVELSIZE

GENERATORS={
        Global.SECTOR_Desert:Generators.DesertGen(),
        Global.SECTOR_Forest:Generators.ForestGen(),
        Global.SECTOR_Hills:Generators.HillsGen(),
        Global.SECTOR_Marsh:Generators.MarshGen(),
        Global.SECTOR_Mountains:Generators.MountainsGen(),
        Global.SECTOR_Plains:Generators.PlainsGen(),
        Global.SECTOR_Ruins:Ruins.Ruins(downtown=1),
        Global.SECTOR_Suburb:Ruins.Ruins(downtown=0),
        Global.SECTOR_Town:Town.Town(),
        Global.SECTOR_Water:Generators.WaterGen(),
    }

class Sector:
    #wx,wy = Int (0..WORLDSIZE-1)
    #name = String
    #sectorType = Char
    #level[] = Level
    # #temple is set by Temple
    #temple = (xcenter, ycenter, (xentrance, yentrance, entranceFacing))
    #playerMap[] = String of level map explored so far
    def __init__(self, wx, wy, name, sectorType):
        util.assertInt(wx, 0, Global.WORLDSIZE-1)
        util.assertInt(wy, 0, Global.WORLDSIZE-1)
        util.assertChar(sectorType)
        self.wx=wx
        self.wy=wy
        self.name=name
        self.sectorType=sectorType
        self.level=[]
        self.playerMap=[]
        self.temple=None

    def __str__(self):
        text = ""
        for lvl in self.level:
            text = "%s\n%d\n%s\n" % ( text, lvl.levelnum, str(lvl) )
        return text

    def blank(self):
        for lvl in self.level:
            lvl.blank()
        self.level = None

    def generate(self):
        Global.umbra.busy(1)
        if Global.TIMING:
            t1=time.clock()
        util.expandArray(self.level, 1)
        level = self.level[0] = Level.Level(sector=self, levelnum=0)
        sectorType = self.sectorType
        if GENERATORS.has_key(sectorType):
            gen = GENERATORS[sectorType]
            gen.generate(self)
        #________________________________________
        else:
            raise ValueError, "Unknown sector type %c at %d,%d" % (sectorType, self.wx, self.wy)
        self.initPlayerMap()
        if Global.SHOWWORLD: print self
        if Global.TIMING:
            t2=time.clock()
            print "Sector.generate()=%dms" % ((t2-t1)*1000)
        Global.umbra.busy(0)

    def initPlayerMap(self):
        self.playerMap = []
        for i in xrange(len(self.level)):
            self.playerMap.append( "--" * (SIZE*SIZE) )

    def getNLevels(self):
        return len(self.level)

    def makeDoorPair(self, lvl0, xdoor0, ydoor0, side0, msg0,
            lvl1, xdoor1, ydoor1, side1, msg1, state):
        self.makeDoor(lvl0, xdoor0, ydoor0, side0, msg0,
            lvl1, xdoor1, ydoor1, side1, state)
        self.makeDoor(lvl1, xdoor1, ydoor1, side1, msg1,
            lvl0, xdoor0, ydoor0, side0, state)

    def makeDoor(self, lvl0, xdoor0, ydoor0, side0, msg0,
            lvl1, xdoor1, ydoor1, side1, state):
        lvl0.setTerrain(xdoor0, ydoor0, Terrain.Doorway)
        door = Door.Door(side0, state)
        door.linkedTo = (xdoor1, ydoor1, lvl1.levelnum)
        lvl0.addStuff(xdoor0, ydoor0, door)
        self.makeTeleport(lvl0, xdoor0, ydoor0, side0, msg0,
            lvl1, xdoor1, ydoor1, side1)

    def makeEncounters(self, level, ncritters, table, okayterrain):
        freespace=[]
        depth = level.levelnum + 1
        for y in xrange(SIZE):
            for x in xrange(SIZE):
                if level.getStuff(x, y)==None and \
                        level.getTerrain(x, y) in okayterrain:
                    freespace.append( (x, y) )
        # This should happen rarely, if ever, but infinite loops are a bad
        # thing.
        if ncritters > len(freespace): ncritters = len(freespace)
        # Now seed the level with critters
        for icritter in xrange(ncritters):
            i = util.d(1, len(freespace))-1
            coord = freespace.pop(i)
            self.makeOneEncounter(level, depth, coord[0], coord[1], table)

    def makeOneEncounter(self, level, depth, x, y, table):
        # maximum hostile encounter rank
        encrank = Global.umbra.game.getAverageLevel() + depth
        while 1:
            species=util.rollOnTable(table)
            # only non-hostiles or those which aren't too weak or too powerful
            # can appear
            data = Bestiary.SPECIES_DATA[species]
            f = Bestiary.getFriendSpecies(Bestiary.S_Adventurer, species)
            if f is not None and f >= 0: break
            rank = data.get("level", 1) - util.d(1, 2) * (util.d(1, 3)-1)
            if rank >= 0 and rank <= encrank: break
        return self.makeOneEntity(level, x, y, species)

    def makeOneEntity(self, level, x, y, species, entityType=Entity.Entity):
        who = Bestiary.makeEntity(species, entityType)
        level.addStuff( x, y, who )
        return who

    def makeBorders(self, level, terlist):
        for x in xrange(1, SIZE-1):
            level.setTerrain(x, 0, whrandom.choice(terlist))
            level.setTerrain(x, SIZE-1, whrandom.choice(terlist))
        for y in xrange(1, SIZE-1):
            level.setTerrain(0, y, whrandom.choice(terlist))
            level.setTerrain(SIZE-1, y, whrandom.choice(terlist))

    def makePaths(self, level, terlist):
        self.makeBorders(level, terlist)
        sides = util.d(1, 3)
        if sides & 1:
            # north-south path
            dirs = (Global.East, Global.South, Global.West)
            x = util.d(1, SIZE-2); y = 0
            while y < SIZE-1:
                level.setTerrain(x, y, whrandom.choice(terlist))
                if x == 1:
                    dir = util.d(1, 2)-1
                elif x == SIZE-2:
                    dir = util.d(1, 2)
                else:
                    dir = util.d(1, 3)-1
                dir = dirs[dir]
                x += Global.DX[dir]
                y += Global.DY[dir]
        if sides & 2:
            # west-east path
            dirs = (Global.South, Global.East, Global.North)
            x = 1; y = util.d(1, SIZE-2)
            while x < SIZE-1:
                level.setTerrain(x, y, whrandom.choice(terlist))
                if y == 1:
                    dir = util.d(1, 2)-1
                elif y == SIZE-2:
                    dir = util.d(1, 2)
                else:
                    dir = util.d(1, 3)-1
                dir = dirs[dir]
                x += Global.DX[dir]
                y += Global.DY[dir]

    def makeRandom(self, level, features):
        for y in xrange(SIZE):
            for x in xrange(SIZE):
                ter = util.rollOnTable(features)
                level.setTerrain(x, y, ter)

    def makeSquiggle(self, level, ter, terrain_table, density=2, chance=33,
            iterations=4, generations=12):
        """ Based on code by Bryan Strait <strait@mail2.quiknet.com>
        density: average number of seeds = map size * density
        chance: percentage chance for a seed to take in each direction.  Low
            values produce long, snaky branches, high values produce blobbier
            branches.
        iterations: number of iterations per seed.  The higher this is, the
            more rounded each forest group will be.
        generations: average number of forest generations.  The higher this is,
            the further out each forest "branch" will extend.
        """
        self.makeRandom(level, terrain_table)
        nforests = SIZE*density
        for forest in xrange(nforests):
            x0 = util.d(1, SIZE)-1; y0 = util.d(1, SIZE)-1
            for it in xrange(iterations):
                x = x0; y = y0
                ngen = util.d(2, generations) / 2
                for gen in xrange(ngen):
                    n = util.d(1, 100); e = util.d(1, 100)
                    s = util.d(1, 100); w = util.d(1, 100)
                    if n <= chance and y > 0:
                        y -= 1
                        level.setTerrain(x, y, ter)
                    if e <= chance and x < SIZE-1:
                        x += 1
                        level.setTerrain(x, y, ter)
                    if s <= chance and y < SIZE-1:
                        y += 1
                        level.setTerrain(x, y, ter)
                    if w <= chance and x > 0:
                        x -= 1
                        level.setTerrain(x, y, ter)

    def makeStairsPair(self, lvl0, xstairs0, ystairs0, side0, msg0, ter0,
            lvl1, xstairs1, ystairs1, side1, msg1, ter1,
            wall=Terrain.Dungeon_Wall):
        self.makeStairs(lvl0, xstairs0, ystairs0, side0, msg0,
            lvl1, xstairs1, ystairs1, side1, wall, ter0)
        self.makeStairs(lvl1, xstairs1, ystairs1, side1, msg1,
            lvl0, xstairs0, ystairs0, side0, wall, ter1)

    def makeStairs(self, lvl0, xstairs0, ystairs0, side0, msg0,
            lvl1, xstairs1, ystairs1, side1, wall, floor):
        if DEBUG: print "makeStairs(self, lvl %d, %d, %d, %d, '%s', lvl %d, %d, %d, %d, %s, %s)" % (lvl0.levelnum, xstairs0, ystairs0, side0, msg0, lvl1.levelnum, xstairs1, ystairs1, side1, wall, floor)
        lvl0.setTerrain(xstairs0, ystairs0, floor)
        self.makeTeleport(lvl0, xstairs0, ystairs0, side0, msg0,
            lvl1, xstairs1, ystairs1, side1)
        if lvl0.levelnum > 0: # make walls around the stairs
            back = Global.turnBack(side0)
            lvl0.setTerrain(xstairs0+Global.DX[back],ystairs0+Global.DY[back],
                    wall)
            left = Global.turnLeft(side0)
            lvl0.setTerrain(xstairs0+Global.DX[left],ystairs0+Global.DY[left],
                    wall)
            right = Global.turnRight(side0)
            lvl0.setTerrain(xstairs0+Global.DX[right],ystairs0+Global.DY[right],
                    wall)

    def makeTeleportPair(self, lvl0, xtport0, ytport0, side0, msg0,
            lvl1, xtport1, ytport1, side1, msg1):
        self.makeTeleport(lvl0, xtport0, ytport0, side0, msg0,
            lvl1, xtport1, ytport1, side1)
        self.makeTeleport(lvl1, xtport1, ytport1, side1, msg1,
            lvl0, xtport0, ytport0, side0)

    def makeTeleport(self, lvl0, xtport0, ytport0, side0, msg0,
            lvl1, xtport1, ytport1, side1):
        enterScript = Script.Script( ( Script.T, Script.ECHO, msg0),
            (Script.T, Script.TELEPORT, lvl1.levelnum, xtport1, ytport1, side1),
            )
        lvl0.addScript(xtport0, ytport0, enterScript)

    def saveSector(self, filename):
        Global.umbra.busy(1)
        try:
            if Global.TIMING:
                t1=time.clock()
            if Global.GZIP: file=gzip.open(filename, "wb", Global.GZIP_LEVEL)
            else: file=open(filename, "wb")

            cPickle.dump(self, file, 1)

            file.close()
            if Global.TIMING:
                t2=time.clock()
                print "saveSector(%s)=%dms" % (filename, (t2-t1)*1000)
        except IOError, detail:
            Global.umbra.alert("Save Sector",
                "Could not save to %s: %s"%(filename, detail),
                type=Global.ALERT_ERROR)
            Global.umbra.busy(0)
            return 0
        Global.umbra.busy(0)
        return 1

    def touchPlayerMap(self, x, y, levelnum):
        #x=2
        #cell=4
        #playerMap='aabbccdd'
        #'aabb' + char + 'dd'
        pmap = self.playerMap[levelnum]
        cell = (y*SIZE+x)*2
        ter = self.level[levelnum].getTerrain(x, y)
        if not ter: char = '??'
        else: char = ter.char
        self.playerMap[levelnum] = "%s%s%s" % (pmap[:cell], char, pmap[cell+2:])

def loadSector(filename):
    Global.umbra.busy(1)
    try:
        if Global.TIMING:
            t1=time.clock()
        if Global.GZIP: file=gzip.open(filename, "rb", Global.GZIP_LEVEL)
        else: file=open(filename, "rb")

        sector = cPickle.load(file)

        file.close()
        if Global.TIMING:
            t2=time.clock()
            print "loadSector(%s)=%dms" % (filename, (t2-t1)*1000)
    except IOError, detail:
        Global.umbra.alert("Load Sector",
            "Could not read from %s: %s"%(filename, detail),
            type=Global.ALERT_ERROR)
        Global.umbra.busy(0)
        return None
    if Global.SHOWWORLD: print sector
    Global.umbra.busy(0)
    return sector

