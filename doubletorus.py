'''In this example we illustrate a Fuchsian group whose orbit space 
is the genus 2 compact orientable surface.'''

from surfacegroup import *


r = acosh(1/tan(pi/8))
t = Tangent.forward(r)*Tangent.rotate(pi/2)*Tangent.forward(r)
p = t.basepoint
points = [Tangent.rotate(2*pi*i/8)*p for i in range(8)]
segments = [Segment(points[i],points[(i+1)%8]) for i in range(-1,7)]
c = [Red,Blue,Red,Blue,Orange,Teal,Orange,Teal]
l = [c[i](segments[i]) for i in range(8)]
# The points and segments are the vertices and sides of an octogonal
# fundamental domain.
# Since there are pairs of sides which are exchanged by transformations in
# the group we make a figure with only half of the sides and one vertex.
# This makes sure we will only draw each segment and point once in the
# final figure.
halfoctogon = Figure([p, segments[0],segments[1],segments[4],segments[5]])

# We add a stickman for good measure.
s = stickman()

f = Figure()
for t in surfacegroup(4):
    f.update(t*halfoctogon)
    f.update(t*s)

f.writepgf('1.pgf')    
f.writesvg('1.svg')

# The output files look pretty good.  But you can see missing octogons near the boundary.
# At the time of writting the svg file is pretty heavy (has to do with the subdivision of segments for drawing).
# The pgf is around the limit allowed by TEX (which imposes a ridiculously low 5MB RAM limit
# while processing a file).