from . import Global, Item, Loot, util


class Ammo(Loot.Loot):
    # ammoType=String
    # ammo=Int
    def __init__(self, name, sprite, ammoType, ammo):
        Loot.Loot.__init__(self, name, sprite, Global.SHOP_Gun)
        self.ammoType = ammoType
        self.ammo = ammo
        self.resale = Item.FULL_PRICE

    def __str__(self):
        return "%s, containing %d rounds, worth $%d" % (
            self.name,
            self.ammo,
            self.cost(),
        )

    def fitsIn(self, gun):
        return util.startsWith(gun.name, self.ammoType)
