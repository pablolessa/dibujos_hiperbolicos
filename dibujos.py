## Module for generating drawing in the hyperbolic disk.
## So far it can generate .pgf files which I open up with KTikz (which in turn can get pgn, eps, and pdf files out of them).
##
## Example usage:
## Open this file in Idle and press f5 (run the interactive interpreter).
##  >>> p1 = Point.frompolar(radius=1,angle=0)
##  >>> p2 = Point.frompolar(radius=1,angle = 2*pi/3)
##  >>> p3 = Point.frompolar(radius=1,angle = -2*pi/3)
##  >>> f = Figure([p1,p2,p3])
##  >>> f.add(Segment(p1,p2))
##  >>> f.add(Segment(p2,p3))
##  >>> f.add(Segment(p3,p1))
##  >>> f.writepgf('test.pgf')
##
## This generates the file 'test.pgf' containing a Tikz figure of a hyperbolic triangle.
## You can easily change the color of segments or points by changing the color attribute.
## For example:
##        >>> s1 = Segment(p1,p2)
##        >>> s1.color = 'red'
##        >>> s2 = Segment(p2,p3)
##        >>> s2.color = 'orange'
##        >>> s3 = Segment(p3,p1)
##        >>> s3.color = 'blue'
##        >>> g = Figure([p1,p2,p3,s1,s2,s3])
##        >>> g.writepgf('test2.pgf')
##
## Generates a similar Tikz figure but with colored edges.
##
## Obviously things get more interesting when you use Python to generate the figure proceeduraly.
## An example of this can be obtained by calling shiqz(100) which generates a file 'shiqz.pgf'.
## 
## So far I have 3 types of drawable objects, Point, Segment, and Figure.
## A Figure is a subclass of Set and is pretty much just a set of Points, Segments and possibly other Figures.
## It has a special writepgf function.
##
## Points represent points in the hyperbolic plane.  At the moment they are complex numbers representing
## the point in the upper half plane model.   But I plan to change that for technical reasons.  I provide several constructors.
## Point.frompolar(radius,angle)   constructs from polar coordinates.
## Point.fromupper(complex)    constructs from a point in the upper half plane (complex number)
## Point.fromtangent(tangent) constructs from a unit tangent vector (more later)
##
## Segments can so far only be constructed from two points.  Al segments are of finite hyperoblic length.
## There are so far no half lines or lines but I plan to add classes for them later (good for drawings of
## of the modular group for example).  Also a Circle class would be nice.
##
## The Tangent class is not drawable.  It is a subclass of numpy.matrix.   The elements are supposed to
## represent unit tangent vectors in the hyperbolic plane and also isometries of the plane.
##
## Tangent.origin()
##
## Is the tangent vector associated to being in the center of the disk looking right.
## One can construct a tangent vector from instructions (like a turtle graphics type thing) as follows:
##
##        >>> t = Tangent.frominstructions(startangle=pi/2,forward=1,rotate = -pi/2)
##
## The constructor takes 3 moves to be followed in order (starting at Tangent.origin())
## , the first is rotation angle, the second is how much (hyperbolic distance) to move forward,
## the third is a rotation angle.
##
## Any unit tangent vector can be obtained in this way.
##
## You can get the basepoint using the fromtangent constructor of Point.
##        >>> p = Point.fromtangent(t)
##
## Tangents also act on Points, Segments, and Figures by left multiplication.  They act like the unique
## isometry of the hyperbolic plane taking the tangent vector Tangent.origin() to the given tangent vector.
##
## For example continuing the above examples one might do:
##
##        >>> newfigure = t*g
##        >>> newfigure.add(p)
##        >>> newfigure.writepgf('test3.pgf')
##
## In the resulting figure the colored triangle is translated (with respect to test2.pgf)
## and a black point appears in its (hyperbolic) center.

import numpy as np
from math import sqrt,cos,sin,pi,atan,exp,acosh,log
from random import choice
from itertools import product

def pointtodisk(z):
    return (z-1j)/(z+1j)

def pointtoupper(z):
    return (z+1)/(1j*z - 1j)

def pointtomatrix(z):
    x,y = z.real,z.imag
    return np.matrix([[sqrt(y),x/sqrt(y)],[0,1/sqrt(y)]])

def matrixtopoint(a):
    return (a[0,0]*1j + a[0,1])/(a[1,0]*1j+a[1,1])

def rotationmatrix(t):
    '''Acts on upper half plane as a counterclockwise rotation of angle t.'''
    return np.matrix([[cos(t/2),sin(t/2)],[-sin(t/2),cos(t/2)]])

def geodesicmatrix(t):
    '''Multiplication on the right in SL2 gives geodesic flow in the hyperbolic plane.'''
    return np.matrix([[exp(t/2),0],[0,exp(-t/2)]])

def hdistance(z,w):
    '''Hyperbolic distance in the upper half plane.'''
    a,b = pointtomatrix(z),pointtomatrix(w)
    c = a**(-1)*b
    return acosh(np.trace(np.transpose(c)*c)/2)

