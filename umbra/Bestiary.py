from . import Brain, Equip, Shop, Skill, Script
from . import Global, util
import copy, random

NAMED_A = 0
NAMED_AN = 1
NAMED_EPITHET = 2
NAMED_FULL = 3
NAMED_TITLE = 4

Cannibalism = Script.Script(
    (Script.T, Script.STAT, Global.Wounds, "-2 2 3"),
    (Script.T, Script.STAT, Global.Fatigue, "-2 2 3"),
    (Script.T, Script.STAT, Global.Madness, "1 3"),
)


def getFriends(group):
    return FRIENDS.get(group)


def getSpeciesData(species, key):
    data = SPECIES_DATA.get(species)
    if not data:
        return None
    return data.get(key, None)


def getFriendSpecies(myspecies, otherspecies):
    group = getSpeciesData(myspecies, "friendSpecies")
    if not group:
        return None
    return FRIENDS[group].get(otherspecies, None)


def makeEntity(species, clazz):
    data = SPECIES_DATA[species]
    sprite = data.get("sprite", species)
    # build a name for it
    named = data.get("named", NAMED_A)
    if util.isString(named):
        name = named
    elif named == NAMED_EPITHET:
        name = "%s the %s" % (util.randomName(1), species)
    elif named == NAMED_FULL:
        name = "%s %s" % (util.randomName(0), util.randomName(1))
    elif named == NAMED_TITLE:
        name = "%s %s %s" % (species, util.randomName(0), util.randomName(1))
    elif named == NAMED_AN:
        name = "%s, an %s" % (util.randomName(0), species)
    else:  # named==NAMED_A
        name = "%s, a %s" % (util.randomName(0), species)
    gender = util.d(1, Global.NGENDERS) - 1
    if "prof" in data:
        prof = data["prof"]
        util.assertInt(prof, 0, Global.NPROFS - 1)
    else:
        prof = util.d(1, Global.NPROFS) - 1
    # roll them bones
    stat = [
        0,
    ] * Global.NSTATS
    if "stat" in data:
        statrolls = data["stat"]
        for i in range(Global.NPRIMES):
            stat[i] = util.diceString(statrolls[i])
    else:
        for i in range(Global.NPRIMES):
            stat[i] = util.d(2, 10)
    who = clazz(*(name, sprite, species, gender, prof, stat))
    if "level" in data:
        level = data["level"]
        who.level = level
        who.xp = who.nextXP(level - 1)
        for i in range(1, level):
            skl = random.choice(who.listSkills())
            who.setSkill(skl, who.getSkill(skl) + 1)
            st = util.d(1, Global.NPRIMES) - 1
            who.stat[st] += 1
    who.brain = data.get("brain", None)
    if "speech" in data:
        who.speech = data["speech"]
        if who.speech == "mogth":
            who.speech = (
                " ".join(
                    [
                        util.randomName(util.d(1, 3) == 1).lower()
                        for i in range(util.d(2, 4))
                    ]
                ).capitalize()
                + " Mogth!"
            )
    if "cash" in data:
        who.cash = util.diceString(data["cash"])
        if who.cash < 0:
            who.cash = 0
    if "equip" in data:
        for i in data["equip"]:
            if util.isString(i):
                item = Shop.getShopItem(i)
                assert item, "%s: Unknown shop item %s" % (name, i)
            else:
                item = copy.deepcopy(i)
            if isinstance(item, Equip.Equip):
                if not who.readyEquip(item):
                    assert 0, "%s: Unable to ready %s" % (name, itemname)
            else:
                who.addItem(item)
    who.defense = int(data.get("defense", 0))
    who.unarmed = data.get("unarmed", None)
    who.size = data.get("size", Global.SIZE_Medium)
    return who


S_Adventurer = "Adventurer"
S_Boss = "Boss"
S_Soldier = "Soldier"
S_Merchant = "Merchant"
S_Teacher = "Teacher"
S_Citizen = "Citizen"
S_Prostitute = "Prostitute"
S_Farmer = "Farmer"
S_Child = "Child"
S_Lunatic = "Lunatic"
S_Mercenary = "Mercenary"
S_Torpedo = "Torpedo"
S_Assassin = "Assassin"
S_Thug = "Thug"
S_Bandit = "Bandit"
S_Thief = "Thief"
S_Nerd = "Nerd"
S_Geek = "Geek"
S_Engineer = "Engineer"
S_Student = "Student"
S_Doctor = "Doctor"
S_Professor = "Professor"
S_Cultist = "Cultist"
S_Acolyte = "Acolyte"
S_High_Priest = "High Priest"

