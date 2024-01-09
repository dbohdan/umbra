import os

from . import Global, util

SPRITES = {}

LIGHT = Global.LIGHT

CMD_DEFINE = "d"  # d:<name>:<value>
CMD_BLOCK = "b"  # b:<side>:<fill color>:<outline color>:<opts>
CMD_PANEL = "p"  # p:<side>:<fill color>:<outline color>:[lrnftbLRNF]:<opts>
CMD_POLYGON = "y"  # y:<side>:<fill color>:<outline color>:<points>:<opts>
CMD_LINE = "l"  # l:<side>:<fill color>:<points>:<opts>
# only two points are used, for top-left and bottom-right
CMD_OVAL = "o"  # o:<side>:<fill color>:<outline color>:<points>:<opts>
# only the y coord of the first point is used
CMD_NAME = "n"  # n:<side>:<fill color>:<points>
# emits all LRNF panels and clears them for another model
CMD_EMIT = "e"  # e
CMD_PANEL_EMIT = "P"

# panels equivalent to ahead, right, back, left
PANEL_EMIT = "NRFL"
EMIT_TRANSLATE = (0, 1, 3, 2)
EMIT_PANEL = [Global.Side_Far, Global.Side_Left, Global.Side_Right, Global.Side_Near]

SIDE_ANY = "a"  # any side
SIDE_LEFT = "l"  # left (nx<0)
SIDE_RIGHT = "r"  # right (nx>0)
SIDE_CENTER = "c"  # center (nx==0)
SIDE_NOT_HERE = "n"  # not here (nx!=0 or ny!=0)


