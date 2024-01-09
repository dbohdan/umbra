# Umbra
# This module defines all of the user interface and control methods.
# Actual implementation of the user interface is in the subclasses, UmbraTk
# and UmbraText.
# All game logic is in Game.

from . import Entity, Game, Equip, Item, Cash, Level, Skill, Vehicle
from . import Sector, Terrain
from . import Global, util
import argparse, glob, os, shutil, string, sys, time

G_New = 0
G_Load = 1
G_Copy = 2
G_Delete = 3
G_Quit = 4
GAME_MENU = (
    "New Game",
    "Load Game",
    "Copy Game",
    "Delete Game",
    "Quit",
)
GAME_MENU_KEYS = ("n", "l", "c", "d", "q")

T_Create = 0
T_View = 1
T_Join = 2
T_Leave = 3
T_Start = 4
T_Hack = 5
T_Quit = 6
TAVERN_MENU = (
    "Create a character",
    "View a character",
    "A character joins your party",
    "A character leaves your party",
    "Start your adventure in town",
    "'Hack' adventure - start at a temple",
    "Quit",
)
TAVERN_MENU_KEYS = ("c", "v", "j", "l", "s", "h", "q")

A_Pass = 0
A_Melee = 1
A_Ranged = 2
ATTACK_MENU = (
    "Pass",
    "Melee",
    "Ranged",
)
ATTACK_MENU_KEYS = ("0", "m", "r")

M_Step_Forward = 0
M_Turn_Left = 1
M_Turn_Right = 2
M_Step_Left = 3
M_Step_Right = 4
M_Step_Back = 5
M_Turn_Back = 6
M_Map = 7
M_Get_Item = 8
M_Talk_Trigger = 9
M_Attack = 10
M_Wait = 11
M_Board = 12
M_Quit = 13
MAIN_MENU = (
    "Step Forward",
    "Turn Left",
    "Turn Right",
    "Step Left",
    "Step Right",
    "Step Back",
    "Turn Back",
    "Map",
    "Get Item",
    "Talk/ Trigger",
    "Attack",
    "Wait",
    "Board/ Debark",
    "Quit/ Save",
)
MAIN_MENU_KEYS = (
    "k",
    "h",
    "l",
    "H",
    "L",
    "J",
    "j",
    "m",
    "g",
    "t",
    "a",
    "w",
    "b",
    "q",
)


def cli():
    parser = argparse.ArgumentParser(allow_abbrev=False)

    parser.add_argument(
        "-viewdist",
        "--view-dist",
        default=8,
        metavar="<squares>",
        type=int,
        help="set the view distance in grid squares (default: %(default)d)",
    )

    parser.add_argument(
        "-hack",
        "--hack",
        action="store_true",
        help="start just outside a temple with some minimal equipment",
    )

    parser.add_argument(
        "-timing", "--timing", action="store_true", help="enable timing debug mode"
    )

    parser.add_argument(
        "-nolight",
        "--no-light",
        action="store_false",
        dest="light",
        help="disable lighting",
    )

    parser.add_argument(
        "-nolightlos",
        "--no-light-los",
        action="store_false",
        dest="light_los",
        help="disable line-of-sight calculation for lighting",
    )

    parser.add_argument(
        "-visible",
        "--visible",
        action="store_true",
        help="enable visibility calculation",
    )

    parser.add_argument(
        "-nodebug",
        "--no-debug",
        action="store_false",
        default=Global.DEBUG,
        dest="debug",
        help="disable debug mode",
    )

    return parser