# S_Alligator="Alligator"
# S_Army_Ant_Swarm="Army Ant Swarm"
# S_Babboon="Babboon"
# S_Barracuda="Barracuda"
# S_Bat="Bat"
# S_Bear="Bear"
# S_Boar="Boar"
# S_Cat="Cat"
# S_Chicken="Chicken"
# S_Cow="Cow"
# S_Coyote="Coyote"
# S_Deer="Deer"
# S_Dolphin="Dolphin"
# S_Duck="Duck"
# S_Goat="Goat"
# S_Goose="Goose"
# S_Horse="Horse"
# S_Killer_Bee_Swarm="Killer Bee Swarm"
# S_Monkey="Monkey"
# S_Moose="Moose"
# S_Orca="Orca"
# S_Panther="Panther"
# S_Pig="Pig"
# S_Piglet="Piglet"
# S_Puma="Puma"
# S_Python="Python"
S_Rabbit = "Rabbit"
S_Rat = "Rat"
# S_Rattlesnake="Rattlesnake"
# S_Raven="Raven"
# S_Sea_Lion="Sea Lion"
# S_Shark="Shark"
# S_Vulture="Vulture"
# S_Wildcat="Wildcat"
# S_Wolf="Wolf"

# S_Angel="Angel"
S_Jumping_Arantula = "Jumping Arantula"
# S_Spitting_Arantula="Spitting Arantula"
# S_Trapdoor_Arantula="Trapdoor Arantula"
S_Harvestman = "Harvestman"
# S_Artillery_Bug="Artillery Bug"
# S_Basilisk="Basilisk"
# S_Billipede="Billipede"
# S_Black_Widowmaker="Black Widowmaker"
S_Zombie = "Zombie"
S_Bloody_Bones = "Bloody Bones"
S_Baron = "Baron"
# S_Rat_Chimera="Rat Chimera"
# S_Vulture_Mutant="Vulture Mutant"
# S_Cockroach_Hybrid="Cockroach Hybrid"
# S_Demon="Demon"
# S_Dero="Dero"
# S_Devil="Devil"
# S_Devilfly="Devilfly"
# S_Digger="Digger"
# S_Dogboy="Dogboy"
# S_Smog_Elemental="Smog Elemental"
# S_Plutonium_Elemental="Plutonium Elemental"
# S_Iodine_Elemental="Iodine Elemental"
# S_Pixie="Pixie"
# S_Elf="Elf"
# S_Nymph="Nymph"
# S_Midget_Freak="Midget Freak"
# S_Deviant_Freak="Deviant Freak"
# S_Giant_Freak="Giant Freak"
# S_Gargoyle="Gargoyle"
# S_Globbo="Globbo"
# S_Gobbler="Gobbler"
# S_Hangman="Hangman"
# S_Hippogriff="Hippogriff"
# S_Hut_Crab="Hut Crab"
# S_Honeytongue="Honeytongue"
# S_Myrmidon="Myrmidon"
S_Phantom = "Phantom"
S_Ghost = "Ghost"
S_Spectre = "Spectre"
S_Jackalope = "Jackalope"
# S_Manticore="Manticore"
# S_Meatgrinder_Slug="Meatgrinder Slug"
# S_Mermaid="Mermaid"
# S_Hag="Hag"
# S_Ogre="Ogre"
# S_Ghoul="Ghoul"
# S_Wendigo="Wendigo"
# S_Supermaggot="Supermaggot"
# S_Sword_Heron="Sword Heron"
# S_Flying_Vampire="Flying Vampire"
# S_Hopping_Vampire="Hopping Vampire"
# S_Swimming_Vampire="Swimming Vampire"
# S_Yardworm="Yardworm"
S_Summoned = "Summoned"

FRIENDS = {}

FRIENDS["humans"] = {
    S_Boss: Global.F_Love,
    S_Merchant: Global.F_Love,
    S_Teacher: Global.F_Love,
    S_Citizen: Global.F_Friendly,
    S_Farmer: Global.F_Friendly,
    S_Child: Global.F_Love,
    S_Soldier: Global.F_Love,
    S_Prostitute: Global.F_Love,
    S_Mercenary: Global.F_Neutral,
    S_Torpedo: Global.F_Neutral,
    S_Assassin: Global.F_Neutral,
    S_Thug: Global.F_Neutral,
    S_Bandit: Global.F_Neutral,
    S_Thief: Global.F_Neutral,
    S_Nerd: Global.F_Friendly,
    S_Geek: Global.F_Friendly,
    S_Engineer: Global.F_Friendly,
    S_Student: Global.F_Friendly,
    S_Doctor: Global.F_Friendly,
    S_Professor: Global.F_Friendly,
    S_Rat: Global.F_Neutral,
}

