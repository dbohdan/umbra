from . import Bestiary, MapGenerator, Terrain, Vehicle
from . import Temple
from . import Global, util

SIZE = Global.LEVELSIZE

Bush = Terrain.Bush
Dock = Terrain.Dock
Grass = Terrain.Grass
Hill = Terrain.Hill
Mountain = Terrain.Mountain
Rough = Terrain.Rough
Sand = Terrain.Sand
Scrub = Terrain.Scrub
Tree = Terrain.Tree
Water = Terrain.Water

DESERT_FEATURES = (
    95,
    Sand,
    4,
    Rough,
    1,
    Scrub,
)

DESERT_ENCOUNTERS = (
    5,
    Bestiary.S_Lunatic,
    4,
    Bestiary.S_Cultist,
    4,
    Bestiary.S_Mercenary,
    20,
    Bestiary.S_Rabbit,
    20,
    Bestiary.S_Jackalope,
    10,
    Bestiary.S_Rat,
    5,
    Bestiary.S_Jumping_Arantula,
)

FOREST_FEATURES = (
    15,
    Tree,
    40,
    Grass,
    30,
    Bush,
    10,
    Rough,
    5,
    Water,
)

FOREST_ENCOUNTERS = (
    5,
    Bestiary.S_Lunatic,
    4,
    Bestiary.S_Cultist,
    20,
    Bestiary.S_Rat,
    10,
    Bestiary.S_Zombie,
    10,
    Bestiary.S_Harvestman,
)

HILLS_FEATURES = (
    25,
    Rough,
    35,
    Hill,
    10,
    Grass,
    10,
    Scrub,
    10,
    Tree,
    10,
    Water,
)

HILLS_ENCOUNTERS = (
    15,
    Bestiary.S_Lunatic,
    5,
    Bestiary.S_Cultist,
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
    20,
    Bestiary.S_Rat,
    10,
    Bestiary.S_Zombie,
    3,
    Bestiary.S_Bloody_Bones,
)

MARSH_FEATURES = (
    35,
    Grass,
    25,
    Water,
    5,
    Rough,
    20,
    Bush,
    13,
    Tree,
    2,
    Hill,
)

MARSH_ENCOUNTERS = (
    30,
    Bestiary.S_Rat,
    10,
    Bestiary.S_Zombie,
)

MOUNTAINS_FEATURES = (
    20,
    Hill,
    50,
    Rough,
    20,
    Scrub,
    10,
    Tree,
)

MOUNTAINS_ENCOUNTERS = (
    10,
    Bestiary.S_Lunatic,
    5,
    Bestiary.S_Cultist,
    1,
    Bestiary.S_Acolyte,
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
    20,
    Bestiary.S_Rat,
)

PLAINS_FEATURES = (
    91,
    Grass,
    2,
    Bush,
    1,
    Hill,
    5,
    Rough,
    1,
    Tree,
)

PLAINS_ENCOUNTERS = (
    10,
    Bestiary.S_Lunatic,
    2,
    Bestiary.S_Cultist,
    1,
    Bestiary.S_Acolyte,
    2,
    Bestiary.S_Mercenary,
    1,
    Bestiary.S_Torpedo,
    2,
    Bestiary.S_Thug,
    1,
    Bestiary.S_Bandit,
    20,
    Bestiary.S_Rabbit,
    20,
    Bestiary.S_Jackalope,
    20,
    Bestiary.S_Rat,
    30,
    Bestiary.S_Zombie,
    5,
    Bestiary.S_Bloody_Bones,
    2,
    Bestiary.S_Harvestman,
)


