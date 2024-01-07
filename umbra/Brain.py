from . import Item, Equip
from . import Bestiary
from . import Global, util
import math, random
import time

NDIRS = Global.NDIRS
DX = Global.DX
DY = Global.DY

#results
RES_Nothing=0
RES_Move=1
RES_Melee=2
RES_Ranged=3
RES_Get=4

def brainAutopilot(self, turn, level):
    if Global.BRAIN_DEBUG:
        print("%s autopilot %d, %s = %c" % (self.name, self.autopilotIndex,
                self.autopilot, self.autopilot[self.autopilotIndex]))
    friends, foes, victims = __getFriendsAndFoes(self, level)
    if friends:
        __gossip(self, level, friends)
    if foes and self.taskStat(Global.Speed)>=0 and \
            __tryRanged(self, turn, level, foes):
        return RES_Ranged
    if victims:
        self.meleeAttack(random.choice(victims))
        return RES_Melee
    if __tryGetStuff(self, turn, level):
        return RES_Get
    # get the next move
    step = self.autopilot[self.autopilotIndex]
    # convert that into a movedir and see if it's legal
    if step == "n": movedir = Global.North
    elif step == "e": movedir = Global.East
    elif step == "s": movedir = Global.South
    elif step == "w": movedir = Global.West
    elif step == ".":
        self.autopilotIndex = (self.autopilotIndex + 1) % len(self.autopilot)
        return RES_Nothing
    okaydirs = __getOkayDirs(self, level)
    if not movedir in okaydirs: return RES_Nothing
    self.autopilotIndex = (self.autopilotIndex + 1) % len(self.autopilot)
    return __doMove(self, level, movedir)

def brainCoward(self, turn, level):
    if Global.BRAIN_DEBUG: print("%s fleeing" % self.name)
    friends, foes, victims = __getFriendsAndFoes(self, level)
    if friends:
        __gossip(self, level, friends)
    if foes and self.taskStat(Global.Speed)>=0 and \
            __tryRanged(self, turn, level, foes):
        return RES_Ranged
    if victims:
        self.meleeAttack(random.choice(victims))
        return RES_Melee

    if not foes:
        if __tryGetStuff(self, turn, level):
            return RES_Get
        return __moveRandom(self, level)

    # Movement requires a speed roll
    if self.taskStat(Global.Speed) >= 0:
        okaydirs = __getOkayDirs(self, level)
        if okaydirs:
            # try to move away from the nearest target
            nearestdirs = __getFoeDirs(self, foes)
            nearestdirs.reverse()
            if Global.BRAIN_DEBUG: print("    nearest=%s, okay=%s" % (nearestdirs, okaydirs))
            movedir = __getOkayMoveDir(self, nearestdirs, okaydirs)
            return __doMove(self, level, movedir)

    if __tryGetStuff(self, turn, level):
        return RES_Get
    return RES_Nothing

def brainHunter(self, turn, level):
    if Global.BRAIN_DEBUG: print("%s hunting" % self.name)
    friends, foes, victims = __getFriendsAndFoes(self, level)
    if friends:
        __gossip(self, level, friends)
    if foes and self.taskStat(Global.Speed)>=0 and \
            __tryRanged(self, turn, level, foes):
        return RES_Ranged
    if victims:
        self.meleeAttack(random.choice(victims))
        return RES_Melee

    if not foes:
        if __tryGetStuff(self, turn, level):
            return RES_Get
        return __moveRandom(self, level)

    # Movement requires a speed roll
    if self.taskStat(Global.Speed) >= 0:
        okaydirs = __getOkayDirs(self, level)
        if okaydirs:
            # try to move toward the nearest target
            nearestdirs = __getFoeDirs(self, foes)
            if Global.BRAIN_DEBUG: print("    nearest=%s, okay=%s" % (nearestdirs, okaydirs))
            movedir = __getOkayMoveDir(self, nearestdirs, okaydirs)
            return __doMove(self, level, movedir)

    if __tryGetStuff(self, turn, level):
        return RES_Get
    return RES_Nothing

