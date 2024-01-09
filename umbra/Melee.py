from . import Equip, Global


class Melee(Equip.Equip):
    def __init__(self, name, sprite):
        Equip.Equip.__init__(self, name, sprite, Equip.T_Melee, Global.SHOP_Cutlery)
