from dibujos import *

p1 = Point.frompolar(radius=1,angle=0)
p2 = Point.frompolar(radius=1,angle = 2*pi/3)
p3 = Point.frompolar(radius=1,angle = -2*pi/3)

s1 = Red(Segment(p1,p2))
s2 = Orange(Segment(p2,p3))
s3 = Blue(Segment(p3,p1))
g = Figure([p1,p2,p3,s1,s2,s3])

g.writepgf('test3.pgf')
