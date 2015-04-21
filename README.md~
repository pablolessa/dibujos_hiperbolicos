# dibujos_hiperbolicos
A python tool to create drawings in the hyperbolic disk for inclusion in LaTex documents.  
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

 Obviously things get more interesting when you use Python to generate the figure proceeduraly.
 An example of this can be obtained by calling shiqz(100) which generates a file 'shiqz.pgf'.
 
 So far I have 3 types of drawable objects, Point, Segment, and Figure.
 A Figure is a subclass of Set and is pretty much just a set of Points, Segments and possibly other Figures.
 It has a special writepgf function.

 Points represent points in the hyperbolic plane.  At the moment they are complex numbers representing
 the point in the upper half plane model.   But I plan to change that for technical reasons.  I provide several constructors.
 Point.frompolar(radius,angle)   constructs from polar coordinates.
 Point.fromupper(complex)    constructs from a point in the upper half plane (complex number)
 Point.fromtangent(tangent) constructs from a unit tangent vector (more later)

 Segments can so far only be constructed from two points.  Al segments are of finite hyperoblic length.
 There are so far no half lines or lines but I plan to add classes for them later (good for drawings of
 of the modular group for example).  Also a Circle class would be nice.

 The Tangent class is not drawable.  It is a subclass of numpy.matrix.   The elements are supposed to
 represent unit tangent vectors in the hyperbolic plane and also isometries of the plane.

 Tangent.origin()

 Is the tangent vector associated to being in the center of the disk looking right.
 One can construct a tangent vector from instructions (like a turtle graphics type thing) as follows:

        >>> t = Tangent.frominstructions(startangle=pi/2,forward=1,rotate = -pi/2)

 The constructor takes 3 moves to be followed in order (starting at Tangent.origin())
 , the first is rotation angle, the second is how much (hyperbolic distance) to move forward,
 the third is a rotation angle.

 Any unit tangent vector can be obtained in this way.

 You can get the basepoint using the fromtangent constructor of Point.
        >>> p = Point.fromtangent(t)

 Tangents also act on Points, Segments, and Figures by left multiplication.  They act like the unique
 isometry of the hyperbolic plane taking the tangent vector Tangent.origin() to the given tangent vector.

 For example continuing the above examples one might do:

        >>> newfigure = t*g
        >>> newfigure.add(p)
        >>> newfigure.writepgf('test3.pgf')

 In the resulting figure the colored triangle is translated (with respect to test2.pgf)
 and a black point appears in its (hyperbolic) center.



