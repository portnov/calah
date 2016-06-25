from copy import copy

from stepgame import T,Position

DEBUG =  False
ENABLE_CALLBACK = True

def step_callback(cell_type,idx,value):
    print "Step: %s[%s] = %s" % (cell_type,idx,value)

def _step_callback(cell_type,idx,value):
    if ENABLE_CALLBACK:
        step_callback(cell_type,idx,value)

if DEBUG:
    def debug(format,*args):
        print "|", (format % args)
else:
    def debug(format,*args):
        pass

class Cells(object):
    def __init__(self,pos):
        self.pos = pos

    def __getitem__(self,idx):
        if not self.pos.comp:
            if 0 <= idx < 6:
                return self.pos.luns_hum[idx]
            elif idx == 6:
                return self.pos.calah_hum
            elif 7 <= idx < 13:
                return self.pos.luns_comp[idx-7]
        else:
            if 0 <= idx < 6:
                return self.pos.luns_comp[idx]
            elif idx == 6:
                return self.pos.calah_comp
            elif 7 <= idx < 13:
                return self.pos.luns_hum[idx-7]

    def __setitem__(self,idx,val):
        global _step_callback

        if not self.pos.comp:
            if 0 <= idx < 6:
                _step_callback('luns_hum',idx,val)
                self.pos.luns_hum[idx] = val
            elif idx == 6:
                _step_callback('calah_hum',idx,val)
                self.pos.calah_hum = val
            elif 7 <= idx < 13:
                _step_callback('luns_comp',idx-7,val)
                self.pos.luns_comp[idx-7] = val
        else:
            if 0 <= idx < 6:
                _step_callback('luns_comp',idx,val)
                self.pos.luns_comp[idx] = val
            elif idx == 6:
                _step_callback('calah_comp',idx,val)
                self.pos.calah_comp = val
            elif 7 <= idx < 13:
                _step_callback('luns_hum',idx-7,val)
                self.pos.luns_hum[idx-7] = val

class CPosition(Position):
    def __init__(self,base=None):
        self.comp = False
        if base:
            self.luns_comp = copy(base.luns_comp)
            self.luns_hum = copy(base.luns_hum)
            self.calah_comp = base.calah_comp
            self.calah_hum = base.calah_hum
        else:
            self.luns_comp = [4 for i in range(6)]
            self.luns_hum =  [4 for i in range(6)]
            self.calah_comp = 0
            self.calah_hum = 0
        self.all = Cells(self)

    def estimate(self,lst):
        return [1 for p in lst]
    
    def __repr__(self):
        if self.comp:
            s = "[Next move: comp]\n"
        else:
            s = "[Next move: human]\n"
        s += '   '
        for i in reversed(range(6)):
            s += "%2d " % self.luns_comp[i]
        s += '   \n'
        s += "%2d                   %2d\n" % (self.calah_comp, self.calah_hum)
        s += '   '
        for i in range(6):
            s += "%2d " % self.luns_hum[i]
        return s + '\n'
    
    def calc_lazy(self):
        c_comp = sum(self.luns_comp)
        c_hum  = sum(self.luns_hum)
        c1 = c_comp + self.calah_comp
        c2 = c_hum + self.calah_hum
        return T(c1-c2, c2-c1)
                 

    def possible_moves(self):
        if self.comp:
            luns = self.luns_comp
        else:
            luns = self.luns_hum

        e = enumerate(luns)
        return [i for i,n in e if n > 0]

    def move(self,s):
        new = CPosition(base=self)
        new.comp = self.comp
        all = Cells(new)
        all,comp = self.move_real(all,s)
        new.comp = comp
        return new, (new.calah_comp, new.calah_hum)

    def move_real(self,all,s):
        h = all[s]
        if not h:
            return all, self.comp
        i = 0
        all[s] = 0
        comp = self.comp
        while True:
            i += 1
            p = (s+i) % 13
            debug("i,p: %s,%s", i,p)
            if i == h:
                debug("Last step: I == H == %s", i)
                if all[p] == 0 and p < 6:
                    debug("Null cell")
                    all[p] += 1
                    a,b = all[p], all[12-p]
                    all[p] = 0
                    all[12-p] = 0
                    all[6] += a
                    all[6] += b
                    comp = not self.comp
                    break
                elif p == 6:
                    debug("Calah")
                    all[6] += 1
                    break
                else:
                    debug("Turn move")
                    all[p] += 1
                    comp = not self.comp
                    break
            else:
                debug("Step")
                all[p] += 1
        return all,comp
        
