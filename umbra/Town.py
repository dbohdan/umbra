from . import Brain, Level, Merchant, Shop, Teacher, Terrain
from . import Ammo, Cash, Door, Lamp, Thing, Window
from . import Bestiary
from . import Global, util
import copy, os, string, random

DEBUG = 0

SIZE = Global.LEVELSIZE

T_OUTLINE = Terrain.Rough
OVERLAP_TERRAIN = {
    None: 1,
    Terrain.Road: 1,
    T_OUTLINE: 1,
    Terrain.Tree: 1,
    Terrain.Bush: 1,
}

START_TOWN_ENCOUNTERS = (
    10,
    Bestiary.S_Boss,
    20,
    Bestiary.S_Soldier,
    20,
    Bestiary.S_Citizen,
    10,
    Bestiary.S_Child,
    4,
    Bestiary.S_Nerd,
    2,
    Bestiary.S_Geek,
    1,
    Bestiary.S_Engineer,
    4,
    Bestiary.S_Student,
    2,
    Bestiary.S_Doctor,
    1,
    Bestiary.S_Professor,
    20,
    Bestiary.S_Rat,
)

TOWN_ENCOUNTERS = (
    10,
    Bestiary.S_Boss,
    10,
    Bestiary.S_Soldier,
    10,
    Bestiary.S_Citizen,
    10,
    Bestiary.S_Prostitute,
    5,
    Bestiary.S_Lunatic,
    4,
    Bestiary.S_Mercenary,
    2,
    Bestiary.S_Torpedo,
    1,
    Bestiary.S_Assassin,
    4,
    Bestiary.S_Thug,
    2,
    Bestiary.S_Bandit,
    1,
    Bestiary.S_Thief,
    4,
    Bestiary.S_Nerd,
    2,
    Bestiary.S_Geek,
    1,
    Bestiary.S_Engineer,
    4,
    Bestiary.S_Student,
    2,
    Bestiary.S_Doctor,
    1,
    Bestiary.S_Professor,
    4,
    Bestiary.S_Cultist,
    2,
    Bestiary.S_Acolyte,
    1,
    Bestiary.S_High_Priest,
    20,
    Bestiary.S_Rat,
)


