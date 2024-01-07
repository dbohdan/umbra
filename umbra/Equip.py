from . import Thing, Item
from . import Global, util

POS_Armor=0
POS_Headgear=1
POS_Shield=2
POS_Melee=3
POS_Ranged=4
POS_LeftRing=5
POS_RightRing=6
POS_Accessory1=7
POS_Accessory2=8
NPOS=9
POS_NAMES=("Armor",
    "Headgear",
    "Shield",
    "Melee Weapon",
    "Ranged Weapon",
    "Left Ring",
    "Right Ring",
    "Accessory 1",
    "Accessory 2")

T_Armor=0
T_Headgear=1
T_Shield=2
T_Melee=3
T_Ranged=4
T_Ring=5
T_Accessory=6
NTYPES=7
TYPES={
    T_Armor:("Armor", "100000000"),
    T_Headgear:("Headgear", "010000000"),
    T_Shield:("Shield", "001000000"),
    T_Melee:("Melee", "000100000"),
    T_Ranged:("Ranged", "000010000"),
    T_Ring:("Ring", "000001100"),
    T_Accessory:("Accessory", "000000011"),
}

class Equip(Item.Item):
    #__type=Int
    #cursed=Boolean
    #readyEffect=Script
    #unreadyEffect=Script
    #range=Int
    #ammo=Int
    #ammoUse=Int
    def __init__(self, name, sprite, type, shoptype):
        """Only instantiate Equip for T_Ring and T_Accessory; use Melee,
        Ranged, or Defense for other types."""
        Item.Item.__init__(self, name, sprite, shoptype)
        self.__type=type
        self.readyEffect=None
        self.unreadyEffect=None
        self.cursed=0
        self.range=1
        self.ammo=-1
        self.ammoUse=-1

    def getType(self):
        return self.__type

    def getTypeName(self):
        return TYPES[self.__type][0]

    def isLegalpos(self, p):
        util.assertInt(p, 0, NPOS-1)
        legalpos = TYPES[self.__type][1]
        return legalpos[p] =="1"

    def setType(self, type):
        util.assertInt(type, 0, NTYPES-1)
        self.__type=type

