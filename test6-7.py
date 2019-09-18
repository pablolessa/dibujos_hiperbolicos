from dibujos import *
from random import choice

f = Figure()
for i in range(20):
	d = Frame.rotate(2*pi*i/20)*Frame.forward(2)*Disk(Point(0),0.6)
	d.color = choice(['teal','magenta','cyan'])
	f.add(d)
f.writepgf('test6.pgf')

for x in f:
	if x.color == 'teal':
		y = Foreground(x)
	if x.color == 'magenta':
		y = Mainlayer(x)
	if x.color == 'cyan':
		y = Background(x)
f.writepgf('test7.pgf')