class Town:
    # sector=Sector
    # startTown=Boolean
    # enc_table=[]
    # allshops=[]

    def generate(self, sector):
        self.sector = sector

        townname = util.randomName(1)
        Global.umbra.showStatus("Creating the town of %s" % townname)

        util.expandArray(sector.level, 2)
        level = sector.level[0]
        level1 = sector.level[1] = Level.Level(sector=sector, levelnum=1)

        if sector.wx == Global.WORLDSIZE // 2 and sector.wy == Global.WORLDSIZE // 2:
            self.startTown = 1
            self.enc_table = START_TOWN_ENCOUNTERS
        else:
            self.startTown = 0
            self.enc_table = TOWN_ENCOUNTERS
        self.allshops = list(range(Global.NSHOPS))

        center = SIZE // 2
        outer = SIZE - 1

        Road = Terrain.Road
        Grass = Terrain.Grass
        Stone_Wall = Terrain.Stone_Wall

        # outer rim of grass
        level.drawRectangle(0, 0, outer, outer, Grass)
        level.drawRectangle(1, 1, outer - 1, outer - 1, Grass)

        # outline of town
        level.drawRectangle(2, 2, outer - 2, outer - 2, T_OUTLINE)

        # east gate
        xgate = SIZE - 3
        ygate = center
        level.drawAt(
            xgate - 2,
            ygate - 3,
            """
== == #S ..
== #S #S #S
== #S #S #S
== == -e ==
== #S #S #S
== #S #S #S
== == #S .. """,
        )
        # west gate
        level.drawAt(
            1,
            center - 3,
            """
.. #S == ==
#S #S #S ==
#S #S #S ==
== -w == ==
#S #S #S ==
#S #S #S ==
.. #S == == """,
        )
        # north gate
        level.drawAt(
            center - 3,
            1,
            """
.. #S #S == #S #S ..
#S #S #S -n #S #S #S
== #S #S == #S #S ==
== == == == == == == """,
        )
        # south gate
        level.drawAt(
            center - 3,
            SIZE - 5,
            """
== == == == == == ==
== #S #S == #S #S ==
#S #S #S -s #S #S #S
.. #S #S == #S #S .. """,
        )
        for coord in (
            (center, 1),
            (outer - 1, center),
            (center, outer - 1),
            (1, center),
        ):
            level.addStuff(
                coord[0],
                coord[1],
                Thing.Thing("Welcome to\n%s" % townname, os.path.join("thing", "sign")),
            )

        if self.startTown:
            self.makeMainStreet(level, level1)

        # place random buildings across the town
        wall0 = 3
        wall1 = SIZE - 3
        walldist = wall1 - wall0 + 1
        nbuildings = 0
        freespace = 0
        for y in range(wall0, wall1):
            for x in range(wall0, wall1):
                if level.getTerrain(x, y) == None:
                    freespace += 1
        #        if DEBUG: print "\nTown: %d freespace" % freespace
        tries = 0
        while freespace > 200 and tries < 300:
            tries += 1
            while 1:
                x0 = util.d(1, walldist) + wall0 - 1
                y0 = util.d(1, walldist) + wall0 - 1
                if level.getTerrain(x0, y0) == None:
                    break
            w = util.d(4, 3) // 2
            if w == 2:
                w = 3
            h = util.d(4, 3) // 2
            if h == 2:
                h = 3

            size = self.getBuildingSize(level, level1, x0, y0, w, h)
            if size == 0:
                continue

                #            if DEBUG: print "Town: building %d,%d %dx%d, tries=%d, freespace=%d" % (x0, y0, w, h, tries, freespace)
            nbuildings += 1
            tries = 0
            freespace -= self.makeBuilding(level, level1, x0, y0, w, h)

        #        if DEBUG: print "\nTown: filling in"
        # fill in all blank spots with smaller buildings
        # these do not count for 'nbuildings'
        for y0 in range(wall0, wall1 + 1):
            for x0 in range(wall0, wall1 + 1):
                freespace = self.fill_in(level, level1, x0, y0, freespace)

        #        if DEBUG: print "Town: %d buildings, %d freespace\n" % (nbuildings, freespace)

        # select from geomorphics, do not overdraw anything already present
        # side streets laid out in a grid, but some randomly dead-end
        # alleys in between side streets
        # "nice" shops on main streets
        # houses on side streets
        # hovels and black-market shops on side streets

        # defensive wall replaces outer roads
        x0 = 2
        y0 = 2
        x1 = outer - 2
        y1 = outer - 2
        for y in range(y0, y1 + 1):
            if level.getTerrain(x0, y) == T_OUTLINE:
                level.setTerrain(x0, y, Stone_Wall)
            if level.getTerrain(x1, y) == T_OUTLINE:
                level.setTerrain(x1, y, Stone_Wall)
        for x in range(x0 + 1, x1):
            if level.getTerrain(x, y0) == T_OUTLINE:
                level.setTerrain(x, y0, Stone_Wall)
            if level.getTerrain(x, y1) == T_OUTLINE:
                level.setTerrain(x, y1, Stone_Wall)

        # finish the map with roads in case we left some blank.
        for y in range(SIZE):
            for x in range(SIZE):
                if level.getTerrain(x, y) == None:
                    level.setTerrain(x, y, Road)

        # finish the indoors map with stone walls or "Unknown"
        for y in range(SIZE):
            for x in range(SIZE):
                if level1.getTerrain(x, y) == None:
                    for d in range(Global.NDIRS):
                        t = level1.getTerrain(x + Global.DX[d], y + Global.DY[d])
                        if t not in (None, Terrain.Unknown, Stone_Wall):
                            level1.setTerrain(x, y, Stone_Wall)
                            break
                    else:
                        level1.setTerrain(x, y, Terrain.Unknown)

        # now place critters all over the place
        sector.makeEncounters(level, nbuildings, self.enc_table, (Road,))

    def doorIsClear(self, level, x, y):
        ter = level.getTerrain(x, y)
        return ter == None

    def fill_in(self, level, level1, x0, y0, freespace):
        if level.getTerrain(x0, y0) != None:
            return freespace
            #        if DEBUG:
            #            print "fill-in %d,%d, freespace=%d" % (x0, y0, freespace)
            #            for y in xrange(y0-1, y0+4+1):
            #                text=""
            #                for x in xrange(x0-1, x0+4+1):
            #                    ter=level.getTerrain(x, y)
            #                    if ter==None: char = "??"
            #                    else: char = ter.char
            #                    text="%s%s" % (text, char)
            #                print text
        size = self.getBuildingSize(level, level1, x0, y0, 1, 1)
        if size == 0:
            self.fill_in_park(level, x0, y0)
            return freespace - 1
        else:
            for w in range(5, 1, -1):
                for h in range(5, 1, -1):
                    size = self.getBuildingSize(level, level1, x0, y0, w, h)
                    if size > 0:
                        break
                if size > 0:
                    break
            if size == 0:
                self.fill_in_park(level, x0, y0)
                return freespace - 1
            #            if DEBUG: print "    building %d,%d %dx%d" % (x0, y0, w, h)
            if self.startTown:
                if w > 2 and h > 2:
                    size = self.makeBuilding(level, level1, x0, y0, w, h)
                    return freespace - size
            else:
                if (w > 1 and h > 1) and (w > 2 or h > 2):
                    size = self.makeBuilding(level, level1, x0, y0, w, h)
                    return freespace - size
            self.fill_in_park(level, x0, y0)
            return freespace - 1

    def fill_in_park(self, level, x0, y0):
        if util.d(1, 4) == 1:
            ter = Terrain.Tree
        else:
            ter = Terrain.Bush
        level.setTerrain(x0, y0, ter)

    def getBuildingSize(self, level, level1, x0, y0, w, h):
        size = 0
        # don't allow walls to overlap anything else
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                ter = level.getTerrain(x, y)
                if ter == None:
                    size += 1
                else:
                    return 0
        # on the upper level, either
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                ter = level1.getTerrain(x, y)
                if ter != None:
                    return 0
        # allow roads to overlap
        for y in range(y0 - 1, y0 + h + 1):
            for x in range(x0 - 1, x0 + w + 1, w + 1):
                ter = level.getTerrain(x, y)
                if not OVERLAP_TERRAIN.get(ter, 0):
                    return 0
        for x in range(x0, x0 + w):
            for y in range(y0 - 1, y0 + h + 1, h + 1):
                ter = level.getTerrain(x, y)
                if not OVERLAP_TERRAIN.get(ter, 0):
                    return 0
        return size

    def getPossibleDoorList(self, level, level1, x0, y0, w, h):
        """Returns a list of: [xdoor, ydoor, state, doorside, clear]; if
        possible, only 'clear' doors (those poking outside the building
        properly) will be returned; if not, then unclear doors if there are
        any; if not, then the top-left corner."""
        doors = []
        unclear_doors = []
        largest = max(w, h)
        DX = Global.DX
        DY = Global.DY
        for doorside in range(0, Global.NDIRS):
            for wh in range(1, largest - 1):
                if doorside == Global.North:
                    if wh >= w - 1:
                        continue
                    xdoor = x0 + wh
                    ydoor = y0
                elif doorside == Global.East:
                    if wh >= h - 1:
                        continue
                    xdoor = x0 + w - 1
                    ydoor = y0 + wh
                elif doorside == Global.South:
                    if wh >= w - 1:
                        continue
                    xdoor = x0 + wh
                    ydoor = y0 + h - 1
                else:  # doorside == Global.West:
                    if wh >= h - 1:
                        continue
                    xdoor = x0
                    ydoor = y0 + wh
                if util.d(1, 4) == 1:
                    state = Door.S_Open
                else:
                    state = Door.S_Closed
                x2 = xdoor + DX[doorside]
                y2 = ydoor + DY[doorside]
                doorstep = level.getTerrain(x2, y2)
                if doorstep == None or doorstep == Terrain.Road:
                    clear = 1
                    # try not to draw over any other doors
                    if not self.doorIsClear(level1, x2, y2):
                        clear = 0
                    if not self.doorIsClear(
                        level1, x2 + DX[doorside], y2 + DY[doorside]
                    ):
                        clear = 0
                    left = Global.turnLeft(doorside)
                    if not self.doorIsClear(level1, x2 + DX[left], y2 + DY[left]):
                        clear = 0
                    right = Global.turnRight(doorside)
                    if not self.doorIsClear(level1, x2 + DX[right], y2 + DY[right]):
                        clear = 0
                    if clear:
                        doors.append([xdoor, ydoor, state, doorside, clear])
                    else:
                        unclear_doors.append([xdoor, ydoor, state, doorside, clear])
        if len(doors) == 0:
            if len(unclear_doors) > 0:
                doors = unclear_doors
            else:
                doors.append([x0, y0, Door.S_Locked, Global.North, 0])
        return doors

    def getShopType(self):
        if self.allshops:
            return self.allshops.pop(util.d(1, len(self.allshops)) - 1)
        else:
            return util.d(1, Global.NSHOPS) - 1

    def makeBuilding(self, level, level1, x0, y0, w, h):
        category = util.d(1, 20)
        RANDOM = 1
        TEACHER = 2
        MERCHANT = 3
        if category <= 3:
            inhabitant = 0
            loot = 1
        elif category <= 6:
            inhabitant = RANDOM
            loot = 0
        elif category <= 9:
            inhabitant = RANDOM
            loot = 1
        elif category <= 10:
            inhabitant = TEACHER
            loot = 0
        elif self.startTown and category <= 11:
            inhabitant = TEACHER
            loot = 0
        elif not self.startTown and category <= 12:
            inhabitant = MERCHANT
            loot = 0
        else:
            inhabitant = 0
            loot = 0
        # pick a door, any door
        doors = self.getPossibleDoorList(level, level1, x0, y0, w, h)
        doordata = random.choice(doors)
        if inhabitant == 1:
            doordata[2] = random.choice((Door.S_Closed, Door.S_Locked))
            lamp = Lamp.S_On
        elif inhabitant == 2:
            doordata[2] = random.choice((Door.S_Open, Door.S_Closed))
            lamp = Lamp.S_On
        elif inhabitant == 3:
            doordata[2] = Door.S_Open
            lamp = Lamp.S_Always_On
        else:
            lamp = Lamp.S_Off
        if loot:
            loot = 1
            doordata[2] = Door.S_Locked
        # create the building
        size = self.makeBuildingWithDoor(level, level1, x0, y0, w, h, doordata)
        level1.addStuff(doordata[0], doordata[1], Lamp.Lamp(10, lamp))
        # create the inhabitant, but not in front of the door!
        if inhabitant == 1:
            x = doordata[0]
            y = doordata[1]
            while x == doordata[0] and y == doordata[1]:
                x = x0 + util.d(1, w) - 1
                y = y0 + util.d(1, h) - 1
            who = self.sector.makeOneEncounter(level1, 5, x, y, self.enc_table)
            who.friendSpecies[Bestiary.S_Adventurer] = Global.F_Hostile
        # create a teacher
        elif inhabitant == 2:
            x = doordata[0]
            y = doordata[1]
            while x == doordata[0] and y == doordata[1]:
                x = x0 + util.d(1, w) - 1
                y = y0 + util.d(1, h) - 1
            who = self.sector.makeOneEntity(
                level1, x, y, Bestiary.S_Teacher, Teacher.Teacher
            )
            x = doordata[0] + Global.DX[doordata[3]]
            y = doordata[1] + Global.DY[doordata[3]]
            signtext = who.name.replace(" ", "\n", 1)
            level.addStuff(x, y, Thing.Thing(signtext, os.path.join("thing", "sign")))
        # create a merchant
        elif inhabitant == 3:
            x = doordata[0]
            y = doordata[1]
            doorside = doordata[3]
            xmerch, ymerch, counters = self.getMerchantCoord(x0, y0, w, h, doorside)
            who = self.sector.makeOneEntity(
                level1, xmerch, ymerch, Bestiary.S_Merchant, Merchant.Merchant
            )
            who.facing = doorside
            shoptype = self.getShopType()
            who.setShopType(shoptype)
            shopname = "%s's\n%s" % (who.name.split()[1], Global.SHOP_NAMES[shoptype])
            level.addStuff(
                x + Global.DX[doorside],
                y + Global.DY[doorside],
                Thing.Thing(shopname, os.path.join("thing", "sign")),
            )
            for counter in counters:
                cx, cy = counter
                if cx != xmerch or cy != ymerch:
                    level1.setTerrain(cx, cy, Terrain.Counter)
        #        if DEBUG and inhabitant:
        #            print "created %s at %d,%d" % (who.name, who.x(), who.y())
        # create the loot
        if loot:
            xloot = x0 + util.d(1, w) - 1
            yloot = y0 + util.d(1, h) - 1
            lvlnum = 1
            if util.d(1, 100) <= 50:
                item = Cash.Cash(util.d(lvlnum, 10) * 5)
            else:
                while 1:
                    shoptype = util.d(1, Global.NSHOPS) - 1
                    products = Shop.CATALOG[shoptype]
                    product = random.choice(products)
                    if util.diceString(product[2]) + lvlnum + 1 > 0:
                        item = copy.deepcopy(product[0])
                        break
            if isinstance(item, Ammo.Ammo):
                for k in range(util.d(1, lvlnum + 1)):
                    level1.addStuff(xloot, yloot, copy.deepcopy(item))
            else:
                level1.addStuff(xloot, yloot, item)
        return size

    def getMerchantCoord(self, x0, y0, w, h, doorside):
        counters = []
        if w > 2:
            wx = w // 2
        else:
            wx = util.d(1, w) - 1
        if h > 2:
            hy = h // 2
        else:
            hy = util.d(1, h) - 1
        if doorside == Global.North:
            xmerch = x0 + wx
            ymerch = y0 + h - 1
            for x in range(x0, x0 + w):
                if x != xmerch:
                    counters.append((x, ymerch))
        elif doorside == Global.East:
            xmerch = x0
            ymerch = y0 + hy
            for y in range(y0, y0 + h):
                if y != ymerch:
                    counters.append((xmerch, y))
        elif doorside == Global.South:
            xmerch = x0 + wx
            ymerch = y0
            for x in range(x0, x0 + w):
                if x != xmerch:
                    counters.append((x, ymerch))
        elif doorside == Global.West:
            xmerch = x0 + w - 1
            ymerch = y0 + hy
            for y in range(y0, y0 + h):
                if y != ymerch:
                    counters.append((xmerch, y))
        if w <= 2 or h <= 2:
            counters = ()
        return (xmerch, ymerch, counters)

    def makeBuildingWithDoor(self, level, level1, x0, y0, w, h, doordata):
        # draw the building
        size = 0
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                level.setTerrain(x, y, Terrain.Stone_Wall)
                level1.setTerrain(x, y, Terrain.Stone_Floor)
                size += 1
        # create a matching set of doors, street and indoors
        x = doordata[0]
        y = doordata[1]
        state = doordata[2]
        side = doordata[3]
        clear = doordata[4]
        if clear:
            x2 = x + Global.DX[side]
            y2 = y + Global.DY[side]
        else:
            x2 = x
            y2 = y
        self.sector.makeDoorPair(
            level,
            x,
            y,
            side,
            "You enter the building.",
            level1,
            x2,
            y2,
            Global.turnBack(side),
            "You exit the building.",
            state,
        )
        # walls around the upper door if it's outside the room
        if clear:
            level1.setTerrain(
                x2 + Global.DX[side], y2 + Global.DY[side], Terrain.Stone_Wall
            )
            left = Global.turnLeft(side)
            level1.setTerrain(
                x2 + Global.DX[left], y2 + Global.DY[left], Terrain.Stone_Wall
            )
            right = Global.turnRight(side)
            level1.setTerrain(
                x2 + Global.DX[right], y2 + Global.DY[right], Terrain.Stone_Wall
            )
        # roads around the building
        for y in range(y0 - 1, y0 + h):
            for x in range(x0 - 1, x0 + w + 1, w + 1):
                ter = level.getTerrain(x, y)
                if ter == None:
                    level.setTerrain(x, y, Terrain.Road)
                    size += 1
        for x in range(x0 - 1, x0 + w):
            for y in range(y0 - 1, y0 + h + 1, h + 1):
                ter = level.getTerrain(x, y)
                if ter == None:
                    level.setTerrain(x, y, Terrain.Road)
                    size += 1
        return size

    def makeMainStreet(self, level, level1):
        center = SIZE // 2
        outer = SIZE - 1
        Road = Terrain.Road
        Grass = Terrain.Grass
        Stone_Wall = Terrain.Stone_Wall
        # east gate
        xgate = SIZE - 3
        ygate = center
        # main street shops
        level.fillRectangle(center + 7, ygate - 4, xgate - 3, ygate + 4, Road)
        for x in range(center + 7, xgate - 3, 4):
            for side in (Global.North, Global.South):
                if side == Global.South:
                    y = ygate - 3
                    ydoor = y + 1
                    ymerch = y
                else:
                    y = ygate + 2
                    ydoor = y
                    ymerch = y + 1
                xdoor = x + 1
                xmerch = x + 1
                door = (xdoor, ydoor, Door.S_Open, side, 1)
                self.makeBuildingWithDoor(level, level1, x, y, 3, 2, door)
                merch = self.sector.makeOneEntity(
                    level1, xmerch, ymerch, Bestiary.S_Merchant, Merchant.Merchant
                )
                shoptype = self.getShopType()
                merch.setShopType(shoptype)
                shopname = "%s's\n%s" % (
                    merch.name.split()[1],
                    Global.SHOP_NAMES[shoptype],
                )
                level.addStuff(
                    xdoor,
                    ydoor + Global.DY[side],
                    Thing.Thing(shopname, os.path.join("thing", "sign")),
                )
                for cx in range(x, x + 3):
                    if cx != xmerch:
                        level1.setTerrain(cx, ymerch, Terrain.Counter)
                level1.addStuff(xmerch, ymerch, Lamp.Lamp(10, Lamp.S_Always_On))

        # create the keep
        level.drawAt(
            center - 6,
            center - 5,
            """
== == == == == == == == == == == == ==
== #S #S #S #S #S #S #S #S #S #S #S ==
== #S ~~ %% .. .. .. .. .. %% ~~ #S ==
== #S ~~ .. #S _S _S _S #S .. .. #S ==
== #S tt .. _S _S _S _S _S .. .. -e ==
== #S %% .. _S _S _S _S +e == == -e ==
== #S tt .. _S _S _S _S _S .. .. -e ==
== #S ~~ .. #S _S _S _S #S .. %% #S ==
== #S ~~ .. .. .. .. .. .. .. ~~ #S ==
== #S #S #S #S #S #S #S #S #S #S #S ==
== == == == == == == == == == == == == """,
        )

        N = Global.North
        E = Global.East
        S = Global.South
        W = Global.West
        for pts in (
            (center + 2, center - 1, E),
            (center + 2, center + 1, E),
            (center - 2, center - 1, W),
            (center - 2, center, W),
            (center - 2, center + 1, W),
            (center + 1, center - 2, N),
            (center, center - 2, N),
            (center - 1, center - 2, N),
            (center + 1, center + 2, S),
            (center, center + 2, S),
            (center - 1, center + 2, S),
        ):
            x, y, side = pts
            window = Window.Window(side)
            level.addStuff(x, y, window)
        level.addStuff(center, center, Lamp.Lamp(10, Lamp.S_On))

        lord = self.sector.makeOneEntity(level, center, center, Bestiary.S_Boss)
        lord.brain = Global.B_Still
        lord.speech = (
            "I've told you before, there is no danger as long as we all stay here!",
        )

        guard = self.sector.makeOneEntity(level, center + 3, center, Bestiary.S_Soldier)
        guard.brain = Global.B_Autopilot
        guard.autopilot = "sss..wwwwww..nnnnnn..eeeeee..sss.."
        guard.autopilotIndex = 0
