#      - - - - + + + + +
#      0 0 0 0 0 0 0 0 0
#      . . . . . . . . .
#      8 6 4 2 0 2 4 6 8
#           A/---\            1.25
#            |y z|
#            \---/B
#         C/-------\          1
#          |  G H  |          0.75
#          |//-^-\\|
#         /|/ / \ \|\
#        / \-------/D\        0
#       / / / / \ \ \ \
#      / / / /   \ \ \ \
#      K L M N   O P Q R      -0.5
#      | | | |   | | | |
#      | | | |   | | | |
#      + + + +   + + + +      -1

# leg connection point
d:gx:-0.1
d:gy:0.75
d:hx:0.1
d:hy:0.75

# most forward/back legs are slightly inward!
# rear legs
d:mx:-0.8
d:mz:0.5
d:nx:-0.6
d:nz:1
d:ox:0.6
d:oz:1
d:px:0.8
d:pz:0.5
l:a:#553322: gx,gy,0; mx,-0.5,mz; mx,-1,mz:width=2,stipple=gray75
l:a:#553322: gx,gy,0; nx,-0.5,nz; nx,-1,nz:width=2,stipple=gray75
l:a:#553322: hx,hy,0; ox,-0.5,oz; ox,-1,oz:width=2,stipple=gray75
l:a:#553322: hx,hy,0; px,-0.5,pz; px,-1,pz:width=2,stipple=gray75

# forward legs
d:kx:-0.8
d:kz:-0.5
d:lx:-0.6
d:lz:-1
d:qx:0.6
d:qz:-1
d:rx:0.8
d:rz:-0.5
l:a:#553322: gx,gy,0; kx,-0.5,kz; kx,-1,kz:width=4,stipple=gray75
l:a:#553322: gx,gy,0; lx,-0.5,lz; lx,-1,lz:width=4,stipple=gray75
l:a:#553322: hx,hy,0; qx,-0.5,qz; qx,-1,qz:width=4,stipple=gray75
l:a:#553322: hx,hy,0; rx,-0.5,rz; rx,-1,rz:width=4,stipple=gray75

# body
d:cx:-0.7
d:cy:1
d:dx:0.7
d:dy:0
o:a:#333333:#000000: cx,cy,0; dx,dy,0

# head
d:ax:-0.2
d:ay:1.25
d:bx:0.2
d:by:0.9
o:a:#333333:#000000: ax,ay,0; bx,by,0
# eyes
o:a:#ff0000:#ff0000: -0.15,1.15,0; -0.05,1.10,0:stipple=gray50
o:a:#ff0000:#ff0000: 0.05,1.15,0; 0.15,1.10,0:stipple=gray50
# fangs
l:a:#663322: -0.15,1.0,0; -0.25,0.9,0; -0.15,0.8,0:width=4
l:a:#663322: 0.15,1.0,0; 0.25,0.9,0; 0.15,0.8,0:width=4

# name
n:a:#ff6666: 0,-0.2,0
