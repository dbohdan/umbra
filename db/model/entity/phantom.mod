#     A/---\       0.8
#     /     \
#     \ C-D /      0.55
#      /   \B      0.50
#     /     \
#    J       E     0.40
#    |       |
#    |       |
#     \     /
#     |     |
#     |     |
#     I   _-F      -0.65
#    /   G         -0.75
#   H---/          -0.90
#                  -1

d:ax:-0.12
d:ay:0.80
d:bx:0.12
d:by:0.50
d:cx:-0.05
d:cy:0.55
d:dx:0.05
d:dy:0.55
d:ex:0.20
d:ey:0.40
d:fx:0.15
d:fy:-0.65
d:gx:0
d:gy:-0.75
d:hx:-0.25
d:hy:-0.90
d:ix:-0.15
d:iy:-0.65
d:jx:-0.20
d:jy:0.40

#body
y:a:#ffffdd:: cx,cy,0; dx,dy,0; ex,ey,0; fx,fy,0; gx,gy,0; hx,hy,0; ix,iy,0; jx,jy,0; :stipple=gray25
#head
o:a:#ffffdd:: ax,ay,0; bx,by,0: stipple=gray25
#eyes
o:a:#00ff00:#00ff00: -0.08,0.69,0; -0.03,0.65,0
o:a:#00ff00:#00ff00: 0.03,0.69,0; 0.08,0.65,0

#name
n:a:#ff0000: 0,1.0,0
