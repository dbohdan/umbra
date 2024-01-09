from . import Equip, Global, util


class Defense(Equip.Equip):
    # defense=Int
    def __init__(self, name, sprite, type, defense):
        Equip.Equip.__init__(self, name, sprite, type, Global.SHOP_Armor)
        util.assertInt(defense)
        self.defense = defense
