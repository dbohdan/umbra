import binascii
import copy
import os
import random
import re
import textwrap
import types

VOWELS = ("a", "e", "i", "o", "u")
NVOWELS = len(VOWELS)
CONSONANTS = (
    "b",
    "c",
    "d",
    "f",
    "g",
    "gh",
    "h",
    "j",
    "k",
    "l",
    "m",
    "n",
    "p",
    "qu",
    "r",
    "s",
    "sh",
    "t",
    "th",
    "v",
    "w",
    "x",
    "y",
    "z",
)
NCONSONANTS = len(CONSONANTS)
NLETTERS = NVOWELS + NCONSONANTS


def assertChar(x):
    assert isChar(x), "Expected char, but was %s '%s'" % (type(x), str(x))


def assertDict(x):
    assert isDict(x), "Expected dict, but was %s '%s'" % (type(x), str(x))


def assertInt(x, min=None, max=None):
    assert isInt(x), "Expected int, but was %s '%s'" % (type(x), str(x))
    if min != None:
        assert x >= min, "Expected min=%d, but was %d" % (min, x)
    if max != None:
        assert x <= max, "Expected max=%d, but was %d" % (max, x)


def assertList(x):
    assert isList(x), "Expected list, but was %s '%s'" % (type(x), str(x))


def assertSequence(x):
    assert isSequence(x), "Expected sequence, but was %s '%s'" % (type(x), str(x))


def assertString(x):
    assert isString(x), "Expected string, but was %s '%s'" % (type(x), str(x))


def assertTuple(x):
    assert isTuple(x), "Expected tuple, but was %s '%s'" % (type(x), str(x))


COLOR_CACHE = {}


def colorTransform(color, scale=None, delta=None):
    if len(color) == 0:
        return color
    set = (color, scale, delta)
    cached = COLOR_CACHE.get(set)
    if cached:
        return cached
        #    if len(color) != 7: raise ValueError, "Invalid color '%s'!" % color
    rgb = binascii.a2b_hex(color[1:7])
    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]
    if scale is not None:
        red = red * scale // 10
        green = green * scale // 10
        blue = blue * scale // 10
    if delta is not None:
        red += delta[0]
        green += delta[1]
        blue += delta[2]
        if red > 255:
            red = 255
        elif red < 0:
            red = 0
        if green > 255:
            green = 255
        elif green < 0:
            green = 0
        if blue > 255:
            blue = 255
        elif blue < 0:
            blue = 0
    s = "#%02x%02x%02x" % (red, green, blue)
    #    print "%s *%s +%s = %d,%d,%d => %s" % (color, scale, delta, red, green, blue, s)
    COLOR_CACHE[set] = s
    return s


def commaList(items, none="None", text=""):
    filtered = [str(item) for item in items if item]

    if not filtered:
        return f"{text}{none}"

    return f"{text}{', '.join(filtered)}"


def cumulative(n):
    return (n + 1) * n // 2


def d(ndice, sides):
    if ndice == 0 or sides <= 0:
        return 0
    elif ndice < 0:
        mul = -1
        ndice = -ndice
    else:
        mul = 1
    t = 0
    rnd = random.randint
    for d in range(ndice):
        t = t + rnd(1, sides)
    return t * mul


def diceString(str):
    """Takes a space-delimited dice string in the form
    "<ndice> <sides> {<bonus> {<mult>}}",
    rolls (<ndice>d<sides>)*<mult>+<bonus> (yes, it's out of order),
    and returns the total."""
    bits = str.split()
    roll = d(int(bits[0]), int(bits[1]))
    if len(bits) >= 4:
        roll *= int(bits[3])
    if len(bits) >= 3:
        roll += int(bits[2])
    return roll


def dictAdd(a, *b):
    assertDict(a)
    if b != None:
        assertTuple(b)
    tmp = copy.copy(a)
    for i in b:
        tmp.update(i)
    return tmp


def dx():
    """Roll an open-ended d10"""
    die = d(1, 10)
    if die == 1:
        return die - dx()
    if die == 10:
        return die + dx()
    return die


def expandArray(a, n, value=None):
    assertInt(n, min=0)
    assertList(a)
    if n > len(a):
        a.extend(
            [
                value,
            ]
            * (n - len(a)),
        )


def foldLines(s, maxlen):
    return "\n".join(textwrap.wrap(s, maxlen))


def indexOf(needle, haystack):
    if not haystack or not needle or needle not in haystack:
        return -1
    if isList(haystack):
        try:
            return haystack.index(needle)
        except ValueError:
            return -1
    for i in range(len(haystack)):
        if haystack[i] == needle:
            return i
    return -1


def isChar(x):
    return isinstance(x, str) and len(x) == 1


def isDict(x):
    return isinstance(x, dict)


def isFloat(x):
    return isinstance(x, float)


def isInt(x):
    return isinstance(x, int)


def isList(x):
    return isinstance(x, list)


def isNumber(x):
    return isinstance(x, (int, float))


def isSequence(x):
    return isList(x) or isTuple(x)


def isString(x):
    return isinstance(x, str)


def isTuple(x):
    return isinstance(x, tuple)


