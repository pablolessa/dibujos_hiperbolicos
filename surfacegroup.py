'''Part of the Dibujos Hiperbólicos program.

We define a generator surfacegroup(n) for the ball of radius n of the
Fuchsian group representing the fundamental group of a surface of genus g 
with respect to genrators t_1,...,t_{4*genus} satifying the standard 
commutation relations [t_1,t_2][t_4,t_5]... = 1.

We use Dehn's algorithm to generate each element only once (see wikipedia page).
'''

from dibujos import *

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