FRIENDS["adventurers"] = util.dictAdd(
    FRIENDS["humans"],
    {
        S_Adventurer: Global.F_Tolerant,
    },
)

FRIENDS["thieves"] = {
    S_Thug: Global.F_Tolerant,
    S_Bandit: Global.F_Tolerant,
    S_Thief: Global.F_Tolerant,
    S_Soldier: Global.F_Neutral,
}

FRIENDS["assassins"] = {
    S_Mercenary: Global.F_Tolerant,
    S_Torpedo: Global.F_Tolerant,
    S_Assassin: Global.F_Tolerant,
    S_Soldier: Global.F_Neutral,
    S_Boss: Global.F_Neutral,
}

FRIENDS["minions"] = {
    S_Lunatic: Global.F_Love,
    S_Cultist: Global.F_Love,
    S_Acolyte: Global.F_Love,
    S_High_Priest: Global.F_Love,
    S_Zombie: Global.F_Love,
    S_Bloody_Bones: Global.F_Love,
    S_Baron: Global.F_Love,
    S_Rat: Global.F_Neutral,
}

FRIENDS["bunnies"] = {
    S_Rabbit: Global.F_Love,
    S_Jackalope: Global.F_Love,
}

FRIENDS["spiders"] = {
    S_Harvestman: Global.F_Love,
    S_Jumping_Arantula: Global.F_Love,
    S_Rat: Global.F_Neutral,
    S_Phantom: Global.F_Neutral,
    S_Ghost: Global.F_Neutral,
    S_Spectre: Global.F_Neutral,
}

FRIENDS["phantoms"] = {
    S_Phantom: Global.F_Love,
    S_Ghost: Global.F_Love,
    S_Spectre: Global.F_Love,
    S_Harvestman: Global.F_Neutral,
    S_Jumping_Arantula: Global.F_Neutral,
    S_Rat: Global.F_Neutral,
}

BadFood = Script.Script(
    (Script.T, Script.STAT, Global.Wounds, "1 3 -1"),
    (Script.T, Script.STAT, Global.Fatigue, "1 3 -1"),
    (Script.T, Script.STAT, Global.Madness, "2 3"),
)

