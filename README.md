# Dibujos Hiperbólicos

Dibujos hiperbólicos is a Python tool for creating figures in the Poincaré disk model of the  hyperbolic plane.

The output is either a Tikz figure (a .pgf file to be used with the Tikz LaTex package) or an SVG.

The pgf files outputed can be used directly from LaTex via the Tikz package.  I usually use a program such as KTikz to preview pgf files and get eps, pdf, and pgn figures from them.

The svg format is very well supported by web browsers.  One can also edit and convert these types of files using programs such as Inkscape.

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
        >>> f.writepgf('test1.pgf')

 This generates the file 'test.pgf' containing a Tikz figure of a hyperbolic triangle.  I've used Ktikz on this to generate the png you see below.  Similarly calling "f.writesvg('test.svg')" would generate an SVG figure directly.  Everything written below applies to both methods of output.  The main difference is that complicated figures can hit Tex's 5MB memory limit with their pgf output.  Hence in these situations generating svg files is preferable (programs like Inscape can convert to eps and pdf formats if the intended use is to include the figure in a LaTex document).

 ![test.pgn](/test1.png)

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
        >>> g.writepgf('test3.pgf')

 ![test3.pgn](/test3.png)


 The supported colors are:  Red Green Blue Cyan Magenta Yellow Black Gray Darkgray Lightgray Brown Lime Olive Orange Pink Purple Teal Violet White.

 One caveat is that one can not apply any of the color functions to a figure (for example with the intent of changing the color of all drawables in
 the figure).  Instead one might use:

        >>> for drawable in figure:
				Red(drawable)

 to achive the same effect.

## Drawables, Figure, and stickman

 The drawable objects are Frame, Tangent, Point, Boundarypoint, Circle, Disk, Segment, Halfline, Line.

 A Figure is a subclass of Set and is pretty much just a set of drawable objects with a writepgf function.

 Points represent points in the hyperbolic plane.  Several constructors are provided, some examples are:
 Point.frompolar(radius,angle)   constructs from polar coordinates.
 Point.fromupper(complex)    constructs from a point in the upper half plane (complex number)

 Another useful way of getting points is by using the .basepoint attribute of a Frame (more on these later).
 In short if f is Frame then f.basepoint is a Point representing its basepoint.

 Segments can so far only be constructed from two points.  Halflines and Lines are supposed to be constructed
 from a Tangent object (a unit tangent vector) whose basepoint is the starting point of the Halfline and just
 a point on the Line in the other case (its direction indicated the direction of the Halfline or line).

 A utility function stickman() returns a figure which is a rudimentary picture in the hyperbolic disk.  Inspecting this functions code should give a good idea of how to use some of the drawables.

        >>> s = stickman(size=0.5)
        >>> s.writepgf('test4.pgf')

 ![test4.pgn](/test4.png)

## Frames and isometries

 The Frame class serves two puposes.   Instances represent orthonormal tangent frames and also isometries of the hyperbolic plane.
 The constructor

        >>> Frame.origin()

 yields the Frame at the center of the disk, with the first vector looking right and the second upwards.  This Frame also represents the
 identity tranformation.

        >>> Frame.flip()

 yields the Frame at the center of the disk, with the first vector looking right and the second downwards.  This Frame also represents the
 axial symmetry with respect to the geodesic in the horizontal direction.

 Other frames can be constructed conveniently from a series of instructions for example:

        >>> Frame.forward(1)*Frame.rotate(pi/2)*Frame.forward(2)

 is obtained from Frame.origin() by going forward along the geodesic in direction of the first vector fo the frame 1 unit then turning
 towards the second vector fo the frame a right angle, and then moving along the geodesic flow for two units.

 The frame Frame.sideways(1) is on the same horocycle of Tangent.origin() and to the right 1 unit (it can also
 be included in multiplication chains as above).

 Any orthonormal frame can be obtained by multiplying those obtained from the given constructors as above.

 The basepoint of a tangent vector is an attribute.  For example

        >>> Tangent.origin().basepoint

 returns the Point representing the center of the disk.

 Tangents also act on drawables and figures by left multiplication.  They act like the unique
 isometry of the hyperbolic plane taking the tangent vector Tangent.origin() to the given tangent vector.

 As an example consider:

        >>> stick = Frame.forward(-5)*stickman(size=0.5)
        >>> f = Frame.forward(1)*Frame.flip()
        >>> g = Figure()
        >>> for i in range(10):
                g.update(stick)
                stick = f*stick
        >>> g.writepgf('test5.pgf')

Which generates the following figure:

 ![test5.pgn](/test5.png)

## Layers

 Each drawable object belongs to one of the three layers 'background', 'main', or 'foreground' (where main is the middle layer).
 The layer an object belongs to is stored in its .layer attribute and can be changed at will.

 Objects on the same layer will be drawn in a random order (because Figure is a subclass of set Python sets are unordered).

 For convenience (as with colors) we have provided the functions Background(drawable), Mainlayer(drawable) and Foreground(drawable)
 to change the layer of a drawable object. These can be used at the time of construction or later on.

 By default Frames, Tangents, and Points belong to the foreground layer, Segments, Circles, Lines, and Halflines to the main layer and Disks to the background.

 To illustrate the use of layers consider the following randomly generated figure:

        >>> from random import choice
        >>> f = Figure()
        >>> for i in range(20):
                d = Frame.rotate(2*pi*i/20)*Frame.forward(2)*Disk(Point(0),0.6)
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

## The modular group

The program modulargroup.py contains a generator for the modulargroup and a function stickmaninmodulargroup() which illustrates some of the possibilities when a set of isometries is systematically applied to a figure.

        >>> from modulargroup import stickmaninmodulargroup
        >>> stickmaninmodulargroup()

 ![test8.pgn](/test8.png)