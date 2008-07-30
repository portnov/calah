
from pprint import pformat

DEBUG =  False

if DEBUG:
    def debug(format,*args):
        print "|", (format % args)
else:
    def debug(format,*args):
        pass

class HaveNotMoves(Exception):
    pass

class T(object):
    def __init__(self,*args):
        if len(args)==1:
            self._tuple = args[0]
        else:
            self._tuple = args

    def __iter__(self):
        return iter(self._tuple)

    def __add__(self,obj):
        return T([x+y for x,y in zip(self,obj)])

    def __mul__(self,num):
        return T([num*x for x in self])

    def __repr__(self):
        return "(" + ", ".join(map(repr,self._tuple)) + ")"

def summ(lst):
    if not lst:
        return T(0,0)
    r = lst[0]
    for t in lst[1:]:
        r = r + t
    return r

class Position(object):
    def __init__(self):
        self.comp = False

    def calc(self,moves=5):
        if not moves:
            return self.calc_lazy()
        else:
            return self.calc_rec(moves)

    def estimate(self,lst):
        if not lst:
            return lst
        m = -1000
        if self.comp:
            for a,b in lst:
                if m < a:
                    m = a
            t = [int(a==m) for a,b in lst]
        else:
            for a,b in lst:
                if m < b:
                    m = b
            t = [int(b==m) for a,b in lst]
        debug("E: lst=%s, m=%s, t=%s", lst,m,t)
        s = sum(t)
        return [float(p)/s for p in t]
    
    def calc_rec(self,moves=5):
        d = []
        for move in self.possible_moves():
            new,r = self.move(move)
            if moves == 0:
                c = new.calc_lazy()
            else:
                c = new.calc(moves-1)
            d.append(c+r)
        e = self.estimate(d)
        if moves==5:
            debug('C_R: return %s', ' + '.join(['%s*%s' % (c,p) for p,c in zip(e,d)]))
        return summ([c*p for p,c in zip(e,d)])

    def estimate_move(self,s,moves=5):
        new,r = self.move(s)
        c = new.calc(moves)
        return c+r

    def estimate_moves(self,moves=5):
        res = []
        debug("E_M: self = %s", pformat(self))
        for move in self.possible_moves():
            new,r = self.move(move)
            c = new.calc(moves)
            debug("E_M: For move %s, we have c=%s, r=%s", move,c,r)
            res.append((move, c+r))
        return res

    def best_move(self,moves=5):
        r = self.estimate_moves(moves)
        debug("R: %s",r)
        ms = [a for a,b in r]
        rs = [b for a,b in r]
        cr = [a for a,b in rs]
        hr = [b for a,b in rs]
        if self.comp:
            if not cr:
                raise HaveNotMoves
            m = max(cr)
            return ms[cr.index(m)]
        else:
            if not hr:
                raise HaveNotMoves
            m = max(hr)
            return ms[hr.index(m)]