def brainRandom(self, turn, level):
    if Global.BRAIN_DEBUG: print("%s wandering" % self.name)
    friends, foes, victims = __getFriendsAndFoes(self, level)
    if friends:
        __gossip(self, level, friends)
    if foes and self.taskStat(Global.Speed)>=0 and \
            __tryRanged(self, turn, level, foes):
        return RES_Ranged
    if victims:
        self.meleeAttack(random.choice(victims))
        return RES_Melee
    if __tryGetStuff(self, turn, level):
        return RES_Get
    return __moveRandom(self, level)

def brainStill(self, turn, level):
    friends, foes, victims = __getFriendsAndFoes(self, level)
    if friends:
        __gossip(self, level, friends)
    if foes and __tryRanged(self, turn, level, foes):
        return RES_Ranged
    if victims:
        self.meleeAttack(random.choice(victims))
        return RES_Melee
    if __tryGetStuff(self, turn, level):
        return RES_Get
    return RES_Nothing

def __adjacent(self, who):
    return abs(self.x()-who.x()) <= 1 and abs(self.y()-who.y()) <= 1

def __doMove(self, level, movedir):
    self.facing = movedir
    x0 = self.x(); y0 = self.y()
    x1 = x0 + DX[movedir]
    y1 = y0 + DY[movedir]
    if Global.BRAIN_DEBUG:
        print("    %s from %d,%d to %d,%d" % (Global.DIR_NAMES[self.facing],
                x0, y0, x1, y1))
    self.move(level, x0, y0, level, x1, y1)
    return RES_Move

def __getFoeDirs(self, foes):
    x0 = self.x()
    y0 = self.y()
    dirdist = []
    for d in range(Global.NDIRS):
        dirdist.append( (1024, d, None) )
    for target in foes:
        xdist = target.x()-x0
        ydist = target.y()-y0
        h = math.hypot(xdist, ydist)
        axdist = abs(xdist); aydist = abs(ydist)
        # no dirs to add?
        if axdist == 0 and aydist == 0: continue
        # only one dir to add?
        if axdist == 0:
            if ydist < 0: d = Global.North
            else: d = Global.South
            if h < dirdist[d][0]:
                dirdist[d] = (int(h), d, target.name)
        elif ydist == 0:
            if xdist < 0: d = Global.West
            else: d = Global.East
            if h < dirdist[d][0]:
                dirdist[d] = (int(h), d, target.name)
        else:
            # add potential dirs
            if ydist < 0: d = Global.North
            else: d = Global.South
            if h < dirdist[d][0]:
                dirdist[d] = (int(h), d, target.name)

            if xdist < 0: d = Global.West
            else: d = Global.East
            if h < dirdist[d][0]:
                dirdist[d] = (int(h), d, target.name)
    dirdist.sort()
    return dirdist

def __getFriendsAndFoes(self, level):
    x0 = self.x()
    y0 = self.y()
    friends=[]
    foes=[]
    victims=[]
    dist = 8
    xmin = max(0, x0-dist)
    xmax = min(Global.LEVELSIZE, x0+dist+1)
    ymin = max(0, y0-dist)
    ymax = min(Global.LEVELSIZE, y0+dist+1)
    for y in range(ymin, ymax):
        for x in range(xmin, xmax):
            ents = level.getEntities(x, y)
            if not ents: continue
            for item in ents:
                if item is self: continue
                f = self.getFriendliness(item)
                if f > Global.F_Neutral:
                    friends.append(item)
                elif f < Global.F_Neutral:
                    if __adjacent(self, item): victims.append(item)
                    foes.append(item)
    if Global.BRAIN_DEBUG:
        def getName(i):
            if i is None: return None
            else: return i.name
        print("friends=%s, foes=%s, victims=%s" % ( list(map(getName, friends)),
                list(map(getName, foes)), list(map(getName, victims)) ))
    return friends, foes, victims