class Umbra:
    # game=Game
    def __init__(self, args):
        Global.umbra = self

        Global.setViewDist(args.view_dist)
        Global.HACK = args.hack
        Global.TIMING = args.timing
        Global.LIGHT = args.light
        Global.LIGHT_LOS = args.light_los
        Global.VISICALC = args.visible
        Global.DEBUG = args.debug

        self.game = None
        self.gameMenu()
        self.turn(Global.REDRAW)
        self.startMainMenu()

    # ________________________________________
    # Override these!
    def alert(self, title, msg, type=Global.ALERT_WARNING):
        """Displays an error message"""
        pass

    def busy(self, state):
        """If state, tells the player to wait; otherwise, clears the busy
        state."""
        pass

    def gameOver(self):
        """Announces that the game is over, then quits."""
        pass

    def gameView(self, game):
        """Displays the party's current location and stats."""
        pass

    def input(self, title, prompt):
        """Return the answer to prompt, or None if the user cancelled."""
        pass

    def menu(self, title, prompts, keys=None, banner=None):
        """Return the index of the chosen prompt item.  A 'banner' may be
        displayed above the menu, and 'keys' gives a list of hotkeys that map
        to each prompt item."""
        pass

    def quit(self, err=0):
        sys.exit(err)

    def showBlood(self, amount):
        """Shows 'amount' blood-splatters on the screen when a character is
        wounded."""
        pass

    def showCharacter(self, ch, main=1):
        """Shows a given character's stats and inventory, then prompts for any
        inventory actions, and returns the index from VIEW_MENU."""
        pass

    def showGunshot(self, x0, y0, x1, y1, fill="#cccccc", player=1):
        """Shows a bullet's path."""
        pass

    def showMap(self, map):
        """Shows the grids in the given map."""
        pass

    def showPlayerMap(self):
        """Shows the player's explored map."""
        pass

    def showStatus(self, text):
        """Displays a short bit of text onscreen"""
        pass

    def showText(self, title, text):
        """Displays a long chunk of text."""
        pass

    def startMainMenu(self):
        """Begins processing the main menu, which makes a callback to
        mainMenu() with the index of the chosen command from MAIN_MENU every
        time a command is chosen."""
        pass

    # ________________________________________
    def gameMenu(self):
        while 1:
            opt = self.menu(Global.TITLE, GAME_MENU, GAME_MENU_KEYS)
            if opt == G_New:
                if self.gameNew():
                    return
            elif opt == G_Load:
                if self.gameLoad():
                    return
            elif opt == G_Copy:
                self.gameCopy()
            elif opt == G_Delete:
                self.gameDelete()
            elif opt == G_Quit:
                self.quit()
            else:
                assert 0, "Unknown menu option %d" % opt

    def gameCopy(self):
        allfiles = glob.glob(os.path.join(Global.SAVEDIR, "*"))
        allfiles.sort()
        dirs = [
            "Cancel",
        ]
        for file in allfiles:
            if os.path.isdir(file):
                dirs.append(os.path.split(file)[1])
        i = self.menu("Copy Game", dirs)
        if i == 0:
            return 0
        dirname = dirs[i]
        newname = self.input("New Name", "Name")
        if not newname:
            return 0
        newname = util.purifyName(newname)
        newpath = os.path.join(Global.SAVEDIR, newname)
        if os.path.exists(newpath):
            self.alert("Cannot Copy", "You already have a game named %s!" % newname)
            return
        shutil.copytree(os.path.join(Global.SAVEDIR, dirname), newpath)

    def gameDelete(self):
        allfiles = glob.glob(os.path.join(Global.SAVEDIR, "*"))
        allfiles.sort()
        dirs = [
            "Cancel",
        ]
        for file in allfiles:
            if os.path.isdir(file):
                dirs.append(os.path.split(file)[1])
        i = self.menu("Delete Game", dirs)
        if i == 0:
            return 0
        dirname = dirs[i]
        if not self.alert(
            "Delete Game",
            "Are you sure you want to delete %s?" % dirname,
            type=Global.ALERT_YESNO,
        ):
            return
        for file in glob.glob(os.path.join(Global.SAVEDIR, dirname, "*")):
            os.remove(file)
        os.rmdir(os.path.join(Global.SAVEDIR, dirname))

    def gameLoad(self):
        allfiles = glob.glob(os.path.join(Global.SAVEDIR, "*"))
        allfiles.sort()
        dirs = [
            "Cancel",
        ]
        for file in allfiles:
            if os.path.isdir(file):
                dirs.append(os.path.split(file)[1])
        i = self.menu("Load Game", dirs)
        if i == 0:
            return 0
        else:
            self.game = Game.loadGame(dirs[i])
            if self.game:
                return 1
            else:
                return 0

    def gameNew(self):
        while 1:
            name = self.input("Name for New Game", "Name")
            if not name:
                return 0
            name = util.purifyName(name)
            if os.path.exists(os.path.join(Global.SAVEDIR, name)):
                self.alert("New Game", "You already have a saved game named %s" % name)
                continue
            self.game = Game.Game(name)
            self.game.generate()
            if Global.TESTCHAR:
                jack = self.game.createChar(
                    "Jack",
                    Global.GEND_Female,
                    Global.P_Jack,
                    [
                        10,
                        10,
                        10,
                        20,
                    ],
                )
                jack.cash = 10000
                killer = self.game.createChar(
                    "Killer",
                    Global.GEND_Male,
                    Global.P_Killer,
                    [
                        20,
                        15,
                        10,
                        10,
                    ],
                )
                sneak = self.game.createChar(
                    "Sneak",
                    Global.GEND_Female,
                    Global.P_Sneak,
                    [
                        15,
                        20,
                        10,
                        10,
                    ],
                )
                techie = self.game.createChar(
                    "Techie",
                    Global.GEND_Male,
                    Global.P_Techie,
                    [
                        10,
                        15,
                        20,
                        10,
                    ],
                )
                arcanist = self.game.createChar(
                    "Arcanist",
                    Global.GEND_Female,
                    Global.P_Arcanist,
                    [
                        10,
                        10,
                        20,
                        15,
                    ],
                )
                for who in self.game.party:
                    who.skillPoints = 1
                self.game.enterWorld()
            else:
                self.tavernMenu()
            return 1

    def mainMenu(self, cmd):
        """Executes a command from the main menu and gets a single action, then
        calls turn()."""
        try:
            if cmd < 0:
                i = (-cmd) - 1
                if i >= len(self.game.party):
                    rc = Global.NOREDRAW
                else:
                    who = self.game.party[i]
                    rc = self.mainViewChar(who)
            elif cmd == M_Step_Forward:
                rc = self.mainMove(self.game.dx(), self.game.dy())
            elif cmd == M_Turn_Left:
                rc = self.game.turnLeft()
            elif cmd == M_Turn_Right:
                rc = self.game.turnRight()
            elif cmd == M_Step_Left:
                rc = self.mainMove(self.game.dx(Global.Left), self.game.dy(Global.Left))
            elif cmd == M_Step_Right:
                rc = self.mainMove(
                    self.game.dx(Global.Right), self.game.dy(Global.Right)
                )
            elif cmd == M_Step_Back:
                rc = self.mainMove(self.game.dx(Global.Back), self.game.dy(Global.Back))
            elif cmd == M_Turn_Back:
                rc = self.game.turnBack()
            elif cmd == M_Map:
                rc = self.mainMap()
            elif cmd == M_Get_Item:
                rc = self.mainGet()
            elif cmd == M_Talk_Trigger:
                rc = self.mainViewTrigger(self.game.getLeader())
            elif cmd == M_Attack:
                rc = self.mainAttack()
            elif cmd == M_Wait:
                rc = Global.NEXTTURN
            elif cmd == M_Board:
                rc = self.mainBoard()
            elif cmd == M_Quit:
                rc = self.mainQuit()
            else:
                assert 0, "Unknown command %d" % opt
            self.turn(rc)
        except Global.GameOverException:
            self.gameOver()

    def mainAttack(self):
        rc = Global.NOREDRAW
        for who in self.game.party:
            while 1:
                mymenu = ATTACK_MENU
                mykeys = ATTACK_MENU_KEYS
                if not who.equip[Equip.POS_Ranged]:
                    mymenu = ATTACK_MENU[:A_Ranged]
                    mykeys = ATTACK_MENU_KEYS[:A_Ranged]
                opt = self.menu("%s's attack" % who.name, mymenu, keys=mykeys)
                if opt == A_Pass:
                    break
                elif opt == A_Melee:
                    if self.mainAttackMelee(who):
                        rc = Global.NEXTTURN
                        break
                elif opt == A_Ranged:
                    if self.mainAttackRanged(who):
                        rc = Global.NEXTTURN
                        break
                else:
                    assert 0, "Unknown attack command %d" % opt
        return rc

    def mainAttackMelee(self, who):
        """Return 1 if the attack took a turn, even if it failed."""
        target = self.selectTarget(
            who, Global.TARGET_Melee, "%s: Select target" % who.name, ahead=1
        )
        if target:
            who.meleeAttack(target)
            return 1
        return 0

    def mainAttackRanged(self, who):
        """Return 1 if the attack took a turn, even if it failed."""
        target = self.selectTarget(
            who, Global.TARGET_Ranged, "%s: Select target" % who.name
        )
        if not target:
            return 0
        gun = who.equip[Equip.POS_Ranged]
        if gun.ammo < gun.ammoUse:
            who.message("<click> <click>  You're out of ammo!")
            return 1
        gun.ammo -= gun.ammoUse
        who.rangedAttack(target)
        return 1

    def mainBoard(self):
        vehicle = self.game.vehicle
        if vehicle != None:
            self.showStatus("You debark the %s." % vehicle.name)
            vehicle.boarded = 0
            self.game.vehicle = None
            return Global.REDRAW
        who = self.game.getLeader()
        levelnum = who.levelnum()
        level = self.game.getLevel()
        x = who.x()
        y = who.y()
        stuff = level.getStuff(x, y)
        for item in stuff:
            if isinstance(item, Vehicle.Vehicle):
                vehicle = item
                break
        else:
            self.showStatus("You see no vehicle here.")
            return Global.NOREDRAW
        vehicle.boarded = 1
        self.game.vehicle = vehicle
        self.showStatus("You board the %s." % vehicle.name)
        return Global.REDRAW

    def mainGet(self):
        who = self.selectParty("Who will get something?")
        if not who:
            return Global.NOREDRAW
        return self.mainViewGetItem(who)

    def mainMap(self):
        levelnum = self.game.getLevelnum()
        while 1:
            if levelnum == -2:
                break
            elif levelnum == -1:
                playerMap = self.game.playerMap
                mapsize = Global.WORLDSIZE
                x = self.game.sector.wx
                y = self.game.sector.wy
                cellchars = 1
            else:
                playerMap = self.game.sector.playerMap[levelnum]
                mapsize = Global.LEVELSIZE
                leader = self.game.getLeader()
                x = leader.x()
                y = leader.y()
                cellchars = 2
            levelnum = self.mainMapViewer(playerMap, mapsize, x, y, cellchars, levelnum)
        return Global.NOREDRAW

    def mainMapViewer(self, playerMap, mapsize, xx, yy, cellchars, levelnum=-1):
        isWorld = levelnum < 0
        VIEW = 40 // (cellchars + 1)
        VIEW2 = VIEW // 2
        x0 = util.minmax(xx - VIEW2, 0, mapsize - VIEW)
        y0 = util.minmax(yy - VIEW2, 0, mapsize - VIEW)

        def addPrompt(d, prompts, keys):
            prompts.append(Global.DIR_NAMES[d])
            keys.append(Global.MOVE_CHARS[d])

        while 1:
            x1 = min(mapsize, x0 + VIEW)
            y1 = min(mapsize, y0 + VIEW)
            if isWorld:
                maptype = "World Map"
                prompts = [
                    "Cancel",
                    "Zoom in to Sector Map",
                    "Map Key",
                ]
                keys = ["0", "z", "m"]
            else:
                maptype = "Sector Map Level %d" % levelnum
                prompts = [
                    "Cancel",
                    "Zoom out to World Map",
                    "Map Key",
                ]
                keys = ["0", "z", "m"]
                if levelnum > 0:
                    prompts.append("Previous level")
                    keys.append("p")
                if levelnum < self.game.sector.getNLevels() - 1:
                    prompts.append("Next level")
                    keys.append("n")
            text = "%s: %d,%d-%d,%d\n" % (maptype, x0, y0, x1 - 1, y1 - 1)
            for y in range(y0, y1):
                line = " "
                for x in range(x0, x1):
                    c0 = (y * mapsize + x) * cellchars
                    c1 = c0 + cellchars
                    if y == yy and x == xx:
                        line = "%s[%s]" % (line[:-1], playerMap[c0:c1])
                    else:
                        line = "%s%s " % (line, playerMap[c0:c1])
                text = "%s%s\n" % (text, line)
            if y0 > 0:
                addPrompt(Global.North, prompts, keys)
            if x1 < mapsize:
                addPrompt(Global.East, prompts, keys)
            if y1 < mapsize:
                addPrompt(Global.South, prompts, keys)
            if x0 > 0:
                addPrompt(Global.West, prompts, keys)
            opt = self.menu(maptype, prompts, keys, banner=text)
            if opt == 0:
                return -2
            elif opt == 1:
                if isWorld:
                    return 0
                else:
                    return -1
            elif opt == 2:
                if isWorld:
                    text = Global.SECTOR_KEY
                else:
                    text = Terrain.TERRAIN_KEY
                self.showText("Map Key", text.strip())
                continue
            elif keys[opt] == "p":
                return levelnum - 1
            elif keys[opt] == "n":
                return levelnum + 1
            else:  # continue looping
                d = Global.MOVE_CHARS.index(keys[opt])
                x0 = util.minmax(x0 + Global.DX[d] * VIEW2, 0, mapsize - VIEW)
                y0 = util.minmax(y0 + Global.DY[d] * VIEW2, 0, mapsize - VIEW)

    def mainMove(self, dx, dy):
        rc = self.game.moveBy(dx, dy)
        if rc:
            self.showStatus(rc)
            return Global.NOREDRAW
        return Global.NEXTTURN

    def mainQuit(self):
        rc = self.alert(
            "Quit", "Are you sure you want to quit?", type=Global.ALERT_YESNO
        )
        if rc and self.game.saveGame():
            self.quit()
        return Global.NOREDRAW

    def mainViewChar(self, who):
        while 1:
            opt = self.showCharacter(who)
            if opt < 0 or opt == Global.V_OK:
                return Global.NOREDRAW
            elif opt == Global.V_Examine_Item_or_Equip:
                rc = self.mainViewExamine(who)
            elif opt == Global.V_Use_Item:
                rc = self.mainViewUseItem(who)
            elif opt == Global.V_Remove_Equip:
                rc = self.mainViewRemoveEquip(who)
            elif opt == Global.V_Move_Item:
                rc = self.mainViewMoveItem(who)
            elif opt == Global.V_Hand_Item:
                rc = self.mainViewHandItem(who)
            elif opt == Global.V_Drop_Item:
                rc = self.mainViewDropItem(who)
            elif opt == Global.V_Get_Item:
                rc = self.mainViewGetItem(who)
            elif opt == Global.V_Use_Skill:
                rc = self.mainViewUseSkill(who)
            elif opt == Global.V_Talk_Trigger:
                rc = self.mainViewTrigger(who)
            elif opt == Global.V_Attack:
                rc = self.mainViewAttack(who)
            else:
                assert 0, "Unknown menu option %d" % opt
            self.turn(rc)

    def mainViewDropItem(self, who):
        item = self.selectItem(who)
        if not item:
            return Global.NOREDRAW
        level = self.game.getLevel()
        x = who.x()
        y = who.y()
        if util.isInt(item):
            who.cash -= item
            stuff = level.getStuff(x, y)
            for st in stuff:
                if isinstance(st, Cash.Cash):
                    st.setCost(st.cost() + item)
                    who.message("You drop $%d cash" % item)
                    return Global.NOREDRAW
            else:
                item = self.game.makeCash(item)
        else:
            who.removeItem(item)
        level.addStuff(x, y, item)
        who.message("You drop %s" % item.name)
        return Global.REDRAW

    def mainViewExamine(self, who):
        item = self.selectItemOrEquip(who)
        if not item:
            return Global.NOREDRAW
        if util.isInt(item):
            self.showText("Examine cash", "%d silver dollars" % item)
        else:
            self.showText("Examine %s" % item.name, str(item))
        return Global.NOREDRAW

    def mainViewGetItem(self, who):
        levelnum = who.levelnum()
        level = self.game.getLevel()
        x = who.x()
        y = who.y()
        locContents = level.getStuff(x, y)
        # collect a menu and refs of the Items
        options = [
            "Cancel",
            "All",
        ]
        items = []
        for item in locContents:
            if isinstance(item, Item.Item):
                items.append(item)
                options.append(item.name)
        n = len(items)
        if n == 0:
            who.message("Get what?  You see nothing here that you can take.")
            return Global.NOREDRAW
        opt = self.menu("Get which item?", options)
        if opt == 0:
            return Global.NOREDRAW
        elif opt == 1:
            for item in items:
                self.__getItem(who, level, x, y, item)
        else:
            self.__getItem(who, level, x, y, items[opt - 2])
        return Global.REDRAW

    def __getItem(self, who, level, x, y, item):
        if isinstance(item, Cash.Cash):
            level.removeStuff(x, y, item)
            who.cash += item.cost()
            who.message("You get %s" % item.name)
            return Global.REDRAW
        if who.addItem(item):
            level.removeStuff(x, y, item)
            who.message("You get %s" % item.name)

    def mainViewHandItem(self, who):
        item = self.selectItem(who)
        if not item:
            return Global.NOREDRAW
        if util.isInt(item):
            item = self.game.makeCash(item)
        target = self.selectTarget(who, Global.TARGET_Melee, "Hand to whom?")
        if not target:
            return Global.NOREDRAW
        rc = target.handedItem(who, item)
        if rc:
            if isinstance(item, Cash.Cash):
                who.cash -= item.cost()
            else:
                who.removeItem(item)
        return Global.NOREDRAW

    def mainViewMoveItem(self, who):
        item = self.selectItem(who)
        if not item:
            return Global.NOREDRAW
        who2 = self.selectParty("Move item to which character?")
        if not who2:
            return Global.NOREDRAW
        if who2.countItems() >= Entity.MAXITEMS:
            who2.message("You cannot carry any more items!")
            return Global.NOREDRAW
        if util.isInt(item):
            who.cash -= item
            who2.cash += item
            itemname = "$%d" % item
        else:
            who.removeItem(item)
            who2.addItem(item)
            itemname = item.name
        who.message("You move %s to %s" % (itemname, who2.name))
        return Global.NOREDRAW

    def mainViewRemoveEquip(self, who):
        item = self.selectEquip(who)
        if not item:
            return Global.NOREDRAW
        who.message("You remove %s" % item.name)
        if not who.unreadyEquip(item):
            return Global.NOREDRAW
        return Global.NOREDRAW

    def mainViewTrigger(self, who):
        level = self.game.getLevel()
        facing = who.facing
        x = who.x() + Global.DX[facing]
        y = who.y() + Global.DY[facing]
        locContents = level.getStuff(x, y)
        count = 0
        if locContents != None:
            for item in locContents:
                count += item.trigger(who)
        if count == 0:
            who.message("Nothing happens.")
            return Global.NOREDRAW
        return Global.NEXTTURN

    def mainViewUseItem(self, who):
        item = self.selectItem(who)
        if not item:
            return Global.NOREDRAW
        if util.isInt(item):
            who.message("Cash only has the usual kind of special power.")
            return Global.NOREDRAW
        who.message("uses %s" % item.name)
        if not who.useItem(item):
            return Global.NOREDRAW
        return Global.NOREDRAW

    def mainViewUseSkill(self, who):
        options = [
            "Cancel",
        ]
        for skill in who.listSkills():
            if Skill.getSkill(skill).use:
                options.append(skill)
        if len(options) == 1:
            who.message("You have no usable skills.")
            return Global.NOREDRAW
        opt = self.menu("Which skill?", options)
        if opt == 0:
            return None
        skill = options[opt]
        return Skill.getSkill(skill).use(who)

    def redraw(self):
        self.game.redraw()
        self.showMap(self.game.view, self.game.getFacing())

    def selectCashAmount(self, who):
        if who.cash <= 0:
            self.alert("Bankrupt!", "You have no cash!")
            return None
        amount = self.input("Cash", "Amount (0-%d)? $" % who.cash)
        if amount == None:
            return None
        try:
            amount = int(amount)
        except ValueError:
            who.message("Cash amounts must be numbers!")
            return None
        if amount > who.cash:
            self.alert("Insufficient Cash", "You only have $%d!" % who.cash)
            return None
        elif amount < 0:
            who.message("Cash amounts must be positive numbers!")
            return None
        return amount

    def selectEquip(self, who):
        # collect a menu and refs of the equipment of 'who'
        options, items = who.listEquip()
        items.insert(0, None)
        n = len(items)
        if n == 0:
            who.message("You have no equipment.")
            return None
        opt = self.menu("Which equipment?", options)
        if opt == 0:
            return None
        return items[opt]

    def selectItem(self, who):
        # collect a menu and refs of the Items in the pack of 'who'
        options = [
            "Cancel",
            "$%d Cash" % who.cash,
        ]
        items = [
            None,
            None,
        ]
        for item in who.listItems():
            options.append(item.name)
            items.append(item)
        opt = self.menu("Which item?", options)
        if opt == 0:
            return None
        if opt == 1:
            return self.selectCashAmount(who)
        return items[opt]

    def selectItemOrEquip(self, who):
        options, items = who.listEquip()
        options.insert(1, "$%d Cash" % who.cash)
        items.insert(0, None)
        items.insert(1, None)
        for item in who.listItems():
            options.append(item.name)
            items.append(item)
        opt = self.menu("Which item or equipment?", options)
        if opt == 0:
            return None
        if opt == 1:
            return self.selectCashAmount(who)
        return items[opt]

    def selectParty(self, title):
        names = [
            "Cancel",
        ] + self.game.listPartyNames()
        keys = [str(i) for i in range(len(names))]
        which = self.menu(title, names, keys)
        if which == 0:
            return None
        return self.game.party[which - 1]

    def selectTarget(self, who, mode, title, ahead=0, rng=0):
        view = self.game.view
        facing = who.facing
        targets = []
        x = Global.VIEWDIST
        y = Global.VIEWDIST
        if mode == Global.TARGET_Ahead:
            self.__addAheadTargets(targets, view, x, y, facing)
        elif mode == Global.TARGET_Melee:
            self.__addMeleeTargets(targets, view, x, y, facing)
        elif mode == Global.TARGET_Ranged:
            if not rng:
                gun = who.equip[Equip.POS_Ranged]
                if not gun:
                    who.message("You have no ranged weapon!")
                    return None
                rng = gun.range
            self.__addTargetsInRange(who, targets, view, facing, rng)
        else:
            assert 0, "Unknown selectTarget mode '%s'" % mode
            #        if not targets:
            #            who.message("There is nothing in range.")
            #            return None
        # choose target from menu
        options = [
            "Cancel",
        ]
        keys = [
            "0",
        ]
        if ahead:
            options.append("Ahead")
            keys.append("1")
        nextkey = "a"
        for item in targets:
            options.append(item.name)
            keys.append(nextkey)
            nextkey = chr(ord(nextkey) + 1)
        opt = self.menu(title, options, keys)
        if opt == 0:
            return None
        if ahead and opt == 1:
            return "Ahead"
        return targets[opt - (ahead + 1)]

    def __addAheadTargets(self, targets, view, x, y, facing):
        # here
        self.__addTargets(targets, view[x][y])
        # ahead
        x0 = x + Global.DX[facing]
        y0 = y + Global.DY[facing]
        self.__addTargets(targets, view[x0][y0])

    def __addMeleeTargets(self, targets, view, x, y, facing):
        left = Global.turnLeft(facing)
        right = Global.turnRight(facing)
        # here,left,right
        self.__addTargets(targets, view[x][y])
        x1 = x + Global.DX[left]
        y1 = y + Global.DY[left]
        self.__addTargets(targets, view[x1][y1])
        x1 = x + Global.DX[right]
        y1 = y + Global.DY[right]
        self.__addTargets(targets, view[x1][y1])
        # ahead,left,right
        x0 = x + Global.DX[facing]
        y0 = y + Global.DY[facing]
        self.__addTargets(targets, view[x0][y0])
        x1 = x0 + Global.DX[left]
        y1 = y0 + Global.DY[left]
        self.__addTargets(targets, view[x1][y1])
        x1 = x0 + Global.DX[right]
        y1 = y0 + Global.DY[right]
        self.__addTargets(targets, view[x1][y1])

    def __addTargetsInRange(self, who, targets, view, facing, rng):
        level = self.game.getLevel()
        VIEWDIST = Global.VIEWDIST
        DX = Global.DX
        DY = Global.DY
        dist = min(VIEWDIST, rng)
        for lr in range(-dist, dist + 1):
            for fb in range(0, dist + 1):
                x = VIEWDIST + fb * DX[facing] - lr * DY[facing]
                y = VIEWDIST + lr * DX[facing] + fb * DY[facing]
                here = []
                self.__addTargets(here, view[x][y])
                for target in here:
                    rc = level.clearLOS(who.x(), who.y(), target.x(), target.y(), rng)
                    if rc == 1:
                        targets.append(target)

    def __addTargets(self, targets, here):
        if not here[1]:
            return
        for what in here[1]:
            if isinstance(what, Entity.Entity):
                if not what.player and not what.isDead() and not what.isBurrowing():
                    targets.append(what)

    def selectTavern(self, title):
        names = [
            "Cancel",
        ] + self.game.listTavernNames()
        keys = [str(i) for i in range(len(names))]
        which = self.menu(title, names, keys)
        if which == 0:
            return None
        return self.game.tavern[which - 1]

    def tavernMenu(self):
        while 1:
            names = ", ".join(self.game.listPartyNames())
            banner = "Characters in the party:\n%s\n" % names
            names = ", ".join(self.game.listTavernNames())
            banner = "%sCharacters in the tavern:\n%s\n" % (banner, names)
            opt = self.menu("Tavern", TAVERN_MENU, TAVERN_MENU_KEYS, banner=banner)
            if opt == T_Create:
                self.tavernCreateChar()
            elif opt == T_View:
                self.tavernViewChar()
            elif opt == T_Join:
                self.tavernJoinParty()
            elif opt == T_Leave:
                self.tavernLeaveParty()
            elif opt in (T_Start, T_Hack):
                if not self.game.party:
                    self.alert(
                        "Enter World",
                        "You need at least one character in your party!",
                    )
                if opt == T_Hack:
                    Global.HACK = True
                self.game.enterWorld()
                return
            elif opt == T_Quit:
                self.quit()
            else:
                assert 0, "Unknown menu option %d" % opt
        # end while

    def tavernCreateChar(self):
        name = self.input("Create Character", "Name")
        if not name:
            return
        options = [
            "Cancel",
        ] + list(Global.PROF_NAMES)
        keys = [
            "0",
        ] + list(Global.PROF_KEYS)
        prof = self.menu("Select Profession", options, keys=keys)
        if prof == 0:
            return
        prof -= 1

        options = [
            "Cancel",
        ] + list(Global.GENDER_NAMES)
        keys = [
            "0",
        ] + list(Global.GENDER_KEYS)
        gender = self.menu("Select Gender", options, keys=keys)
        if gender == 0:
            return
        gender -= 1

        while 1:
            banner = "Name: %s\nGender: %s\nProfession: %s\n" % (
                name,
                Global.GENDER_NAMES[gender],
                Global.PROF_NAMES[prof],
            )
            stat = util.makeArray(8)
            for i in range(Global.NPRIMES):
                stat[i] = util.d(2, 10)
                banner = "%s%s: %d\n" % (banner, Global.STAT_NAMES[i], stat[i])
            i = self.menu(
                "Determine Stats",
                (
                    "Try Again",
                    "Accept",
                    "Cancel",
                ),
                keys=(
                    "t",
                    "a",
                    "c",
                ),
                banner=banner,
            )
            if i == 0:
                continue
            elif i == 1:
                break
            else:
                return
        self.game.createChar(name, gender, prof, stat)

    def tavernJoinParty(self):
        who = self.selectTavern("Which character joins the party?")
        if not who:
            return
        self.game.joinParty(who)

    def tavernLeaveParty(self):
        who = self.selectParty("Which character leaves the party?")
        if not who:
            return
        self.game.leaveParty(who)

    def tavernViewChar(self):
        who = self.selectParty("View which character?")
        if not who:
            return
        self.showCharacter(who, main=0)

    def turn(self, nextstate):
        if nextstate == Global.NOREDRAW:
            return
        elif nextstate == Global.REDRAW:
            self.redraw()
            return
        self.game.nextTurn()
        self.redraw()
