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
# G   |     |   I  0
#     M-----N      -0.2

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
d:my:-0.2
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

#counter wall
b:a:#995522:#884411:height=0.8
#counter top
y:a:#995522:#884411: -1,my,0; 1,my,0; 1,my,-1; -1,my,-1:

#neck
y:a:#ffff00:#000000: cx,cy,0; dx,cy,0; dx,ey,0; cx,ey,0:
#head
o:a:#ffff00:#000000: ax,ay,0; bx,by,0:
#eyes
o:a:#000000:#ffff00: -0.08,0.69,0; -0.03,0.65,0
o:a:#000000:#ffff00: 0.03,0.69,0; 0.08,0.65,0

#shirt
y:a:#ffffff:#000000: vx,ey,0; wx,ey,0; wx,my,0; vx,my,0:
#coat
y:a:#664411:#000000: vx,ey,0; cx,ey,0; xx,xy,0; dx,ey,0; wx,ey,0; wx,my,0; vx,my,0

#left arm
y:a:#664411:#000000: vx,ey,0; vx,ky,0; gx,gy,0; gx,hy,0:
#right arm
y:a:#664411:#000000: wx,ey,0; wx,ky,0; jx,gy,0; jx,hy,0:

#name
n:a:#ffff00: 0,0.8,-1

