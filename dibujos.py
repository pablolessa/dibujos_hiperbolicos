# "Dibujos Hiperbólicos" is a tool for generating figures of the Poincaré disk model of the hyperbolic plane.
#    Copyright (C) 2015 Pablo Lessa

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''Dibujos Hiperbólicos: a tool for generating figures of the Poincaré disk model of the hyperbolic plane.'''

import numpy as np
from math import *
from itertools import product
from random import choice

# These constants control the pgf output files.
# The diskradius is the radius of the boundary circle in the pgf figure
# pointsize is the size in hyperbolic units of a point (i.e. pointsize*diskradius is the size of a point at the origin in the pgf file)
# tangentsize is a hyperbolic length of arrows used to represent tangent vectors.

diskradius = 3.
pointsize = 0.05
tangentsize = 0.15

# Here we define convenience functions Red(drawable), Green(drawable), etc.
# All they do is change the .color attribute of the given drawable object and return the result.
# For example one can create a red point at the origin using Red(Point(0)).
# The colors supported are:
# Red Green Blue Cyan Magenta Yellow Black Gray Darkgray Lightgray Brown Lime Olive Orange Pink Purple Teal Violet White
# There is a function for each (generated by a trick using exec) and they all have docstrings.

colors = 'red green blue cyan magenta yellow black gray darkgray lightgray brown lime olive orange pink purple teal violet white'.split()
for c in colors:
    exec('def '+c.capitalize()+'(drawable):\n\tdrawable.color = '+"'"+c+"'"+'\n\t'+'return drawable\n')
    exec(c.capitalize()+'.__doc__ = '+'"'+c.capitalize()+'(drawable) Changes the .color attribute of the drawable to '+c+'.\\n It also returns the object so, for example, '+c.capitalize()+'(Tangent.origin()) returns a '+c+' tangent object at the origin."')

# The following two dictionaries are used to set the correct layer when calculating the .tikzline attributes of drawables.
 
layerstartstr = {'background':'\\begin{pgfonlayer}{background}','main':'','foreground':'\\begin{pgfonlayer}{foreground}'}
layerendstr = {'background':'\\end{pgfonlayer}','main':'','foreground':'\\end{pgfonlayer}'}


# Similar to the color functions defined above we provide functions to change the .layer attribute of drawables.
# There are 3 layers, foreground, main, and background.
# There is one function for each (since there are only three we define them all without the nasty exec trick we did for the color functions).

def Foreground(drawable):
    '''Sets drawable.layer to 'foreground' and returns the object.'''
    drawable.layer = 'foreground'
    return drawable

def Mainlayer(drawable):
    '''Sets drawable.layer to 'foreground' and returns the object.'''
    drawable.layer = 'main'
    return drawable

def Background(drawable):
    '''Sets drawable.layer to 'main' and returns the object.'''
    drawable.layer = 'background'
    return drawable

# Finally, we start with the actual classes.  The drawables are Point, Tangent, Segment, Halfline, Line, Circle and Disk.
# The Figure class is a subclass of set and instances are supposed to hold drawables.
# In particular if f is a figure you use f.add(drawable) to add a drawable to it but f.update(g) to add all drawables in some other figure g.
# Each drawable has a .tikzline attribute which is used by the Figure writepgf method to write a pgf file.

class Point(complex):
    '''A point in the Poincaré disk model of the hyperbolic plane.\n'''
    '''Basically a complex number of modulus less than 1.\n'''
    '''You can construct them with modulus 1 (points at infinity or boundary points),\n'''
    '''But some methods (such as p.hyperboloid) will fail (yielding infinite values.'''
    def __init__(self,*args,**kwargs):
        self.color = 'black'
        self.layer = 'foreground'

    @classmethod
    def fromdisk(cls,z):
        return cls(z)

    @classmethod
    def fromklein(cls,z):
        return cls(z/(1+ sqrt(1-min(1,abs(z)** 2))))

    @classmethod
    def fromhalfplane(cls,z):
        return cls((z-1j)/(z+1j))

    @classmethod
    def fromhyperboloid(cls,vector):
        x,y,t = vector
        return cls(x/(1+t) + y*1j/(1+t))

    @classmethod
    def frompolar(cls,angle = 0., radius =0.):
        return (Tangent.rotate(angle)*Tangent.forward(radius)).basepoint

    @property
    def disk(self):
        return complex(self)

    @property
    def klein(self):
        z = complex(self)
        return 2*z/(1+abs(z)**2)

    @property
    def halfplane(self):
        z = complex(self)
        return complex((z*1j + 1j)/(-z + 1))

    @property
    def hyperboloid(self):
        p = 1+abs(self)**2
        m = 1-abs(self)**2
        return [2*self.real/m, 2*self.imag/m , p/m]

    @property
    def polar(self):
        '''Returns a tuple (angle, distance to origin).'''
        return np.angle(self),Point.distance(self,Point(0,0))

    @staticmethod
    def distance(p,q):
        '''The distance between two points p and q.'''
        deltapq = 2*abs(p-q)**2/((1-abs(p)**2)*(1-abs(q)**2))
        return acosh(1+deltapq)

    @staticmethod
    def midpoint(p,q):
        '''Returns the midpoint of two points p and q.'''
        px,py,pt = p.hyperboloid
        qx,qy,qt = q.hyperboloid
        midx,midy,midt = (px+qx)/2,(py+qy)/2,(pt+qt)/2
        midnorm = sqrt(midt**2 - midx**2 + midy**2)
        return Point.fromhyperboloid([midx/midnorm,midy/midnorm,midt/midnorm])

    @property
    def tikzline(self):
        x = diskradius*complex(self)
        size = (pointsize/2)*(diskradius**2-abs(x)**2)/diskradius**2
        sizestr = '{:.3f}'.format(size)  
        if sizestr ==  '0.000':
            return ''                       # We avoid outputting points of radius (0.000).
        return layerstartstr[self.layer]+'\\draw[fill='+self.color+','+self.color+'] '+'({:.3f},{:.3f})'.format(x.real,x.imag)+' circle '+'({:.3f})'.format(size)+';'+layerendstr[self.layer]

    def __rmul__(self,tangent):
        '''Tangents acting on points as isometries.'''
        a,b,c,d = tangent[0,0],tangent[0,1],tangent[1,0],tangent[1,1]
        z = complex(self)
        result = Point((a*z+b)/(c*z+d))
        result.color = self.color
        result.layer = self.layer
        return result



class Tangent(np.matrix):
    '''Tangents represent both unit tangent vectors in the disk and hyperbolic isometries.'''
    '''Hence they can be drawn (as a small arrow) but also can act by multiplication on other drawables (including other tangents)'''
    '''Several constructors are provided.  Tangent.origin(), Tangent.forward(d), Tangent.rotate(a), Tangent.sideways(d).'''
    '''A useful pattern is to create a tangent out of "instructions" e.g. t = Tangent.forward(1)*Tangent.rotate(pi/2)*Tangent.forward(2)*Tangent.rotate(pi/3).'''
    def __array_finalize__(self,*args,**kwargs):
        self.color = 'black'
        self.layer = 'foreground'

    def __mul__(self,other):
        if type(self) != type(other):
            return NotImplemented
        else:
            result = super().__mul__(other)
            result.color = other.color
            result.layer = other.layer
            return result
 
    def __hash__(self):
        return hash(str(self))

    def __eq__(self,other):
        return self[0,0] == other[0,0] and self[0,1] == other[0,1] and self[1,0] == other[1,0] and self[1,1] == other[1,1] and self.color == other.color and self.layer == other.layer

    @classmethod
    def fromrealmatrix(cls,matrix):
        '''Takes a 2x2 matrix with real coeficients and positive determinant.'''
        matrix = np.matrix(matrix)
        halfplanetodisk = np.matrix([[1., -1j], [1., 1j]])
        disktohalfplane = halfplanetodisk.getI()
        result = halfplanetodisk * matrix * disktohalfplane
        return cls([ [result[0,0],result[0,1]],[result[1,0],result[1,1]] ])

    @classmethod
    def origin(cls):
        '''At the origin of the Poincaré disk looking right (i.e. towards positive reals).'''
        return cls([[1.,0.],[0.,1.]])

    @classmethod
    def forward(cls,distance):
        '''Move forward a distance (or backward if distance is negative).'''
        return cls.fromrealmatrix(np.matrix([[exp(distance/2),0.], [0., exp(-distance/2)]]))

    @classmethod
    def rotate(cls,angle):
        '''Rotate an angle counterclockwise.'''
        return cls([[cos(angle)+sin(angle)*1j,0.],[0.,1.]])

    @classmethod
    def sideways(cls,distance):
        '''Move right a certain distance (or left if distance is negative) while looking at the same point on the horizon.'''
        return cls.fromrealmatrix(np.matrix([[1.,distance], [0., 1.]]))

    @property
    def basepoint(self):
        a,b,c,d = self[0,0],self[0,1],self[1,0],self[1,1]
        return Point(b/d)

    @property
    def tikzline(self):
        x = diskradius*complex(self.basepoint)
        y = diskradius* complex((self*Tangent.forward(tangentsize)).basepoint)
        left = diskradius * complex((self*Tangent.forward(tangentsize)*Tangent.rotate(2*pi/3)*Tangent.forward(tangentsize/3)).basepoint)
        right = diskradius * complex((self*Tangent.forward(tangentsize)*Tangent.rotate(-2*pi/3)*Tangent.forward(tangentsize/3)).basepoint)
        return layerstartstr[self.layer]+'\\draw['+self.color+'] '+'({:.3f},{:.3f})'.format(x.real,x.imag) +' -- '+'({:.3f},{:.3f})'.format(y.real,y.imag)+' -- '+'({:.3f},{:.3f})'.format(left.real,left.imag)+' -- '+'({:.3f},{:.3f})'.format(y.real,y.imag)+' -- '+'({:.3f},{:.3f})'.format(right.real,right.imag)+';'+layerendstr[self.layer]



class Figure(set):
    '''A figure is a set of Points, Tangents, etc, with a writepgf method to output a pgf file.\n'''
    '''It can also be acted on by Tangents (as isometries).'''
    def writepgf(self,filename,drawboundary=True):
        f = open(filename,'w')
        f.write('\\pgfdeclarelayer{background}\n')
        f.write('\\pgfdeclarelayer{foreground}\n')
        f.write('\\pgfsetlayers{background,main,foreground}\n')
        f.write('\\begin{tikzpicture}\n')
        if drawboundary:
            f.write('\\begin{pgfonlayer}{foreground}\\draw (0,0) circle ('+str(diskradius)+');\\end{pgfonlayer}\n')
        for x in self:
            line = x.tikzline
            if line != '':      # Avoid writting empty lines
                f.write(x.tikzline+'\n')
        f.write('\\end{tikzpicture}\n')
        f.close()
    def __rmul__(self,tangent):
        return Figure([tangent*x for x in self])

class Segment():
    '''A segment between two points.'''
    def __init__(self,start,end):
        self.start = start
        self.end = end
        self.color = 'black'
        self.layer = 'main'
    def __str__(self):
        return str((self.start,self.end))
    def __repr__(self):
        return repr((self.start,self.end))

    @property
    def tikzline(self):
        start,end = self.start,self.end
        subdivisions = int(diskradius*10*abs(start-end))+10
        startklein,endklein = complex(start.klein), complex(end.klein)
        points = [Point.fromklein((1-i/subdivisions)*startklein + i*endklein/subdivisions) for i in range(subdivisions+1)]
        # This is kind of a hack
        # As segments are transformed and end up closer to the boundary they get very small
        # This means that we were sometimes outputting lines like \draw (x,y) -- (x,y) -- (x,y) -- (x,y+0.001);
        # To avoid this we make a list of points in the subdivision which have unique strings in the output file
        # If the list has only one element it means the line is two small to see (points coincide up to 3 decimal digits on page).
        # It would be better to avoid calculating all these extra points.
        # But this hack has concrete benefits (e.g. one can now draw all images of a stickman under the transformations in modulagroup(20)
        # whereas before we could only go up to modulargroup(15), the difference is visually noticible).
        x = points[0]
        currentstr = '({:.3f},{:.3f})'.format(diskradius*x.real,diskradius*x.imag)
        pointstrings = [currentstr]
        for x in points[1:]:
            pointstr = '({:.3f},{:.3f})'.format(diskradius*x.real,diskradius*x.imag)
            if pointstr != currentstr:              
                currentstr = pointstr
                pointstrings.append(currentstr)
        if len(pointstrings) == 1:
            return ''   # Avoid outputting segments whose endpoints coincide
        return layerstartstr[self.layer]+'\\draw['+self.color+'] '+' -- '.join(pointstrings)+';'+layerendstr[self.layer]

    def __rmul__(self,tangent):
        s = Segment(tangent*self.start,tangent*self.end)
        s.color = self.color
        return s

class Halfline(Segment):
    '''An infinite halfline starting at a tangent's basepoint and extending in the direction given by the tangent.'''
    def __init__(self,tangent):
        self.start = tangent.basepoint
        start = self.start
        forward = (tangent * Tangent.forward(1)).basepoint
        z = complex(start.klein)
        w = complex(forward.klein)
        u = w-z
        a = abs(u)**2
        b = 2*(z*u.conjugate()).real
        c = abs(z)**2 - 1
        t = (-b + sqrt(b**2 - 4*a*c))/(2*a)
        endklein = z + t*u
        self.end = Point.fromklein(endklein)
        self.color = 'black'
        self.layer = 'main'

    @classmethod
    def fromtwopoints(cls,start,end):
        self = Halfline(Tangent.origin())
        self.start = start
        self.end = end
        self.color = 'black'
        return self

    def __rmul__(self,tangent):
        s = Halfline.fromtwopoints(tangent*self.start,tangent*self.end)
        s.color = self.color
        return s

class Line(Segment):
    '''An infinite line through a given tangent vector.'''
    def __init__(self,tangent):
        base = tangent.basepoint
        forward = (tangent * Tangent.forward(1)).basepoint
        z = complex(base.klein)
        w = complex(forward.klein)
        u = w-z
        a = abs(u)**2
        b = 2*(z*u.conjugate()).real
        c = abs(z)**2 - 1
        t = (-b + sqrt(b**2 - 4*a*c))/(2*a)
        endklein = z + t*u
        self.end = Point.fromklein(endklein)
        t = (-b - sqrt(b**2 - 4*a*c))/(2*a)
        startklein = z+t*u
        self.start = Point.fromklein(startklein)
        self.color = 'black'
        self.layer = 'main'

    @classmethod
    def fromtwopoints(cls,start,end):
        self.start = start
        self.end = end
        self.color = 'black'

    def __rmul__(self,tangent):
        s = Halfline.fromtwopoints(tangent*self.start,tangent*self.end)
        s.color = self.color
        return s


class Circle():
    '''A circle with a given center and radius.'''
    def __init__(self,center,radius):
        self.center = center
        self.radius = radius
        self.color = 'black'
        self.layer = 'main'

    def __str__(self):
        return 'Circle('+str((self.center,self.radius))+')'

    def __repr__(self):
        return 'Circle('+repr((self.center,self.radius))+')'

    @property
    def tikzline(self):
        angle,distance = self.center.polar
        z = complex(Point.frompolar(angle,distance-self.radius))
        w = complex(Point.frompolar(angle,distance+self.radius))
        center = (z+w)/2
        radius = abs(z - center)
        radiusstr = '{:.3f}'.format(diskradius*radius)
        if radiusstr == '0.000':
            return ''               # Avoid outputting circles of radius 0 to the file.
        return layerstartstr[self.layer]+'\\draw['+self.color+'] '+'({:.3f},{:.3f})'.format(diskradius*center.real,diskradius*center.imag)+' circle '+'({:.3f})'.format(diskradius*radius)+';'+layerendstr[self.layer]
        

    def __rmul__(self,tangent):
        '''Tangents acting on points as isometries.'''
        result = Circle(tangent*self.center,self.radius)
        result.color = self.color
        result.layer = self.layer
        return result

class Disk(Circle):
    '''A disk (or filled circle) with a given center and radius.'''
    def __init__(self,center,radius):
        self.center = center
        self.radius = radius
        self.color = 'black'
        self.layer = 'background'

    def __str__(self):
        return 'Disk('+str((self.center,self.radius))+')'

    def __repr__(self):
        return 'Disk('+repr((self.center,self.radius))+')'

    @property
    def tikzline(self):
        angle,distance = self.center.polar
        z = complex(Point.frompolar(angle,distance-self.radius))
        w = complex(Point.frompolar(angle,distance+self.radius))
        center = (z+w)/2
        radius = abs(z - center)
        radiusstr = '{:.3f}'.format(diskradius*radius)
        if radiusstr == '0.000':
            return ''               # Avoid outputting circles of radius 0 to the file.
        return layerstartstr[self.layer]+'\\draw['+self.color+', fill='+self.color+'] '+'({:.3f},{:.3f})'.format(diskradius*center.real,diskradius*center.imag)+' circle '+'({:.3f})'.format(diskradius*radius)+';'+layerendstr[self.layer]

    def __rmul__(self,tangent):
        '''Tangents acting on points as isometries.'''
        result = Disk(tangent*self.center,self.radius)
        result.color = self.color
        result.layer = self.layer
        return result

def modulargroup(n):
    '''Generator for elements of length n or less in the modular group with respect to the generating set\n'''
    '''{a = Tangent.rotate(pi), b=Tangent.rotate(pi)*Tangent.sideways(1), b**2}.'''
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

def stickman(size=1):
    '''Returns a (rudimentary) stickman figure at the origin.'''
    head = Circle((Tangent.rotate(pi/2)*Tangent.forward(0.75*size)).basepoint,0.25*size)
    stick = Segment(Point(0),(Tangent.rotate(pi/2)*Tangent.forward(0.5*size)).basepoint)
    leftleg = Segment(Point(0),(Tangent.rotate(-pi/3)*Tangent.forward(0.5*size)).basepoint)
    rightleg = Segment(Point(0),(Tangent.rotate(-pi/2 - pi/10)*Tangent.forward(0.5*size)).basepoint)
    armbase = (Tangent.rotate(pi/2)*Tangent.forward(0.4*size)).basepoint
    leftarmend = (Tangent.rotate(pi/2)*Tangent.forward(0.4*size)*Tangent.rotate(-2*pi/3)*Tangent.forward(0.4*size)).basepoint
    rightarmend = (Tangent.rotate(pi/2)*Tangent.forward(0.4*size)*Tangent.rotate(-pi-pi/10)*Tangent.forward(0.4*size)).basepoint
    leftarm = Segment(armbase,leftarmend)
    rightarm = Segment(armbase,rightarmend)
    eye = Disk(Point.frompolar(angle=pi/2-pi/20, radius=0.8*size),radius=0.02*size)
    return Figure([head,stick,rightleg,leftleg,leftarm,rightarm,eye])

def stickmaninmodulargroup(n=10,name='test3.pgf'):
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


def stickmanwalkinmodulargroup(name='1.pgf',n=10,walksteps=10):
    '''Another example figure which illustrates a random walk in the modular group.'''
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

    startpoint = Tangent.forward(0.3).basepoint
    current = Tangent.origin()
    last = Tangent.origin()
    f.add(startpoint)
    for i in range(walksteps):
        last,current = current, current * choice([Tangent.sideways(1),Tangent.sideways(-1),Tangent.rotate(pi)])
        s = Segment(last*startpoint,current*startpoint)
        s.color = 'gray'
        f.add(s)
        f.add(current*startpoint)

    f.update(current*stick)
    
    f.writepgf(name)
    
