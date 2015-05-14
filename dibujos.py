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

# To begin we define the radii of the boundary circle for pgf and svg output figures.
# Even though both are vector formats this affects the output because
# lines have a certain width (0.0015cm for pgf figures and 1 pixel for svg).

pgfdiskradius = 3.
svgdiskradius = 300

# The following control the appearance of Point, Boundarypoint, and Tangent drawables.
# pointsize*pgfdiskradius is the size of a point at the origin or a boundary point in the pgf file.
# pointsize*svgdiskradius plays a similar role for svg output.
# tangentsize is a hyperbolic length of arrows used to represent tangent vectors.

pointsize = 0.016
tangentsize = 0.15

# Things smaller than this proportion of the radius of the disk are not drawn.

smallestsize = 0.01*2*pi/360

# Geodesic segments who turn less than this angle are drawn as Euclidean segments.

smallestangle = 2*pi/360

# Here we define the following 19 functions:
# Red Green Blue Cyan Magenta Yellow Black Gray Darkgray Lightgray Brown Lime Olive Orange Pink Purple Teal Violet White

# They can be applied to drawables and act by changing the .color attribute and returning the result, 
# so for example Red(Point(0)) yields a red point at the origin.

# The 19 functions are defined by using the infamous exec statement in a for loop.
# They have docstrings.

colors = 'red green blue cyan magenta yellow black gray darkgray lightgray brown lime olive orange pink purple teal violet white'.split()
for c in colors:
    exec('def '+c.capitalize()+'(drawable):\n\tdrawable.color = '+"'"+c+"'"+'\n\t'+'return drawable\n')
    exec(c.capitalize()+'.__doc__ = '+'"'+c.capitalize()+'(drawable) Changes the .color attribute of the drawable to '+c+'.\\n It also returns the object so, for example, '+c.capitalize()+'(Tangent.origin()) returns a '+c+' tangent object at the origin."')

 
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

# Finally, we start with the actual classes.  The drawables are Tangent, Point, Boundarypoint, Circle, Disk, Segment, Halfline, Line.
# The Figure class is a subclass of set and instances are supposed to hold drawables.
# In particular if f is a figure you use f.add(drawable) to add a drawable to it but f.update(g) to add all drawables in some other figure g.
# Each drawable has a .tikzline and a .svgline attribute which are used by the Figure writepgf and writesvg methods respectively.

