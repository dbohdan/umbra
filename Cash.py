import Item, Loot

class Cash(Loot.Loot):
    def __init__(self, amount):
        Loot.Loot.__init__(self, "cash", "cash")
        self.setCost(amount)
        self.resale = Item.FULL_PRICE

    def __str__(self):
        return "%d silver dollars" % self.cost()

    def setCost(self, amount):
        self.name = "$%d cash" % amount
        Loot.Loot.setCost(self, amount)

