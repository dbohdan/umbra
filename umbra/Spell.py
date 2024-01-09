from . import Bestiary, Entity, Global, Script, util

SPELLS = {}
SPELL_NAMES = []


class Spell:
    # factors=String
    # name=String
    # targeted=Boolean
    # rank=Int
    # cost=Int # rank*rank
    # difficulty=Int # sum of 1..rank, used for skill check and for minimum MAG
    # use=Method
    def __init__(self, rank, name, targeted=0):
        self.rank = rank
        self.cost = rank * rank
        self.difficulty = 0
        for i in range(1, rank + 1):
            self.difficulty += i
        self.name = name
        self.targeted = targeted
        method = "use_%s" % util.purifyName(name)
        if hasattr(self, method):
            self.use = getattr(self, method)
        else:
            self.use = None
        SPELLS[self.name] = self
        SPELL_NAMES.append(self.name)

    def burnout(self):
        amount = self.rank * self.rank
        who.message("Using %s costs you %d Burnout" % (self.name, amount))
        who.stat[Global.Burnout] += amount
        who.checkStatus()

    def lesser_summon(self, who, species, num):
        e = self.greater_summon(who, species, num)
        e.effects.append(
            Script.Script(
                (Script.T, Script.STAT, Global.Wounds, "0 0 1"),
            ),
        )
        return e

    def greater_summon(self, who, species, num):
        e = Bestiary.makeEntity(species, Entity.Entity)
        e.name = "Summoned %s %d" % (species, num)
        e.food = None
        e.species = Bestiary.S_Summoned
        e.friendliness = who.friendliness  # not a copy!
        e.friendSpecies = who.friendSpecies  # not a copy!
        friendSpecies = Bestiary.getSpeciesData(who.species, "friendSpecies")
        if friendSpecies:
            e.friendSpecies.update(Bestiary.getFriends(friendSpecies))
        if who.player:
            for p in Global.umbra.game.party:
                e.friendliness[p.name] = Global.F_Love
        level = Global.umbra.game.getLevel()
        f = who.facing
        e.facing = f
        x = who.x() + Global.DX[f]
        y = who.y() + Global.DY[f]
        level.addStuff(x, y, e)
        return e

    def use_lesser_summon_rats(self, who, target):
        nrats = util.d(1, 6)
        for i in range(1, nrats + 1):
            self.lesser_summon(who, Bestiary.S_Rat, i)


def getSpell(name):
    return SPELLS[name]


# Summon <critter> spells:
# Creates 1 or more of the critter in front of the caster, with friendliness
# set to match his own (personal and race), name="Summoned "+race, food=None
# Lesser Summon spells only last for a few turns - a timer counts down their
# Presence until 0, then they vanish.
# Greater Summon spells do not have the timer, but when the critter dies it
# vanishes.

# Lesser Summon Rats
# Summons 1d6 rats
Spell(1, "Lesser Summon Rats")

##
##
# Spell(x, "x", targeted=1)

NSPELLS = len(SPELLS)
