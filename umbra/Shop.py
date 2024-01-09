import copy

from . import Ammo, Defense, Equip, Global, Loot, Melee, Ranged, Script

# Global.SHOP_* := [ (item template, cost, quantityDice), ]
CATALOG = {}

# melee
ITEM_switchblade = "switchblade"
ITEM_machete = "machete"
ITEM_replica_katana = "replica katana"
ITEM_replica_claymore = "replica claymore"
ITEM_chainsaw = "chainsaw"

# ranged
ITEM_staple_gun = "staple gun"
ITEM_5mm_derringer = "5mm derringer"
ITEM_38_revolver = ".38 revolver"
ITEM_9mm_auto_pistol = "9mm auto pistol"
ITEM_45_auto_pistol = ".45 auto pistol"
ITEM_10mm_auto_pistol = "10mm auto pistol"
ITEM_44_magnum = ".44 magnum"
ITEM_Uzi_9mm_submachinegun = "Uzi 9mm submachinegun"
ITEM_20_gauge_shotgun = "20-gauge shotgun"
ITEM_12_gauge_shotgun = "12-gauge shotgun"
ITEM_10_gauge_double_barrel_shotgun = "10-gauge double-barrel shotgun"
ITEM_22_hunting_rifle = ".22 hunting rifle"
ITEM_30_30_hunting_rifle = ".30-30 hunting rifle"
ITEM_7_62mm_assault_rifle = "7.62mm assault rifle"
ITEM_5_56mm_assault_rifle = "5.56mm assault rifle"

# ammo
ITEM_staple_ammo = "staple ammo"
ITEM_5mm_ammo = "5mm ammo"
ITEM_38_ammo = ".38 ammo"
ITEM_9mm_ammo = "9mm ammo"
ITEM_45_ammo = ".45 ammo"
ITEM_10mm_ammo = "10mm ammo"
ITEM_44_ammo = ".44 ammo"
ITEM_Uzi_ammo = "Uzi ammo"
ITEM_20_gauge_ammo = "20-gauge ammo"
ITEM_12_gauge_ammo = "12-gauge ammo"
ITEM_10_gauge_ammo = "10-gauge ammo"
ITEM_22_ammo = ".22 ammo"
ITEM_30_30_ammo = ".30-30 ammo"
ITEM_7_62mm_ammo = "7.62mm ammo"
ITEM_5_56mm_ammo = "5.56mm ammo"

# armor
ITEM_leather_jacket = "leather jacket"
ITEM_leather_duster = "leather duster"
ITEM_kevlar_jacket = "kevlar jacket"
ITEM_kevlar_duster = "kevlar duster"
ITEM_chainmail = "chainmail"
ITEM_riot_vest = "riot vest"
ITEM_riot_armor = "riot armor"
ITEM_flak_vest = "flak vest"
ITEM_tactical_vest = "tactical vest"
ITEM_ceramic_armor = "ceramic armor"
ITEM_hard_case_armor = "hard case armor"

# headgear
ITEM_hard_hat = "hard hat"
ITEM_motorcycle_helmet = "motorcycle helmet"
ITEM_metal_helmet = "metal helmet"
ITEM_riot_gear_helmet = "riot gear helmet"
ITEM_flak_helmet = "flak helmet"
ITEM_ceramic_helmet = "ceramic helmet"

# shield
ITEM_garbage_can_lid = "garbage can lid"
ITEM_wood_shield = "wood shield"
ITEM_metal_shield = "metal shield"
ITEM_riot_shield = "riot shield"

# accessories
ITEM_gold_ring = "gold ring"
ITEM_digital_watch = "digital watch"
ITEM_mirrorshades = "mirrorshades"
ITEM_flashlight = "flashlight"

# loot
ITEM_can_of_food = "can of food"
ITEM_box_of_chocolates = "box of chocolates"


