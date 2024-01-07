from . import Entity, Skill
from . import Global, util
import copy, string, random

NSKILLS = 2
BASE_COST = 10

class Teacher(Entity.Entity):
    #teaching={} # String skillname := Int maxlevel
    def __init__(self, *args, **opts):
        Entity.Entity.__init__(self, *args, **opts);
        self.teaching = {}
        for i in range(util.d(1, NSKILLS)):
            sk = random.choice(Skill.SKILL_NAMES)
            maxlevel = util.d(2, 8) + 4
            self.teaching[sk] = maxlevel
            self.setSkill(sk, max(maxlevel, self.getSkill(sk)) )

    def trigger(self, who):
        u = Global.umbra
        if who.skillPoints <= 0:
            opt = u.showText("%s says:"%self.name,
                    "Sorry, but you're not ready to be trained.")
            return 1
        skillnames = list(self.teaching.keys())
        skillnames.sort()
        prompts = ["Cancel",] + skillnames
        opt = u.menu("%s asks:"%self.name,
                prompts,
                banner="Hi, %s, what skill\nwould you like to be trained in?" % who.name)
        if opt == 0: return 1
        sk = skillnames[opt-1]
        oldlevel = who.getSkill(sk)
        print(sk, oldlevel)
        if oldlevel <= 0:
            cost = BASE_COST * 5
            newlevel = 1
        else:
            cost = util.cumulative(oldlevel) * BASE_COST
            newlevel = oldlevel + 1
        if newlevel > self.teaching[sk]:
            opt = u.showText("%s says:"%self.name,
                    "Sorry, but you know more about that than I do.")
            return 1
        yesno = u.alert("%s says:" % self.name,
                "It will cost you $%d to improve %s.  You have $%d.  Want to do it?" % (cost, sk, who.cash),
                type=Global.ALERT_YESNO)
        if not yesno: return 1
        if who.cash < cost:
            who.message("You cannot afford training in %s." % sk)
            return 1
        who.cash -= cost
        self.cash += cost
        who.setSkill( Skill.getSkill(sk), newlevel )
        who.skillPoints -= 1
        who.message("You now know %s at level %d!" % (sk, newlevel) )
        return 1

