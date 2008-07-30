#!/usr/bin/python

from calahgame import CPosition
import calahgame as cg
cg.ENABLE_CALLBACK = False

p = CPosition()
p.luns_hum = [1,1,10,1,1,1]
p.luns_comp = [1,1,1,1,1,1]
p.comp = True
print p

print p.estimate_move(2)
print p.best_move()

n,r = p.move(5)
print n
print n.best_move()
