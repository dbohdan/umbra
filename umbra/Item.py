from . import Thing
import os

NOT_FOR_SALE=0
HALF_PRICE=0.5
FULL_PRICE=1

class Item(Thing.Thing):
    #__cost=Int
    #resale=Int
    #effect=String
    #shoptype=Int  # Global.SHOP_*
    def __init__(self, name, sprite, shoptype):
        Thing.Thing.__init__(self, name, os.path.join("item", sprite) )
        self.__cost=0
        self.resale=HALF_PRICE
        self.effect=None
        self.shoptype=shoptype

    def __str__(self):
        return self.name

    def cost(self):
        return self.__cost

    def resaleValue(self):
        return int(self.resale * self.cost)

    def setCost(self, amount):
        self.__cost = amount

