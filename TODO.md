# Things to do

## Smarter Segment.tikzline

This is the main deal.  I really disliked the idea of having to detect when two points in the disks
are (more or less) on the same diameter and then either use a circle arc or a straight (euclidean) line to draw
the hyperbolic segment between them.

Also, I think the current Dibujos API doesn't need to be limited to generating pgf files as output.
In fact, it might even be a good API to use for a game-like interactive interface.  Or maybe some other
language for specifying figures such as Asymptote.

Anyway, with those two things in mind I decided that Segment.tikzline would be implemented by generating points
on the hyperbolic segment and joining them with straight Euclidean lines.  This poses the question:  How many times
should one subdivide a hyperbolic segment in order to get good looking results.

At the moment the formula is 
        subdivisions = int(diskradius*10*abs(start-end))+10

Which basically means that the minimum number of subdivisions is 10 and then grows proportionally to
the Euclidean distance (on page) between the endpoints.

This means that segments which are close to the boundary still generate at least 10 (very short) Euclidean
segments.  This makes the pgf file longer than necessary.

As a consequence we sometimes hit the (ridiculous in modern times) 5MB limit imposed by Tex and cannot
generate an output image in Tikz (without hacking around with the LaTex configuration that is).

Hence the main implementation issue to be solved is a better algorithm for approximating a hyperbolic geodesic
by straight Euclidean segments in a visually pleasing and efficient way.

At present the subdivision is evenly spaced when one looks at the points in the Klein model.  This is
probably not the optimal solution for visually pleasing results.  Probably one should do something like
recursively look at each subsegment and decide whether to subdivide it in two (at the hyperbolic midpoint?)
or something.

## Smarter Point.tikzline

Points are drawn smaller if they are close to the boundary of the disk.  At the moment this means that we sometimes
output points of radius 0.000 to the pgf file.  This also contributes to bulking up the pgf output and hitting that
5MB limit.   This should be easy enough to fix.

## Changing layers

The figure.writepgf function calls on each drawable to generate its own line in the resulting pgf file.  This includes
specifying the layer on which it is drawn.   This bulks up the pgf file with a bunch of \begin{pgfonlayer}{background}
and \end{pgfonlayer}.

Maybe its better to have the figure group the drawables according to the layer they are on and then output a single

        \begin{pgfonlayer}{layer}
        \end{pgfonlayer}

block for each of the three layers.

I like the API for adding drawables to figures with figure.add and updating figures with figure.update so I don't
want to complicate the inner structure of the Figure class (i.e. I want to keep it as a subclass of set).

This means the solution should be done inside the writepgf method.  And implies that there will be a cost in terms
of performance at the time of generating the pgf file.

As a hack I kept almost all drawables on the main layer by default and this works pretty well.  But there is still
room for improvement.

## Boundary points, Halfline and Line

At the moment Halfline and Line are kind of hacks.  They're basically segments except one of the endpoints is on
the boundary.  You can call something like Point(1) to make a boundary point.  But it really is a hack because
some methods (such as Point.hyperboloid) will fail.   Also arithmetic errors can creep up and make the point go
out of the disk.

This caused some bugs where an expression like sqrt(1- abs(z)**2) would raise an exception.  The bugs would occur
while trying to subdivide (to draw) a Halfline or Line.

I hacked this away by replacing the above expression by sqrt(1- min(1,abs(z)**2)).  Clearly this is not ideal.

Maybe it's a good idea to make a BoundaryPoint class or something.   Clearly it's a good idea to test and 
have a good look at the Halfline and Line classes.

## Ordered figures?

Since Figure is a subclass of set the order in which things on the same layer are drawn is random.

Maybe it's better to use some sort of ordered set class (while keeping the API) to make things get
drawn in the order they where added (provided they're on the same layer)?


## Example gallery, Fuschsian group generators

The modulargroup(n) generator is a big win.  In a smaller measure so was the stickman() function.  They both allow
generating a bunch of nice examples with minimal coding.

I think that once the program has stabalized a bit (maybe after addressing the issues above) it would be a good idea
to systematically add generators for a bunch of interesting Fuchsian groups and compile a nice gallery of examples.

These could also serve to detect mistakes or places where the API is lacking.  For example, the modular group already
shows that one would need better constructors for Halflines and Lines.  Its pretty hard (at least harder than necessary)
to specify the standard fundamental domain with the current API (in the current example I
 actually just define a finite triangle).

Also, as a clean up thing.  The examples such as stickmaninmodulargroup, etc, should probably be moved out of the 
main file and into some examples.py file or something.

## Real documentation and packaging

So far I have a blog post, a youtube video, a README.md with several examples and images and this file.

After the issues above are dealt with and there's a nice gallery of examples I think it would be a good moment
to more or less freeze the API and document it as clearly as possible.  With a tutorial for example as well as
some documents.

Also, it would be nice to package this thing so it can be installed and included easily in other projects.

## Things I do not intend to do

I don't think I will increase the number of drawable classes much further.  I'd like to keep the program around its
current size of 500 lines (not counting the example gallery) and keep the API simple and memorable.

## Dreams

Something interactive (maybe based on pygame) can probably be developed on this API (notice that the tikzline
attributes are never actually calculated unless needed by some call to Figure.writepgf).  There are already nice
programs to show tesselations but maybe a game could be made (Asteroids on some cocompact Fuchsian group?).
