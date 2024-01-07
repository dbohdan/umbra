from . import Entity, Level, Umbra
from . import Canvas3D, OkayDialog
from . import Global, util
from tkinter import *
import os, string, sys, time, types

STATUS_WIDTH = 64
CHAR_STATUS_WIDTH = 220
DEFAULT_SIZE = 480
FOG = 0

XGEOM = 0
YGEOM = 0


# ________________________________________
class UmbraTk(Umbra.Umbra):
    def __init__(self, root):
        i = util.indexOf("-fog", sys.argv)
        if i >= 0:
            global FOG
            FOG = 1
            sys.argv.pop(i)

        self.size = DEFAULT_SIZE
        i = util.indexOf("-size", sys.argv)
        if i >= 0 and i < len(sys.argv) - 1:
            self.size = int(sys.argv[i + 1])
            sys.argv.pop(i)
            sys.argv.pop(i)

        self.dialog_geometry = "+%d+%d" % (XGEOM + self.size, YGEOM)

        self.root = root
        root.tk_strictMotif(1)
        root.title(Global.TITLE)
        root.geometry("+%d+%d" % (XGEOM, YGEOM))
        root.tk_setPalette(
            activeBackground="#333333",
            activeForeground="#00ff00",
            background="#000000",
            disabledForeground="#006666",
            foreground="#00ff00",
            highlightBackground="#006600",
            highlightColor="#00ff00",
            insertBackground="#ff0000",
            selectBackground="#003300",
            selectForeground="#00ff00",
            selectColor="#00ffff",
            troughColor="#00ff00",
        )
        self.__cursor = self.root["cursor"]

        if os.name == "nt":
            self.__tinyfont = ("Courier", 8)
            self.__statusfont = ("Helvetica", 12)
            self.__titlefont = ("Helvetica", 64)
            self.__normalfont = ("Lucida", 10)
            self.__buttonfont = ("Courier", 8)
            self.__charfont = ("Courier", 10, "bold")
        else:
            self.__tinyfont = ("Lucida Typewriter", 8)
            self.__statusfont = ("Helvetica", 14)
            self.__titlefont = ("Helvetica", 72)
            self.__normalfont = ("Lucida", 12)
            self.__buttonfont = ("Lucida Typewriter", 10)
            self.__charfont = ("Courier", 12, "bold")

        root.option_add("*Label*font", self.__normalfont)

        left = Frame(root, borderwidth=-1, relief=FLAT)
        right = Frame(root, borderwidth=-1, relief=FLAT)

        self.status = []
        for i in range(3):
            lbl = Label(
                left,
                text="",
                font=self.__statusfont,
                foreground="#ffff00",
                anchor=NW,
                justify=LEFT,
            )
            lbl.pack(side=TOP, fill=X, anchor=NW)
            self.status.append(lbl)

        self.canvas = Canvas3D.Canvas3D(
            left,
            width=self.size,
            height=self.size,
            highlightthickness=0,
            borderwidth=-1,
            relief=FLAT,
        )
        if os.name == "nt":
            self.canvas.font3dsize = 58
        else:
            self.canvas.font3dsize = 72
        # the center of the screen for 3D projection
        self.canvas.ORIGIN = self.size // 2
        # the smaller this is, the wider the FOV
        self.canvas.SCREEN_Z = self.size * 2 // 3

        self.canvas.create_text(
            self.size // 2,
            self.size // 2 - 72,
            text=Global.TITLE,
            font=self.__titlefont,
            fill="#00ff00",
        )
        self.canvas.create_text(
            self.size // 2,
            self.size // 2,
            text=Global.COPYRIGHT,
            font=self.__normalfont,
            fill="#00ff00",
        )
        self.canvas.pack(side=TOP)

        self.charStatus = Canvas(
            right,
            highlightthickness=0,
            width=CHAR_STATUS_WIDTH,
            borderwidth=-1,
            relief=FLAT,
        )
        self.charStatus.pack(side=TOP, fill=BOTH, expand=YES, anchor=N)
        buttonfunc = lambda e, s=self: s.__charButton(e)
        self.charStatus.bind("<Button-1>", buttonfunc)
        self.charButtons = []

        buttons = Frame(right, borderwidth=-1, relief=FLAT)
        self.__makeMainButton(buttons, Umbra.M_Turn_Left, 0, 0, "<Left>")
        self.__makeMainButton(buttons, Umbra.M_Step_Forward, 1, 0, "<Up>")
        self.__makeMainButton(buttons, Umbra.M_Turn_Right, 2, 0, "<Right>")
        self.__makeMainButton(buttons, Umbra.M_Step_Left, 0, 1, "<Shift-Left>")
        self.__makeMainButton(buttons, Umbra.M_Wait, 1, 1)
        self.__makeMainButton(buttons, Umbra.M_Step_Right, 2, 1, "<Shift-Right>")
        self.__makeMainButton(buttons, Umbra.M_Turn_Back, 0, 2, "<Down>")
        self.__makeMainButton(buttons, Umbra.M_Step_Back, 1, 2, "<Shift-Down>")
        self.__makeMainButton(buttons, Umbra.M_Map, 2, 2)
        self.__makeMainButton(buttons, Umbra.M_Board, 2, 3)
        Frame(buttons, width=8, borderwidth=-1, relief=FLAT).grid(column=3, row=0)
        Frame(buttons, width=8, borderwidth=-1, relief=FLAT).grid(column=3, row=1)
        Frame(buttons, width=8, borderwidth=-1, relief=FLAT).grid(column=3, row=2)
        self.__makeMainButton(buttons, Umbra.M_Get_Item, 4, 0)
        self.__makeMainButton(buttons, Umbra.M_Talk_Trigger, 4, 1)
        self.__makeMainButton(buttons, Umbra.M_Attack, 4, 2)
        self.__makeMainButton(buttons, Umbra.M_Quit, 4, 3)
        buttons.pack(side=BOTTOM, fill=X, anchor=S)

        left.pack(side=LEFT, anchor=NW, fill=Y, expand=YES)
        right.pack(side=LEFT, anchor=NW, fill=Y, expand=YES)

        self.acceptMainMenu = 0

        Umbra.Umbra.__init__(self)

    def __charButton(self, event):
        y = event.y
        for btn in self.charButtons:
            if y <= btn[0]:
                self.__mainMenuButton(btn[1])
                return

    def __makeMainButton(self, buttons, m, x, y, extrakey=None):
        key = Umbra.MAIN_MENU_KEYS[m]
        text = "[%s]\n%s" % (key, Umbra.MAIN_MENU[m])
        text = text.replace(" ", "\n")
        b = Button(
            buttons,
            text=text,
            font=self.__buttonfont,
            padx=0,
            pady=0,
            width=7,
            height=3,
            borderwidth=1,
            takefocus=0,
            highlightthickness=0,
            command=lambda s=self, m=m: s.__mainMenuButton(m),
        )
        buttonfunc = lambda e, s=self, m=m: s.__mainMenuButton(m)
        self.root.bind(key, buttonfunc)
        if extrakey:
            self.root.bind(extrakey, buttonfunc)
        b.grid(column=x, row=y, sticky=NSEW)

    def __mainMenuButton(self, m):
        if Global.DEBUG:
            print("__mainMenuButton(self, %d), accept=%d" % (m, self.acceptMainMenu))
        if not self.acceptMainMenu:
            return
        self.acceptMainMenu = 0
        self.mainMenu(m)
        self.acceptMainMenu = 1

    def __showFog(self):
        ny = Global.VIEWDIST + 1
        left = -Global.VIEWDIST
        right = Global.VIEWDIST
        for nx in range(left, right + 1):
            self.canvas.drawPanel3D(
                Global.Side_Near, nx, ny, "#ffffff", "", stipple="gray75"
            )

    def __showGridAs3D(self, nx, ny, grid, facing):
        if not grid[3]:
            return
        light = grid[2]
        if grid[0] == None:
            self.canvas.drawBlock3D(nx, ny, "", "#00ff00")
            return
        grid[0].draw(self.canvas, nx, ny, facing, light)
        if grid[1]:
            for item in grid[1]:
                item.draw(self.canvas, nx, ny, facing, light)

    def __showGridAsText(self, grid, sx, sy):
        if grid[0] != None:
            if grid[1]:
                n = len(grid[1])
            else:
                n = 0
            text = "%2s%1d" % (grid[0], n)
            self.canvas.create_text(
                sx, sy, text=text, font=self.__tinyfont, fill="#ff0000", anchor=NW
            )
        else:
            self.canvas.create_rectangle(sx, sy, sx + 20, sy + 20, outline="#663333")

    def __showMapAs3D(self, map, facing):
        self.timing_sky_start = time.time()
        self.__showSky(facing)
        self.timing_sky_end = time.time()

        size = Global.VIEWSIZE
        center = Global.VIEWDIST
        left = center - Global.VIEWSIDEDIST
        right = center + Global.VIEWSIDEDIST
        if FOG:
            self.__showFog()
        if facing == Global.North:
            self.__showMapNS3D(
                map, facing, 0, center + 1, 1, left, center, right, center - 1, 1
            )
        elif facing == Global.East:
            self.__showMapEW3D(
                map,
                facing,
                size - 1,
                center - 1,
                -1,
                left,
                center,
                right,
                center - 1,
                1,
            )
        elif facing == Global.South:
            self.__showMapNS3D(
                map,
                facing,
                size - 1,
                center - 1,
                -1,
                right,
                center,
                left,
                center + 1,
                -1,
            )
        else:  # facing == Global.West
            self.__showMapEW3D(
                map, facing, 0, center + 1, 1, right, center, left, center + 1, -1
            )

    def __showMapNS3D(self, map, facing, y0, y1, dy, x0, x1, x2, x3, dx):
        ny = Global.VIEWDIST
        for y in range(y0, y1, dy):
            nx = -Global.VIEWSIDEDIST
            for x in range(x0, x1, dx):
                self.__showGridAs3D(nx, ny, map[x][y], facing)
                nx += 1
            nx = Global.VIEWSIDEDIST
            for x in range(x2, x3, -dx):
                self.__showGridAs3D(nx, ny, map[x][y], facing)
                nx -= 1
            ny -= 1

    def __showMapEW3D(self, map, facing, x0, x1, dx, y0, y1, y2, y3, dy):
        ny = Global.VIEWDIST
        for x in range(x0, x1, dx):
            nx = -Global.VIEWSIDEDIST
            for y in range(y0, y1, dy):
                self.__showGridAs3D(nx, ny, map[x][y], facing)
                nx += 1
            nx = Global.VIEWSIDEDIST
            for y in range(y2, y3, -dy):
                self.__showGridAs3D(nx, ny, map[x][y], facing)
                nx -= 1
            ny -= 1

    def __showMapAsText(self, map, facing, cellsize):
        left = Global.VIEWDIST - 5
        right = Global.VIEWDIST + 5
        if facing == Global.North:
            sy = 0
            for y in range(left, right + 1):
                sx = 0
                for x in range(left, right + 1):
                    grid = map[x][y]
                    self.__showGridAsText(grid, sx, sy)
                    sx += cellsize
                sy += cellsize
        elif facing == Global.East:
            sy = 0
            for x in range(right, left - 1, -1):
                sx = 0
                for y in range(left, right + 1):
                    grid = map[x][y]
                    self.__showGridAsText(grid, sx, sy)
                    sx += cellsize
                sy += cellsize
        elif facing == Global.South:
            sy = 0
            for y in range(right, left - 1, -1):
                sx = 0
                for x in range(right, left - 1, -1):
                    grid = map[x][y]
                    self.__showGridAsText(grid, sx, sy)
                    sx += cellsize
                sy += cellsize
        else:  # facing == Global.West:
            sy = 0
            for x in range(left, right + 1):
                sx = 0
                for y in range(right, left - 1, -1):
                    grid = map[x][y]
                    self.__showGridAsText(grid, sx, sy)
                    sx += cellsize
                sy += cellsize

    def __showSky(self, facing):
        size = self.size
        if self.game.getLevel().levelnum != 0:
            self.canvas.create_rectangle(
                0, 0, size, size, fill="#000000", outline="#000000"
            )
            return
        half = size // 2
        hour = self.game.hour
        ihour = int(hour)
        eclipse = self.game.eclipse
        sunfacing = self.game.sunfacing
        if sunfacing != -1:
            sunheight = int(size * self.game.sunheight)
        moonfacing = self.game.moonfacing
        if moonfacing != -1:
            moonheight = int(size * self.game.moonheight)
        moonphase = self.game.moonphase
        moonorbit = self.game.moonorbit

        if not eclipse and hour >= 5.0 and hour < 20.0:
            # fill the sky
            if ihour == 5 or ihour == 19:
                skyfill = "#ccbbee"
            elif facing == sunfacing or sunfacing == -1:
                skyfill = "#77aaff"
            elif facing == Global.turnBack(sunfacing):
                skyfill = "#5588dd"
            else:
                skyfill = "#6699ee"
            self.canvas.create_rectangle(
                0, 0, size, size, fill=skyfill, outline=skyfill
            )

            # sunrise
            if ihour == 5:
                if facing == Global.East:
                    self.canvas.create_rectangle(
                        0,
                        size // 3,
                        size,
                        size,
                        fill="#eebbcc",
                        outline="",
                        stipple="gray25",
                    )
                elif facing == Global.West:
                    self.canvas.create_rectangle(
                        0, 0, size, size, fill="#000044", outline="", stipple="gray50"
                    )
            # sunset
            elif ihour == 19:
                if facing == Global.West:
                    self.canvas.create_rectangle(
                        0,
                        size // 3,
                        size,
                        size,
                        fill="#221166",
                        outline="",
                        stipple="gray25",
                    )
                elif facing == Global.East:
                    self.canvas.create_rectangle(
                        0, 0, size, size, fill="#000044", outline="", stipple="gray50"
                    )

            # father sun
            if facing == sunfacing:
                self.canvas.create_oval(
                    half - 16,
                    sunheight,
                    half + 16,
                    sunheight + 32,
                    fill="#ffeeaa",
                    outline="",
                )

        else:  # night or eclipse
            skyfill = "#000000"
            self.canvas.create_rectangle(
                0, 0, size, size, fill=skyfill, outline=skyfill
            )
            stars = self.game.stars
            for i in range(0, len(stars), 4):
                x = int(stars[i] * size)
                y = int(stars[i + 1] * size)
                width = stars[i + 2]
                color = stars[i + 3]
                if facing == Global.North:
                    x = (x - hour * size // 24) % size
                elif facing == Global.East:
                    y = (y - hour * size // 24) % size
                elif facing == Global.South:
                    x = (x + hour * size // 24) % size
                elif facing == Global.West:
                    y = (y + hour * size // 24) % size
                self.canvas.create_line(x, y, x, y + width, fill=color)

        # mother moon
        moonout = ""
        moonfill = util.colorTransform(
            skyfill,
            delta=(0x08, 0x08, 0x10),
        )
        if facing == moonfacing:
            if eclipse:
                # corona
                corona = util.d(2, 8) + 8
                for i in range(0, corona, 2):
                    self.canvas.create_oval(
                        half - 16 - i,
                        moonheight - i,
                        half + 16 + i,
                        moonheight + 32 + i,
                        fill="",
                        outline="#ffeeaa",
                    )
                # umbra
                self.canvas.create_oval(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill="#000000",
                    outline="",
                )
            elif moonphase == 0:  # new moon
                self.canvas.create_oval(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill=moonfill,
                    outline=moonout,
                )
            elif moonphase == 1:  # waxing crescent moon
                self.canvas.create_oval(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill=moonfill,
                    outline=moonout,
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill="#ddddff",
                    outline="",
                    start=135,
                    extent=90,
                    style=CHORD,
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    outline="#ddddff",
                    start=125,
                    extent=110,
                    style=ARC,
                    width=2,
                )
            elif moonphase == 2:  # waxing half moon
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill="#ddddff",
                    outline="",
                    start=90,
                    extent=180,
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill=moonfill,
                    outline=moonout,
                    start=270,
                    extent=180,
                )
            elif moonphase == 3:  # waxing gibbous moon
                self.canvas.create_oval(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill="#ddddff",
                    outline="",
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill=moonfill,
                    outline=moonout,
                    start=315,
                    extent=90,
                    style=CHORD,
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    outline=moonfill,
                    start=295,
                    extent=130,
                    style=ARC,
                    width=2,
                )
            elif moonphase == 4:  # full moon
                self.canvas.create_oval(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill="#ddddff",
                    outline="",
                )
            elif moonphase == 5:  # waning gibbous moon
                self.canvas.create_oval(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill="#ddddff",
                    outline="",
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill=moonfill,
                    outline=moonout,
                    start=135,
                    extent=90,
                    style=CHORD,
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    outline=moonfill,
                    start=115,
                    extent=130,
                    style=ARC,
                    width=2,
                )
            elif moonphase == 6:  # waning half moon
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill="#ddddff",
                    outline="",
                    start=270,
                    extent=180,
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill=moonfill,
                    outline=moonout,
                    start=90,
                    extent=180,
                )
            elif moonphase == 7:  # waning crescent moon
                self.canvas.create_oval(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill=moonfill,
                    outline=moonout,
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    fill="#ddddff",
                    outline="",
                    start=315,
                    extent=90,
                    style=CHORD,
                )
                self.canvas.create_arc(
                    half - 16,
                    moonheight,
                    half + 16,
                    moonheight + 32,
                    outline="#ddddff",
                    start=305,
                    extent=110,
                    style=ARC,
                    width=2,
                )

    def __update(self):
        if not self.game:
            return
        if Global.TIMING:
            self.timing_update_start = time.clock()
        party = self.game.party
        cs = self.charStatus
        for i in cs.find_all():
            cs.delete(i)
        self.charButtons = []
        y = 0
        w = cs["width"]
        for i in range(len(party)):
            key = str(i + 1)
            who = party[i]
            y = who.drawStatus(cs, self.__charfont, self.__tinyfont, y, key)
            m = -(i + 1)
            charfunc = lambda e, s=self, m=m: s.__mainMenuButton(m)
            self.root.bind(key, charfunc)
            self.charButtons.append((y, m))
        if Global.TIMING:
            self.timing_update_end = time.clock()
        self.root.update_idletasks()

    def alert(self, title, msg, type=Global.ALERT_WARNING):
        rc = OkayDialog.alert(self.root, title, msg, type)
        if type == Global.ALERT_YESNO:
            if rc:
                answer = "Yes"
            else:
                answer = "No"
            self.showStatus("%s %s" % (msg, answer))
        else:
            self.showStatus(msg)
        return rc

    def busy(self, state):
        if state:
            self.root.configure(cursor="watch")
            self.root.title(Global.TITLE + " - Please wait...")
        else:
            self.root.configure(cursor=self.__cursor)
            self.root.title(Global.TITLE)
        self.root.update_idletasks()

    def gameOver(self):
        self.alert(Global.TITLE, "Game Over", type=Global.ALERT_INFO)
        self.quit()

    def input(self, title, prompt):
        if Global.DEBUG:
            print("input title=%s, prompt=%s" % (title, prompt))
        dlg = OkayDialog.InputDialog(
            self.root, title, self.dialog_geometry, prompts=(prompt,)
        )
        return dlg.getAnswer(0)

    def menu(self, title, prompts, keys=None, banner=None):
        if Global.DEBUG:
            print(
                "menu title=%s, prompts=%s, keys=%s, banner=%s"
                % (title, prompts, keys, banner)
            )
        if not keys:
            a = ord("a")
            n = len(prompts)
            keys = []
            if prompts[0] == "Cancel":
                keys.append("0")
                n -= 1
            for i in range(n):
                if i <= 25:
                    keys.append(chr(a + i))
                else:
                    keys.append("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"[i - 25])
        dlg = OkayDialog.MenuDialog(
            self.root,
            title,
            self.dialog_geometry,
            prompts=prompts,
            keys=keys,
            banner=banner,
        )
        rc = dlg.getSelected()
        #        self.showStatus("%s %s" % (title, prompts[rc]) )
        return rc

    def showBlood(self, amount):
        for hit in range(amount):
            w = util.d(1, 10) + 5
            h = util.d(1, 10) + 5
            x = util.d(1, self.size - w - w)
            y = util.d(1, self.size - h - h)
            self.canvas.create_oval(
                x - w, y - h, x + w, y + h, fill="#ff0000", outline="", stipple="gray75"
            )
            i = x - w + util.d(1, 3) + 1
            j = x + w - 1
            while i < j:
                self.canvas.create_line(
                    i, y, i, self.size, width=2, fill="#ff0000", stipple="gray50"
                )
                i += util.d(1, 3) + 1
        self.root.update_idletasks()
        time.sleep(0.25)

    def showCharacter(self, ch, main=1):
        d = Entity.EntityDialog(
            self.root, ch.name, self.dialog_geometry, entity=ch, main=main
        )
        if main:
            return util.indexOf(d.button, Global.VIEW_MENU)

    def __relativeView(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        facing = self.game.getFacing()
        if facing == Global.North:
            vx = dx
            vz = -dy
        elif facing == Global.East:
            vx = dy
            vz = dx
        elif facing == Global.South:
            vx = -dx
            vz = dy
        else:
            vx = -dy
            vz = -dx
        return vx, 0, vz

    def showGunshot(self, x0, y0, x1, y1, fill="#cccccc", player=1):
        if player:
            vx0, vy0, vz0 = 0, 0, 0
            vx1, vy1, vz1 = self.__relativeView(x0, y0, x1, y1)
        else:
            leader = self.game.getLeader()
            px = leader.x()
            py = leader.y()
            vx0, vy0, vz0 = self.__relativeView(px, py, x0, y0)
            vx1, vy1, vz1 = self.__relativeView(px, py, x1, y1)
        if Global.DEBUG:
            print(
                "showGunshot %d,%d, %d,%d, v=%d,%d,%d, %d,%d,%d"
                % (x0, y0, x1, y1, vx0, vy0, vz0, vx1, vy1, vz1)
            )
        if vz0 >= 0 and vz1 >= 0:  # can't see it for back shots
            if player:
                vy0 = -0.75
                vz0 = -0.5
            self.canvas.drawLine3D(
                [vx0 * 2, vy0, vz0 * 2 + 2, vx1 * 2, vy1, vz1 * 2 + 2],
                fill,
                width=3,
                stipple="gray50",
            )
        self.root.update_idletasks()
        time.sleep(0.1)

    def showMap(self, map, facing):
        if Global.TIMING:
            t1 = time.clock()
        self.canvas.cls()
        self.__showMapAs3D(map, facing)
        #        self.__showMapAsText(map, facing, 20)
        self.__update()
        if Global.TIMING:
            t2 = time.clock()
            print(
                "showMap=%dms, showSky=%dms, update=%dms"
                % (
                    (t2 - t1) * 1000,
                    (self.timing_sky_end - self.timing_sky_start) * 1000,
                    (self.timing_update_end - self.timing_update_start) * 1000,
                )
            )

    def showText(self, title, text):
        if Global.DEBUG:
            print("showText title=%s, text=%s" % (title, text))
        OkayDialog.TextDialog(self.root, title, self.dialog_geometry, text=text)

    def startMainMenu(self, setAccept=1):
        if setAccept:
            self.acceptMainMenu = 1

    def showStatus(self, text):
        if Global.DEBUG:
            print("showStatus '%s'" % text)
        print(text)
        oldtext = self.status[2]["text"]
        textlen = len(text)
        if oldtext == text:
            self.status[2]["text"] = "%s (x2)" % text
        elif len(oldtext) - textlen >= 5 and util.startsWith(oldtext, "%s (x" % text):
            n = int(oldtext[textlen + 3 : -1]) + 1
            self.status[2]["text"] = "%s (x%d)" % (text, n)
        else:
            self.status[0]["text"] = self.status[1]["text"]
            self.status[1]["text"] = oldtext
            self.status[2]["text"] = util.foldLines(text, STATUS_WIDTH)
        self.root.update_idletasks()

    def usage(self):
        self.showText(
            Global.TITLE,
            "Usage: %s [-viewdist <viewdist>] [-fog] [-size <pixels>]" % sys.argv[0],
        )


# ________________________________________
if __name__ == "__main__":
    u = None
    try:
        master = Tk()
        u = UmbraTk(master)
        master.mainloop()
    except TclError as detail:
        print(detail)
    except Global.GameOverException:
        u.gameOver()
