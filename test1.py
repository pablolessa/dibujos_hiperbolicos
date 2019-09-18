from dibujos import *

p1 = Point.frompolar(radius=1,angle=0)
p2 = Point.frompolar(radius=1,angle = 2*pi/3)
p3 = Point.frompolar(radius=1,angle = -2*pi/3)
f = Figure([p1,p2,p3])
f.add(Segment(p1,p2))
f.add(Segment(p2,p3))
f.add(Segment(p3,p1))

f.writepgf('test1.pgf')
