from dibujos import *
from math import acosh,sin,cos,pi

def side(alpha,beta,gamma):
    '''side of hyperbolic triangle from angles''' 
    return acosh((cos(alpha) + cos(beta)*cos(gamma))/(sin(beta)*sin(gamma)))

l,m,n = 8,8,4

alpha,beta,gamma = pi/l, pi/m, pi/n
A,B,C = side(alpha,beta,gamma),side(beta,gamma,alpha),side(gamma,alpha,beta)

p1 = Point.frompolar(radius=0,angle=0)
p2 = Point.frompolar(radius=A,angle = 0)
p3 = Point.frompolar(radius=B,angle = gamma)

s1 = Gray(Segment(p1,p2))
s2 = Blue(Segment(p2,p3))
s3 = Gray(Segment(p3,p1))
triangle = Figure([s1,s3,s2])

triangle.update([Tangent.rotate(gamma/2)*Tangent.forward(A/2)*Gray(x) for x in stickman(A/6)])
a = Tangent.flip()
b = Tangent.rotate(gamma)*Tangent.flip()*Tangent.rotate(-gamma)
c = Tangent.forward(A)*Tangent.rotate(pi-beta)*Tangent.flip()*Tangent.rotate(beta-pi)*Tangent.forward(-A)

def is_reduced(word):
    forbidden = ['aa','bb','cc','ab'*l,'ba'*l,'bc'*m,'cb'*m,'ca'*n,'ac'*n]
    for rel in forbidden:
        if word.find(rel) != -1:
            return False
    return True
    
def extend(word):
    '''Yields reduced words that extend a given non-empty word'''
    if word == '':
        yield 'a'
        yield 'b'
        yield 'c'
    else:
        for x in 'abc':
            possible = word + x
            if is_reduced(possible):
                yield possible


T = {'a':a,'b':b,'c':c}

g = Figure()
g.update(triangle)
for w in T:
    g.update(T[w]*triangle)

def newtransforms(S):
    words = []
    for w in S:
        for wp in extend(w):
           words.append(wp)
    return dict([(w,S[w[:-1]]*T[w[-1]]) for w in words])

S = T
for i in range(12):
    for w in S:
        g.update(S[w]*triangle)
    S = newtransforms(S)

f = Figure()
f.update(g)

f.writesvg('triangles.svg')
 
