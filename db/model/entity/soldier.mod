#     A/---\       0.8
#     /     \
#     \ C-D /      0.55
#      \| |/B      0.5
#       | |
#     V-F-E-W      0.45
#    /K     L\     0.30
#   //|     |\\
#  // |     | \\
# H/  |     |  \J  0.1
# G   M-----N   I  0
#    /   R   \     -0.1
#   /   / \   \
# _-Q  /   \  S-_  -0.95
#O____P     T____U -1

d:ax:-0.12
d:ay:0.80
d:bx:0.12
d:by:0.50
d:cx:-0.05
d:cy:0.55
d:dx:0.05
d:ey:0.45
d:gx:-0.32
d:gy:-0.05
d:hx:-0.40
d:hy:-0.05
d:ix:0.32
d:iy:-0.05
d:jx:0.40
d:jy:-0.05
d:ky:0.30
d:my:0
d:ox:-0.40
d:py:-1
d:qx:-0.25
d:qy:-0.95
d:rx:0
d:ry:-0.1
d:sx:0.25
d:ux:0.40
d:vx:-0.15
d:wx:0.15

#neck
y:a:#ffff00:#000000: cx,cy,0; dx,cy,0; dx,ey,0; cx,ey,0:
#head
o:a:#ffff00:#000000: ax,ay,0; bx,by,0:
#mirrorshades
#A------B------C
# \    / \    /
#  G--F   E--D
d:yax:-0.11
d:yay:0.70
d:ybx:0
d:yby:0.70
d:ycx:0.11
d:ycy:0.70
d:ydx:0.11
d:ydy:0.63
d:yex:0.02
d:yey:0.63
d:yfx:-0.02
d:yfy:0.63
d:ygx:-0.11
d:ygy:0.63
y:a:#000000:#000000: yax,yay,0; ybx,yby,0; ycx,ycy,0; ydx,ydy,0; yex,yey,0; ybx,yby,0; yfx,yfy,0; ygx,ygy,0;

#torso
y:a:#000000:#000033: vx,ey,0; wx,ey,0; wx,my,0; vx,my,0:
#left arm
y:a:#ffff00:#000000: vx,ey,0; vx,ky,0; gx,gy,0; hx,hy,0:
#right arm
y:a:#ffff00:#000000: wx,ey,0; wx,ky,0; ix,iy,0; jx,jy,0:
#legs
y:a:#000000:#000033: vx,my,0; qx,qy,0; vx,py,0; rx,ry,0; wx,py,0; sx,qy,0; wx,my,0:
#left foot
y:a:#442211:#000000: qx,qy,0; ox,py,0; vx,py,0:
#right foot
y:a:#442211:#000000: sx,qy,0; ux,py,0; wx,py,0:

#name
n:a:#ffff00: 0,0.8,0