SPECIES_DATA = {
    S_Adventurer: {
        "named": NAMED_FULL,
        "friendSpecies": "adventurers",
        "food": Cannibalism,
    },
    S_Boss: {
        "sprite": "boss",
        "named": NAMED_TITLE,
        "prof": Global.P_Jack,
        "level": 4,
        "stat": ("1 10 10", "1 10 10", "1 10 10", "1 10 10"),
        "brain": Global.B_Random,
        "speech": (
            ("Aren't you supposed be at work?", ("Yes", "No"), (1, 3)),
            "Then get to it, man!  We don't have all day!",
            -1,
            "You shiftless bum!",
            None,
        ),
        "cash": "2 10 0 5",
        "friendSpecies": "adventurers",
        "desc": """Bosses are the leaders of the human communities, mostly
former organized crime leaders.""",
        "equip": (
            Shop.ITEM_replica_katana,
            Shop.ITEM_44_magnum,
            Shop.ITEM_44_ammo,
            Shop.ITEM_gold_ring,
        ),
        "food": Cannibalism,
    },
    S_Merchant: {
        "sprite": "merchant",
        "named": NAMED_TITLE,
        "brain": Global.B_Still,
        "prof": Global.P_Killer,
        "level": 10,
        "stat": ("2 10 0", "2 10 0", "2 8 4", "1 10 10"),
        "cash": "2 10 0 20",
        "friendSpecies": "adventurers",
        "desc": """Merchants buy and sell various goods; those who survived the
collapse without being robbed and killed are not to be underestimated.""",
        "equip": (
            Shop.ITEM_chainsaw,
            Shop.ITEM_44_magnum,
            Shop.ITEM_44_ammo,
            Shop.ITEM_flak_vest,
            Shop.ITEM_riot_shield,
        ),
        "food": Cannibalism,
    },
    S_Teacher: {
        "sprite": "boss",
        "named": NAMED_TITLE,
        "brain": Global.B_Still,
        "prof": Global.P_Killer,
        "level": 10,
        "stat": ("2 10 0", "2 10 0", "2 8 4", "2 10 0"),
        "cash": "2 10 0 20",
        "friendSpecies": "adventurers",
        "desc": """Teachers face a world almost as harsh as the LA school system.See _The Substitute_.""",
        "equip": (
            Shop.ITEM_switchblade,
            Shop.ITEM_10_gauge_double_barrel_shotgun,
            Shop.ITEM_10_gauge_ammo,
            Shop.ITEM_hard_case_armor,
            Shop.ITEM_ceramic_helmet,
            Shop.ITEM_riot_shield,
        ),
        "food": Cannibalism,
    },
    S_Citizen: {
        "sprite": "human",
        "named": NAMED_TITLE,
        "brain": Global.B_Random,
        "speech": (
            """Life is hard,
And then you die,
And then they throw dirt in your face.\n
Just be glad it happens in that order.""",
        ),
        "cash": "1 10 0 3",
        "friendSpecies": "adventurers",
        "desc": "A common citizen.",
        "food": Cannibalism,
    },
    S_Farmer: {
        "sprite": "human",
        "named": NAMED_TITLE,
        "prof": Global.P_Jack,
        "level": 3,
        "brain": Global.B_Random,
        "speech": ("Ayup.",),
        "cash": "1 10",
        "friendSpecies": "adventurers",
        "desc": "A field laborer.",
        "food": Cannibalism,
    },
    S_Child: {
        "sprite": "human",
        "named": NAMED_A,
        "prof": Global.P_Jack,
        "stat": ("1 10", "1 10", "1 10", "1 10"),
        "brain": Global.B_Coward,
        "speech": ("Wanna play tag?",),
        "cash": "1 3 -1",
        "friendSpecies": "adventurers",
        "desc": "A future citizen.",
        "food": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "-1 3"),
            (Script.T, Script.STAT, Global.Fatigue, "-1 3"),
            (Script.T, Script.STAT, Global.Madness, "2 3"),
        ),
    },
    S_Prostitute: {
        "sprite": "human",
        "named": NAMED_TITLE,
        "prof": Global.P_Sneak,
        "stat": ("2 10", "2 10", "2 10", "1 10 10"),
        "brain": Global.B_Random,
        "speech": ("See anything you like?",),
        "cash": "0 0 50",
        "friendSpecies": "adventurers",
        "desc": "A common streetwalker.",
        "equip": (Shop.ITEM_switchblade, Shop.ITEM_leather_jacket),
        "food": Cannibalism,
    },
    S_Soldier: {
        "sprite": "soldier",
        "named": NAMED_TITLE,
        "prof": Global.P_Killer,
        "stat": ("1 10 10", "2 10", "2 10", "2 10"),
        "level": 3,
        "brain": Global.B_Hunter,
        "speech": ("""Nothing to see here.  Move along.""",),
        "cash": "1 10 0 5",
        "friendSpecies": "adventurers",
        "desc": "Soldiers work for the bosses, maintaining order in the towns.",
        "equip": (
            Shop.ITEM_machete,
            Shop.ITEM_38_revolver,
            Shop.ITEM_38_ammo,
            Shop.ITEM_riot_vest,
            Shop.ITEM_riot_shield,
            Shop.ITEM_mirrorshades,
            Shop.ITEM_flashlight,
        ),
        "food": Cannibalism,
    },
    S_Lunatic: {
        "sprite": "human",
        "named": NAMED_EPITHET,
        "prof": Global.P_Killer,
        "level": 2,
        "brain": Global.B_Hunter,
        "friendSpecies": "minions",
        "speech": (
            """Hahahameathahahahahahahahahahahahahaha
ahahahahahameathahahahahahahahahahahah
hahahahahahahahameathahahahahahahahaha
ahahahahahahahahahahameathahahahahahah
hahahahahahahahahahahahahameathahahaha""",
        ),
        "cash": "1 14 -5",
        "desc": """The collapse of civilization snapped the fragile grasp on
sanity of many people.  Exiled from the towns, they wander the wilderness
looking for victims.  Many end up in the service of Mogth.""",
        "equip": (Shop.ITEM_machete,),
        "food": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "-2 2 3"),
            (Script.T, Script.STAT, Global.Fatigue, "-2 2 3"),
            (Script.T, Script.STAT, Global.Madness, "2 3"),
        ),
    },
    S_Mercenary: {
        "sprite": "soldier",
        "named": NAMED_EPITHET,
        "prof": Global.P_Killer,
        "level": 3,
        "stat": ("1 10 10", "2 10", "2 10", "2 10"),
        "brain": Global.B_Hunter,
        "friendSpecies": "assassins",
        "speech": ("No questions asked.",),
        "cash": "1 10 0 5",
        "desc": "A simple hired killer.",
        "equip": (
            Shop.ITEM_machete,
            Shop.ITEM_9mm_auto_pistol,
            Shop.ITEM_9mm_ammo,
            Shop.ITEM_kevlar_jacket,
        ),
        "food": Cannibalism,
    },
    S_Torpedo: {
        "sprite": "soldier",
        "named": NAMED_EPITHET,
        "prof": Global.P_Killer,
        "level": 5,
        "stat": ("1 10 10", "2 10", "2 10", "2 10"),
        "brain": Global.B_Hunter,
        "friendSpecies": "assassins",
        "speech": ("Who did you need killed?",),
        "cash": "2 10 0 5",
        "desc": "A professional cleaner.",
        "equip": (
            Shop.ITEM_replica_katana,
            Shop.ITEM_Uzi_9mm_submachinegun,
            Shop.ITEM_Uzi_ammo,
            Shop.ITEM_kevlar_duster,
        ),
        "food": Cannibalism,
    },
    S_Assassin: {
        "sprite": "soldier",
        "named": NAMED_EPITHET,
        "prof": Global.P_Killer,
        "level": 10,
        "stat": ("1 10 10", "2 10", "2 10", "2 10"),
        "brain": Global.B_Hunter,
        "friendSpecies": "assassins",
        "speech": ("...",),
        "cash": "2 10 0 10",
        "desc": "Death on two legs.",
        "equip": (
            Shop.ITEM_replica_claymore,
            Shop.ITEM_30_30_hunting_rifle,
            Shop.ITEM_30_30_ammo,
            Shop.ITEM_kevlar_duster,
            Shop.ITEM_flak_helmet,
        ),
        "food": Cannibalism,
    },
    S_Thug: {
        "sprite": "soldier",
        "named": NAMED_EPITHET,
        "prof": Global.P_Sneak,
        "level": 3,
        "stat": ("2 10", "1 10 10", "2 10", "2 10"),
        "brain": Global.B_Random,
        "friendSpecies": "thieves",
        "speech": ("Hand over your money and you won't get hurt.",),
        "cash": "2 6 0 3",
        "desc": "Criminals are a cowardly, superstitious lot.",
        "equip": (
            Shop.ITEM_switchblade,
            Shop.ITEM_5mm_derringer,
            Shop.ITEM_5mm_ammo,
            Shop.ITEM_5mm_ammo,
            Shop.ITEM_leather_jacket,
        ),
        "food": Cannibalism,
    },
    S_Bandit: {
        "sprite": "soldier",
        "named": NAMED_EPITHET,
        "prof": Global.P_Sneak,
        "level": 5,
        "stat": ("2 10", "1 10 10", "2 10", "2 10"),
        "brain": Global.B_Random,
        "friendSpecies": "thieves",
        "speech": ("Your money or your life.",),
        "cash": "2 8 0 3",
        "desc": "Criminals are a cowardly, superstitious lot.",
        "equip": (
            Shop.ITEM_switchblade,
            Shop.ITEM_38_revolver,
            Shop.ITEM_38_ammo,
            Shop.ITEM_leather_duster,
        ),
        "food": Cannibalism,
    },
    S_Thief: {
        "sprite": "soldier",
        "named": NAMED_EPITHET,
        "prof": Global.P_Sneak,
        "level": 10,
        "stat": ("2 10", "1 10 10", "2 10", "2 10"),
        "brain": Global.B_Random,
        "friendSpecies": "thieves",
        "speech": ("This is not your lucky day.",),
        "cash": "2 10 0 3",
        "desc": "Criminals are a cowardly, superstitious lot.",
        "equip": (
            Shop.ITEM_machete,
            Shop.ITEM_45_auto_pistol,
            Shop.ITEM_45_ammo,
            Shop.ITEM_leather_duster,
        ),
        "food": Cannibalism,
    },
    S_Nerd: {
        "sprite": "boss",
        "named": NAMED_A,
        "prof": Global.P_Techie,
        "level": 3,
        "stat": ("2 10", "2 10", "1 10 10", "2 10"),
        "brain": Global.B_Random,
        "friendSpecies": "adventurers",
        "speech": ("Man, I miss the Internet.",),
        "cash": "2 10 0 3",
        "desc": "Better living through technology.",
        "equip": (
            Shop.ITEM_10mm_auto_pistol,
            Shop.ITEM_10mm_ammo,
            Shop.ITEM_riot_vest,
            Shop.ITEM_hard_hat,
            Shop.ITEM_digital_watch,
            Shop.ITEM_flashlight,
        ),
        "food": Cannibalism,
    },
    S_Geek: {
        "sprite": "boss",
        "named": NAMED_A,
        "prof": Global.P_Techie,
        "level": 5,
        "stat": ("2 10", "2 10", "1 10 10", "2 10"),
        "brain": Global.B_Random,
        "friendSpecies": "adventurers",
        "speech": ("Now if only I could solve the power problem...",),
        "cash": "2 10 0 5",
        "desc": "Better living through technology.",
        "equip": (
            Shop.ITEM_5_56mm_assault_rifle,
            Shop.ITEM_5_56mm_ammo,
            Shop.ITEM_riot_vest,
            Shop.ITEM_motorcycle_helmet,
            Shop.ITEM_digital_watch,
            Shop.ITEM_flashlight,
        ),
        "food": Cannibalism,
    },
    S_Engineer: {
        "sprite": "boss",
        "named": NAMED_EPITHET,
        "prof": Global.P_Techie,
        "level": 10,
        "stat": ("2 10", "2 10", "1 10 10", "2 10"),
        "brain": Global.B_Random,
        "friendSpecies": "adventurers",
        "speech": ("What was your userid? <clickety-clack>",),
        "cash": "4 10 0 5",
        "desc": "Better living through technology.",
        "equip": (
            Shop.ITEM_7_62mm_assault_rifle,
            Shop.ITEM_7_62mm_ammo,
            Shop.ITEM_riot_vest,
            Shop.ITEM_riot_gear_helmet,
            Shop.ITEM_digital_watch,
            Shop.ITEM_flashlight,
        ),
        "food": Cannibalism,
    },
    S_Student: {
        "sprite": "boss",
        "named": NAMED_EPITHET,
        "prof": Global.P_Arcanist,
        "level": 3,
        "stat": ("2 10", "2 10", "1 10 10", "1 10 10"),
        "brain": Global.B_Random,
        "friendSpecies": "adventurers",
        "speech": ("The Sumerians knew more than most think...",),
        "cash": "1 10 0 3",
        "desc": "A mere student of the occult.",
        "food": Cannibalism,
    },
    S_Doctor: {
        "sprite": "boss",
        "named": NAMED_TITLE,
        "prof": Global.P_Arcanist,
        "level": 5,
        "stat": ("2 10", "2 10", "1 10 10", "1 10 10"),
        "brain": Global.B_Random,
        "friendSpecies": "adventurers",
        "speech": (
            """The universe is not only stranger than we think,
it is stranger than we CAN think.""",
        ),
        "cash": "1 10 0 3",
        "desc": "A full practitioner of mystic arts.",
        "food": Cannibalism,
    },
    S_Professor: {
        "sprite": "boss",
        "named": NAMED_TITLE,
        "prof": Global.P_Arcanist,
        "level": 10,
        "stat": ("2 10", "2 10", "1 10 10", "1 10 10"),
        "brain": Global.B_Random,
        "friendSpecies": "adventurers",
        "speech": ("I think, therefore I am.",),
        "cash": "1 10 0 3",
        "desc": "A master of the arcane.",
        "food": Cannibalism,
    },
    S_Cultist: {
        "sprite": "cultist",
        "named": NAMED_A,
        "prof": Global.P_Arcanist,
        "level": 5,
        "stat": ("2 10", "2 10", "1 10 10", "1 10 10"),
        "brain": Global.B_Hunter,
        "friendSpecies": "minions",
        "speech": "mogth",
        "cash": "1 10",
        "equip": (
            Shop.ITEM_switchblade,
            Shop.ITEM_5mm_derringer,
            Shop.ITEM_5mm_ammo,
            Shop.ITEM_leather_duster,
        ),
        "desc": "A brainwashed Mogth cult-worshipper.",
        "food": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "-2 2 3"),
            (Script.T, Script.STAT, Global.Fatigue, "-2 2 3"),
            (Script.T, Script.STAT, Global.Madness, "2 3"),
        ),
    },
    S_Acolyte: {
        "sprite": "cultist",
        "named": NAMED_TITLE,
        "prof": Global.P_Arcanist,
        "level": 10,
        "stat": ("1 10 10", "1 10 10", "1 10 10", "1 10 10"),
        "brain": Global.B_Hunter,
        "friendSpecies": "minions",
        "speech": "mogth",
        "cash": "3 10 0 3",
        "equip": (
            Shop.ITEM_replica_katana,
            Shop.ITEM_38_revolver,
            Shop.ITEM_38_ammo,
            Shop.ITEM_kevlar_duster,
        ),
        "desc": "An advanced Mogth cultist.",
        "food": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "-2 2 3"),
            (Script.T, Script.STAT, Global.Fatigue, "-2 2 3"),
            (Script.T, Script.STAT, Global.Madness, "2 3"),
        ),
    },
    S_High_Priest: {
        "sprite": "cultist",
        "named": NAMED_TITLE,
        "prof": Global.P_Arcanist,
        "level": 15,
        "stat": ("1 10 20", "1 10 20", "1 10 20", "1 10 20"),
        "brain": Global.B_Hunter,
        "friendSpecies": "minions",
        "speech": "mogth",
        "cash": "5 10 0 3",
        "equip": (
            Shop.ITEM_replica_claymore,
            Shop.ITEM_10mm_auto_pistol,
            Shop.ITEM_10mm_ammo,
            Shop.ITEM_kevlar_duster,
        ),
        "desc": "The highest of Mogth's human minions.",
        "food": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "-2 2 3"),
            (Script.T, Script.STAT, Global.Fatigue, "-2 2 3"),
            (Script.T, Script.STAT, Global.Madness, "2 3"),
        ),
    },
    S_Rabbit: {
        "prof": Global.P_Sneak,
        "stat": ("1 4 0", "1 10 10", "1 5 0", "1 5 0"),
        "brain": Global.B_Coward,
        "size": Global.SIZE_Small,
        "desc": "Small furry food sources.",
        "friendSpecies": "bunnies",
        "food": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "-2 2 2"),
            (Script.T, Script.STAT, Global.Fatigue, "-2 2 2"),
        ),
    },
    S_Jackalope: {
        "sprite": "rabbit",
        "prof": Global.P_Killer,
        "level": 1,
        "stat": ("1 4 6", "1 10 10", "1 5 0", "1 5 0"),
        "brain": Global.B_Hunter,
        "size": Global.SIZE_Small,
        "unarmed": Script.Script(
            (Script.T, Script.DMG, Global.Wounds, "1 6"),
        ),
        "friendSpecies": "bunnies",
        "desc": "A cute little rabbit with razor-sharp antlers.",
        "food": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "-2 2 3"),
            (Script.T, Script.STAT, Global.Fatigue, "-2 2 3"),
        ),
    },
    S_Rat: {
        "prof": Global.P_Sneak,
        "stat": ("1 5 0", "1 6 6", "1 5 0", "1 5 0"),
        "brain": Global.B_Hunter,
        "speech": ("Eeek!",),
        "size": Global.SIZE_Small,
        "friendSpecies": "rats",
        "desc": "Small furry plague-bearers.",
        "food": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "-2 2 2"),
            (Script.T, Script.STAT, Global.Fatigue, "-2 2 2"),
        ),
    },
    #    S_Angel:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":5,
    #        "brain":Global.B_Hunter,
    #        "defense":2,
    #        "desc":"A human/crane hybrid - beautiful but deadly.",
    #    },
    S_Jumping_Arantula: {
        "sprite": "spider",
        "prof": Global.P_Killer,
        "level": 3,
        "stat": ("2 8 4", "1 6 20", "1 5 0", "1 10 10"),
        "brain": Global.B_Hunter,
        "friendSpecies": "spiders",
        "size": Global.SIZE_Large,
        "defense": 3,
        "unarmed": Script.Script(
            (Script.T, Script.DMG, Global.Wounds, "1 6"),
        ),
        "desc": "4m-tall tarantula",
        "food": BadFood,
    },
    #    S_Spitting_Arantula:{
    #        "sprite":"spider",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "stat":("2 8 4", "1 6 20", "1 5 0", "1 10 10"),
    #        "brain":Global.B_Hunter,
    #        "size":Global.SIZE_Large,
    #        "defense":1,
    #        "desc":"4m-tall tarantula with spitting venom",
    #        "food":BadFood,
    #    },
    #
    #    S_Trapdoor_Arantula:{
    #        "sprite":"spider",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "stat":("2 8 4", "1 6 20", "1 5 0", "1 10 10"),
    #        "brain":Global.B_Hunter,
    #        "size":Global.SIZE_Large,
    #        "defense":1,
    #        "desc":"4m-tall tarantula that hides in the ground",
    #        "food":BadFood,
    #    },
    S_Harvestman: {
        "sprite": "spider",
        "prof": Global.P_Killer,
        "level": 6,
        "stat": ("2 8 0", "1 10 5", "1 5 0", "1 10 10"),
        "brain": Global.B_Hunter,
        "friendSpecies": "spiders",
        "size": Global.SIZE_Large,
        "defense": 5,
        "unarmed": Script.Script(
            (Script.T, Script.DMG, Global.Wounds, "1 12 2"),
        ),
        "desc": "Giant 'Daddy Long-Legs', with *BIG* fangs.",
        "food": BadFood,
    },
    #    S_Artillery_Bug:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Basilisk:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Billipede:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Black_Widowmaker:{
    #        "sprite":"spider",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    S_Zombie: {
        "undead": 1,
        "prof": Global.P_Killer,
        "stat": ("2 10 0", "2 5", "1 6", "4 4 4"),
        "brain": Global.B_Hunter,
        "unarmed": Script.Script(
            (Script.T, Script.DMG, Global.Wounds, "1 4"),
        ),
        "speech": ("BRAINS!",),
        "friendSpecies": "minions",
        "desc": "A shambling reanimated corpse, driven solely by hunger.",
        "food": BadFood,
    },
    S_Bloody_Bones: {
        "undead": 1,
        "prof": Global.P_Killer,
        "level": 2,
        "stat": ("2 10 4", "1 4 4", "2 5 0", "4 4 4"),
        "brain": Global.B_Hunter,
        "defense": 2,
        "unarmed": Script.Script(
            (Script.T, Script.DMG, Global.Wounds, "1 6"),
        ),
        "friendSpecies": "minions",
        "desc": """The dead no longer rest easy, and rise from the grave, gore
still clinging to their bones.""",
        "food": BadFood,
    },
    S_Baron: {
        "undead": 1,
        "named": NAMED_TITLE,
        "prof": Global.P_Killer,
        "level": 20,
        "stat": ("4 10 0", "1 10 4", "2 10", "4 4 4"),
        "brain": Global.B_Hunter,
        "desc": """An undead warrior, armed with a chainsaw and a shotgun.""",
        "friendSpecies": "minions",
        "equip": (
            Shop.ITEM_chainsaw,
            Shop.ITEM_10_gauge_double_barrel_shotgun,
            Shop.ITEM_chainmail,
            Shop.ITEM_metal_shield,
            Shop.ITEM_metal_helmet,
        ),
        "food": BadFood,
    },
    #    S_Rat_Chimera:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Vulture_Mutant:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Cockroach_Hybrid:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Demon:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Dero:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Devil:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Devilfly:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Digger:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Dogboy:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Smog_Elemental:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Plutonium_Elemental:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Iodine_Elemental:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Pixie:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Elf:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Nymph:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Midget_Freak:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Deviant_Freak:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Giant_Freak:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Gargoyle:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Globbo:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Gobbler:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Hangman:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Hippogriff:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Hut_Crab:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Honeytongue:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Myrmidon:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    S_Phantom: {
        "undead": 1,
        "sprite": "phantom",
        "prof": Global.P_Killer,
        "stat": ("1 10 0", "1 10 5", "2 10 0", "2 10 0"),
        "level": 3,
        "brain": Global.B_Random,
        "friendSpecies": "phantoms",
        "defense": 6,
        "unarmed": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "1 2"),
            (Script.T, Script.STAT, Global.Fatigue, "1 2"),
        ),
        "desc": "Luminous semi-substantial life-hunters",
        "food": None,
    },
    S_Ghost: {
        "undead": 1,
        "sprite": "phantom",
        "prof": Global.P_Killer,
        "stat": ("1 10 5", "1 10 10", "2 10 0", "2 10 0"),
        "level": 8,
        "brain": Global.B_Hunter,
        "friendSpecies": "phantoms",
        "defense": 9,
        "unarmed": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "1 4"),
            (Script.T, Script.STAT, Global.Fatigue, "1 4"),
        ),
        "desc": "Luminous semi-substantial life-hunters",
        "food": None,
    },
    S_Spectre: {
        "undead": 1,
        "sprite": "phantom",
        "prof": Global.P_Killer,
        "stat": ("1 10 10", "1 5 15", "2 10 0", "2 10 0"),
        "level": 13,
        "brain": Global.B_Hunter,
        "friendSpecies": "phantoms",
        "defense": 12,
        "unarmed": Script.Script(
            (Script.T, Script.STAT, Global.Wounds, "1 6"),
            (Script.T, Script.STAT, Global.Fatigue, "1 6"),
        ),
        "desc": "Luminous semi-substantial life-hunters",
        "food": None,
    },
    #    S_Manticore:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Meatgrinder_Slug:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Mermaid:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Hag:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Ogre:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Ghoul:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Wendigo:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Supermaggot:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Sword_Heron:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Flying_Vampire:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Hopping_Vampire:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Swimming_Vampire:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    #
    #    S_Yardworm:{
    #        "sprite":"bloody_bones",
    #        "prof":Global.P_Killer,
    #        "level":1,
    #        "brain":Global.B_Hunter,
    #        "defense":1,
    #        "desc":"x",
    #        "food":BadFood,
    #    },
    S_Summoned: {},
}
NSPECIES = len(SPECIES_DATA)


def ratFriends():
    us = {}
    for group in list(FRIENDS.values()):
        if group.get(S_Rat, -1) < 0:
            continue
        for who in list(group.keys()):
            us[who] = Global.F_Neutral
    us[S_Rat] = Global.F_Love
    us[S_Adventurer] = Global.F_Hostile
    FRIENDS["rats"] = us


ratFriends()