def makeArray(dims, value=None):
    if isinstance(dims, int):
        return [
            value,
        ] * dims
    assertSequence(dims)
    n = dims[0]
    assertInt(n)
    if len(dims) == 1:
        a = [
            value,
        ] * n
    else:
        sub = dims[1:]
        a = [makeArray(sub, value) for i in range(n)]
    return a


def minmax(n, low, high):
    if n < low:
        return low
    elif n > high:
        return high
    return n


BIG_LEVEL = 10
BIG_XP = 100000


def nextXP(level):
    if level < BIG_LEVEL:
        xp = 100 * (1 << level)
    elif level >= BIG_LEVEL:
        n = level - BIG_LEVEL + 1
        xp = BIG_XP * n * n
    return xp


def number(str):
    """Attempts to convert str to an int, then a float, then just returns
    it."""
    try:
        return int(str)
    except ValueError:
        try:
            return float(str)
        except ValueError:
            return str


def print2cols(lines):
    colsize1 = colsize2 = len(lines) // 2
    if colsize1 + colsize2 < len(lines):
        colsize1 += 1
    for i in range(colsize1):
        c1 = lines[i]
        if i < colsize2:
            c2 = lines[colsize1 + i]
        else:
            c2 = ""
        COLWIDTH = 39
        while len(c1) > 0 or len(c2) > 0:
            print("%-39s|%s" % (c1[:COLWIDTH], c2[:COLWIDTH]))
            if len(c1) < COLWIDTH:
                c1 = ""
            else:
                c1 = c1[COLWIDTH:]
            if len(c2) < COLWIDTH:
                c2 = ""
            else:
                c2 = c2[COLWIDTH:]


def purifyName(name, slashOkay=0):
    assertString(name)
    name = name.strip().lower()
    if slashOkay:
        chars = repr("[^a-z0-9_%s]" % os.sep)[1:-1]
    else:
        chars = "[^a-z0-9_]"
    name = re.sub(chars, "_", name)
    return name


def randomName(longname):
    lastvowel = d(1, NLETTERS) <= NCONSONANTS
    word = ""
    if longname:
        wordlen = d(3, 3)
    else:
        wordlen = d(1, 4) + 1
    for i in range(wordlen):
        if lastvowel:
            vowelchance = 5
        else:
            vowelchance = 95
        if d(1, 100) <= vowelchance:
            n = d(1, NVOWELS) - 1
            letter = VOWELS[n]
            lastvowel = 1
        else:
            n = d(1, NCONSONANTS) - 1
            letter = CONSONANTS[n]
            lastvowel = 0
        if i == 0:
            word = "%s%s" % (word, letter.capitalize())
        else:
            word = "%s%s" % (word, letter)
    return word


def reflect(obj):
    if isinstance(obj, types.InstanceType):
        text = str(obj.__class__)
        for prop in list(vars(obj).keys()):
            text = "%s\n    %s=%s" % (text, prop, getattr(obj, prop))
    else:
        text = str(obj)
    return text


def rollOnTable(table):
    total = 0
    for i in range(0, len(table), 2):
        total += table[i]
    roll = d(1, total)
    chance = 0
    for i in range(0, len(table), 2):
        chance += table[i]
        if roll <= chance:
            return table[i + 1]
    assert 0, "Roll of %d fell out of table %s!" % (roll, table)


def sign(i):
    if i > 0:
        return 1
    elif i == 0:
        return 0
    return -1


def taskRoll(score):
    """Return the result quality of a task roll against 'score'"""
    roll = dx() + dx()
    result = roll + score - 20
    return result


def testNextXP():
    STEP = 77
    for level in range(1, STEP + 1):
        n0 = nextXP(level)
        d0 = n0 - nextXP(level - 1)
        n1 = nextXP(level + STEP)
        d1 = n1 - nextXP(level + STEP - 1)
        print("%3d %10d %10d     %3d %10d %10d" % (level, n0, d0, level + STEP, n1, d1))


def testTaskRolls():
    print("Roll\tChance")
    score = makeArray(60, 0)
    for i in range(1000):
        roll = dx() + dx()
        index = roll + 20
        if index < 0:
            index = 0
        elif index >= 60:
            index = 59
        score[index] = score[index] + 1
    for i in range(60):
        chance = score[i] / 10.0
        #        print "%d:\t%3.1f%%\t%d" % (i-20, chance, score[i])
        print("%d:\t%s" % (i - 20, "*" * (score[i] // 2)))
    print()

    for score in range(3, 31):
        win = 0
        for i in range(1, 1000):
            #        for i in xrange(1, 100):
            if taskRoll(score) > 0:
                win = win + 1
        chance = win / 10.0
        #        chance = win / 1.0
        print("%d:\t%3.1f%%" % (score, chance))


def toString(obj):
    if obj is None:
        return "None"
    if isSequence(obj):
        strlist = [toString(i) for i in obj]
        if isList(obj):
            return "[" + (", ".join(strlist)) + "]"
        else:
            return "(" + (", ".join(strlist)) + ")"
    return str(obj).split("\n")[0]


if __name__ == "__main__":
    for i in range(30):
        print(randomName(0), randomName(1))