def __getOkayDirs(self, level):
    x0 = self.x()
    y0 = self.y()
    okaydirs=[]
    for dir in range(NDIRS):
        x1 = x0 + DX[dir]
        y1 = y0 + DY[dir]
        if not self.moveBlocked(level, x1, y1):
            okaydirs.append(dir)
    return okaydirs

def __getOkayMoveDir(self, nearestdirs, okaydirs):
    if Global.BRAIN_DEBUG:
        print("%s: getOkayMoveDir %s, %s" % (self.name, nearestdirs, okaydirs), end=' ')
    for movedir in nearestdirs:
        if movedir[1] in okaydirs:
            if Global.BRAIN_DEBUG: print("%s" % str(movedir))
            return movedir[1]
    if Global.BRAIN_DEBUG: print("None")
    return None

def __gossip(self, level, friends):
    for who in friends:
        # nobody wants the opinion of adventurers
        if self.player or who.player: continue
        # or summoned critters
        if self.species == Bestiary.S_Summoned or who.species == Bestiary.S_Summoned:
            continue
        if not __adjacent(self, who): continue
        myfriends = self.friendliness
        gossip = who.friendliness
        if not myfriends and not gossip: continue
        merged = util.dictAdd(myfriends)
        for key in list(gossip.keys()):
            if key in merged:
                merged[key] = (merged[key] + gossip[key]) // 2
            else:
                merged[key] = gossip[key]
        if Global.BRAIN_DEBUG: print("gossip:\n    %s: %s\n    %s: %s\n    %s" % (self.name,
                self.friendliness, who.name, who.friendliness, merged))
        self.friendliness = merged
        who.friendliness = merged

def __moveRandom(self, level):
    if Global.BRAIN_DEBUG: print("    random")
    # Movement requires a speed roll
    if self.taskStat(Global.Speed) < 0: return RES_Nothing

    # just stagger around randomly
    okaydirs=__getOkayDirs(self, level)
    # I'm stuck!
    if not okaydirs: return

    movedir = random.choice(okaydirs)
    return __doMove(self, level, movedir)

def __tryRanged(self, turn, level, foes):
    gun = self.equip[Equip.POS_Ranged]
    if not gun: return 0
    targets = []
    for foe in foes:
        if level.clearLOS(self.x(), self.y(), foe.x(), foe.y(), gun.range):
            targets.append(foe)
    if targets:
        self.rangedAttack(random.choice(targets))
        return RES_Ranged

def __tryGetStuff(self, turn, level):
    # only really dim critters need to make a Mind roll
    if self.stat[Global.Mind] < 5 and self.taskStat(Global.Mind) < 0:
        return 0
    x = self.x(); y = self.y()
    stuff = level.getStuff(x, y)
    if not stuff: return 0
    getme = []
    for item in stuff:
        if isinstance(item, Item.Item) and item.cost() > 0:
            getme.append(item)
    if not getme: return 0
    for item in getme:
        if self.addItem(item):
            level.removeStuff(x, y, item)
            self.message("You get %s" % item.name)
    return RES_Get

#________________________________________
BRAINS={
    Global.B_Autopilot:brainAutopilot,
    Global.B_Coward:brainCoward,
    Global.B_Hunter:brainHunter,
    Global.B_Random:brainRandom,
    Global.B_Still:brainStill,
    }

def think(self, turn, level):
    if Global.BRAIN_DEBUG and Global.TIMING:
        t1=time.clock()
    brainkey = self.brain
    if brainkey == None: return RES_Nothing
    brain = BRAINS[brainkey]
    rc = brain(self, turn, level)
    if Global.BRAIN_DEBUG and Global.TIMING:
        t2=time.clock()
        print("%s %s=%dms" % (self.name, Global.BRAIN_NAMES[brainkey], (t2-t1)*1000))
    return rc