def addToShop(item, cost, quantityDice):
    shoptype = item.shoptype
    if shoptype in CATALOG:
        products = CATALOG[shoptype]
    else:
        products = []
        CATALOG[shoptype] = products
    item.setCost(cost)
    products.append((item, cost, quantityDice))

    if isinstance(item, Ranged.Ranged):
        ammoType = item.name.split()[0]
        ammo = Ammo.Ammo("%s ammo" % ammoType, "ammo", ammoType, item.ammoCapacity)
        ammo.setCost(cost // 10)
        dice = quantityDice.split()
        if len(dice) < 3:
            dice.append("0")
        if len(dice) < 4:
            dice.append("4")
        else:
            dice[3] = "4"
        products.append((ammo, cost // 10, quantityDice))


def getShopItem(itemname):
    for shoptype in range(Global.NSHOPS):
        for line in CATALOG[shoptype]:
            if line[0].name == itemname:
                return copy.deepcopy(line[0])
    return None


def fillShopTypes():
    item = Melee.Melee(ITEM_switchblade, "sword")
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 4"),
    )
    addToShop(item, 10, "1 6 1")

    item = Melee.Melee(ITEM_machete, "sword")
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 6"),
    )
    addToShop(item, 50, "1 3 -1")

    item = Melee.Melee(ITEM_replica_katana, "sword")
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 8"),
    )
    addToShop(item, 250, "1 3 -1")

    item = Melee.Melee(ITEM_replica_claymore, "sword")
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 10"),
    )
    addToShop(item, 500, "1 3 -1")

    item = Melee.Melee(ITEM_chainsaw, "sword")
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 6 6"),
    )
    addToShop(item, 1000, "1 3 -1")

    # ________________________________________
    item = Ranged.Ranged(ITEM_staple_gun, "gun", 3, 100, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 3"),
    )
    addToShop(item, 50, "1 20 -10")

    item = Ranged.Ranged(ITEM_5mm_derringer, "gun", 5, 2, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 4"),
    )
    addToShop(item, 100, "1 6 -3")

    item = Ranged.Ranged(ITEM_38_revolver, "gun", 10, 6, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 6"),
    )
    addToShop(item, 250, "1 6 -4")

    item = Ranged.Ranged(ITEM_9mm_auto_pistol, "gun", 12, 17, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 8"),
    )
    addToShop(item, 500, "1 8 -6")

    item = Ranged.Ranged(ITEM_45_auto_pistol, "gun", 8, 6, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 8 2"),
    )
    addToShop(item, 600, "1 8 -6")

    item = Ranged.Ranged(ITEM_10mm_auto_pistol, "gun", 9, 10, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 10"),
    )
    addToShop(item, 750, "1 10 -8")

    item = Ranged.Ranged(ITEM_44_magnum, "gun", 6, 6, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 12"),
    )
    addToShop(item, 900, "1 20 -19")

    item = Ranged.Ranged(ITEM_Uzi_9mm_submachinegun, "gun", 10, 30, 3)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "2 6"),
    )
    addToShop(item, 1500, "1 20 -19")

    item = Ranged.Ranged(ITEM_20_gauge_shotgun, "gun", 15, 14, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "2 4"),
    )
    addToShop(item, 600, "1 8 -6")

    item = Ranged.Ranged(ITEM_12_gauge_shotgun, "gun", 12, 5, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "2 8"),
    )
    addToShop(item, 1400, "1 8 -7")

    item = Ranged.Ranged(ITEM_10_gauge_double_barrel_shotgun, "gun", 8, 2, 2)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "2 10"),
    )
    addToShop(item, 1600, "1 10 -9")

    item = Ranged.Ranged(ITEM_22_hunting_rifle, "gun", 32, 14, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 4"),
    )
    addToShop(item, 800, "1 10 -8")

    item = Ranged.Ranged(ITEM_30_30_hunting_rifle, "gun", 64, 8, 1)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "1 10 2"),
    )
    addToShop(item, 2000, "1 10 -9")

    item = Ranged.Ranged(ITEM_7_62mm_assault_rifle, "gun", 64, 10, 2)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "4 6"),
    )
    addToShop(item, 2400, "1 20 -19")

    item = Ranged.Ranged(ITEM_5_56mm_assault_rifle, "gun", 64, 30, 3)
    item.effect = Script.Script(
        (Script.T, Script.DMG, Global.Wounds, "3 6"),
    )
    addToShop(item, 3200, "1 20 -19")

    # ________________________________________
    item = Defense.Defense(ITEM_leather_jacket, "sword", Equip.T_Armor, 1)
    addToShop(item, 150, "1 4 -1")

    item = Defense.Defense(ITEM_leather_duster, "sword", Equip.T_Armor, 2)
    addToShop(item, 300, "1 4 -2")

    item = Defense.Defense(ITEM_kevlar_jacket, "sword", Equip.T_Armor, 3)
    addToShop(item, 600, "1 6 -4")

    item = Defense.Defense(ITEM_kevlar_duster, "sword", Equip.T_Armor, 4)
    addToShop(item, 900, "1 6 -4")

    item = Defense.Defense(ITEM_chainmail, "sword", Equip.T_Armor, 5)
    addToShop(item, 1000, "1 6 -4")

    item = Defense.Defense(ITEM_riot_vest, "sword", Equip.T_Armor, 5)
    addToShop(item, 1200, "1 6 -5")

    item = Defense.Defense(ITEM_riot_armor, "sword", Equip.T_Armor, 6)
    addToShop(item, 1800, "1 8 -7")

    item = Defense.Defense(ITEM_flak_vest, "sword", Equip.T_Armor, 7)
    addToShop(item, 2400, "1 10 -9")

    item = Defense.Defense(ITEM_tactical_vest, "sword", Equip.T_Armor, 8)
    addToShop(item, 4800, "1 12 -11")

    item = Defense.Defense(ITEM_ceramic_armor, "sword", Equip.T_Armor, 9)
    addToShop(item, 6000, "1 14 -13")

    item = Defense.Defense(ITEM_hard_case_armor, "sword", Equip.T_Armor, 10)
    addToShop(item, 10000, "1 16 -15")

    item = Defense.Defense(ITEM_hard_hat, "sword", Equip.T_Headgear, 1)
    addToShop(item, 100, "1 6 -1")

    item = Defense.Defense(ITEM_motorcycle_helmet, "sword", Equip.T_Headgear, 2)
    addToShop(item, 200, "1 4 -1")

    item = Defense.Defense(ITEM_metal_helmet, "sword", Equip.T_Headgear, 2)
    addToShop(item, 200, "1 6 -4")

    item = Defense.Defense(ITEM_riot_gear_helmet, "sword", Equip.T_Headgear, 3)
    addToShop(item, 400, "1 6 -5")

    item = Defense.Defense(ITEM_flak_helmet, "sword", Equip.T_Headgear, 4)
    addToShop(item, 600, "1 10 -9")

    item = Defense.Defense(ITEM_ceramic_helmet, "sword", Equip.T_Headgear, 5)
    addToShop(item, 800, "1 14 -13")

    item = Defense.Defense(ITEM_garbage_can_lid, "sword", Equip.T_Shield, 1)
    addToShop(item, 50, "1 10")

    item = Defense.Defense(ITEM_wood_shield, "sword", Equip.T_Shield, 2)
    addToShop(item, 100, "1 6 -1")

    item = Defense.Defense(ITEM_metal_shield, "sword", Equip.T_Shield, 3)
    addToShop(item, 200, "1 6 -1")

    item = Defense.Defense(ITEM_riot_shield, "sword", Equip.T_Shield, 4)
    addToShop(item, 400, "1 6")

    # ________________________________________
    item = Equip.Equip(ITEM_gold_ring, "sword", Equip.T_Ring, Global.SHOP_Pawn_Shop)
    item.readyEffect = Script.Script(
        (Script.T, Script.STAT, Global.Presence, "0 0 1"),
    )
    item.unreadyEffect = Script.Script(
        (Script.T, Script.STAT, Global.Presence, "0 0 -1"),
    )
    addToShop(item, 500, "1 6 -1")

    item = Equip.Equip(
        ITEM_digital_watch,
        "sword",
        Equip.T_Accessory,
        Global.SHOP_Pawn_Shop,
    )
    item.readyEffect = Script.Script(
        (Script.T, Script.STAT, Global.Mind, "0 0 1"),
    )
    item.unreadyEffect = Script.Script(
        (Script.T, Script.STAT, Global.Mind, "0 0 -1"),
    )
    addToShop(item, 30, "1 6 0")

    item = Equip.Equip(
        ITEM_mirrorshades,
        "sword",
        Equip.T_Accessory,
        Global.SHOP_Pawn_Shop,
    )
    item.readyEffect = Script.Script(
        (Script.T, Script.STAT, Global.Presence, "0 0 2"),
    )
    item.unreadyEffect = Script.Script(
        (Script.T, Script.STAT, Global.Presence, "0 0 -2"),
    )
    addToShop(item, 20, "1 10 0")

    # ________________________________________
    item = Loot.Loot(ITEM_can_of_food, "food", Global.SHOP_General)
    item.oneshot = 1
    item.effect = Script.Script(
        (Script.T, Script.STAT, Global.Wounds, "-2 2 1"),
        (Script.T, Script.STAT, Global.Fatigue, "-2 2 1"),
    )
    addToShop(item, 5, "2 20 -5")

    item = Loot.Loot(ITEM_box_of_chocolates, "food", Global.SHOP_General)
    item.oneshot = 1
    item.effect = Script.Script(
        (Script.T, Script.STAT, Global.Wounds, "-2 3 1"),
        (Script.T, Script.STAT, Global.Fatigue, "-2 3 1"),
    )
    addToShop(item, 100, "1 8 -4")

    item = Equip.Equip(ITEM_flashlight, "sword", Equip.T_Accessory, Global.SHOP_General)
    item.readyEffect = Script.Script(
        (Script.T, Script.LIGHT, 4),
    )
    item.unreadyEffect = Script.Script(
        (Script.T, Script.LIGHT, 0),
    )
    addToShop(item, 50, "1 6 -2")


fillShopTypes()
