#rotate 90&deg;
#A---------------------D    -0.5
# \                   /
#  \                 /
#   \               /
#    B-------------C        -1
#
#   /------------------D    z0
#  /                 /
# /   /------------C
#A---B             |
# \   \------------C
#  \                 \
#   \------------------D    z1

d:ax:0
d:ay:-0.5
d:az:1

d:bx:0
d:by:-1
d:bz:0.75

d:cx0:-0.75
d:cx1:0.75
d:cy:-1
d:cz:-0.75

d:dx0:-1
d:dx1:1
d:dy:-0.5
d:dz:-1

#bottom
y:a:#cccccc:#ff7700: bx,by,bz; cx0,cy,cz; cx1,cy,cz;
#starboard
y:a:#ffffff:#ff7700: ax,ay,az; bx,by,bz; cx0,cy,cz; dx0,dy,dz;
#port
y:a:#ffffff:#ff7700: ax,ay,az; bx,by,bz; cx1,cy,cz; dx1,dy,dz; 

