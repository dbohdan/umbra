from . import util
import binascii, string
import time

MAX = 100000
color = "#ffcc99"


def print_time(label, start, end):
    print("{0} took {1:.2f} ms".format(label, (end - start) * 1000))


t1 = time.clock()
for i in range(MAX):
    pass
t2 = time.clock()
print_time("calibration", t1, t2)

t1 = time.clock()
for i in range(MAX):
    red = int(color[1:3], 16)
    green = int(color[3:5], 16)
    blue = int(color[5:7], 16)
t2 = time.clock()
print_time("int", t1, t2)

t1 = time.clock()
for i in range(MAX):
    rgb = binascii.a2b_hex(color[1:7])
    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]
t2 = time.clock()
print_time("binascii", t1, t2)
