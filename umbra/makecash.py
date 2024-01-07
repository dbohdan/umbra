from . import util

RADIUS=0.06

for i in range(8):
    x = (util.d(1, 11)-6) / 10.0
    z = (util.d(1, 11)-6) / 10.0

    print("o:a:#cccccc:#ffffff: %4.2f,-1,%4.2f; %4.2f,-1,%4.2f:" % (x-RADIUS,z-RADIUS, x+RADIUS,z+RADIUS))