# ________________________________________
class DesertGen(MapGenerator.MapGenerator):
    def generate(self, sector):
        level = sector.level[0]
        sector.makeRandom(level, DESERT_FEATURES)
        level.drawRectangle(0, 0, SIZE - 1, SIZE - 1, Sand)
        if Global.START_DEBUG or util.d(1, 4) == 1:
            temple = Temple.Temple()
            if Global.START_DEBUG:
                coord = (
                    SIZE // 2 - 1,
                    SIZE // 2 - 1,
                    (SIZE // 2 - 1, SIZE // 2, Global.West),
                )
            else:
                coord = temple.findTemple(sector, Sand)
            temple.makeBunker(sector, coord)
            temple.generate(sector, coord)
            sector.makeEncounters(
                level, util.d(3, 10), DESERT_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )
        else:
            sector.makeEncounters(
                level, util.d(5, 10), DESERT_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )


# ________________________________________
class ForestGen(MapGenerator.MapGenerator):
    def generate(self, sector):
        level = sector.level[0]
        sector.makeSquiggle(
            level,
            Tree,
            FOREST_FEATURES,
            density=2,
            chance=33,
            iterations=4,
            generations=12,
        )
        sector.makeBorders(level, (Grass, Bush))
        if Global.START_DEBUG or util.d(1, 4) == 1:
            temple = Temple.Temple()
            coord = temple.findTemple(sector, Tree)
            temple.generate(sector, coord)
            sector.makeEncounters(
                level, util.d(3, 10), FOREST_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )
        else:
            sector.makeEncounters(
                level, util.d(5, 10), FOREST_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )


# ________________________________________
class HillsGen(MapGenerator.MapGenerator):
    def generate(self, sector):
        level = sector.level[0]
        sector.makeSquiggle(
            level,
            Mountain,
            HILLS_FEATURES,
            density=1,
            chance=16,
            iterations=3,
            generations=12,
        )
        sector.makeBorders(level, (Rough, Scrub))
        if Global.START_DEBUG or util.d(1, 4) == 1:
            temple = Temple.Temple()
            coord = temple.findTemple(sector, Hill)
            temple.makeBunker(sector, coord)
            temple.generate(sector, coord)
            sector.makeEncounters(
                level, util.d(3, 10), HILLS_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )
        else:
            sector.makeEncounters(
                level, util.d(5, 10), HILLS_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )


# ________________________________________
class MarshGen(MapGenerator.MapGenerator):
    def generate(self, sector):
        level = sector.level[0]
        sector.makeRandom(level, MARSH_FEATURES)
        sector.makePaths(level, (Grass, Bush))
        if Global.START_DEBUG or util.d(1, 4) == 1:
            temple = Temple.Temple()
            if Global.START_DEBUG:
                coord = (
                    SIZE // 2 - 1,
                    SIZE // 2 - 1,
                    (SIZE // 2 - 1, SIZE // 2, Global.West),
                )
            else:
                coord = temple.findTemple(sector, Grass)
            temple.makeBunker(sector, coord)
            temple.generate(sector, coord)
            sector.makeEncounters(
                level, util.d(3, 10), MARSH_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )
        else:
            sector.makeEncounters(
                level, util.d(5, 10), MARSH_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )


# ________________________________________
class MountainsGen(MapGenerator.MapGenerator):
    def generate(self, sector):
        level = sector.level[0]
        sector.makeSquiggle(
            level,
            Mountain,
            MOUNTAINS_FEATURES,
            density=2,
            chance=50,
            iterations=6,
            generations=8,
        )
        sector.makeBorders(level, (Rough, Scrub))
        hack = (
            Global.HACK
            and sector.wx == Global.START_HACK[0]
            and sector.wy == Global.START_HACK[1]
        )
        if Global.START_DEBUG:
            print(
                "hack=%d, mountains %d,%d, START_HACK=%s"
                % (hack, sector.wx, sector.wy, Global.START_HACK)
            )
        if hack or Global.START_DEBUG or util.d(1, 4) == 1:
            temple = Temple.Temple()
            coord = temple.findTemple(sector, Mountain)
            temple.generate(sector, coord)
            sector.makeEncounters(
                level, util.d(3, 10), MOUNTAINS_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )
        else:
            sector.makeEncounters(
                level, util.d(5, 10), MOUNTAINS_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
            )


# ________________________________________
class PlainsGen(MapGenerator.MapGenerator):
    def generate(self, sector):
        level = sector.level[0]
        sector.makeRandom(level, PLAINS_FEATURES)
        level.drawRectangle(0, 0, SIZE - 1, SIZE - 1, Grass)
        for i in range(util.d(1, 10) - 5):
            d = util.d(2, 4)
            x0 = util.d(1, SIZE - d - 1)
            y0 = util.d(1, SIZE - d - 1)
            x1 = x0 + d - 1
            y1 = y0 + d - 1
            level.fillRectangle(x0 + 1, y0 + 1, x1 - 1, y1 - 1, Water)
            level.fillRectangle(x0 + 1, y0, x1 - 1, y0, Sand)
            level.fillRectangle(x0 + 1, y1, x1 - 1, y1, Sand)
            level.fillRectangle(x0, y0 + 1, x0, y1 - 1, Sand)
            level.fillRectangle(x1, y0 + 1, x1, y1 - 1, Sand)
            for y in range(y0 + 1, y1):
                if util.d(1, 2) == 1:
                    level.setTerrain(x0 + 1, y, Sand)
                if util.d(1, 2) == 1:
                    level.setTerrain(x1 - 1, y, Sand)
            for x in range(x0 + 1, x1):
                if util.d(1, 2) == 1:
                    level.setTerrain(x, y0 + 1, Sand)
                if util.d(1, 2) == 1:
                    level.setTerrain(x, y1 - 1, Sand)
        # now place critters and monsters
        sector.makeEncounters(
            level, util.d(5, 10), PLAINS_ENCOUNTERS, Terrain.ENC_TERRAIN_OUTDOORS
        )


# ________________________________________
class WaterGen(MapGenerator.MapGenerator):
    def generate(self, sector):
        level = sector.level[0]
        level.fillRectangle(0, 0, SIZE - 1, SIZE - 1, Water)
        # add a beach, and possibly a dock, if the next sector is not water
        for d in range(Global.NDIRS):
            dx = Global.DX[d]
            dy = Global.DY[d]
            neighbor = Global.umbra.game.getSectorType(sector.wx + dx, sector.wy + dy)
            if not neighbor or neighbor == Global.SECTOR_Water:
                continue
            if d == Global.North:
                x = -1
                y = 0
            elif d == Global.East:
                x = SIZE - 1
                y = -1
            elif d == Global.South:
                x = -1
                y = SIZE - 1
            elif d == Global.West:
                x = 0
                y = -1
            if x < 0:
                level.fillRectangle(0, y, SIZE - 1, y, Terrain.Sand)
                x = util.d(1, SIZE - 2)
                y -= dy
            else:
                level.fillRectangle(x, 0, x, SIZE - 1, Terrain.Sand)
                x -= dx
                y = util.d(1, SIZE - 2)
            if util.d(1, 2) == 1:
                level.setTerrain(x, y, Terrain.Dock)
                boat = Vehicle.makeBoat(d)
                level.addStuff(x, y, boat)
