import Entity, Level, Terrain, Umbra
import Global, util
import string, types

class UmbraText(Umbra.Umbra):
    def __init__(self):
        print Global.TITLE
        print Global.COPYRIGHT
        Umbra.Umbra.__init__(self)
        Global.VISICALC=1

    def alert(self, title, msg, type=Global.ALERT_WARNING):
        print title
        print "[%s] %s " % (type, msg),
        if type==Global.ALERT_YESNO:
            yesno=raw_input()
            rc = (yesno and string.lower(yesno[0])=='y')
        else:
            rc=0
            print
        print
        return rc

    def busy(self, state):
        if state:
            print "Please wait..."
        else:
            print "...okay!"

    def gameOver(self):
        print """
.-----------.
|.-----------.
||           |
|| GAME OVER |
||           |
||           |
||           |
||           |
\|           |
 \___________/"""
        self.quit()

    def input(self, title, prompt):
        print title
        return raw_input("%s? "%prompt)

    def menu(self, title, prompts, keys=None, banner=None):
        if not keys:
            a = ord('a')
            n = len(prompts)
            keys = []
            if prompts[0] == "Cancel":
                keys.append("0")
                n -= 1
            for i in xrange(n):
                keys.append( chr(a+i) )
        print title
        if banner:
            print banner
        menu=[]
        for i in xrange(len(prompts)):
            menu.append( "[%s] %s" % (keys[i], prompts[i]) )
        util.print2cols(menu)
        while 1:
            line=raw_input("> ")
            ok=0
            keyi = util.indexOf(line, keys)
            if keyi >= 0:
                return keyi
            if not ok:
                print "Please choose from the menu.\n"
        #end while

    def showBlood(self, amount):
        for hit in xrange(amount):
            print "***blood***",
        print

    def showCharacter(self, who, main=1):
        if main:
            prompts = Global.VIEW_MENU
            opt = self.menu("", prompts, Global.VIEW_MENU_KEYS, banner=str(who))
            return opt

    def showGunshot(self, x0, y0, x1, y1, fill="#cccccc", player=1):
        dx = x1-x0; dy = y1-y0
        facing = self.game.getFacing()
        if facing == Global.North:
            vx = dx; vy = -dy
        elif facing == Global.East:
            vx = dy; vy = dx
        elif facing == Global.South:
            vx = -dx; vy = dy
        else:
            vx = -dy; vy = -dx
        self.showStatus("Gunshot %d,%d" % (vx, vy))

    def showMap(self, map, facing):
        print "%s:" % Global.DIR_NAMES[facing]
        level = self.game.getLevel()
        leader = self.game.getLeader()
        x0 = leader.x(); y0 = leader.y()
        left=0
        center=Global.VIEWDIST
        right=Global.VIEWSIZE-1
        text = ""
        desc = {}
        mapdesc = {}
        if facing == Global.North:
            for y in xrange(left, center+1):
                for x in xrange(left, right+1):
                    grid = map[x][y]
                    text = self.__showGrid(text, level, x0, y0, x, y, grid, desc, mapdesc)
                text = "%s\n" % text
        elif facing == Global.East:
            for x in xrange(right, center-1, -1):
                for y in xrange(left, right+1):
                    grid = map[x][y]
                    text = self.__showGrid(text, level, x0, y0, x, y, grid, desc, mapdesc)
                text = "%s\n" % text
        elif facing == Global.South:
            for y in xrange(right, center-1, -1):
                for x in xrange(right, left-1, -1):
                    grid = map[x][y]
                    text = self.__showGrid(text, level, x0, y0, x, y, grid, desc, mapdesc)
                text = "%s\n" % text
        else: # facing == Global.West:
            for x in xrange(left, center+1):
                for y in xrange(right, left-1, -1):
                    grid = map[x][y]
                    text = self.__showGrid(text, level, x0, y0, x, y, grid, desc, mapdesc)
                text = "%s\n" % text
        print text
        keys = []
        for key in util.sort(desc.keys()):
            keys.append( "%s=%s" % (key, desc[key]) )
        for key in util.sort(mapdesc.keys()):
            keys.append( "%s=%s" % (key, mapdesc[key]) )
        util.print2cols(keys)

    def __showGrid(self, text, level, x0, y0, x, y, grid, desc, mapdesc):
        center = (x == Global.VIEWDIST and y == Global.VIEWDIST)
        if grid[0] == None or not grid[3]:
            here = "    "
        elif grid[2] <= 0 and not center:
            here = "    "
        else:
            mapdesc[grid[0].char] = grid[0].name

            if grid[1] == None:
                key = ' '
            else:
                if center: key = '@'
                else: key = chr(ord('A')+len(desc))
                value = ""
                for th in grid[1]:
                    name = th.name.replace('\n', ' ')
                    value = "%s%s%s" % (value, util.test(len(value)==0,"","; "),
                            name )
                desc[key] = value

            light = grid[2]
            if light <= 0: light = '0'
            elif light >= 10: light = ' '

            here ="%1s%2s%1s" % (key, grid[0], light)
        return "%s %s" % (text, here)

    def showStatus(self, text):
        print text

    def showText(self,title,text):
        print "%s:\n%s"%(title,text)

    def startMainMenu(self):
        while 1:
            party=self.game.listPartyNames()
            prompts=list(Umbra.MAIN_MENU) + party
            keys=list(Umbra.MAIN_MENU_KEYS)
            for i in xrange(len(party)):
                keys.append( str(i+1) )
            keys.append('?')
            prompts.append("Redraw map")
            cmd = self.menu(Global.TITLE, prompts, keys)
            if keys[cmd] == '?':
                self.redraw()
                continue
            if cmd >= len(Umbra.MAIN_MENU):
                cmd = -int(keys[cmd])
            self.mainMenu(cmd)

if __name__ == "__main__":
    try:
        u = UmbraText()
    except Global.GameOverException:
        u.gameOver()

