import time

from . import Global, Terrain, util

SIZE = Global.LEVELSIZE

OPT_ITERATIONS = "iterations (1+)"
OPT_WALL_CHANCE = "wall chance (%)"
OPT_COUNT_WALLS = "count walls (0/1)"
OPT_WALL_N_MIN = "wall neighbors min (0-9)"
OPT_WALL_N_MAX = "wall neighbors max (0-9)"
OPT_CLEAR_N_MIN = "clear neighbors min (0-9)"
OPT_CLEAR_N_MAX = "clear neighbors max (0-9)"
OPT_WALL_TERRAIN = "wall terrain (Terrain)"
OPT_CLEAR_TERRAIN = "clear terrain (Terrain)"

DEFAULT_OPTS = {
    OPT_ITERATIONS: 2,
    OPT_WALL_CHANCE: 50,
    OPT_COUNT_WALLS: 1,
    OPT_WALL_N_MIN: 3,
    OPT_WALL_N_MAX: 3,
    OPT_CLEAR_N_MIN: 6,
    OPT_CLEAR_N_MAX: 9,
    OPT_WALL_TERRAIN: Terrain.Stone_Wall,
    OPT_CLEAR_TERRAIN: Terrain.Grass,
}

# Giant alien buildings:
# Iterations=20, wall_n_min=0, wall_n_max=4, clear_n_min=3, clear_n_max=4

# Tunnels:
# Iterations=2, wall_n_min=0, wall_n_max=2, clear_n_min=4, clear_n_max=4,
# count_walls=0

# Maze:
# Iterations=2, wall_n_min=4, wall_n_max=4, clear_n_min=0, clear_n_max=2

# Ruins:
# Iterations=3, wall_n_min=3, wall_n_max=3, clear_n_min=6, clear_n_max=9


class CALevel:
    # level=Level
    # terrain=Terrain[][]
    # opts={}
    def __init__(self, level, opts):
        self.level = level
        self.opts = util.dictAdd(DEFAULT_OPTS, opts)
        self.fillTerrain()
        self.generate()

    def count(self, x, y):
        COUNT_WALLS = self.opts[OPT_COUNT_WALLS]
        WALL = self.opts[OPT_WALL_TERRAIN]
        CLEAR = self.opts[OPT_CLEAR_TERRAIN]
        n = 0
        terrain = self.terrain
        for ny in range(y - 1, y + 2):
            for nx in range(x - 1, x + 2):
                if nx == x and ny == y:
                    continue
                if nx < 0 or nx >= SIZE or ny <= 0 or ny >= SIZE:
                    continue
                if COUNT_WALLS:
                    if terrain[ny * SIZE + nx] == WALL:
                        n += 1
                else:
                    if terrain[ny * SIZE + nx] == CLEAR:
                        n += 1
        return n

    def fillTerrain(self):
        WALL_CHANCE = self.opts[OPT_WALL_CHANCE]
        WALL = self.opts[OPT_WALL_TERRAIN]
        CLEAR = self.opts[OPT_CLEAR_TERRAIN]
        terrain = self.terrain = util.makeArray(SIZE * SIZE, None)
        for y in range(SIZE):
            for x in range(SIZE):
                if util.d(1, 100) <= WALL_CHANCE:
                    ter = WALL
                else:
                    ter = CLEAR
                terrain[y * SIZE + x] = ter

    def generate(self):
        ITERATIONS = self.opts[OPT_ITERATIONS]
        WALL_N_MIN = self.opts[OPT_WALL_N_MIN]
        WALL_N_MAX = self.opts[OPT_WALL_N_MAX]
        CLEAR_N_MIN = self.opts[OPT_CLEAR_N_MIN]
        CLEAR_N_MAX = self.opts[OPT_CLEAR_N_MAX]
        WALL = self.opts[OPT_WALL_TERRAIN]
        CLEAR = self.opts[OPT_CLEAR_TERRAIN]
        terrain = self.terrain

        for iter in range(ITERATIONS):
            if Global.TIMING:
                t1 = time.clock()
            for y in range(SIZE):
                for x in range(SIZE):
                    n = self.count(x, y)
                    xy = y * SIZE + x
                    if terrain[xy] == WALL:
                        if n >= WALL_N_MIN and n <= WALL_N_MAX:
                            terrain[xy] = CLEAR
                    else:
                        if n >= CLEAR_N_MIN and n <= CLEAR_N_MAX:
                            terrain[xy] = WALL
            if Global.TIMING:
                t2 = time.clock()
                print("CALevel iteration %d took %dms" % (iter, (t2 - t1) * 1000))

        level = self.level
        for y in range(SIZE):
            for x in range(SIZE):
                level.setTerrain(x, y, terrain[y * SIZE + x])
