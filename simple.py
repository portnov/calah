#!/usr/bin/python

import sys

import calahgame as cg
from calahgame import CPosition

cg.ENABLE_CALLBACK = False

def ask_move():
    try:
        s = raw_input('Your move> ')
        n = int(s)
    except EOFError:
        print "Exiting."
        sys.exit()
    except ValueError,e:
        print e
        print "Try again:"
    else:
        return n

def end_game(pos):
    c = p.calah_comp + sum(p.luns_comp)
    h = p.calah_hum + sum(p.luns_hum)
    if h > c:
        print "Human win."
    elif h == c:
        print "Nobody win."
    else:
        print "Comp win."
    sys.exit()

p = CPosition()

print p

while True:
    while not p.comp:
        pm = p.possible_moves()
        if len(pm) == 0:
            print "You have not moves."
            end_game(p)
        n = ask_move()
        if not n in pm:
            print "This cell is empty."
            continue
        cg.ENABLE_CALLBACK = True
        p,r = p.move(n)
        cg.ENABLE_CALLBACK = False
        print p

    while p.comp:
        pm =  p.possible_moves()
        if not pm:
            print "Comp has not moves."
            end_game(p)
        n = p.best_move()
        print "Comp move:", n
        cg.ENABLE_CALLBACK = True
        p,r = p.move(n)
        cg.ENABLE_CALLBACK = False
        print p



