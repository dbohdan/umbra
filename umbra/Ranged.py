from . import Equip, Global


class Ranged(Equip.Equip):
    # range=Int
    # ammoCapacity=Int
    # ammo=Int
    # ammoUse=Int
    def __init__(self, name, sprite, range, ammo, ammoUse):
        Equip.Equip.__init__(self, name, sprite, Equip.T_Ranged, Global.SHOP_Gun)
        self.range = range
        self.ammo = ammo
        self.ammoCapacity = ammo
        self.ammoUse = ammoUse

    def __str__(self):
        return "%s, containing %d rounds" % (self.name, self.ammo)
