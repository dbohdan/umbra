from . import util
import binascii, string
import time

MAX=100000
color = "#ffcc99"

t1 = time.clock()
for i in range(MAX):
    pass
t2 = time.clock()
print("calibration took", (t2-t1)*1000, "ms")

t1 = time.clock()
for i in range(MAX):
    red = int(color[1:3], 16)
    green = int(color[3:5], 16)
    blue = int(color[5:7], 16)
t2 = time.clock()
print("string.atoi took", (t2-t1)*1000, "ms")

t1 = time.clock()
for i in range(MAX):
    rgb = binascii.a2b_hex(color[1:7])
    red = ord(rgb[0])
    green = ord(rgb[1])
    blue = ord(rgb[2])
t2 = time.clock()
print("binascii took", (t2-t1)*1000, "ms")

