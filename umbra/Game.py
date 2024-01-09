import gzip
import math
import os
import pickle
import random
import time

from . import (
    Bestiary,
    Cash,
    Entity,
    Global,
    Sector,
    Shop,
    Skill,
    Spell,
    Terrain,
    Thing,
    util,
)

FILENAME = "game.dat"

MAXCHARS = 9
NSTARS = 128

NO_MOON_HEIGHT = -1
NO_SUN_HEIGHT = -2

WORLDSIZE = Global.WORLDSIZE
LEVELSIZE = Global.LEVELSIZE


class Game:
    # version=String
    # name=String
    # party[]=Entity
    # tavern[]=Entity
    # __sectorType[y*WORLDSIZE+x]=Char sector type used to generate Sectors
    # sector=Sector currently loaded
    # turn=Int (1 minute turns)
    # hour=Float #hour of the day
    # stars=[] # Int x, y, width, String color
    # eclipse=Int # 1 during an eclipse
    # light_level=Int # 0-10
    # sunfacing=-1
    # sunheight=NO_SUN_HEIGHT
    # moonfacing=-1
    # moonheight=NO_MOON_HEIGHT
    # moonorbit = 0
    # moonphase = 0
    # playerMap=String of world map explored so far
    # altarsDestroyed = 0
    # vehicle=Vehicle
    # view=[][][] # [x][y]=grid, grid[0]=terrain char, grid[1]=stuff,
    #           # grid[2]=light 0-10, grid[3]=visible?
    def __init__(self, filename):
        self.version = Global.VERSION
        self.name = filename
        self.sector = None
        self.party = []
        self.tavern = []
        self.__sectorType = util.makeArray(WORLDSIZE * WORLDSIZE, Global.SECTOR_Water)
        self.initPlayerMap()
        self.stars = []
        self.turn = 360  # 6am
        self.hour = 0
        self.eclipse = 0
        self.light_level = Global.LIGHT_DAY
        self.sunfacing = -1
        self.sunheight = NO_SUN_HEIGHT
        self.moonfacing = -1
        self.moonheight = NO_MOON_HEIGHT
        self.moonorbit = 0
        self.moonphase = 0
        self.__astronomy()
        self.altarsDestroyed = 0
        self.vehicle = None
        self.view = util.makeArray((Global.VIEWSIZE, Global.VIEWSIZE, 4))

    def __str__(self):
        text = ""
        for y in range(WORLDSIZE):
            for x in range(WORLDSIZE):
                text = "%s%c" % (text, self.getSectorType(x, y))
            text = "%s\n" % text
        return text

    def __astronomy(self):
        turn = self.turn
        if Global.FASTDAY:
            self.hour = (turn % 48) / 2.0  # 2 turns per hour for debugging
        else:
            self.hour = (turn % 1440) / 60.0  # 60*24 turns per day
        ihour = int(self.hour)

        # Sun orbit and height relation:
        #    W          E
        #            +-----+
        #            |  13 |
        #            |  12 |
        #            |  11 |
        # +-----+    +-----+
        # |  14 |    |  10 |
        # |  15 |    |  9  |
        # |  16 |    |  8  |
        # |  17 |    |  7  |
        # |  18 |    |  6  |
        # -+-----+----+-----+--horizon
        # |  19 |    |  5  |
        # |  20 |    |  4  |
        # |  21 |    |  3  |
        # |  22 |    |  2  |
        # |  23 |    |  1  |
        # +-----+    |  0  |
        #            +-----+
        if self.hour < 11.0:
            self.sunfacing = Global.East
            self.sunheight = (10.0 - self.hour) / 10.0
        elif self.hour >= 14.0:
            self.sunfacing = Global.West
            self.sunheight = (self.hour - 14.0) / 10.0
        else:
            self.sunfacing = -1
            self.sunheight = NO_SUN_HEIGHT
        if Global.DEBUG:
            print(
                "turn=%d, hour=%4.1f, Sun height=%d, facing=%d"
                % (turn, self.hour, self.sunheight, self.sunfacing),
            )

        # Moon orbit and height relation:
        #    W          E
        #            +-----+
        #            |  24 |
        #            |  23 |
        #            |  22 |
        #            |  21 |
        #            |  20 |
        # +-----+    +-----+
        # |  0  |    |  19 |
        # |  1  |    |  18 |
        # |  2  |    |  17 |
        # |  3  |    |  16 |
        # |  4  |    |  15 |
        # -+-----+----+-----+--horizon
        # |  5  |    |  14 |
        # |  6  |    |  13 |
        # |  7  |    |  12 |
        # |  8  |    |  11 |
        # |  9  |    |  10 |
        # +-----+    +-----+
        if Global.FASTDAY:
            self.moonorbit = (turn % 50) / 2.0  # 50-turn orbital period for debugging
            self.moonphase = (turn // 6) % 8  # 6-turn phases for debugging
        else:
            self.moonorbit = (turn % 1500) / 60.0  # 25-hour orbital period
            self.moonphase = (turn // 40320) % 8  # 28*24*60 = 40320

        if self.moonorbit < 10:
            self.moonfacing = Global.West
            self.moonheight = self.moonorbit / 10.0
        elif self.moonorbit < 20:
            self.moonfacing = Global.East
            self.moonheight = (19 - self.moonorbit) / 10.0
        else:
            self.moonfacing = -1
            self.moonheight = NO_MOON_HEIGHT
        if Global.DEBUG:
            print(
                "turn=%d, hour=%4.1f, Moon orbit=%d, height=%d, phase=%d, facing=%d"
                % (
                    turn,
                    self.hour,
                    self.moonorbit,
                    self.moonheight,
                    self.moonphase,
                    self.moonfacing,
                ),
            )

        if self.sunfacing == self.moonfacing and self.sunheight == self.moonheight:
            self.eclipse = 1
            self.light_level = Global.LIGHT_ECLIPSE
        else:
            self.eclipse = 0
            if ihour > 5 and ihour < 20:
                self.light_level = Global.LIGHT_DAY
            elif ihour in (5, 19):
                self.light_level = Global.LIGHT_TWILIGHT
            else:
                self.light_level = Global.LIGHT_NIGHT

    def __makeFractal(self, step):
        mapSize = WORLDSIZE
        for y in range(0, mapSize, step):
            for x in range(0, mapSize, step):
                # add random offsets
                cx = x
                cy = y
                if util.d(1, 100) <= 50:
                    dx = 0
                else:
                    dx = step
                if util.d(1, 100) <= 50:
                    dy = 0
                else:
                    dy = step
                cx += dx
                cy += dy

                # Truncate to nearest multiple of step*2,
                # since step*2 is the previous detail level calculated.
                cx = (cx // (step + step)) * (step + step)
                cy = (cy // (step + step)) * (step + step)

                # Read from the randomized cell.
                # Assume the world beyond the boundaries is nothing but endless
                # water.
                if self.inBounds(cx, cy):
                    type = self.getSectorType(cx, cy)
                else:
                    type = Global.SECTOR_Water

                self.setSectorType(x, y, type)

        # Generate finer details until we reach the unit scale.
        if step > 1:
            self.__makeFractal(step // 2)

    def __randomizePlains(self, x, y):
        newtype = None
        bordertypes = {}
        for dir in (Global.North, Global.West):
            x1 = x + Global.DX[dir]
            y1 = y + Global.DY[dir]
            if not self.inBounds(x1, y1):
                continue
            border = self.getSectorType(x1, y1)
            if border != Global.SECTOR_Water and border != Global.SECTOR_Plains:
                bordertypes[border] = bordertypes.get(border, 0) + 1
        if util.d(1, 2) == 1:
            # find the most common border terrain other than water or
            # plains, or shift randomly if none is more common than
            # any other
            max = 0
            for border in list(bordertypes.keys()):
                if bordertypes[border] > max:
                    max = bordertypes[border]
                    newtype = border
                elif bordertypes[border] == max:
                    newtype = None
        if not newtype:
            roll = util.d(1, 100)
            if roll <= 70:
                return
            elif roll <= 85:
                newtype = Global.SECTOR_Forest
            elif roll <= 95:
                newtype = Global.SECTOR_Hills
            elif roll <= 100:
                if Global.SECTOR_Water in bordertypes:
                    return
                newtype = Global.SECTOR_Desert
        self.setSectorType(x, y, newtype)

    def __randomizeWater(self, x, y):
        nearLand = 0
        for dir in range(Global.NDIRS):
            x1 = x + Global.DX[dir]
            y1 = y + Global.DY[dir]
            if not self.inBounds(x1, y1):
                continue
            if self.getSectorType(x1, y1) != Global.SECTOR_Water:
                nearLand = 1
                if util.d(1, 4) == 1:
                    self.setSectorType(x1, y1, Global.SECTOR_Marsh)
            # find out how far it is across the island
            dist = 1
            while 1:
                x1 = x + Global.DX[dir] * dist
                y1 = y + Global.DY[dir] * dist
                if not self.inBounds(x1, y1):
                    break
                if self.getSectorType(x1, y1) == Global.SECTOR_Water:
                    break
                dist += 1
            if dist >= 16:
                # make mountains that follow the coastline
                dist //= 4
                mx = x + Global.DX[dir] * dist
                my = y + Global.DY[dir] * dist
                x1 = mx
                y1 = my
                width = util.d(1, 3)
                for i in range(width):
                    if util.d(1, 4) == 1:
                        self.setSectorType(x1, y1, Global.SECTOR_Hills)
                    else:
                        self.setSectorType(x1, y1, Global.SECTOR_Mountains)
                    x1 += Global.DX[dir]
                    y1 += Global.DY[dir]
                x1 = mx - Global.DX[dir]
                y1 = my - Global.DY[dir]
                self.setSectorType(x1, y1, Global.SECTOR_Hills)
                x1 = mx + Global.DX[dir] * width
                y1 = my + Global.DY[dir] * width
                self.setSectorType(x1, y1, Global.SECTOR_Hills)
        return nearLand

    def __saveSector(self):
        if not self.sector:
            return 1
        dirname = os.path.join(Global.SAVEDIR, self.name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename = self.getSectorFilename(self.sector.wx, self.sector.wy)
        rc = self.sector.saveSector(filename)
        self.sector = None
        return rc

    def createChar(self, name, gender, prof, stat):
        pname = util.purifyName(name)
        for who in self.tavern + self.party:
            if util.purifyName(who.name) == pname:
                Global.umbra.alert(
                    "Create Character",
                    "You already have a character named %s." % name,
                )
                return None
        p = Entity.Entity(name, "human", Bestiary.S_Adventurer, gender, prof, stat)
        p.player = 1
        self.party.append(p)
        return p

    def dx(self, turn=Global.Ahead):
        return Global.dx(self.getFacing(), turn)

    def dy(self, turn=Global.Ahead):
        return Global.dy(self.getFacing(), turn)

    def enterWorld(self):
        nplayers = len(self.party)
        # starting equipment
        for p in self.party:
            if Global.HACK or Global.TESTCHAR == 1:
                # 1 point of armor
                onePointArmors = (
                    Shop.ITEM_leather_jacket,
                    Shop.ITEM_garbage_can_lid,
                    Shop.ITEM_hard_hat,
                )
                p.readyEquip(Shop.getShopItem(random.choice(onePointArmors)))
                # a melee weapon if you can use it
                if p.getSkill(Skill.Melee) > 0:
                    p.readyEquip(Shop.getShopItem(Shop.ITEM_switchblade))
                # a ranged weapon if you can use it
                if p.getSkill(Skill.Ranged) > 0:
                    p.readyEquip(Shop.getShopItem(Shop.ITEM_staple_gun))
                    nclips = max(1, (util.d(1, 6) + 6) // nplayers)
                    for clip in range(nclips):
                        p.addItem(Shop.getShopItem(Shop.ITEM_staple_ammo))
                # a flashlight if you can understand it
                if p.getSkill(Skill.Science) > 0:
                    p.readyEquip(Shop.getShopItem(Shop.ITEM_flashlight))
                # all first-rank spells if you know magic
                if p.getSkill(Skill.Magic) > 0:
                    p.spells = []
                    for sp in list(Spell.SPELLS.values()):
                        if sp.rank == 1:
                            p.spells.append(sp.name)
                # and a few cans of food.
                ncans = max(1, (util.d(1, 6) + 6) // nplayers)
                for can in range(ncans):
                    p.addItem(Shop.getShopItem(Shop.ITEM_can_of_food))
            else:
                p.cash = util.d(2, 5) * 20 // nplayers
        if Global.TESTCHAR == 1:
            self.party[0].cash = 10000
        # starting location
        if Global.HACK:
            start_loc = Global.START_HACK
        else:
            start_loc = Global.START_LOC
        if Global.START_DEBUG:
            print("start_loc=%s" % str(start_loc))
        wx, wy, levelnum, x, y = start_loc
        self.getSector(wx, wy)
        if Global.HACK:
            entrance = self.sector.temple[2]
            if Global.START_DEBUG:
                print("hacking at %s" % str(entrance))
            x = entrance[0] + Global.DX[entrance[2]]
            y = entrance[1] + Global.DY[entrance[2]]
            self.setFacing(Global.turnBack(entrance[2]))
        else:
            self.setFacing(Global.West)
        if not Global.START_DEBUG:
            self.moveTo(levelnum, x, y, safety=0)
            return
        # Well, that temple's gotta be somewhere nearby...
        elif Global.START_DEBUG == 1:
            temple = self.sector.temple
            self.moveTo(levelnum, temple[0] - 1, temple[1] - 2, safety=0)
            return
        # Ooh, bad luck, Dr. Jones, looks like a soul-sucking altar!
        elif Global.START_DEBUG == 2:
            lvl1 = self.sector.level[1]
            for y in range(LEVELSIZE):
                for x in range(LEVELSIZE):
                    if lvl1.getTerrain(x, y) == Terrain.Altar:
                        self.moveTo(1, x - 1, y + 1, safety=0)
                        return
        # Ruins
        elif Global.START_DEBUG == 3:
            self.moveTo(levelnum, x, y, safety=0)
            return

    def generate(self):
        Global.umbra.busy(1)
        Global.umbra.showStatus("Creating the world...")
        step = WORLDSIZE // 2
        self.setSectorType(step, step, Global.SECTOR_Plains)
        self.__makeFractal(step // 2)
        # apply geological forces
        for y in range(WORLDSIZE):
            for x in range(WORLDSIZE):
                type = self.getSectorType(x, y)
                if type == Global.SECTOR_Plains:
                    self.__randomizePlains(x, y)
        # create the coasts
        coastcoords = []
        for y in range(WORLDSIZE):
            for x in range(WORLDSIZE):
                type = self.getSectorType(x, y)
                if type == Global.SECTOR_Water:
                    if self.__randomizeWater(x, y):
                        # remember sectors near water, but not surrounded by it
                        nearwater = 0
                        for d in range(Global.NDIRS):
                            if (
                                self.getSectorType(x + Global.DX[d], y + Global.DY[d])
                                == Global.SECTOR_Water
                            ):
                                nearwater += 1
                        if nearwater <= 1:
                            coastcoords.append((x, y))
        # place towns near water 90% of the time
        ntowns = WORLDSIZE // 8
        for i in range(ntowns):
            while 1:
                if util.d(1, 10) < 10:
                    x, y = random.choice(coastcoords)
                else:
                    while 1:
                        x = util.d(1, WORLDSIZE) - 1
                        y = util.d(1, WORLDSIZE) - 1
                        if self.getSectorType(x, y) != Global.SECTOR_Water:
                            break
                # don't put one at the center of the world, that's automatic
                if abs(x - step) <= 1 and abs(y - step) <= 1:
                    continue
                if self.getSectorType(x, y) == Global.SECTOR_Town:
                    continue
                break
            self.setSectorType(x, y, Global.SECTOR_Town)
        # place ruins
        nruins = WORLDSIZE // 32
        noruinter = (Global.SECTOR_Town, Global.SECTOR_Water)
        for i in range(nruins):
            while 1:
                x = util.d(1, WORLDSIZE) - 1
                y = util.d(1, WORLDSIZE) - 1
                okay = 1
                for dy in range(y - 1, y + 2):
                    for dx in range(x - 1, x + 2):
                        if self.getSectorType(dx, dy) in noruinter:
                            okay = 0
                if okay:
                    break
            for dy in range(y - 1, y + 2):
                for dx in range(x - 1, x + 2):
                    self.setSectorType(dx, dy, Global.SECTOR_Suburb)
            self.setSectorType(x, y, Global.SECTOR_Ruins)
        # now plant some deliberate things
        self.setSectorType(step - 1, step - 1, Global.SECTOR_Hills)
        self.setSectorType(step, step - 1, Global.SECTOR_Forest)
        self.setSectorType(step + 1, step - 1, Global.SECTOR_Desert)
        self.setSectorType(step - 1, step, Global.SECTOR_Mountains)
        self.setSectorType(step, step, Global.SECTOR_Town)
        self.setSectorType(step + 1, step, Global.SECTOR_Plains)
        #        self.setSectorType(step-1, step+1, Global.SECTOR_Water)
        self.setSectorType(step, step + 1, Global.SECTOR_Water)
        self.setSectorType(step + 1, step + 1, Global.SECTOR_Marsh)
        if Global.START_DEBUG == 3:
            self.setSectorType(step + 1, step - 1, Global.SECTOR_Suburb)
            self.setSectorType(step + 1, step, Global.SECTOR_Ruins)
        # all done with the world
        if Global.SHOWWORLD:
            print(self)
        # create the stars
        stars = self.stars
        for i in range(NSTARS):
            x = util.d(1, 1024) / 1024.0
            y = util.d(1, 1024) / 1024.0
            if util.d(1, 3) == 3:
                width = 2
            else:
                width = 1
            icolor = util.d(1, 5)
            if icolor == 1:
                color = "#ffdddd"
            elif icolor == 2:
                color = "#ddffdd"
            elif icolor == 3:
                color = "#ddddff"
            else:
                color = "#ffffff"
            stars.append(x)
            stars.append(y)
            stars.append(width)
            stars.append(color)
        Global.umbra.busy(0)

    def getAverageLevel(self):
        total = 0
        for who in self.party:
            total += who.level
        return total // len(self.party)

    def getFacing(self):
        who = self.getLeader()
        if who:
            return who.facing
        return Global.North

    def getLeader(self):
        if self.party:
            return self.party[0]
        raise Global.GameOverException

    def getLevel(self, levelnum=None):
        if levelnum == None:
            levelnum = self.getLeader().levelnum()
        if levelnum < 0:
            return None
        return self.sector.level[levelnum]

    def getLevelnum(self):
        return self.getLeader().levelnum()

    def getX(self):
        return self.getLeader().x()

    def getY(self):
        return self.getLeader().y()

    def getPartyChar(self, name):
        if not self.party:
            return None
        for who in self.party:
            if who.name == name:
                return who
        return None

    def getSector(self, wx, wy):
        if self.sector and self.sector.wx == wx and self.sector.wy == wy:
            return self.sector
        if not self.__saveSector():
            return None
        filename = self.getSectorFilename(wx, wy)
        if os.path.exists(filename):
            if not self.loadSector(filename):
                return None
        else:
            stype = self.getSectorType(wx, wy)
            self.sector = Sector.Sector(wx, wy, "Sector %d,%d" % (wx, wy), stype)
            self.sector.generate()
        self.touchPlayerMap(wx, wy)
        return self.sector

    def getSectorFilename(self, wx, wy):
        return os.path.join(Global.SAVEDIR, self.name, "%03d_%03d.sec" % (wx, wy))

    def getSectorType(self, wx, wy):
        if not self.inBounds(wx, wy):
            return None
        return self.__sectorType[wy * WORLDSIZE + wx]

    def getTavernChar(self, name):
        if not self.tavern:
            return None
        for who in self.tavern:
            if who.name == name:
                return who
        return None

    def initPlayerMap(self):
        self.playerMap = "-" * (WORLDSIZE * WORLDSIZE)

    def inBounds(self, wx, wy):
        WS = WORLDSIZE
        return wx >= 0 and wx < WS and wy >= 0 and wy < WS

    def joinParty(self, who):
        if len(self.party) >= MAXCHARS:
            Global.umbra.alert(
                "Join Party",
                "You can have a maximum of %d characters in your party." % MAXCHARS,
            )
            return
        i = self.tavern.index(who)
        self.tavern.pop(i)
        self.party.append(who)

    def killChar(self, i):
        # FIXME
        self.party.pop(i)

    def leaveParty(self, who):
        i = self.party.index(who)
        self.party.pop(i)
        self.tavern.append(who)

    def listPartyNames(self):
        return [c.name for c in self.party]

    def listTavernNames(self):
        return [c.name for c in self.tavern]

    def loadSector(self, filename):
        self.sector = Sector.loadSector(filename)
        if self.sector:
            return 1
        return 0

    def makeCash(self, amount):
        return Cash.Cash(amount)

    def moveTo(self, levelnum, x1=0, y1=0, safety=1):
        """Moves the party in the same sector.
        Returns None if the move was okay, or a string saying why not."""
        leader = self.getLeader()
        lvl0 = self.getLevel(leader.levelnum())
        x0 = leader.x()
        y0 = leader.y()
        #        print "move from %d,%d,%d to %d,%d,%d, safety=%d" % (leader.levelnum(),
        #                x0, y0, levelnum, x1, y1, safety)
        # see if it's legal...
        if levelnum >= 0:
            lvl1 = self.sector.level[levelnum]
            if safety:
                if safety == 1:
                    polite = 1
                else:
                    polite = 0
                for c in self.party:
                    rc = c.moveBlocked(lvl1, x1, y1, polite=polite)
                    if rc:
                        return rc
        else:
            lvl1 = None
        # then leave the old grid...
        for c in self.party:
            c.move(lvl0, x0, y0, lvl1, x1, y1)
        if self.vehicle and self.vehicle.boarded:
            self.vehicle.move(lvl0, x0, y0, lvl1, x1, y1)
        return None

    def moveToSector(self, wx, wy, levelnum, x1, y1, x0=0, y0=0):
        """Moves the party to another sector.
        Returns None if the move was okay, or a string saying why not."""
        #        if Global.DEBUG: print "moveToSector(%d, %d, %d, %d, %d, %d, %d)" % (wx, wy, levelnum, x1, y1, x0, y0)
        wx0 = self.sector.wx
        wy0 = self.sector.wy
        if wx == wx0 and wy == wy0:
            return self.moveTo(levelnum, x1, y1)
        oldsector = self.sector
        self.moveTo(Thing.VOID)  # don't want to save the party in an old sector!
        # load the new sector
        newsector = self.getSector(wx, wy)
        if newsector == None:
            self.sector = oldsector
            self.moveTo(levelnum, x0, y0, safety=0)
            return "Couldn't load new sector %d, %d" % (wx, wy)
        # try to go to the same level, default to surface
        if levelnum < len(self.sector.level):
            newlevel = levelnum
        else:
            newlevel = 0
        # now try to move...
        moveResult = self.moveTo(newlevel, x1, y1, safety=2)
        if moveResult:
            # put everything back the way it was
            self.sector = self.getSector(wx0, wy0)
            self.moveTo(levelnum, x0, y0, safety=0)
            return moveResult
        # remove references for the benefit of the garbage collector
        oldsector.blank()
        return None

    def moveBy(self, dx, dy):
        """Moves the party, possibly across sectors.
        Returns None if the move was okay, or a string saying why not."""
        leader = self.getLeader()
        lvl0 = self.getLevel(leader.levelnum())
        x0 = leader.x()
        y0 = leader.y()
        x1 = x0 + dx
        y1 = y0 + dy
        if lvl0.inBounds(x1, y1):
            return self.moveTo(lvl0.levelnum, x1, y1)
        else:
            # move to the adjacent sector
            wx = self.sector.wx + dx
            wy = self.sector.wy + dy
            if not self.inBounds(wx, wy):
                return "You have reached the end of the world!\nTurn back!"
            # wrap to the other side of the level map
            if x1 < 0:
                x1 += LEVELSIZE
            elif x1 >= LEVELSIZE:
                x1 -= LEVELSIZE
            if y1 < 0:
                y1 += LEVELSIZE
            elif y1 >= LEVELSIZE:
                y1 -= LEVELSIZE
            return self.moveToSector(wx, wy, lvl0.levelnum, x1, y1, x0, y0)

    def nextTurn(self):
        if Global.TIMING:
            t1 = time.clock()
        self.turn += 1

        self.__astronomy()
        level = self.getLevel()
        levelnum = level.levelnum

        # FIXME: any time-based events?

        # duplicate party list, so if one is removed someone won't be skipped.
        for item in self.party[:]:
            item.nextTurn(self.turn, level)

        leader = self.getLeader()
        x0 = leader.x()
        y0 = leader.y()

        sector = self.sector
        if sector:
            # FIXME: should be VIEWDIST, but clearLOS is too slow.
            dist = Global.VIEWDIST * 2 // 3
            for y in range(max(y0 - dist, 0), min(y0 + dist + 1, LEVELSIZE)):
                for x in range(max(x0 - dist, 0), min(x0 + dist + 1, LEVELSIZE)):
                    if level.clearLOS(x0, y0, x, y, rng=dist, into=1):
                        sector.touchPlayerMap(x, y, levelnum)

        # special effect: chanting of the cultists
        chantTurn = (self.turn % 3) == util.d(1, 3) - 1
        if levelnum == 0 and self.sector.temple and chantTurn:
            xtemple = self.sector.temple[0]
            ytemple = self.sector.temple[1]
            if xtemple != x0 or ytemple != y0:
                if ytemple < y0:
                    ns = "north"
                elif ytemple > y0:
                    ns = "south"
                else:
                    ns = ""
                if xtemple < x0:
                    ew = "west"
                elif xtemple > x0:
                    ew = "east"
                else:
                    ew = ""
                dist = int(math.hypot(x0 - xtemple, y0 - ytemple))
                if dist <= Global.VIEWDIST:
                    volume = "loud "
                elif dist <= Global.VIEWDIST * 2:
                    volume = ""
                elif dist <= Global.VIEWDIST * 3:
                    volume = "distant "
                else:
                    volume = "faint "
                Global.umbra.showStatus(
                    "You hear %schanting to the %s%s!" % (volume, ns, ew),
                )

        dist = Global.VIEWDIST + 1
        xmin = max(0, x0 - dist)
        xmax = min(LEVELSIZE, x0 + dist + 1)
        ymin = max(0, y0 - dist)
        ymax = min(LEVELSIZE, y0 + dist + 1)
        for y in range(ymin, ymax):
            for x in range(xmin, xmax):
                stuff = level.getEntities(x, y)
                if not stuff:
                    continue
                for item in stuff:
                    if not item.player:
                        item.nextTurn(self.turn, level)
        # FIXME: find a way to make this faster, then shift back to updating
        # everything on the level.
        #        stuff = level.getAllEntities()
        #        if stuff:
        #            for who in stuff:
        #                if not who.player:
        #                    who.nextTurn(self.turn, level)
        if Global.TIMING:
            t2 = time.clock()
            print("turn %d=%dms," % (self.turn, (t2 - t1) * 1000), end=" ")

    def redraw(self):
        # collect the map and show it
        if Global.TIMING:
            t1 = time.clock()
        leader = self.getLeader()
        levelnum = leader.levelnum()
        level = self.getLevel(levelnum)
        x = leader.x()
        y = leader.y()
        facing = self.getFacing()
        dist = Global.VIEWDIST
        side = Global.VIEWSIDEDIST
        if not Global.LIGHT:
            light_level = 10
        elif levelnum == 0:
            light_level = self.light_level
        else:
            light_level = 0
        if Global.VISICALC:
            defaultVisible = 0
        else:
            defaultVisible = 1
        for vy in range(Global.VIEWSIZE):
            for vx in range(Global.VIEWSIZE):
                self.view[vx][vy][0] = None
                self.view[vx][vy][1] = None
                self.view[vx][vy][2] = light_level
                self.view[vx][vy][3] = defaultVisible
        dist = Global.VIEWDIST
        DX = Global.DX
        DY = Global.DY
        for dx in range(-dist, dist + 1):
            for dy in range(-dist, dist + 1):
                self.__makeView(level, x, y, dist, dx, dy)
        # if Global.LIGHT_DEBUG:
        # for vy in xrange(0, Global.VIEWSIZE):
        # for vx in xrange(0, Global.VIEWSIZE):
        # print "%2d" % self.view[vx][vy][2],
        # print
        if Global.TIMING:
            t2 = time.clock()
            print("redraw=%dms," % ((t2 - t1) * 1000), end=" ")

    def __makeView(self, level, x, y, dist, dx, dy):
        wx = x + dx
        wy = y + dy
        vx = dist + dx
        vy = dist + dy
        view = self.view
        view[vx][vy][0] = level.getTerrain(wx, wy)
        view[vx][vy][1] = level.getStuff(wx, wy)
        if Global.VISICALC:
            view[vx][vy][3] = level.clearLOS(x, y, wx, wy, rng=Global.VIEWDIST, into=1)
        if not Global.LIGHT or not view[vx][vy][3]:
            return
        light = level.getLight(wx, wy)
        view[vx][vy][2] = util.minmax(view[vx][vy][2] + light, 0, 10)
        if light <= 1:
            return
        # if Global.LIGHT_DEBUG: print "light", light, "at", vx, vy, ':'
        for dist in range(1, min(light // 2 + 1, Global.VIEWDIST + 1)):
            light -= 2
            if light < 0:
                break
            # if Global.LIGHT_DEBUG: print "dist", dist, "light", light
            x0 = vx - dist
            y0 = vy - dist
            x1 = vx + dist
            y1 = vy + dist
            for y2 in range(y0, y1 + 1):
                self.__setLight(level, wx, wy, vx, vy, x0, y2, light)
                self.__setLight(level, wx, wy, vx, vy, x1, y2, light)
            for x2 in range(x0 + 1, x1):
                self.__setLight(level, wx, wy, vx, vy, x2, y0, light)
                self.__setLight(level, wx, wy, vx, vy, x2, y1, light)
        # if Global.LIGHT_DEBUG: print

    def __setLight(self, level, wxlamp, wylamp, vxlamp, vylamp, vx, vy, light):
        if vx < 0 or vx >= Global.VIEWSIZE or vy < 0 or vy >= Global.VIEWSIZE:
            return
        wx1 = wxlamp + vx - vxlamp
        wy1 = wylamp + vy - vylamp
        view = self.view
        if Global.LIGHT_LOS:
            los = level.clearLOS(wxlamp, wylamp, wx1, wy1, rng=Global.VIEWDIST, into=1)
        else:
            los = 1
        # if Global.LIGHT_DEBUG:
        # print "  %2d,%2d, los=%d, light=%d + %d" % (vx, vy, los, view[vx][vy][2], light)
        if not los:
            return
        view[vx][vy][2] = util.minmax(view[vx][vy][2] + light, 0, 10)

    def removeCharacter(self, late):
        self.party.remove(late)

    def saveGame(self):
        leader = self.getLeader()
        self.savedParty = (
            self.sector.wx,
            self.sector.wy,
            leader.levelnum(),
            leader.x(),
            leader.y(),
        )
        self.__saveSector()

        Global.umbra.busy(1)
        dirname = os.path.join(Global.SAVEDIR, self.name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename = os.path.join(Global.SAVEDIR, self.name, FILENAME)
        try:
            if Global.TIMING:
                t1 = time.clock()
            if Global.GZIP:
                file = gzip.open(filename, "wb", Global.GZIP_LEVEL)
            else:
                file = open(filename, "wb")

            pickle.dump(self, file, 1)

            if Global.TIMING:
                t2 = time.clock()
                print("saveGame(%s)=%dms" % (filename, (t2 - t1) * 1000))
            file.close()
        except OSError as detail:
            Global.umbra.alert(
                "Save Game",
                "Could not save to %s: %s" % (filename, detail),
                type=Global.ALERT_ERROR,
            )
            Global.umbra.busy(0)
            return 0
        Global.umbra.busy(0)
        return 1

    def setFacing(self, facing):
        for c in self.party:
            c.facing = facing

    def setSectorType(self, wx, wy, type):
        self.__sectorType[wy * WORLDSIZE + wx] = type

    def touchPlayerMap(self, wx, wy):
        # playerMap='abcd'
        # wx,wy=1
        # cell=1
        #'a'+stype+'cd'
        cell = wy * WORLDSIZE + wx
        self.playerMap = "%s%c%s" % (
            self.playerMap[:cell],
            self.getSectorType(wx, wy),
            self.playerMap[cell + 1 :],
        )

    def turnBack(self):
        facing = Global.turnBack(self.getFacing())
        self.setFacing(facing)
        return Global.REDRAW

    def turnLeft(self):
        facing = Global.turnLeft(self.getFacing())
        self.setFacing(facing)
        return Global.REDRAW

    def turnRight(self):
        facing = Global.turnRight(self.getFacing())
        self.setFacing(facing)
        return Global.REDRAW


def loadGame(dirname):
    Global.umbra.busy(1)
    filename = os.path.join(Global.SAVEDIR, dirname, FILENAME)
    try:
        if Global.TIMING:
            t1 = time.clock()
        if Global.GZIP:
            file = gzip.open(filename, "rb", Global.GZIP_LEVEL)
        else:
            file = open(filename, "rb")

        game = pickle.load(file)
        game.name = dirname
        if game.version.split(".")[0:2] != Global.VERSION.split(".")[0:2]:
            Global.umbra.alert(
                "Load Game",
                "Version mismatch: %s is from incompatible version %s"
                % (filename, game.version),
                type=Global.ALERT_ERROR,
            )
            Global.umbra.busy(0)
            return None
        data = game.savedParty
        del game.savedParty
        party_wx = data[0]
        party_wy = data[1]
        party_levelnum = data[2]
        party_x = data[3]
        party_y = data[4]

        if Global.TIMING:
            t2 = time.clock()
            print("loadGame(%s)=%dms" % (dirname, (t2 - t1) * 1000))
        file.close()
    except OSError as detail:
        Global.umbra.alert(
            "Load Game",
            "Could not load from %s: %s" % (filename, detail),
            type=Global.ALERT_ERROR,
        )
        Global.umbra.busy(0)
        return None
    # find the party
    sectorFilename = game.getSectorFilename(party_wx, party_wy)
    if not game.loadSector(sectorFilename):
        return None
    stuff = game.getLevel(party_levelnum).getEntities(party_x, party_y)
    if not stuff:
        Global.umbra.alert(
            "Load Game",
            "Could not locate party!",
            type=Global.ALERT_ERROR,
        )
        Global.umbra.busy(0)
        return None
    game.party = []
    for thing in stuff:
        if thing.player:
            game.party.append(thing)
    if Global.SHOWWORLD:
        print(game)
    Global.umbra.busy(0)
    return game
