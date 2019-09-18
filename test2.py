from dibujos import *

p1 = Point.frompolar(radius=1,angle=0)
p2 = Point.frompolar(radius=1,angle = 2*pi/3)
p3 = Point.frompolar(radius=1,angle = -2*pi/3)

s1 = Segment(p1,p2)
s1.color = 'red'

s2 = Segment(p2,p3)
s2.color = 'orange'

s3 = Segment(p3,p1)
s3.color = 'blue'

g = Figure([p1,p2,p3,s1,s2,s3])
g.writepgf('test2.pgf')
