from . import Ammo, Cash, Door, Dungeon, Lamp, Level, Script, Skill, Terrain
from . import Bestiary, Shop
from . import Global, util
import copy, random

DEBUG = 0

SIZE = Global.LEVELSIZE

CULTIST_ENCOUNTERS = (
    20,
    Bestiary.S_Lunatic,
    10,
    Bestiary.S_Cultist,
    5,
    Bestiary.S_Acolyte,
    1,
    Bestiary.S_High_Priest,
    20,
    Bestiary.S_Zombie,
    7,
    Bestiary.S_Bloody_Bones,
    1,
    Bestiary.S_Baron,
)


class Temple:
    def findTemple(self, sector, ter):
        """Finds a place for a temple entrance in deep terrain."""
        import random

        lvl = sector.level[0]
        temples = []
        # first locate all possible temples
        for y in range(2, SIZE - 4):
            for x in range(2, SIZE - 4):
                walls = 0
                for h in range(-1, 2):
                    for w in range(-1, 2):
                        if lvl.getTerrain(x + w, y + h) == ter:
                            walls += 1
                if walls != 9:
                    continue
                entrances = []
                for d in range(Global.NDIRS):
                    x1 = x + Global.DX[d]
                    y1 = y + Global.DY[d]
                    x2 = x1 + Global.DX[d]
                    y2 = y1 + Global.DY[d]
                    if lvl.getTerrain(x2, y2) in Terrain.ENC_TERRAIN_OUTDOORS:
                        entrances.append((x1, y1, d))
                if not entrances:
                    continue
                temples.append((x, y, random.choice(entrances)))
        if not temples:
            x = util.d(1, SIZE - 4) + 1
            y = util.d(1, SIZE - 4) + 1
            d = util.d(1, Global.NDIRS) - 1
            return (x, y, (x + Global.DX[d], y + Global.DY[d], d))
        # now select a location
        temple = random.choice(temples)
        return temple

    def findClearLoc(self, lvl, radius=2):
        size = SIZE - radius - radius
        while 1:
            xtry = util.d(1, size) + 1
            ytry = util.d(1, size) + 1
            okay = 1
            for y in range(ytry - radius, ytry + radius + 1):
                for x in range(xtry - radius, xtry + radius + 1):
                    if lvl.getTerrain(x, y) != Terrain.Dungeon_Floor:
                        okay = 0
            if okay:
                break
        return xtry, ytry

    def makeBunker(self, sector, coord):
        lvl = sector.level[0]
        xcoord, ycoord, doorside = coord
        for y in range(ycoord - 1, ycoord + 2):
            for x in range(xcoord - 1, xcoord + 2):
                lvl.setTerrain(x, y, Terrain.Stone_Wall)

    def generate(self, sector, coord):
        Global.umbra.showStatus("You hear chanting in the distance!")
        Global.umbra.showStatus("This could take a minute or two, please wait...")
        if DEBUG:
            print("Temple.generate(%s)" % str(coord))
        lvl = sector.level[0]
        xcoord = coord[0]
        ycoord = coord[1]
        entrance = coord[2]
        Dungeon_Wall = Terrain.Dungeon_Wall
        Dungeon_Floor = Terrain.Dungeon_Floor
        # store coord in sector
        sector.temple = coord
        # place the door
        xdoor = entrance[0]
        ydoor = entrance[1]
        side = entrance[2]
        door = Door.Door(side, Door.S_Closed)
        lvl.setTerrain(xdoor, ydoor, Terrain.Stone_Floor)
        lvl.addStuff(xdoor, ydoor, door)
        backside = Global.turnBack(side)
        xstairs0 = xcoord
        ystairs0 = ycoord
        # put some cultists on the surface
        sector.makeEncounters(
            lvl, util.d(3, 10), CULTIST_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
        )
        # dig out the lower levels, undefined squares = None
        #        util.expandArray(sector.level, util.d(2, 3))
        util.expandArray(sector.level, util.d(1, 2) + 2)
        for i in range(1, len(sector.level)):
            sector.level[i] = Level.Level(sector=sector, levelnum=i)
            sector.level[i].drawRectangle(0, 0, SIZE - 1, SIZE - 1, Dungeon_Wall)

        # now generate levels and create stairs all the way down
        # the last level doesn't go down, thus the len()-1
        for lvlnum in range(len(sector.level) - 1):
            if lvlnum == len(sector.level) - 2:
                Global.umbra.showStatus(
                    "." * (len(sector.level) - lvlnum - 1) + " - Almost done!"
                )
            else:
                Global.umbra.showStatus("." * (len(sector.level) - lvlnum - 1))
            lvl = sector.level[lvlnum]
            lvl1 = sector.level[lvlnum + 1]
            # generate the lower level
            dungeon = Dungeon.Dungeon(lvl1)
            # choose stairway up on lower level
            xstairs1, ystairs1 = self.findClearLoc(lvl1)
            sector.makeStairsPair(
                lvl,
                xstairs0,
                ystairs0,
                side,
                "You descend stairs...",
                Terrain.Stairs_Down,
                lvl1,
                xstairs1,
                ystairs1,
                backside,
                "You ascend stairs...",
                Terrain.Stairs_Up,
            )

            # choose new stairway down on lower level for the next pass
            xstairs0, ystairs0 = self.findClearLoc(lvl1)
            side = util.d(1, Global.NDIRS) - 1
            backside = Global.turnBack(side)
            # and fill any unused space with walls
            for y in range(SIZE):
                for x in range(SIZE):
                    if lvl1.getTerrain(x, y) is None:
                        lvl1.setTerrain(x, y, Terrain.Dungeon_Wall)

            # scatter guardians
            sector.makeEncounters(
                lvl1, util.d(5, 10), CULTIST_ENCOUNTERS, Terrain.ENC_TERRAIN_INDOORS
            )
            # and a sanity-blasting black altar...
            xaltar, yaltar = self.findClearLoc(lvl1, radius=2)
            lvl1.setTerrain(xaltar, yaltar, Terrain.Altar)
            lamp = Lamp.Lamp(5, Lamp.S_Always_On)
            lamp.name = "a blood-stained altar"
            lamp.sprite = None
            lvl1.addStuff(xaltar, yaltar, lamp)
            altarScript = Script.Script(
                (Script.T, Script.SAVESTAT, Global.Presence, 0),
                (
                    Script.T,
                    Script.SAVESKILL,
                    Skill.Magic.name,
                    0,
                    "You magically resist the pull of the altar!",
                ),
                (
                    Script.T,
                    Script.ECHO,
                    "Your mind reels near the blood-stained altar!",
                ),
                (Script.T, Script.STAT, Global.Madness, "1 6"),
            )
            for y in range(yaltar - 1, yaltar + 2):
                for x in range(xaltar - 1, xaltar + 2):
                    lvl1.addScript(x, y, altarScript)

            # and loot...
            for j in range(4 + util.d(lvlnum + 1, 4)):
                xloot, yloot = self.findClearLoc(lvl1, radius=1)
                if util.d(1, 100) <= 50:
                    item = Cash.Cash(util.d(lvlnum + 1, 10) * 5)
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
                        lvl1.addStuff(xloot, yloot, copy.deepcopy(item))
                else:
                    lvl1.addStuff(xloot, yloot, item)
                if DEBUG:
                    print("loot %d,%d: %s" % (xloot, yloot, item))
