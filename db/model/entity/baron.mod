#     A/---\       0.8
#     /     \
#     \ C-D /      0.55
#      \| |/B      0.5
#       | |
#     V-F-E-W      0.45
#    /K     L\     0.35
#   //|     |\\
#  // |  X  | \\   0.2
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
d:gx:-0.5
d:gy:0
d:hy:0.1
d:jx:0.5
d:ky:0.35
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
d:xx:0
d:xy:0.2

#neck
y:a:#ffffdd:#ffffdd: cx,cy,0; dx,cy,0; dx,ey,0; cx,ey,0:
#head
o:a:#ffffdd:#ffffdd: ax,ay,0; bx,by,0:
#eyes
o:a:#00ff00:#00ff00: -0.08,0.69,0; -0.03,0.65,0
o:a:#00ff00:#00ff00: 0.03,0.69,0; 0.08,0.65,0
#dead man's grin
y:a:#000000::-0.08,0.57,0; 0.08,0.57,0; 0.08,0.52,0; -0.08,0.52,0:stipple=gray50

#top hat
y:a:#000000:#000000: -0.20,0.75,0; -0.10,0.75,0; -0.10,0.95,0; 0.10,0.95,0; 0.10,0.75,0; 0.20,0.75,0

#shirt
y:a:#ffffff:#000000: vx,ey,0; wx,ey,0; wx,my,0; vx,my,0:
#coat
y:a:#000000:#000000: vx,ey,0; cx,ey,0; xx,xy,0; dx,ey,0; wx,ey,0; wx,my,0; vx,my,0

#left arm
y:a:#000000:#000000: vx,ey,0; vx,ky,0; gx,gy,0; gx,hy,0:
#right arm
y:a:#000000:#000000: wx,ey,0; wx,ky,0; jx,gy,0; jx,hy,0:
#legs
y:a:#000000:#000000: vx,my,0; qx,qy,0; vx,py,0; rx,ry,0; wx,py,0; sx,qy,0; wx,my,0:
#left foot
y:a:#000000:#000000: qx,qy,0; ox,py,0; vx,py,0:
#right foot
y:a:#000000:#000000: sx,qy,0; ux,py,0; wx,py,0:

#name
n:a:#ff0000: 0,1.0,0
