import Brain, Skill, Script, Sprite
import Thing, Item, Equip, Loot, Melee, Ranged, Defense, Ammo
import Bestiary, Terrain
import Global, util
import OkayDialog
import Tkinter
import copy, os, string, whrandom

DEBUG_WITNESS=1

MAXITEMS=25

MIST_SPRITE = os.path.join("thing", "mist")

Fisticuffs = Script.Script( (Script.T, Script.DMG, Global.Wounds, "1 2"), )

class Entity(Thing.Thing):
    #species=String
    #gender=Int
    #stat=Int[]
    #prof=String
    #level=Int
    #xp=Int
    #skillPoints=Int
    #__skill={} # skill.name=String := level=Int
    #brain=Int
    #equip=Thing[]
    #__items=Thing[]
    #player=Boolean
    #lastTurn=Int
    #effects=Script[] # applied every turn
    #speech=None # List of: String=canned speech item, OK to hear next item
    #       # Sequence=(banner, prompts=List of String, gotoState=List of Int)
    #speechState=Int
    #cash=Int
    #defense=Int
    #unarmed=Script
    #friendliness={} # entity.name := mod (negative = hate, positive = like)
    #friendSpecies={} # species name := mod (negative = hate, positive = like)
    #autopsy=String # what you died of
    #killedSpecies={} # entity.species := 1 if you have killed any of them
    #size=Int
    #spells=String[] # optional, names of all spells known
    #food=Script # optional, overrides species food value
    def __init__(self, name, sprite, species, gender, prof, stat):
        if sprite != None: sprite = os.path.join("entity", sprite)
        Thing.Thing.__init__(self, name, sprite)
        self.species=species

        util.assertInt(gender, 0, Global.NGENDERS-1)
        self.gender=gender

        self.stat=stat
        util.expandArray(self.stat, Global.NSTATS)
        for i in xrange(Global.NPRIMES, Global.NSTATS):
            self.stat[i] = 0

        util.assertInt(prof, 0, Global.NPROFS-1)
        self.prof=prof
        self.level=1
        self.xp=100
        self.skillPoints=0
        self.__skill={}
        if prof == Global.P_Killer:
            self.setSkill(Skill.Melee, 5)
            self.setSkill(Skill.Ranged, 5)
            self.setSkill(Skill.Dodge, 2)
        elif prof == Global.P_Sneak:
            self.setSkill(Skill.Dodge, 5)
            self.setSkill(Skill.Locksmith, 5)
            self.setSkill(Skill.Melee, 2)
        elif prof == Global.P_Techie:
            self.setSkill(Skill.Repair, 5)
            self.setSkill(Skill.Science, 5)
            self.setSkill(Skill.Ranged, 2)
        elif prof == Global.P_Arcanist:
            self.setSkill(Skill.Magic, 5)
            self.setSkill(Skill.Archaeology, 5)
            self.setSkill(Skill.Dodge, 2)
        else:
            self.setSkill(Skill.Melee, 1)
            self.setSkill(Skill.Ranged, 1)
            self.setSkill(Skill.Dodge, 1)
            self.setSkill(Skill.Science, 1)
            self.setSkill(Skill.Archaeology, 1)

        self.brain=None
        self.equip=util.makeArray(Equip.NPOS)
        self.__items=[]
        self.player=0
        self.lastTurn=0
        self.effects=[]
        self.speech=None
        self.speechState=0
        self.cash=0
        self.defense=0
        self.unarmed=Fisticuffs
        self.friendliness={}
        self.friendSpecies={}
        self.killedSpecies={}
        self.size=Global.SIZE_Medium

    def __str__(self):
        text="Name: %s\n%s" % (self.name, self.charText(80))
        return text

    def addItem(self, item):
        if self.countItems() >= MAXITEMS:
            return 0
        if Global.COMBAT_DEBUG:
            print "%s.addItem(%s): count=%d" % (self.name, item.name,
                    self.countItems() )
        self.__items.append(item)
        return 1

    def meleeAttack(self, target):
        weapon = self.equip[ Equip.POS_Melee ]
        if weapon == None: effect = self.unarmed
        else: effect = weapon.effect
        if target == "Ahead":
            self.meleeAttackAhead(effect)
        else:
            self.attack(target, Skill.Melee, effect)

    def meleeAttackAhead(self, effect):
        game = Global.umbra.game
        level = game.getLevel()
        d = self.facing
        tx = self.x()+Global.DX[d]; ty = self.y()+Global.DY[d]
        door = level.getDoor(tx, ty)
        if door:
            ahead = Entity("the door", None, "Door", 0, 0,
                    [Global.DOOR_TOUGHNESS,]*Global.NPRIMES )
        else:
            terrain = level.getTerrain(tx, ty)
            if terrain.toughness == 0:
                self.message("You have no effect.")
                return
            ahead = Entity("the %s" % terrain.name.lower(), None,
                    terrain.name, 0, 0,
                    [terrain.toughness,]*Global.NPRIMES )
        effect.run(self, ahead, 0)
        if ahead.isDead():
            if door:
                level.removeStuff(tx, ty, door)
                if door.linkedTo:
                    tx1, ty1, lvlnum1 = door.linkedTo
                    level1 = game.getLevel(lvlnum1)
                    door1 = level1.getDoor(tx1, ty1)
                    if door1:
                        level1.removeStuff(tx1, ty1, door1)
            else:
                terrain.damage(level, tx, ty)
                if terrain.name == "Altar":
                    for p in game.party:
                        p.awardXP((p.level + level.levelnum) * 20)
                    # double helping of XP
                    self.awardXP((p.level + level.levelnum) * 20)
                    game.altarsDestroyed += 1
                    for y in xrange(ty-1, ty+2):
                        for x in xrange(tx-1, tx+2):
                            catalog = level.getScript(x, y)
                            if catalog:
                                for script in catalog[:]:
                                    level.removeScript(x, y, script)
            self.message("You destroy %s!" % ahead.name)

    def rangedAttack(self, target):
        weapon = self.equip[ Equip.POS_Ranged ]
        if weapon == None: return
        else: effect = weapon.effect
        if self.player or target.player:
            if self.player:
                x0 = self.x(); y0 = self.y()
                x1 = target.x(); y1 = target.y()
            else:
                x0 = target.x(); y0 = target.y()
                x1 = self.x(); y1 = self.y()
            Global.umbra.showGunshot(x0+0.5, y0+0.5, x1+0.5, y1+0.5)
        self.attack(target, Skill.Ranged, effect)

    def attack(self, target, skill, weaponEffect):
        target.friendliness[self.name] = Global.F_Enmity
        self.friendliness[target.name] = Global.F_Enmity
        if target.brain == Global.B_Random:
            target.brain = Global.B_Hunter
        result = self.taskSkill(skill, 0)
        if Global.COMBAT_DEBUG:
            print "%s attacks %s" % (self.name, target.name)
            print "strike %d" % result
        if result < 0:
            self.message("You miss %s!" % target.name)
            target.message("%s misses you!" % self.name)
            return
        # dodge
        dodge = target.taskSkill(Skill.Dodge, 0)
        if Global.COMBAT_DEBUG:
            print "dodge %d" % dodge
        if dodge >= result:
            diff = dodge - result
            if diff <= 3:
                mymsg = "%s barely dodges your attack..."
                yourmsg = "You barely dodge an attack from %s..."
            elif diff <= 6:
                mymsg = "%s dodges your attack."
                yourmsg = "You dodge an attack from %s."
            elif diff <= 9:
                mymsg = "%s dodges superbly!"
                yourmsg = "You superbly dodge an attack from %s!"
            else:
                mymsg = "%s makes an unbelievable dodge!"
                yourmsg = "You make an unbelievable dodge against an attack from %s!"
            self.message(mymsg % target.name)
            target.message(yourmsg % self.name)
            return
        else:
            # positive dodge rolls subtract from result quality
            if dodge > 0:
                result -= dodge
            if result <= 3:
                mymsg = "You barely land a blow on %s..."
                yourmsg = "%s barely hits you..."
            elif result <= 6:
                mymsg = "You hit %s."
                yourmsg = "%s hits you."
            elif result <= 9:
                mymsg = "You make a superb strike on %s!"
                yourmsg = "%s makes a superb strike on you."
            else:
                mymsg = "You make an unbelievable strike on %s!"
                yourmsg = "%s makes an unbelievable strike on you."
            self.message(mymsg % target.name)
            target.message(yourmsg % self.name)
        self.attackEffect(target, weaponEffect, result)
        self.witnessAttack(target)

    def attackEffect(self, target, effect, result):
        if not effect:
            self.message("You have no effect on %s!" % target.name)
            target.message("%s has no effect on you!" % self.name)
            return
        effect.run(self, target, result)
        if target.isDead() and self.player:
            self.message("%s!" % target.autopsy)
            self.murdersReward(target)

    def awardXP(self, award):
        # don't let anyone jump more than 1 level at once
        n = self.nextXP(self.level+1)
        if self.xp + award > n:
            award = n-1 - self.xp
        self.xp += award