def segment(z,w,subdivisions=10,tolerance=0.0001):
    if abs(z.real-w.real) < tolerance:
        return [z] + [complex(z.real*(1-i/subdivisions)+w.real*i/subdivisions +exp(log(z.imag)*(1-i/subdivisions)+log(w.imag)*i/subdivisions)*1j) for i in range(1,subdivisions)] + [w]
        
    def getcenter(z,w):
        '''Euclidean center of the circle which is the hyperbolic geodesic between z and w.'''
        mid = (z+w)/2
        perp = (z-w)*1j
        t = -mid.imag/perp.imag
        return mid + t*perp
    def getangle(c,z):
        '''Angle (in (-pi/2,pi/2)) between the vertical line throu c (real) and z (in upper half plane).'''
        return atan(-(z-c).real/(z-c).imag)
    def gettangent(z,w):
        '''Returns the matrix representing the unit tangent vector at z to the segment joining z,w, pointing in the direction of w'''
        c = getcenter(z,w)
        t = getangle(c,z)
        if z.real < w.real:
            return pointtomatrix(z)*rotationmatrix(t)*rotationmatrix(-pi/2)
        else:
            return pointtomatrix(z)*rotationmatrix(t)*rotationmatrix(pi/2)
    
    return [z]+[matrixtopoint(gettangent(z,w)*geodesicmatrix(hdistance(z,w)*i/subdivisions)) for i in range(1,subdivisions)]+[w]


class Tangent(np.matrix):
    @classmethod
    def origin(cls):
        return Tangent([[1,0],[0,1]])
    
    @classmethod
    def frominstructions(cls,startangle=0,forward=0,rotate=0,start=rotationmatrix(0)):
        return Tangent(start*rotationmatrix(startangle)*geodesicmatrix(forward)*rotationmatrix(rotate))

    
class Point(complex):
    @classmethod
    def frompolar(cls,radius=0,angle=0,start=Tangent.origin()):
        return Point(matrixtopoint(start*rotationmatrix(angle)*geodesicmatrix(radius)))

    @classmethod
    def fromupper(cls,z):
        return Point(z)
        
    @classmethod
    def fromdisk(cls,z):
        return Point(pointtoupper(z))

    @classmethod
    def fromtangent(cls,t):
        return Point(matrixtopoint(t))

    def gettikzline(self):
        if hasattr(self,'color') == False:
            self.color = 'black'
        if hasattr(self,'radius') == False:
            self.radius = 0.2
        x = pointtodisk(self)*10
        size = (self.radius/2)*(100-abs(x)**2)/100
        return '\\begin{pgfonlayer}{foreground}\\draw[fill='+self.color+','+self.color+'] '+'({:.3f},{:.3f})'.format(x.real,x.imag)+' circle '+'({:.3f})'.format(size)+';\\end{pgfonlayer}'

    def __getattr__(self,attr):
        if attr=='tikzline':
            return self.gettikzline()
        else:
            raise AttributeError

    def __rmul__(self,tangent):
        p = Point.fromtangent(tangent*pointtomatrix(self))
        if hasattr(self,'color'):
                   p.color = self.color
        if hasattr(self,'radius'):
                   p.radius = self.radius
        return p
        

class Segment():
    def __init__(self,start,end):
        self.start = start
        self.end = end
    def __str__(self):
        return str((self.start,self.end))
    def __repr__(self):
        return repr((self.start,self.end))
    
    def gettikzline(self):
        if hasattr(self,'color') == False:
            self.color = 'black'
        subdivisions = int(100*abs(pointtodisk(self.start)-pointtodisk(self.end)))+10
        points = [pointtodisk(z) for z in segment(self[0],self[1],subdivisions)]        
        return '\\begin{pgfonlayer}{background}\\draw['+self.color+'] '+' -- '.join(['({:.3f},{:.3f})'.format(10*x.real,10*x.imag) for x in points])+';\\end{pgfonlayer}'

    def __getattr__(self,attr):
        if attr=='tikzline':
            return self.gettikzline()
        else:
            raise AttributeError

    def __getitem__(self,index):
        if index == 0:
            return self.start
        elif index == 1:
            return self.end
        else:
            raise AttributeError
        
    def __rmul__(self,tangent):
        s = Segment(tangent*self[0],tangent*self[1])
        if hasattr(self,'color'):
                   s.color = self.color
        return s
    

class Figure(set):
    def writepgf(self,filename,drawboundary=True):
        f = open(filename,'w')
        f.write('\\pgfdeclarelayer{background}\n')
        f.write('\\pgfdeclarelayer{foreground}\n')
        f.write('\\pgfsetlayers{background,foreground}\n')
        f.write('\\begin{tikzpicture}\n')
        if drawboundary:
            f.write('\\begin{pgfonlayer}{foreground}\\draw (0,0) circle (10);\\end{pgfonlayer}\n')
        for x in self:
            f.write(x.tikzline+'\n')
        f.write('\\end{tikzpicture}\n')
        f.close()
    def __rmul__(self,tangent):
        return Figure([tangent*x for x in self])



def shiqz(numpoints = 100):
    points = [Point(i+1j) for i in range(numpoints)]
    colors = {-1:'red',0:'white',1:'blue'}
    
    segments = []
    for i,p in enumerate(points[:-1]):
        s = Segment(p,points[i+1])
        s.value = choice((-1,0,1))
        s.color = colors[s.value]
        segments.append(s)

    orangesegments = []
    for i,s in enumerate(segments[:-1]):
        value = 0
        for j,s2 in enumerate(segments[i:]):
            value += s2.value
            if value == -1:
                if j != i:
                    t = Segment(s.start,s2.end)
                    t.color = 'orange'
                    orangesegments.append(t)
                break

    t = Tangent(pointtomatrix(-numpoints//2 + 1j))
    f = rotationmatrix(pi/2)*geodesicmatrix(-3)*t*Figure(points+segments+orangesegments)
    f.writepgf('shiqz.pgf')
