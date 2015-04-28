# Dibujos Hiperbólicos
A Python tool to create drawings in the hyperbolic disk for inclusion in LaTex documents.  
The output is a Tikz figure (a .pgf file).  
I usually use KTikz to get eps, pdf, and pgn figures from this.

## Example usage

 Example usage:
 Open dibujos.py in Idle and press f5 (run the interactive interpreter).
 
        >>> p1 = Point.frompolar(radius=1,angle=0)
        >>> p2 = Point.frompolar(radius=1,angle = 2*pi/3)
        >>> p3 = Point.frompolar(radius=1,angle = -2*pi/3)
        >>> f = Figure([p1,p2,p3])
        >>> f.add(Segment(p1,p2))
        >>> f.add(Segment(p2,p3))
        >>> f.add(Segment(p3,p1))
        >>> f.writepgf('test.pgf')

 This generates the file 'test.pgf' containing a Tikz figure of a hyperbolic triangle.
 Viewing this in KTikz one can get a png,eps, or pdf file.
 
 ![test.pgn](/test.png)
 
 
 You can easily change the color of segments or points by changing the color attribute.
 For example:
 
        >>> s1 = Segment(p1,p2)
        >>> s1.color = 'red'
        >>> s2 = Segment(p2,p3)
        >>> s2.color = 'orange'
        >>> s3 = Segment(p3,p1)
        >>> s3.color = 'blue'
        >>> g = Figure([p1,p2,p3,s1,s2,s3])
        >>> g.writepgf('test2.pgf')

 Generates a similar Tikz figure but with colored edges.

 ![test2.pgn](/test2.png)


 Obviously things get more interesting when you use Python to generate the figure proceeduraly.
 An example of this can be obtained by calling shiqz(100) which generates a file 'shiqz.pgf'.

        >>> stickmaninmodulargroup()
 
  ![test3.pgn](/test3.png)

 
 The drawable objects are Tangent, Point, Segment, Halfline, Line, Circle, and Disk.
 A Figure is a subclass of Set and is pretty much just a set of drawable objects with a writepgf function.

 Points represent points in the hyperbolic plane.  I provide several constructors some examples are:
 Point.frompolar(radius,angle)   constructs from polar coordinates.
 Point.fromupper(complex)    constructs from a point in the upper half plane (complex number)
 Point.fromtangent(tangent) constructs from a unit tangent vector (more later)

 Segments can so far only be constructed from two points.  Halflines and Lines are supposed to be constructed
 from a Tangent object (a unit tangent vector) whose basepoint is the starting point of the Halfline and just
 a point on the Line in the other case (its direction indicated the direction of the Halfline or line).

 The Tangent class serves two puposes.   They represent unit tangent vectors and also isometries of the hyperbolic plane.
 The constructor

        >>> Tangent.origin()

 yields the Tangent representing being at the center of the disk looking right (towards the positive real numbers).  And the
 identity tranformation.

 Other tangents can be constructed conveniently form a series of instructions for example:

        >>> Tangent.forward(1)*Tangent.rotate(pi/2)*Tangent.forward(2)
 
 is the unit tangent vector obtained from Tangent.origin() by going forward along the geodesic flow for 1 unit then turning 
 counter-clockwise a right angle and then moving along the geodesic flow for two units.

 The tangent vector Tangent.sideways(1) is on the same horocycle of Tangent.origin() and to the right 1 unit (it can also
 be included in multiplication chains as above). 

 Any unit tangent vector can be obtained by multiplying those obtained from the given constructors as above.

 The basepoint of a tangent vector is an attribute.  For example

        >>> Tangent.origin().basepoint
 
 returns the Point representing the center of the disk.

 Tangents also act on Points, Segments, Halflines, Lines, Circles, Disks, and Figures by left multiplication.  They act like the unique
 isometry of the hyperbolic plane taking the tangent vector Tangent.origin() to the given tangent vector.

 As an example consider:

        >>> stick = stickman(size=0.5)
        >>> g = Figure()
        >>> for i in range(-5,6):
				g.update(Tangent.forward(i)*stick)
        >>> g.writepgf('test4.pgf')

Which generates the following figure:

 ![test4.pgn](/test4.png)

We provide the generator modulargroup(n) for the ball of radius n in the modular group.  As an example consider:

		>>> g = Figure()
		>>> stick = Tangent.forward(0.5)*stickman(size=0.3)
		>>> for t in modulargroup(12):
				g.update(t*stick)	
		>>> g.writepgf('test5.pgf')

 ![test5.pgn](/test5.png)

