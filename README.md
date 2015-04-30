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
 The resulting file could be included into a LaTex document directly (using the Tikz package) but 
 it's more convenient to use a program such as KTikz to preview the result and generate png,eps, or pdf files as needed.
 
 ![test.pgn](/test.png)
 
## Colors
 
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

 We provide functions to change the color attribute of drawable objects.  So the above example could've been written as follows:

        >>> s1 = Red(Segment(p1,p2))
        >>> s2 = Orange(Segment(p2,p3))
        >>> s3 = Blue(Segment(p3,p1))
        >>> g = Figure([p1,p2,p3,s1,s2,s3])
        >>> g.writepgf('test2.pgf')

 The supported colors are:  Red Green Blue Cyan Magenta Yellow Black Gray Darkgray Lightgray Brown Lime Olive Orange Pink Purple Teal Violet White.

 One caveat is that one can not apply any of the color functions to a figure (for example with the intent of changing the color of all drawables in
 the figure).  Instead one might use:

        >>> for drawable in figure:
				Red(drawable)

 to achive the same effect.

## An example


 Obviously things get more interesting when you use Python to generate the figure proceeduraly.
 For an example of this inspect the stickmaninmodulargroup() function.

        >>> stickmaninmodulargroup()
 
  ![test3.pgn](/test3.png)


## Drawables
 
 The drawable objects are Tangent, Point, Segment, Halfline, Line, Circle, and Disk.
 A Figure is a subclass of Set and is pretty much just a set of drawable objects with a writepgf function.

 Points represent points in the hyperbolic plane.  I provide several constructors some examples are:
 Point.frompolar(radius,angle)   constructs from polar coordinates.
 Point.fromupper(complex)    constructs from a point in the upper half plane (complex number)
 
 Another useful way of getting points is by using the .basepoint attribute of a Tangent (more on these later).
 In short if t is Tangent respresenting some tangent vector then t.basepoint is a Point representing its basepoint.


 Segments can so far only be constructed from two points.  Halflines and Lines are supposed to be constructed
 from a Tangent object (a unit tangent vector) whose basepoint is the starting point of the Halfline and just
 a point on the Line in the other case (its direction indicated the direction of the Halfline or line).

## Tangents and isometries

 The Tangent class serves two puposes.   They represent unit tangent vectors and also isometries of the hyperbolic plane.
 The constructor

        >>> Tangent.origin()

 yields the Tangent representing being at the center of the disk looking right (towards the positive real numbers).  And the
 identity tranformation.

 Other tangents can be constructed conveniently from a series of instructions for example:

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

## The modular group

We provide the generator modulargroup(n) for the ball of radius n in the modular group.  As an example consider:

		>>> g = Figure()
		>>> stick = Tangent.forward(0.5)*stickman(size=0.3)
		>>> for t in modulargroup(12):
				g.update(t*stick)	
		>>> g.writepgf('test5.pgf')

 ![test5.pgn](/test5.png)

## Layers

 Each drawable object belongs to one of the three layers 'background', 'main', or 'foreground' (where main is the middle layer).   
 The layer an object belongs to is stored in its .layer attribute and can be changed at will.  

 Objects on the same layer will be drawn in a random order (because a figure is a subclass of set Python sets are unordered).  Maybe
 in the future this will be changed by implementing some sort of ordered set subclass (I know there's a recipe for this out there).
 
 For convenience (as with colors) we have provided the functions Background(drawable), Mainlayer(drawable) and Foreground(drawable)
 to change the layer of a drawable object. These can be used at the time of construction or later on.

 By default Points and Tangents belong to the main layer and all other drawables to the background.  

 To illustrate the use of layers consider the following randomly generated figure:

		>>> from random import choice
		>>> f = Figure()
		>>> for i in range(20):
				d = Tangent.rotate(2*pi*i/20)*Tangent.forward(2)*Disk(Point(0),0.6)
				d.color = choice(['teal','magenta','cyan'])
				f.add(d)	
		>>> f.writepgf('test6.pgf')

 ![test6.pgn](/test6.png)

 We can force the 'teal' colored disks to be in the foreground, the 'magenta' colored ones in the middle, and the 'cyan' colored disks
 to the background as follows (the variable y's only purpose is to avoid a long printout of return values of the layer functions, the code also works without it):

		>>> for x in f:
				if x.color == 'teal':
					y = Foreground(x)
				if x.color == 'magenta':
					y = Mainlayer(x)
				if x.color == 'cyan':
					y = Background(x)
		>>> f.writepgf('test7.pgf')

 ![test7.pgn](/test7.png)
 


