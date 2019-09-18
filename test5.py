from dibujos import *

stick = Frame.forward(-5)*stickman(size=0.5)
f = Frame.forward(1)*Frame.flip()
g = Figure()

for i in range(10):
	g.update(stick)
	stick = f*stick

g.writepgf('test5.pgf')
