from . import Global, Sprite, util

VOID = -1


class Thing:
    # id=String
    # name=String
    # __coord=Int (levelnum<<20)|(y<<10)|x, -1=void
    # facing=Int
    # sprite=String
    # pose=Int
    # light_level=Int #0-10, optional attribute
    def __init__(self, name, sprite):
        self.name = name
        self.id = "%s%d" % (name, id(self))
        self.__coord = VOID
        self.facing = Global.North
        self.sprite = sprite
        self.pose = 0

    def __str__(self):
        return self.name

    def checkStatus(self):
        pass

    def draw(self, canvas, nx, ny, facing, light):
        if not self.sprite:
            return  # invisible things
        spr = Sprite.getSprite(self.sprite)
        if spr:
            spr.draw(self, canvas, nx, ny, facing, light, self.facing)
        else:
            canvas.drawBlock3D(nx, ny, "#ff0000", "#000000", height=0.8)

    def isBlocking(self, who):
        return 0

    def isOpaque(self):
        return 0

    def light(self, color, light):
        if Global.LIGHT and light < 10:
            return util.colorTransform(color, scale=light)
        return color

    def message(self, msg):
        pass

    def move(self, level0, x0, y0, level1, x1, y1):
        # leave the old grid...
        if level0:
            if not level0.removeStuff(x0, y0, self):
                return 0
        # move to the new one...
        if level1:
            if not level1.addStuff(x1, y1, self):
                return 0
            level1.checkScript(x1, y1, self)
        return 1

    def moveBlocked(self, level, x, y):
        """Returns None if okay to move, or a string explaining why not."""

    def nextTurn(self, turn, level):
        pass

    def setCoord(self, levelnum, x=0, y=0):
        #        if Global.DEBUG:
        #            print "%s.setCoord(%d, %d, %d)" % (self.name, levelnum, x, y)
        if levelnum < 0:
            self.__coord = levelnum
        else:
            self.__coord = (levelnum << 20) | (y << 10) | x

    def trigger(self, who):
        """Returns 0 if the item cannot be triggered, or 1 if it was, even if
        it was an unsuccessful attempt."""
        return 0

    def x(self):
        if self.__coord < 0:
            return self.__coord
        return self.__coord & 0x3FF

    def y(self):
        if self.__coord < 0:
            return self.__coord
        return (self.__coord >> 10) & 0x3FF

    def levelnum(self):
        if self.__coord < 0:
            return self.__coord
        return self.__coord >> 20