class Figure(set):
    '''A figure is a set of Points, Tangents, etc, with a writepgf method to output a pgf file.
    
    It can also be acted on by Tangents (as isometries).'''
    def writepgf(self,filename,drawboundary=True):
        f = open(filename,'w')
        f.write('\\pgfdeclarelayer{background}\n')
        f.write('\\pgfdeclarelayer{foreground}\n')
        f.write('\\pgfsetlayers{background,main,foreground}\n')
        f.write('\\begin{tikzpicture}\n')

        if drawboundary:
            f.write('\\begin{pgfonlayer}{foreground}\\draw (0,0) circle ('+str(pgfdiskradius)+');\\end{pgfonlayer}\n')
        
        layerstartstr = {'background':'\n\\begin{pgfonlayer}{background}\n','main':'\n','foreground':'\n\\begin{pgfonlayer}{foreground}\n'}
        layerendstr = {'background':'\\end{pgfonlayer}\n','main':'','foreground':'\\end{pgfonlayer}\n'}

        for layer in ['background','main','foreground']:
            f.write(layerstartstr[layer])
            for x in self:
                if x.layer == layer:
                    line = x.tikzline
                    if line != '':      # Avoid writting empty lines
                        f.write(x.tikzline+'\n')
            f.write(layerendstr[layer])

        f.write('\\end{tikzpicture}\n')
        f.close()

    def writesvg(self,filename,drawboundary=True):
        f = open(filename,'w')
        size = int(3*svgdiskradius)
        f.write('<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}" version="1.1">\n'.format(str(size),str(size)))
        # the y-coordinate needs to be flipped because in svg it grows downwards this is done with scale(1,-1)
        f.write('<g transform="translate({} {}) scale(1,-1)">'.format(str(size//2),str(size//2)))

        if drawboundary:
            f.write('<circle cx="0" cy="0" r="{}" fill="none" stroke="black"/>'.format(str(int(svgdiskradius))))
        
        for layer in ['background','main','foreground']:
            for x in self:
                if x.layer == layer:
                    line = x.svgline
                    if line != '':      # Avoid writting empty lines
                        f.write(x.svgline+'\n')

        f.write('</g>')
        f.write('</svg>')
        f.close()

    def __rmul__(self,tangent):
        return Figure([tangent*x for x in self])

class Tangent(np.matrix):
    '''Tangents represent both unit tangent vectors in the disk and hyperbolic isometries.
    
    Hence they can be drawn (as a small arrow) but also can act by multiplication on other drawables (including other tangents)
    Several constructors are provided.  Tangent.origin(), Tangent.forward(d), Tangent.rotate(a), Tangent.sideways(d).
    A useful pattern is to create a tangent out of "instructions" e.g. t = Tangent.forward(1)*Tangent.rotate(pi/2)*Tangent.forward(2)*Tangent.rotate(pi/3).'''
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
        x = pgfdiskradius*complex(self.basepoint)
        y = pgfdiskradius* complex((self*Tangent.forward(tangentsize)).basepoint)
        if (abs(x-y) < smallestsize*pgfdiskradius):
            return ''
        left = pgfdiskradius * complex((self*Tangent.forward(tangentsize)*Tangent.rotate(2*pi/3)*Tangent.forward(tangentsize/3)).basepoint)
        right = pgfdiskradius * complex((self*Tangent.forward(tangentsize)*Tangent.rotate(-2*pi/3)*Tangent.forward(tangentsize/3)).basepoint)
        return '\\draw['+self.color+'] '+'({:.3f},{:.3f})'.format(x.real,x.imag) +' -- '+'({:.3f},{:.3f})'.format(y.real,y.imag)+' -- '+'({:.3f},{:.3f})'.format(left.real,left.imag)+' -- '+'({:.3f},{:.3f})'.format(y.real,y.imag)+' -- '+'({:.3f},{:.3f})'.format(right.real,right.imag)+';'

    @property
    def svgline(self):
        x = svgdiskradius*complex(self.basepoint)
        y = svgdiskradius* complex((self*Tangent.forward(tangentsize)).basepoint)
        if (abs(x-y) < smallestsize*svgdiskradius):
            return ''
        left = svgdiskradius * complex((self*Tangent.forward(tangentsize)*Tangent.rotate(2*pi/3)*Tangent.forward(tangentsize/3)).basepoint)
        right = svgdiskradius * complex((self*Tangent.forward(tangentsize)*Tangent.rotate(-2*pi/3)*Tangent.forward(tangentsize/3)).basepoint)
        return '<path d="{}" fill="none" stroke="{}"/>'.format(' L'.join(['M{:.3f},{:.3f}'.format(x.real,x.imag),'{:.3f},{:.3f}'.format(y.real,y.imag), '{:.3f},{:.3f}'.format(left.real,left.imag),'{:.3f},{:.3f}'.format(y.real,y.imag),'{:.3f},{:.3f}'.format(right.real,right.imag) ]), self.color)


class Point(complex):
    '''A point in the Poincaré disk model of the hyperbolic plane.
    
    Basically a complex number of modulus less than 1.
    You can construct them with modulus 1 (points at infinity or boundary points),
    But some methods (such as p.hyperboloid) will fail (yielding infinite values.'''

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
        if (pointsize/2)*(1-abs(complex(self))**2) < smallestsize:
            return ''
        x = pgfdiskradius*complex(self)
        size = pgfdiskradius*(pointsize/2)*(pgfdiskradius**2-abs(x)**2)/pgfdiskradius**2
        sizestr = '{:.3f}'.format(size)  
        if sizestr ==  '0.000':
            return ''                       # We avoid outputting points of radius (0.000).
        return '\\draw[fill='+self.color+','+self.color+'] '+'({:.3f},{:.3f})'.format(x.real,x.imag)+' circle '+'({:.3f})'.format(size)+';'

    @property
    def svgline(self):
        if (pointsize/2)*(1-abs(complex(self))**2) < smallestsize:
            return ''
        x = svgdiskradius*complex(self)
        size = svgdiskradius*(pointsize/2)*(svgdiskradius**2-abs(x)**2)/svgdiskradius**2
        sizestr = '{:.3f}'.format(size)
        if sizestr ==  '0.000':
            return ''                       # We avoid outputting points of radius (0.000).
        return '<circle cx="{:.3f}" cy="{:.3f}" r="{:.3f}" fill="{}" stroke="{}"/>'.format(x.real,x.imag,size,self.color,self.color)

    def __rmul__(self,tangent):
        '''Tangents acting on points as isometries.'''
        a,b,c,d = tangent[0,0],tangent[0,1],tangent[1,0],tangent[1,1]
        z = complex(self)
        result = Point((a*z+b)/(c*z+d))
        result.color = self.color
        result.layer = self.layer
        return result

class Boundarypoint():
    '''Boundary points represent points on the boundary circle.

    They are constructed by giving an angle'''
    def __init__(self, angle):
        '''Construct the boundary point e^{i angle}.'''
        self.angle = angle
        self.color = 'black'
        self.layer = 'foreground'

    def __repr__(self):
        return 'Boundarypoint(angle={:.3f})'.format(self.angle)

    def __str__(self):
        return 'Boundarypoint(angle={:.3f})'.format(self.angle)

    def __complex__(self):
        return cos(self.angle) + sin(self.angle)*1j

    @property
    def tikzline(self):
        x = pgfdiskradius*complex(self)
        size = pgfdiskradius*(pointsize/2)
        return '\\draw[fill='+self.color+','+self.color+'] '+'({:.3f},{:.3f})'.format(x.real,x.imag)+' circle '+'({:.3f})'.format(size)+';'

    @property
    def svgline(self):
        x = svgdiskradius*complex(self)
        size = svgdiskradius*(pointsize/2)
        return '<circle cx="{:.3f}" cy="{:.3f}" r="{:.3f}" fill="{}" stroke="{}"/>'.format(x.real,x.imag,size,self.color,self.color)

    def __rmul__(self,tangent):
        '''Tangents acting on points as isometries.'''
        a,b,c,d = tangent[0,0],tangent[0,1],tangent[1,0],tangent[1,1]
        z = complex(self)
        result = Boundarypoint(np.angle((a*z+b)/(c*z+d)))
        result.color = self.color
        result.layer = self.layer
        return result

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
        if 2*radius < smallestsize:
            return ''
        radiusstr = '{:.3f}'.format(pgfdiskradius*radius)
        if radiusstr == '0.000':
            return ''               # Avoid outputting circles of radius 0 to the file.
        return '\\draw['+self.color+'] '+'({:.3f},{:.3f})'.format(pgfdiskradius*center.real,pgfdiskradius*center.imag)+' circle '+'({:.3f})'.format(pgfdiskradius*radius)+';'

    @property
    def svgline(self):
        angle,distance = self.center.polar
        z = complex(Point.frompolar(angle,distance-self.radius))
        w = complex(Point.frompolar(angle,distance+self.radius))
        center = (z+w)/2
        centerxstr = '{:.3f}'.format(svgdiskradius*center.real)
        centerystr = '{:.3f}'.format(svgdiskradius*center.imag)
        radius = abs(z - center)
        if 2*radius < smallestsize:
            return ''
        radiusstr = '{:.3f}'.format(svgdiskradius*radius)
        if radiusstr == '0.000':
            return ''               # Avoid outputting circles of radius 0 to the file.
        return '<circle cx="{}" cy="{}" r="{}" fill="none" stroke="{}"/>'.format(centerxstr,centerystr,radiusstr,self.color)
        

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
        if 2*radius < smallestsize:
            return ''
        radiusstr = '{:.3f}'.format(pgfdiskradius*radius)
        if radiusstr == '0.000':
            return ''               # Avoid outputting circles of radius 0 to the file.
        return '\\draw['+self.color+', fill='+self.color+'] '+'({:.3f},{:.3f})'.format(pgfdiskradius*center.real,pgfdiskradius*center.imag)+' circle '+'({:.3f})'.format(pgfdiskradius*radius)+';'

    @property
    def svgline(self):
        angle,distance = self.center.polar
        z = complex(Point.frompolar(angle,distance-self.radius))
        w = complex(Point.frompolar(angle,distance+self.radius))
        center = (z+w)/2
        centerxstr = '{:.3f}'.format(svgdiskradius*center.real)
        centerystr = '{:.3f}'.format(svgdiskradius*center.imag)
        radius = abs(z - center)
        if 2*radius < smallestsize:
            return ''
        radiusstr = '{:.3f}'.format(svgdiskradius*radius)
        if radiusstr == '0.000':
            return ''               # Avoid outputting circles of radius 0 to the file.
        return '<circle cx="{}" cy="{}" r="{}" fill="{}" stroke="{}"/>'.format(centerxstr,centerystr,radiusstr,self.color,self.color)


    def __rmul__(self,tangent):
        '''Tangents acting on points as isometries.'''
        result = Disk(tangent*self.center,self.radius)
        result.color = self.color
        result.layer = self.layer
        return result


class Segment(object):
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

    def __rmul__(self,tangent):
        result = Segment(tangent*self.start,tangent*self.end)
        result.color = self.color
        result.layer = self.layer
        return result

    @property
    def boundarypoints(self):
        '''Returns the boundary points of the geodesic containing the segment'''
        start, end = complex(self.start), complex(self.end)
        startklein, endklein = complex(Point(start).klein), complex(Point(end).klein)
        a, b, c = abs(endklein-startklein)**2, 2*((endklein-startklein)*startklein.conjugate()).real, abs(startklein)**2 -1
        tplus, tminus = -b/(2*a) + sqrt(b**2 - 4*a*c)/(2*a), -b/(2*a) - sqrt(b**2 - 4*a*c)/(2*a)
        startboundary, endboundary = startklein + tminus*(endklein-startklein), startklein + tplus*(endklein-startklein)
        return Boundarypoint(np.angle(startboundary)),Boundarypoint(np.angle(endboundary))

    @property
    def center(self):
        '''Center of the Euclidean circle the segment belongs to.'''
        boundary1, boundary2 = self.boundarypoints
        complex1, complex2 = complex(boundary1), complex(boundary2)
        tangent = tan(np.angle(complex2/complex1)/2)
        return complex1 + tangent* (complex1*1j)

    @property
    def tikzline(self):
        # check if the end points are too close to draw
        start, end = complex(self.start), complex(self.end)
        if abs(start-end) < smallestsize:
            return ''
        # If they are not get the string for each point.
        pointstrings = ['({:.3f}, {:.3f})'.format(pgfdiskradius*p.real,pgfdiskradius*p.imag) for p in [start,end]]
        
        # check if the boundarypoints are almost opposite so we can draw a straight line
        boundarypoints = self.boundarypoints
        boundary1, boundary2 = complex(boundarypoints[0]), complex(boundarypoints[1])
        if abs(np.angle(-boundary2/boundary1)) < smallestangle:
            return '\\draw['+self.color+'] '+' -- '.join(pointstrings)+';'

        # If they are not we get the center of the Euclidean circle the geodesic is on.
        center = self.center
        radius = pgfdiskradius*abs(start-center)
        startangle = 360*np.angle(start-center)/(2*pi)
        # make sure the difference between startangle and endangle is less than 180
        endangle = startangle + 360*np.angle((end-center)/(start-center))/(2*pi)

        return '\\draw['+self.color+'] '+ pointstrings[0] +' arc ' + '({:.3f}:{:.3f}:{:.3f});'.format(startangle,endangle,radius)

    @property
    def svgline(self):
        # check if the end points are too close to draw
        start, end = complex(self.start), complex(self.end)
        if abs(start-end) < smallestsize:
            return ''
        # If they are not get the string for each point.
        pointstrings = ['{:.3f},{:.3f}'.format(svgdiskradius*p.real,svgdiskradius*p.imag) for p in [start,end]]
        pointstrings[0] = 'M'+pointstrings[0]
        pointstrings[1] = 'L'+pointstrings[1]
        
        # check if the boundarypoints are almost opposite so we can draw a straight line
        boundarypoints = self.boundarypoints
        boundary1, boundary2 = complex(boundarypoints[0]), complex(boundarypoints[1])
        if abs(np.angle(-boundary2/boundary1)) < smallestangle:
            return '<path d="{}" fill="none" stroke="{}"/>'.format(''.join(pointstrings),self.color)

        # We're not going to line_to so we need to remove the leading L from the string for the second point
        pointstrings[1] = pointstrings[1][1:]

        # Get the center of the Euclidean circle the geodesic is on.
        center = self.center
        radius = svgdiskradius*abs(start-center)

        angle = 360*np.angle((end-center)/(start-center))/(2*pi)

        # Svg needs the start point, endpoint radius (actually x and y radius both equal in our case),
        # rotation of x axis (0 in our case),
        # a flag noting if the long arc is drawn or the short one (0 for short arc is always our case),
        # and one flat determines which side the center is on (the one we will set now)
        # If you do this wrong either Segment(p,q) or Segment(q,p) will bend in the wrong direction.
        if angle <= 0:
            sweepflag = '0'
        else:
            sweepflag = '1'
        d = pointstrings[0]+ ' A{:3f},{:3f} 0 0 {} '.format(radius,radius, sweepflag)+pointstrings[1]

        return '<path d="{}" fill="none" stroke="{}"/>'.format(d,self.color)


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
        self.end = Boundarypoint(np.angle(endklein))
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
        result = Halfline.fromtwopoints(tangent*self.start,tangent*self.end)
        result.color = self.color
        result.layer = self.layer
        return result

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
        self.end = Boundarypoint(np.angle(endklein))
        t = (-b - sqrt(b**2 - 4*a*c))/(2*a)
        startklein = z+t*u
        self.start = Boundarypoint(np.angle(startklein))
        self.color = 'black'
        self.layer = 'main'

    @classmethod
    def fromtwopoints(cls,start,end):
        self = Line(Tangent.origin())
        self.start = start
        self.end = end
        self.color = 'black'
        return self

    def __rmul__(self,tangent):
        result = Line.fromtwopoints(tangent*self.start,tangent*self.end)
        result.color = self.color
        result.layer = self.layer
        return result


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

def permutation(genus=2):
    '''Edge identifications of a 4*genus-gon for constructions of a surface of genus g.

    Labeling the sides 0, 1, 2, .., 4*genus-1 we return a dictionary such that
    where edge i is identified with edge d[i].

    If genus=2 you get d = {0:2, 2:0, 1:3, 3:1, 4:6, 6:4, 5:7, 7:5}'''
    d = {0:2, 2:0, 1:3, 3:1}
    for i in range(1,genus):
        d[4*i] = 4*i+2
        d[4*i+1] = 4*i+3
        d[4*i+2] = 4*i
        d[4*i+3] = 4*i+1
    return d

def midpointtangents(genus=2):
    '''Returns a list of tangents representing outer normals at the midpoints of the sides
    of a regular 4*genus-gon with interior angles 2*pi/4*genus.'''
    r = acosh(1/tan(pi/(4*genus)))
    return [Tangent.rotate(2*pi*i/(4*genus))*Tangent.forward(r) for i in range(4*genus)]

def transformationlist(genus=2):
    '''Returns a list of Tangents which identify the sides of the 4*genus-gon.

    The i-th transformation sends side permutation(genus)[i] to i.'''
    midpoints = midpointtangents(genus)
    perm = permutation(genus)

    return [midpoints[i]*Tangent.rotate(pi)*(midpoints[perm[i]]**(-1)) for i in range(4*genus)]

def getrelations(genus=2):
    '''Returns a list of tuples of indices which are to be avoided in a product of generators
    if one wants each element of the surface group to be expressed only once.

    The theoretical justification is what's called Dehn's algorithm.'''
    perm = permutation(genus)
    relations = list(perm.items()) # start with the (transformation,inverse) pairs
    # now add 2*genus+1 counterclockwise turns around each vertex
    # and the 2*genus clockwise ones
    for start in range(4*genus):
        current = start
        counterclockwise = []
        for i in range(2*genus+1):
            counterclockwise.append(current)
            current = (perm[current]-1)%(4*genus)
        relations.append(tuple(counterclockwise))
    
    for start in range(4*genus):
        current = start
        clockwise = []
        for i in range(2*genus):
            clockwise.append(current)
            current = (perm[current]+1)%(4*genus)
        relations.append(tuple(clockwise))
    return relations


def surfacegroup(n,genus=2):
    '''Generates the ball of radius n in the fundamental group of the surface of the given genus.'''
    if n < 0:
        return
    perm = permutation(genus)
    transform = transformationlist(genus)
    relations = getrelations(genus)

    def tupletotangent(t):
        result = Tangent.origin()
        for i in t:
            result = result*transform[i]
        return result

# The following implementation sucks harry balls.
# I should do something smarter e.g. extend tuples from previous generation checking to not add a relation.
# Or even actually smart (like the finite state machine everybody on the planet knows I should be implementing).
# It'll still be an exponential runtime but we should be able to go deep enough to get a good picture instantly.
# Depth 5 seems more or less indistinguishable from infinity in print I think. 
# Another option (Beneath my dignity?) is to precalculate some moderate good looking depth.
    for i in range(n+1):
        for t in product(range(4*genus), repeat= i):   
            for r in relations:                      
                if r in [t[i:i+len(r)] for i in range(1+len(t)-len(r))]:
                    break
            else:
                # Para testear las palabras generadas en el bitoro descomentar la siguiente linea
                #print(''.join(['abABcdCD'[i] for i in t]))
                yield tupletotangent(t)


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

def stickmaninsurfacegroup(n=4, name='1'):
    r = acosh(1/tan(pi/8))
    t = Tangent.forward(r)*Tangent.rotate(pi/2)*Tangent.forward(r)
    p = t.basepoint
    alpha,R = p.polar
    p = Point.frompolar(angle=alpha,radius=R)
    points = [Tangent.rotate(2*pi*i/8)*p for i in range(8)]
    segments = [Segment(points[i],points[(i+1)%8]) for i in range(-1,7)]
    for i,c in enumerate('red blue red blue orange teal orange teal'.split()):
        segments[i].color = c
    s = stickman()
    s.update([segments[0],segments[1],segments[4],segments[5]])
    f = Figure()
    for t in surfacegroup(n):
        f.update(t*s)
    f.writepgf(name+'.pgf')
    f.writesvg(name+'.svg')

