from . import Door, Spell
from . import Global, util

SKILLS = {}
SKILL_NAMES = []


class Skill:
    # name=String
    # stat=Int
    # use=Method
    def __init__(self, name, stat):
        self.name = name
        self.stat = stat
        method = "use%s" % name
        if hasattr(self, method):
            self.use = getattr(self, method)
        else:
            self.use = None
        SKILLS[name] = self
        SKILL_NAMES.append(name)

    def cost(self, who, st, amount):
        if amount == 0:
            return
        who.message(
            "Using %s costs you %d %s" % (self.name, amount, Global.STAT_NAMES[st])
        )
        who.stat[st] += amount
        who.checkStatus()

    def useLocksmith(self, who):
        level = Global.umbra.game.getLevel()
        award = (who.level + level.levelnum) * 5
        f = who.facing
        x1 = who.x() + Global.DX[f]
        y1 = who.y() + Global.DY[f]
        door = level.getDoor(x1, y1)
        if not door:
            who.message("Try it in front of a door...")
            return Global.NOREDRAW
        if door.trap:
            rq = who.taskSkill(self)
            if rq >= 0:
                door.trap = None
                who.message("You find and remove a trap!")
                who.awardXP(award)
            elif rq <= -10:
                door.trigger(who)
            else:
                who.message("You find a trap, but can't remove it.")
            door.updateLink()
            self.cost(who, Global.Fatigue, util.d(1, 6))
            return Global.NEXTTURN
        state = door.getState()
        if state == Door.S_Open:
            who.message("That door's already open!")
            return Global.NOREDRAW
        elif state == Door.S_Closed:
            door.trigger(who)
            door.updateLink()
            return Global.NEXTTURN
        if who.taskSkill(self) >= 0:
            door.setState(Door.S_Open)
            door.updateLink()
            who.message("You unlock and open the door!")
            who.awardXP(award)
        else:
            who.message("You fail to unlock it.")
        self.cost(who, Global.Fatigue, util.d(1, 6))
        return Global.NEXTTURN

    def useMagic(self, who, spell=None):
        if not hasattr(who, "spells"):
            who.message("You do not know any spells.")
            return Global.NOREDRAW
        if not spell:
            if not who.player:
                who.message("You can't decide which spell to use!")
                return Global.NOREDRAW
            prompts = [
                "Cancel",
            ]
            for spell in who.spells:
                prompts.append(spell)
            opt = Global.umbra.menu("%s: Cast which spell?" % who.name, prompts)
            if opt == 0:
                return Global.NOREDRAW
            spell = Spell.getSpell(who.spells[opt - 1])
        if who.taskSkill(self, spell.difficulty) < 0:
            self.cost(who, Global.Burnout, spell.cost // 2)
            who.message("You fail to get the spell off!")
            return Global.NOREDRAW
        if spell.targeted:
            target = Global.umbra.selectTarget(
                who,
                Global.TARGET_Ranged,
                "%s: Target for %s" % (who.name, spell.name),
                rng=Global.VIEWDIST,
            )
            if target is None:
                return Global.NOREDRAW
        else:
            target = None
        text = "You cast %s" % spell.name
        if target:
            text = "%s at %s" % (text, target.name)
        who.message(text)
        self.cost(who, Global.Burnout, spell.cost)
        spell.use(who, target)
        return Global.REDRAW


def getSkill(name):
    return SKILLS[name]


Melee = Skill("Melee", Global.Body)
Ranged = Skill("Ranged", Global.Speed)
Dodge = Skill("Dodge", Global.Speed)
Locksmith = Skill("Locksmith", Global.Speed)
Repair = Skill("Repair", Global.Mind)
Science = Skill("Science", Global.Mind)
Magic = Skill("Magic", Global.Mind)
Archaeology = Skill("Archaeology", Global.Mind)

NSKILLS = len(SKILLS)
