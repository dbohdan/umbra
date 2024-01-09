import copy

from . import Ammo, Entity, Global, Item, Ranged, Shop, util


class Merchant(Entity.Entity):
    # shoptype=Int # Global.SHOP_*
    # products=[] # := (item, quantity, maxQuantity)
    # respawnTurns=1440
    # lastRespawn=Int
    def __init__(self, *args, **opts):
        Entity.Entity.__init__(self, *args, **opts)
        self.products = []
        if Global.FASTDAY:
            self.respawnTurns = 48
        else:
            self.respawnTurns = 1440
        self.lastRespawn = util.d(1, 1440)

    def addProduct(self, item, quantity):
        assert isinstance(item, Item.Item), "%s is not an Item!" % item
        self.products.append([item, quantity, quantity])

    def getCostMod(self, who):
        whoPresence = who.stat[Global.Presence]
        myPresence = self.stat[Global.Presence]
        # double or halve the price for every 5 point difference
        costMod = (myPresence - whoPresence) / 5.0
        if costMod >= 0:
            costMod += 1.0
        elif costMod < 0:
            #            costMod = 1.0 / (1.0 - costMod)
            costMod = 1.0
        if Global.COMBAT_DEBUG:
            print(
                "%s.presence=%d, %s.presence=%d, costMod=%f"
                % (self.name, myPresence, who.name, whoPresence, costMod),
            )
        return costMod

    def handedItem(self, who, item):
        if Global.COMBAT_DEBUG:
            print(self)
        if not self.handedItemTest(who, item):
            return 0
        if item.resale == Item.NOT_FOR_SALE:
            who.message("%s is not interested." % self.name)
            return 0
        if item.shoptype >= 0 and item.shoptype != self.shoptype:
            who.message("%s is not interested." % self.name)
            return 0
        costMod = self.getCostMod(who)
        price = max(0, int(item.cost() * item.resale / costMod))
        if Global.COMBAT_DEBUG:
            print(
                "%s: cost=%d, resale=%f, costMod=%f, price=$%d"
                % (item.name, item.cost(), item.resale, costMod, price),
            )
        if price > self.cash:
            who.message("%s cannot afford it." % self.name)
            return 0
        yesno = Global.umbra.alert(
            "Sell %s" % item.name,
            "%s offers you $%d for %s.  Accept?" % (self.name, price, item.name),
            type=Global.ALERT_YESNO,
        )
        if not yesno:
            return 0
        who.message("%s gives you $%d for the %s." % (self.name, price, item.name))
        self.cash -= price
        who.cash += price
        # now combine it with any other duplicate items
        itemcost = item.cost()
        for i in range(len(self.products)):
            prod = self.products[i][0]
            if prod.name == item.name and prod.cost() == itemcost:
                self.products[i][1] += 1
                break
        else:
            self.addProduct(item, 1)
        return 1

    def nextTurn(self, turn, level):
        if Global.COMBAT_DEBUG:
            print(
                self.name,
                "lastRespawn",
                self.lastRespawn,
                "respawnTurns",
                self.respawnTurns,
            )
        rturns = turn - self.lastRespawn
        if rturns >= self.respawnTurns:
            # dividing rather than just modding, because you may reenter a
            # Sector days after leaving it.
            nrespawns = rturns // self.respawnTurns
            self.lastRespawn = turn
            for inv in self.products:
                for i in range(nrespawns):
                    inv[1] += util.d(1, inv[2])
                if inv[1] > inv[2]:
                    inv[1] = inv[2]
                self.cash += inv[0].cost()
        Entity.Entity.nextTurn(self, turn, level)

    def setShopType(self, shoptype):
        self.shoptype = shoptype
        shop = Shop.CATALOG[shoptype]
        costScale = util.d(1, 151) + 49
        for line in shop:
            quantity = util.diceString(line[2])
            if quantity < 0:
                continue
            item = copy.deepcopy(line[0])
            item.setCost(max(1, costScale * line[1] // 100))
            self.addProduct(item, quantity)
            self.cash += item.cost()
            if isinstance(item, Ranged.Ranged):
                ammoType = item.name.split()[0]
                ammo = Ammo.Ammo(
                    "%s ammo" % ammoType,
                    "ammo",
                    ammoType,
                    item.ammoCapacity,
                )
                ammo.setCost(max(1, item.cost() // 10))
                self.addProduct(ammo, quantity * util.d(2, 3) - 1)
                self.cash += ammo.cost()

    def trigger(self, who):
        u = Global.umbra
        if who.gender == Global.GEND_Male:
            banner = "How can I help you, sir?"
        else:
            banner = "How can I help you, ma'am?"
        banner = "%s\nYour cash: $%d" % (banner, who.cash)
        prompts = [
            "Cancel",
        ]
        indices = [
            -1,
        ]
        cantAfford = 0
        costMod = self.getCostMod(who)
        for i in range(len(self.products)):
            inv = self.products[i]
            item = inv[0]
            cost = max(1, int(costMod * item.cost()))
            if Global.COMBAT_DEBUG:
                print(
                    "%s: cost=%d, resale=%f, costMod=%f, price=$%d"
                    % (item.name, item.cost(), item.resale, costMod, cost),
                )
            quantity = inv[1]
            if quantity <= 0:
                continue
            itemname = item.name
            if len(itemname) > 25:
                itemname = itemname[:25]
            line = "$%5d %3d %s" % (cost, quantity, item.name)
            if who.cash < cost:
                if not cantAfford:
                    cantAfford = 1
                    banner = "%s\nYou cannot afford:" % banner
                banner = "%s\n%s" % (banner, line)
            else:
                prompts.append(line)
                indices.append(i)
        opt = u.menu(title="%s asks:" % self.name, banner=banner, prompts=prompts)
        if opt == 0:
            return 1
        opt = indices[opt]
        inv = self.products[opt]
        item = inv[0]
        cost = max(1, int(costMod * item.cost()))
        if inv[1] == 1:
            amount = 1
            pluralText = ""
            countText = "a"
            if who.countItems() >= Entity.MAXITEMS:
                who.message("You cannot carry any more items.")
                return 1
        else:
            amount = u.input(
                "%s asks:" % self.name,
                "How many %ss\ndo you want (0-%d)?" % (item.name, inv[1]),
            )
            try:
                amount = int(amount)
            except ValueError:
                who.message("That doesn't make any sense...")
                return 1
            if amount == 0:
                return 1
            if amount < 0 or amount > inv[1]:
                who.message("Hey, just what you see on the shelves!")
                return 1
            if amount == 1:
                pluralText = ""
            else:
                pluralText = "s"
            countText = str(amount)
            if who.countItems() + amount > Entity.MAXITEMS:
                who.message("You cannot carry that many more items.")
                return 1
            if who.cash < cost * amount:
                who.message("You cannot afford %d %s" % (amount, item.name))
                return 1
        who.cash -= cost * amount
        self.cash += cost * amount
        for i in range(amount):
            who.addItem(copy.deepcopy(item))
        inv[1] -= amount
        who.message(
            "You buy %s %s%s for $%d"
            % (countText, item.name, pluralText, cost * amount),
        )
        return 1
