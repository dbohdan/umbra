from . import Item


class Loot(Item.Item):
    # oneshot=Boolean
    def __init__(self, name, sprite, shoptype=-1):
        Item.Item.__init__(self, name, sprite, shoptype)
        self.oneshot = 0