#        self.message("You gain %d experience" % award)
        if self.xp >= self.nextXP():
            self.level += 1
            self.skillPoints += 1
            st = util.d(1, Global.NPRIMES)-1
            self.stat[st] += 1
            self.message("You are now level %d!  Your %s improves, and you have %d skill point%s." % (self.level,
                    Global.STAT_NAMES[st], self.skillPoints,
                    util.test(self.skillPoints>1, "s", "")) )

    def charText(self, columns):
        text="%s %s\nProfession: %s\nLevel: %d\tXP: %d (next level at %d XP)\n\n" % \
                (Global.GENDER_NAMES[self.gender], self.species,
                Global.PROF_NAMES[self.prof], self.level, self.xp,
                self.nextXP() )
        # stats
        STAT_NAMES=Global.STAT_NAMES
        NPRIMES=Global.NPRIMES
        for i in xrange(NPRIMES):
            text = "%s%-9s  %2d\t%-9s  %2d\n" % (text,
                STAT_NAMES[i]+":", self.stat[i],
                STAT_NAMES[i+NPRIMES]+":", self.stat[i+NPRIMES])
        text = "%s\n%s\n" % (text, util.foldLines(self.skillsText(), columns) )
        text = "%s\n%s" % (text, util.foldLines(self.inventoryText(), columns) )
        return text

    def checkStatus(self):
        """Called to make the Entity aware of being dead, insane, higher level,
            etc."""
        # now check the pulse...
        dead = self.isDead()
        if dead:
            self.die(dead)
            return
        # every fatigue overflow causes one wound point.
        if self.stat[Global.Fatigue] > self.stat[Global.Speed]:
            rec = max(1, self.stat[Global.Speed])
            self.stat[Global.Fatigue] -= rec
            self.stat[Global.Wounds] += 1
            self.checkStatus()
            return
        # every burnout overflow costs you one point of Mind and Presence.
        if self.stat[Global.Burnout] > self.stat[Global.Mind]:
            rec = max(1, self.stat[Global.Mind])
            self.stat[Global.Burnout] -= rec
            self.stat[Global.Mind] -= 1
            self.stat[Global.Presence] -= 1
            self.checkStatus()
            return
        # every madness overflow costs you one point of Mind and Presence.
        if self.stat[Global.Madness] > self.stat[Global.Presence]:
            rec = max(1, self.stat[Global.Presence])
            self.stat[Global.Madness] -= rec
            self.stat[Global.Presence] -= 1
            self.stat[Global.Mind] -= 1
            self.checkStatus()
            return

    def countItems(self):
        return len(self.__items)

    def die(self, cause):
        if self.player and (cause == "No Mind" or cause == "No Presence"):
            if self.stat[Global.Presence] < 0:
                self.autopsy = "%s goes mad!" % self.name
                self.message("You go mad, and turn on your trusting comrades!")
                return
        self.autopsy = "%s dies of %s" % (self.name, cause)
        self.message("You die of %s!" % cause)
        if Global.COMBAT_DEBUG:
            print self

    def draw(self, canvas, nx, ny, facing, light):
        if self.player and nx==0 and ny==0: return
        if self.isBurrowing():
            if util.d(1, 2) == 1:
                spr = Sprite.getSprite("%s%d" % (MIST_SPRITE, util.d(1, 2)) )
                spr.draw(self, canvas, nx, ny, facing, light, self.facing)
        else:
            Thing.Thing.draw(self, canvas, nx, ny, facing, light)

    def drawStatus(self, canvas, charfont, tinyfont, y, key):
        y0 = y
        w = int(canvas["width"])
        canvas.create_line(0, y, w, y, fill="#cccccc")
        canvas.create_text(0, y, text="[%s] %s" % (key, self.name),
            font=charfont, fill="#ffff00", anchor=Tkinter.NW)
        y += charfont[1]
        htiny = tinyfont[1]
        if os.name == "nt":
            y += 4
            htiny += 2
        y += 1
        NSTATS=Global.NSTATS
        NPRIMES=Global.NPRIMES
        NPRIMES2=NPRIMES/2
        row=0
        x = 0
        ystats = y
        for st in xrange(NPRIMES, NSTATS):
            if row == NPRIMES2:
                x = w/2
                y = ystats
            row += 1
            maxscore = self.stat[st-NPRIMES]
            score = self.stat[st]
            if score >= maxscore*3/4: scorecolor="#ff0000"
            elif score >= maxscore/2: scorecolor="#ffff00"
            else: scorecolor="#00ff00"
            if score > 0:
                xscore = min(w/2, w/2 * score / maxscore)
                canvas.create_rectangle(x, y, x+xscore, y+htiny+1,
                    fill="", outline=scorecolor)
            text = "%-7s %2d [%2d]"%(Global.STAT_NAMES[st], score, maxscore)
            canvas.create_text(x+2, y, text=text,
                font=tinyfont, fill=scorecolor, anchor=Tkinter.NW)
            y += htiny + 2
        canvas.create_line(0, y, w, y, fill="#cccccc")
        if self.isDead():
            canvas.create_rectangle(0,y0,w,y, fill="#990000", stipple="gray25")
        return y

    def getArmor(self):
        armor = self.defense
        for item in self.equip:
            if item and isinstance(item, Defense.Defense):
                armor += item.defense
        if Global.COMBAT_DEBUG:
            print "armor %d" % armor
        return armor

    def getFriendliness(self, target):
        if self.friendliness.has_key(target.name):
            return self.friendliness[target.name]
        if target.species == self.species:
            return Global.F_Tolerant
        if self.friendSpecies.has_key(target.species):
            return self.friendSpecies[target.species]
        fspecies = Bestiary.getFriendSpecies(self.species, target.species)
        if fspecies != None:
            return fspecies
        return Global.F_Hostile

    def getSkill(self, skill):
        if isinstance(skill, Skill.Skill): skillname = skill.name
        else: skillname = skill
        return self.__skill.get(skillname, -5)

    def handedItem(self, who, item):
        if not self.handedItemTest(who, item): return 0
        who.message("%s thanks you for the %s." % (self.name, item.name))
        self.addItem(item)
        return 1

    def handedItemTest(self, who, item):
        if self.countItems() >= MAXITEMS:
            who.message("%s is carrying too much already." % self.name)
            return 0
        if self.stat[Global.Mind] < 5:
            if self.taskStat(Global.Mind) < 0:
                who.message("%s is confused by the offer." % self.name)
                return 0
        f = self.getFriendliness(who)
        if f < 0:
            who.message("%s doesn't trust you." % self.name)
            return 0
        return 1

    def inventoryText(self):
        text = "Cash:\t$%d\n" % (self.cash)
        for i in xrange(Equip.NPOS):
            if self.equip[i]:
                text = "%s%s: %s\n"%(text,Equip.POS_NAMES[i],self.equip[i].name)
        text="%sItems:\t" % text
        items=[]
        for item in self.__items:
            items.append( item.name )
        items.sort()
        textitems = []
        for i in xrange(len(items)):
            itemname = items[i]
            if itemname == None: continue
            count = 0
            for j in xrange(len(items)):
                othername = items[j]
                if othername == None: continue
                if itemname == othername:
                    count += 1
                    items[j] = None
            if count == 1:
                textitems.append( "%s" % itemname )
            else:
                textitems.append( "%s (x%d)" % (itemname, count) )
        text = util.commaList(textitems, text=text)
        return text

    def isBlocking(self, who):
        return not self.isBurrowing()

    def isBurrowing(self):
        return self.levelnum() == 0 and self.isUndead() and \
                Global.umbra.game.light_level >= Global.LIGHT_DAY

    def isDead(self):
        # if any stat falls below 0, you die.
        for i in xrange(Global.NPRIMES):
            if self.stat[i] < 0:
                return "No %s" % Global.STAT_NAMES[i]
        # If wounds overflow, you die.
        wndover = self.stat[Global.Wounds] - self.stat[Global.Body]
        if wndover > 0:
            return "%d wounds" % wndover
        # Better get a bigger gun, I'm not dead yet!
        if hasattr(self, "autopsy"):
            del self.autopsy
        return None

    def isUndead(self):
        u = Bestiary.getSpeciesData(self.species, "undead")
        return util.test(u)

    def listEquip(self):
        options = ["Cancel", ]
        items=[]
        for i in xrange(Equip.NPOS):
            item = self.equip[i]
            if item:
                items.append(item)
                options.append( "%s: %s" % (Equip.POS_NAMES[i], item.name) )
        return (options, items)

    def listItems(self):
        return list(self.__items)

    def listSkills(self):
        return self.__skill.keys()

    def message(self, msg):
        if self.player:
            Global.umbra.showStatus("%s: %s" % (self.name, msg) )
        else:
            if Global.COMBAT_DEBUG:
                print "%s: %s" % (self.name, msg)

    def moveBlocked(self, level, x, y, polite=1):
        if level.getBlocking(x, y, self):
            return "You cannot move there!"
        if polite:
            ents = level.getEntities(x, y)
            if ents:
                for who in ents:
                    if who.isBlocking(self):
                        return "You are blocked by %s." % who.name
        return None

    def murdersReward(self, target):
        """Only players need to track this stuff."""
        if not self.player: return
        sp = target.species
        self.killedSpecies[sp] = self.killedSpecies.get(sp, 0) + 1
        # gain madness for killing a nominally friendly species
        fspecies = Bestiary.getFriendSpecies(self.species, sp)
        if fspecies != None:
            roll = max(0, fspecies*util.d(1, 6))
            if roll > 0:
                self.stat[Global.Madness] += max(0, fspecies*util.d(1, 6))
                self.message("You take %d Madness for killing %s!" % (roll, target.name))
                self.checkStatus()
        # distribute XP
        party = Global.umbra.game.party
        nparty = len(party)
        xp = max(1, target.xp / 10 / nparty)
        if Global.COMBAT_DEBUG:
            print "%s.xp=%d, party xp=%d" % (target.name, target.xp, xp)
        for who in party:
            award = xp
            # second helpings for the killer
            if who is self: award += xp
            who.awardXP(award)

    def nextTurn(self, turn, level):
        # You don't get to move multiple times!
        if self.lastTurn == turn: return
        self.lastTurn=turn
        #FIXME: any recoveries, effects...
        for e in self.effects:
            e.run(None, self)
            #FIXME: allow some way for a script to remove itself
        if self.isDead():
            self.thingsToDoWhenYoureDeadIn(level)
            return
        if self.player: return
        #NPC-only stuff below
        # the undead cannot abide sunlight!
        if self.isBurrowing(): return
        Brain.think(self, turn, level)

    def nextXP(self, level=None):
        if level == None: level = self.level
        xp = util.nextXP(level)
        if self.prof == Global.P_Jack:
            xp = xp / 10 * 8
        return xp

    def readyEquip(self, item):
        #FIXME: if canUse...
        for p in xrange(Equip.NPOS):
            if not self.equip[p] and item.isLegalpos(p):
                self.removeItem(item)
                self.equip[p]=item
                if item.readyEffect:
                    item.readyEffect.run(item, self)
                return 1
        else:
            if self.player:
                Global.umbra.alert("Ready Equipment", "Cannot use %s until something else is removed."%item)
            return 0

    def removeItem(self, item):
        i = util.indexOf(item, self.__items)
        if i >= 0:
            self.__items.pop(i)
            return 1
        return 0

    def setSkill(self, skill, level):
        if isinstance(skill, Skill.Skill): skillname = skill.name
        else: skillname = skill
        self.__skill[skillname] = level

    def skillsText(self):
        text = ""
        if self.skillPoints > 0:
            text = "Skills (%d skill points):  " % self.skillPoints
        else:
            text = "Skills:  "
        skills = []
        skillkeys = self.listSkills(); skillkeys.sort()
        for key in skillkeys:
            skills.append( "%s: %d" % (key, self.getSkill(key)) )
        text = util.commaList(skills, text=text)
        return text

    def taskStat(self, statnum, mod=0):
        score = self.stat[statnum] + mod
        return util.taskRoll(score)

    def taskSkill(self, skill, mod=0):
        bonus = self.getSkill(skill)
        score = self.stat[skill.stat]/2 + bonus + mod
        return util.taskRoll(score)

    def thingsToDoWhenYoureDeadIn(self, level): # probably not Denver.
        if util.endsWith(self.autopsy, "goes mad!"):
            for i in xrange(Global.NPRIMES):
                self.stat[i] = util.d(1, 10) + 10
            for i in xrange(Global.NPRIMES, Global.NSTATS):
                self.stat[i] = 0
            self.name = "%s the Lunatic" % self.name
            self.species = Bestiary.S_Lunatic
            self.brain = Global.B_Hunter
            self.friendliness = {}
            self.speech = ("Hi, guys...  HEehhahaHAHheemph...",)
            del self.autopsy
            if self.player:
                self.player = 0
                Global.umbra.game.removeCharacter(self)
            return
        x = self.x(); y = self.y()
        level.removeStuff( x, y, self )
        myspecies = Bestiary.SPECIES_DATA.get(self.species, None)
        if hasattr(self, "food"): food = self.food
        elif myspecies: food = myspecies.get("food", None)
        else: food = None
        if food:
            corpse = Loot.Loot("corpse of %s" % self.name, "corpse")
            corpse.oneshot = 1
            corpse.effect = food
            level.addStuff( x, y, corpse )
        if self.equip:
            for item in self.equip:
                if item:
                    level.addStuff( x, y, item )
        if self.__items:
            for item in self.__items:
                if item:
                    level.addStuff( x, y, item )
        if self.cash > 0:
            cash = Global.umbra.game.makeCash(self.cash)
            level.addStuff( x, y, cash )
        if self.player:
            Global.umbra.game.removeCharacter(self)

    def trigger(self, who):
        if not self.speech:
            who.message("%s says nothing." % self.name)
            return 1
        u = Global.umbra
        if Global.DEBUG:
            print "%s: speech=%s len=%d" % (self.name, self.speech, len(self.speech))
        while 1:
            if Global.DEBUG:
                print "speechState=%d" % self.speechState
            ss=self.speechState
            x=self.speech[ss]
            if x == None:
                self.speechState = 0
                return 1
            elif util.isInt(x):
                self.speechState = x
            elif util.isString(x):
                u.showText("%s says:" % self.name, x)
                self.speechState += 1
                if self.speechState == len(self.speech):
                    self.speechState = 0
                    return 1
            elif util.isSequence(x):
                opt = u.menu(title="%s asks:" % self.name, banner=x[0],
                    prompts=x[1])
                self.speechState = x[2][opt]
                if self.speechState < 0:
                    self.speechState = 0
                    return 1
            else: assert 0, "Unknown speech type (%s) '%s'" % (type(x), x)
            #FIXME: effect/script support

    def tryAmmo(self, item):
        gun = self.equip[ Equip.POS_Ranged ]
        if not gun:
            self.message("You must have a gun ready to reload it!")
            return 0
        if not item.fitsIn(gun):
            self.message("You can't put %s ammo in a %s!" % (item.ammoType,
                gun.name) )
            return 0
        load = gun.ammo + item.ammo
        if load > gun.ammoCapacity:
            self.message("%s is already loaded with %d rounds!" % (gun.name, gun.ammo) )
            return 0
        gun.ammo = load
        self.removeItem(item)
        return 1

    def unreadyEquip(self, item):
        if item.cursed:
            if self.player:
                Global.umbra.showStatus("%s cannot remove %s - it is cursed!" % (self.name, item.name) )
            return 0
        if self.countItems() >= MAXITEMS:
            if self.player:
                Global.umbra.showStatus("%s: You cannot remove that until you drop some items!" % self.name)
            return 0
        if item.unreadyEffect:
            item.unreadyEffect.run(item, self)
        p=self.equip.index(item)
        self.equip[p]=None
        self.addItem(item)
        return 1

    def useItem(self, item):
        #FIXME: if canUse...
        if isinstance(item, Equip.Equip):
            return self.readyEquip(item)
        elif isinstance(item, Ammo.Ammo):
            return self.tryAmmo(item)
        elif isinstance(item, Loot.Loot):
            if item.oneshot:
                self.removeItem(item)
            if item.effect:
                item.effect.run(item, self)
        else:
            self.message("Nothing happens.")
        return 1

    def witnessAttack(self, victim):
        if DEBUG_WITNESS:
            print "%s attacked %s:" % (self.name, victim.name)
        level = Global.umbra.game.getLevel()
        x0 = max(0, self.x()-Global.VIEWDIST)
        x1 = min(Global.LEVELSIZE, self.x()+Global.VIEWDIST+1)
        y0 = max(0, self.y()-Global.VIEWDIST)
        y1 = min(Global.LEVELSIZE, self.y()+Global.VIEWDIST+1)
        if self.player or victim.player: notplayers = 0
        else: notplayers = 1
        for y in xrange(y0, y1):
            for x in xrange(x0, x1):
                wits = level.getEntities(x, y)
                if not wits: continue
                for who in wits:
                    if who is self or who is victim: continue
                    fperp = who.getFriendliness(self)
                    fvictim = who.getFriendliness(victim)
                    if DEBUG_WITNESS:
                        print "    witness %s, fperp=%s, fvictim=%s, friends=%s" % \
                                (who.name, fperp, fvictim, str(who.friendliness)),
                    # love is blind.
                    if fperp == Global.F_Love:
                        if DEBUG_WITNESS: print "love is blind"
                        continue
                    # you only care if you can see who the victim is
                    if not level.clearLOS(who.x(), who.y(),
                            victim.x(), victim.y(), Global.VIEWDIST):
                        if DEBUG_WITNESS: print "can't see %s" % victim.name
                        continue
                    if not level.clearLOS(who.x(), who.y(),
                            self.x(), self.y(), Global.VIEWDIST):
                        if DEBUG_WITNESS: print "can't see %s" % self.name
                        continue
                    # the enemy of my enemy is my friend
                    if fvictim < Global.F_Neutral:
                        who.friendliness[self.name]=min(Global.F_Friendly,
                                fperp+1)
                        if DEBUG_WITNESS: print "hooray!"
                    elif fvictim > Global.F_Neutral:
                        who.friendliness[self.name]=max(Global.F_Enmity,
                                fperp-2)
                        if DEBUG_WITNESS: print "I hate you!"
                    else:
                        if DEBUG_WITNESS: print "I don't care."
                    # now show the player what's happening, if it's visible
                    if who.player and notplayers:
                        if DEBUG_WITNESS: print "%s sees it!" % who.name
                        Global.umbra.showGunshot(self.x(), self.y(),
                            victim.x(), victim.y(), "#ff0000", player=0)
                        Global.umbra.showStatus("%s attacks %s" % (self.name,
                                victim.name) )

#________________________________________
class EntityDialog(OkayDialog.OkayDialog):
    def makeBody(self, body, args):
        NW=Tkinter.NW
        W=Tkinter.W
        LEFT=Tkinter.LEFT
        who = args["entity"]
        main = args["main"]

        self.title(who.name)

        Tkinter.Label(body, text=who.name, font=("Lucida", 20, "bold"),
            bg="#000000", fg="#ffff00", justify=LEFT).pack(anchor=W)
        text = who.charText(40)
        self.__makeLabel(body, text).pack(anchor=W)

        # controls
        if main:
            for i in xrange(1, len(Global.VIEW_MENU)):
                text=Global.VIEW_MENU[i]
                key=Global.VIEW_MENU_KEYS[i]
                b = self.addButton(text, key, side=Tkinter.TOP, fill=Tkinter.X,
                    font=OkayDialog.MENU_FONT, anchor=NW, highlightthickness=0,
                    borderwidth=1, padx=0, pady=0)
        self.top.bind("0", self.event)

        self.ok.focus_set()
        return

    def __makeLabel(self, cont, text):
        return Tkinter.Label(cont, text=text, font=OkayDialog.MONO_FONT,
            bg="#000000", fg="#33ff33", justify=Tkinter.LEFT)