class Sprite:
    # name=String
    # nfacings=Int
    # nposes=Int
    # commands=[][]
    def __init__(self, name, nfacings=1, nposes=1):
        name = util.purifyName(name, slashOkay=1)
        self.name = name
        self.nfacings = nfacings
        self.nposes = nposes
        filename = os.path.join("db", "model", "%s.mod" % name)
        file = open(filename)
        lines = file.readlines()
        file.close()
        self.__parseCommands(lines)

    def __checkSides(self, side, nx, ny):
        for s in side:
            if s == SIDE_ANY:
                return 1
            elif s == SIDE_LEFT:
                if nx < 0:
                    pass
                else:
                    return 0
            elif s == SIDE_RIGHT:
                if nx > 0:
                    pass
                else:
                    return 0
            elif s == SIDE_CENTER:
                if nx == 0:
                    pass
                else:
                    return 0
            elif s == SIDE_NOT_HERE:
                if nx != 0 or ny != 0:
                    pass
                else:
                    return 0
            else:
                raise OSError("%s: Unknown side condition '%s'" % (self.name, s))
        return 1

    def __parseCommands(self, lines):
        self.commands = []
        dict = {}
        i = 0
        for line in lines:
            ++i
            line = line.strip()
            if not line or line[0] == "#":
                continue
            command = line.split(":")
            cmdlen = len(command)
            cmd = command[0]
            if cmd == CMD_DEFINE:
                name = command[1]
                value = command[2]
                dict[name] = util.number(value)
                continue
            # drawing commands:
            if cmdlen > 1:
                side = command[1]
                self.__checkSides(side, 0, 0)
            if cmdlen > 2:
                fill = command[2]
            if cmd == CMD_BLOCK:
                outline = command[3]
                if len(command) > 4:
                    command[4] = self.__parseOpts(command[4])
                else:
                    command.append({})
            elif cmd == CMD_PANEL:
                outline = command[3]
                panel = command[4]
                if panel in PANEL_EMIT:
                    command[0] = CMD_PANEL_EMIT
                else:
                    try:
                        panel = Global.SIDE_CHARS.index(panel)
                    except ValueError:
                        raise OSError("%s: Unknown panel '%s'" % (self.name, panel))
                command[4] = panel
                if len(command) > 5:
                    command[5] = self.__parseOpts(command[5])
                else:
                    command.append({})
            elif cmd == CMD_POLYGON:
                outline = command[3]
                command[4] = self.__parsePoints(command[4], dict)
                if len(command) > 5:
                    command[5] = self.__parseOpts(command[5])
                else:
                    command.append({})
            elif cmd == CMD_LINE:
                command[3] = self.__parsePoints(command[3], dict)
                if len(command) > 4:
                    command[4] = self.__parseOpts(command[4])
                else:
                    command.append({})
            elif cmd == CMD_OVAL:
                outline = command[3]
                command[4] = self.__parsePoints(command[4], dict)
                if len(command) > 5:
                    command[5] = self.__parseOpts(command[5])
                else:
                    command.append({})
            elif cmd == CMD_NAME:
                command[3] = self.__parsePoints(command[3], dict)
            elif cmd == CMD_EMIT:
                pass
            self.commands.append(command)

    def __parseOpts(self, str):
        dict = {}
        if not str:
            return dict
        for opt in str.split(","):
            kw = opt.split("=")
            key = kw[0].strip()
            value = kw[1].strip()
            dict[key] = util.number(value)
        return dict

    def __parsePoints(self, str, dict={}):
        points = []
        for xyz in str.split(";"):
            xyz = xyz.strip()
            if not xyz:
                continue
            xyz = xyz.split(",")
            x = util.number(xyz[0])
            try:
                if util.isString(x):
                    x = dict[x.strip()]
            except KeyError:
                raise KeyError("%s: Did not find '%s' in %s" % (self.name, x, dict))
            y = util.number(xyz[1])
            try:
                if util.isString(y):
                    y = dict[y.strip()]
            except KeyError:
                raise KeyError("%s: Did not find '%s' in %s" % (self.name, y, dict))
            z = util.number(xyz[2])
            try:
                if util.isString(z):
                    z = dict[z.strip()]
            except KeyError:
                raise KeyError("%s: Did not find '%s' in %s" % (self.name, z, dict))
            points.append(x)
            points.append(y)
            points.append(z)
        return points

    def light(self, color, light):
        if LIGHT and light != 10:
            return util.colorTransform(color, scale=light)
        return color

    def draw(self, thing, canvas, nx, ny, facing, light, spritefacing):
        iline = 0
        emit_data = None
        for command in self.commands:
            ++iline
            #            if Global.DEBUG:
            #                print "%s: draw %d,%d, %s" % (self.name, nx, ny, command)
            cmd = command[0]
            cmdlen = len(command)
            if cmdlen > 1:
                side = command[1]
                okay = self.__checkSides(side, nx, ny)
                if not okay:
                    continue
            if cmdlen > 2:
                fill = self.light(command[2], light)
            if cmd == CMD_BLOCK:
                outline = self.light(command[3], light)
                opts = command[4]
                canvas.drawBlock3D(nx, ny, fill, outline, **opts)
            elif cmd == CMD_PANEL:
                outline = self.light(command[3], light)
                panel = command[4]
                opts = command[5]
                canvas.drawPanel3D(panel, nx, ny, fill, outline, **opts)
            elif cmd == CMD_PANEL_EMIT:
                outline = self.light(command[3], light)
                panel = command[4]
                opts = command[5]
                #       sprite            F=0 R=1 L=2 N=3
                #       N=0 E=1 S=2 W=3
                # player+---------------   (player-sprite+NDIRS)%NDIRS  side
                #   N=0| F   R   N   L                              0  F=0
                #   E=1| L   F   R   N                              1  L=2
                #   S=2| N   L   F   R                              2  N=3
                #   W=3| R   N   L   F                              3  R=1
                i = (facing - spritefacing + Global.NDIRS) % Global.NDIRS
                # The order given by the above formula is Far, Left, Near, Right; but since it
                # must be drawn in the order listed in EMIT_PANEL: Far, Left, Right, Near
                # (I have no hidden surface removal and I must scream!), it needs to be
                # transformed to get the index into emit_data.
                k = EMIT_TRANSLATE[(i + PANEL_EMIT.index(panel)) % Global.NDIRS]
                if emit_data is None:
                    emit_data = [[], [], [], []]
                emit_data[k].append((fill, outline, opts))
            elif cmd == CMD_POLYGON:
                outline = self.light(command[3], light)
                points = command[4][:]  # duplicate for translation
                for i in range(0, len(points), 3):
                    points[i] = points[i] + nx * 2
                    points[i + 2] = points[i + 2] + ny * 2 + 2
                opts = command[5]
                canvas.drawPolygon3D(points, fill, outline, **opts)
            elif cmd == CMD_LINE:
                points = command[3][:]  # duplicate for translation
                for i in range(0, len(points), 3):
                    points[i] = points[i] + nx * 2
                    points[i + 2] = points[i + 2] + ny * 2 + 2
                opts = command[4]
                canvas.drawLine3D(points, fill, **opts)
            elif cmd == CMD_OVAL:
                outline = self.light(command[3], light)
                points = command[4][:]  # duplicate for translation
                for i in range(0, len(points), 3):
                    points[i] = points[i] + nx * 2
                    points[i + 2] = points[i + 2] + ny * 2 + 2
                opts = command[5]
                canvas.drawOval3D(points, fill, outline, **opts)
            elif cmd == CMD_NAME:
                points = command[3]
                if ny <= Global.TEXT3D_DIST:
                    canvas.drawText3D(
                        nx * 2,
                        points[1],
                        ny * 2 + 2,
                        thing.name,
                        fill=fill,
                    )
            elif cmd == CMD_EMIT:
                for k in range(Global.NDIRS):
                    panel = EMIT_PANEL[k]
                    for data in emit_data[k]:
                        fill, outline, opts = data
                        canvas.drawPanel3D(panel, nx, ny, fill, outline, **opts)
                emit_data = None
            else:
                assert 0, "%s: Unknown command %s" % (self.name, command)
        # end for


def getSprite(name):
    if not name:
        return None
    if name in SPRITES:
        return SPRITES[name]
    try:
        spr = Sprite(name)
        SPRITES[name] = spr
        return spr
    except OSError as detail:
        print("Unable to read model %s: %s" % (name, detail))
        SPRITES[name] = None
        return None
