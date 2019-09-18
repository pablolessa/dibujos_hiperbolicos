from dibujos import *
from itertools import product

def modulargroup(n):
    '''Generator for elements of length n or less in the modular group.
    The generating set is {a = Tangent.rotate(pi), b=Tangent.rotate(pi)*Tangent.sideways(1), b**2}.'''
    a = Tangent.rotate(pi)
    b = Tangent.rotate(pi)*Tangent.sideways(1)
    B = [b,b**2]
    for length in range(n):
        for bees in product(B,repeat=length//2):
            result = Tangent.origin()
            for x in bees:
                result = result * x * a
            if length%2 == 1:
                yield a * result
                yield result * b
                yield result * b**2
            else:
            	yield result
            	yield a*result*a

def stickmaninmodulargroup(n=10,name='test8.pgf'):
    '''An example test figure.  A stickman in the modular group.''' 
    left = Point.fromhalfplane(-0.5*0.95+1.05*sin(acos(0.5))*1j)
    right = Point.fromhalfplane(0.5*0.95+1.05*sin(acos(0.5))*1j)
    stick = Tangent.forward(0.3)*stickman(0.3)
    seg = Segment(left,right)
    seg.color = 'red'
    righthalf = Segment(right,Point(0.999))
    righthalf.color = 'blue'
    lefthalf = Segment(left,Point(0.999))
    lefthalf.color = 'green'
    f = Figure()
    for t in modulargroup(n):
        f.add(t*seg)
        f.add(t*lefthalf)
        f.add(t*righthalf)
        f.update(t*stick)
    f.writepgf(name)