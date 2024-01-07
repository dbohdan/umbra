from . import Entity, Skill, Terrain
from . import Global, util
import string

T = "t"  # target
U = "u"  # user
TARGETS = (T, U)

ECHO = 0
TELEPORT = 1
DMG = 2
STAT = 3
SAVESTAT = 4
SAVESKILL = 5
LIGHT = 6
NCOMMANDS = 7
COMMAND_METHODS = (
    "do_echo",
    "do_teleport",
    "do_stat",  # DMG uses the same method as stat
    "do_stat",
    "do_savestat",
    "do_saveskill",
    "do_light",
)


class Script:
    # program=[][] # [0]=target, [1]=command, [2+]=args
    def __init__(self, *program):
        self.program = program
        for line in program:
            assert line[0] in TARGETS, "Unknown target in script line: '%s'" % str(line)
            (
                util.assertInt(line[1], 0, NCOMMANDS - 1),
                "Unknown command in script line: '%s'" % str(line),
            )

    def run(self, user, target, result=0):
        #        if Global.DEBUG:
        #            print "run(%d, %d, %d, %s, %s): %s" % (util.toString(user),
        #                    util.toString(target), self.program)
        for line in self.program:
            # find out who it's supposed to affect
            if line[0] == T:
                who = target
            else:
                who = user
            assert who is not None
            cmd = line[1]
            func = getattr(self, COMMAND_METHODS[cmd])
            rc = func(*(user, target, who, line, result))
            if not rc:
                return 0
        return 1

    def do_echo(self, user, target, who, line, result):
        assert isinstance(who, Entity.Entity), str(who)
        text = line[2]
        who.message(text)
        return 1

    def do_teleport(self, user, target, who, line, result):
        assert isinstance(who, Entity.Entity), str(who)
        sector = Global.umbra.game.sector
        level0 = sector.level[who.levelnum()]
        level1 = sector.level[int(line[2])]
        x0 = who.x()
        y0 = who.y()
        x1 = int(line[3])
        y1 = int(line[4])
        if not level0.removeStuff(x0, y0, who):
            assert 0
        if not level1.addStuff(x1, y1, who):
            assert 0
        if len(line) >= 6:
            who.facing = int(line[5])
        return 1

    def do_stat(self, user, target, who, line, result):
        if user is None:
            username = None
        else:
            username = user.name
        if target is None:
            targetname = None
        else:
            targetname = target.name
        stat = line[2]
        statname = Global.STAT_NAMES[stat]
        roll = util.diceString(line[3])
        if Global.COMBAT_DEBUG:
            print("    roll=%d" % roll)
        bonus = util.sign(roll) * result // 3
        if bonus > 4:
            bonus = 4
        elif bonus < -4:
            bonus = -4
        roll += bonus
        if Global.COMBAT_DEBUG:
            print("    result/3,[-4..4]=%d" % bonus)
        if line[1] == DMG and stat == Global.Wounds:
            a = target.getArmor()
            roll -= a
            if roll <= 0:
                if user:
                    user.message(
                        "You have no effect%s!"
                        % util.test(target, " on %s" % targetname, "")
                    )
                if target:
                    target.message(
                        "You are hit%s, but suffer no effect!"
                        % util.test(user, " by %s" % username, "")
                    )
                return 0
            if target.player:
                Global.umbra.showBlood(roll)
        who.stat[stat] += roll
        if stat >= Global.NPRIMES:
            if who.stat[stat] < 0:
                roll += who.stat[stat]  # negating the extra
                who.stat[stat] = 0
        if roll == 0:
            if user:
                user.message(
                    "You have no effect on %s!"
                    % util.test(target, " on %s" % targetname, "")
                )
            if target:
                target.message(
                    "%s has no effect on you!" % util.test(user, "%s" % username, "It")
                )
            return 0
        if stat < Global.NPRIMES:
            if roll < 0:
                doText = "strip %d" % (-roll)
                takeText = "lose %d" % (-roll)
            else:
                doText = "restore %d" % roll
                takeText = "gain %d" % roll
        else:
            if roll > 0:
                doText = "do %d" % roll
                takeText = "take %d" % roll
            else:
                doText = "restore %d" % (-roll)
                takeText = "recover %d" % (-roll)
        if user:
            user.message(
                "You %s %s%s!"
                % (doText, statname, util.test(target, " to %s" % targetname, ""))
            )
        if target:
            target.message(
                "You %s %s%s!"
                % (takeText, statname, util.test(user, " from %s" % username, ""))
            )
        # all done, see if they're alive.
        if user:
            user.checkStatus()
        if target:
            target.checkStatus()
        return 1

    def do_savestat(self, user, target, who, line, result):
        assert isinstance(who, Entity.Entity), str(who)
        stat = line[2]
        mod = line[3]
        if who.taskStat(stat, mod) >= 0:
            if len(line) >= 5:
                who.message(line[4])
            return 0
        return 1

    def do_saveskill(self, user, target, who, line, result):
        assert isinstance(who, Entity.Entity), str(who)
        skill = Skill.getSkill(line[2])
        mod = line[3]
        if who.taskSkill(skill, mod) >= 0:
            if len(line) >= 5:
                who.message(line[4])
            return 0
        return 1

    def do_light(self, user, target, who, line, result):
        light = int(line[2])
        if light:
            who.light_level = light
        elif hasattr(who, "light_level"):
            del who.light_level
        return 1
