#  D__C
#  /  \
# /    \
#A------B
d:ax:-1
d:ay:1
d:bx:1
d:by:1
d:cx:0.5
d:cy:6
d:dx:-0.5
d:dy:6
d:z0:-1
d:z1:-0.25
d:z2:0.25
d:z3:1

#cap
#left side
y:r:#995522:#884411: ax,ay,z0; ax,ay,z3; dx,dy,z2; dx,dy,z1:
#right side
y:l:#995522:#884411: bx,by,z0; bx,by,z3; cx,cy,z2; cx,cy,z1:
#front
y:a:#aa6633:#995522: ax,ay,z0; bx,by,z0; cx,cy,z1; dx,dy,z1:

#body
p:r:#995522:#884411:l:
p:l:#995522:#884411:r:
p:a:#aa6633:#995522:n:
