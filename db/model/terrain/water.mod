#A----B
# \  /
#  \/
#   C
d:ax:-1
d:ay:-1
d:bx:1
d:by:-1
d:cx:0
d:cy:-1.5

#back
y:a:#0066ee:: ax,ay,1; bx,by,1; cx,cy,0:
#left side
y:a:#0055dd:: ax,ay,1; ax,ay,-1; cx,cy,0:
#right side
y:a:#0055dd:: bx,by,1; bx,by,-1; cx,cy,0:
#top
p:a:#aaccff::b:stipple=gray25
