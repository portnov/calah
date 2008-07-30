#!/usr/bin/python

import sys
import time

import gtk
import gtk.gdk

from stepgame import HaveNotMoves
import calahgame as cg
from calahgame import CPosition

cg.ENABLE_CALLBACK = False

GRAY = (0.5,0.5,0.5)

class Cell(gtk.DrawingArea):
    def __init__(self,idx,value,active=False,width=64,height=64):
        self.idx = idx
        self.value = str(value)
        self.active = active
        gtk.DrawingArea.__init__(self)
        self.connect("expose-event",self.on_expose)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)
        self.callback = None
        self.connect("button-press-event",self.on_click)
        self.connect('enter-notify-event', self.on_mouse_over)
        self.connect('leave-notify-event', self.on_mouse_out)
        self.set_size_request(width,height)
        self.width = width
        self.height = height
        self.fg = GRAY

    def set_text(self,value):
        self.value = value
        self.queue_draw()

    def blink(self):
        self.fg = (0,0,1)
        self.queue_draw()
        gtk.gdk.window_process_all_updates()
        time.sleep(0.4)
        self.fg = GRAY
        self.queue_draw()
        gtk.gdk.window_process_all_updates()

    def on_mouse_over(self,widget,event):
        if self.value == '0' or not self.active:
            return
        self.fg = (0,0,0)
        self.queue_draw()

    def on_mouse_out(self,widget,event):
        self.fg = GRAY
        self.queue_draw()

    def on_click(self,widget,event):
        if self.callback:
            self.callback(self.idx)

    def on_expose(self,widget,event):
        x,y,self.width,self.height,b = widget.window.get_geometry()
        cr = widget.window.cairo_create()
        cr.set_source_rgb(*self.fg)
        cr.rectangle(4,4,self.width-8,self.height-8)
        cr.stroke()
        cr.move_to(self.width//2, self.height//2)
        if self.value == '0':
            cr.set_source_rgb(*GRAY)
        else:
            cr.set_source_rgb(0,0,0)
        cr.set_font_size(int(0.3*min(self.height,self.width)))
        cr.show_text(self.value)

class GUI(object):
    def __init__(self):
        self.window = gtk.Window()
        self.window.set_title('Calah')
        self.big = gtk.HBox()
        self.c_comp = Cell(0,'0',height = 128)
#         self.c_comp.set_width_chars(3)
        self.buttons = []
        self.bot_row = gtk.HBox()
        for i in range(6):
            btn = Cell(i,'4',active=True)
            btn.callback = self.user_clicked
            self.buttons.append(btn)
            self.bot_row.pack_start(btn,expand=True)
        self.luns_comp = []
        self.top_row = gtk.HBox()
        for i in range(6):
            lbl = Cell(i,'4')
            self.luns_comp.append(lbl)
            self.top_row.pack_end(lbl,expand=True)
        self.c_hum = Cell(0,'0',height = 128)
        self.rows = gtk.VBox()
        self.rows.pack_start(self.top_row)
        self.rows.pack_start(self.bot_row)
        self.big.pack_start(self.c_comp,expand=False)
        self.big.pack_start(self.rows, expand=True)
        self.big.pack_start(self.c_hum,expand=False)
        self.info = gtk.Label('Hello.')
        self.all = gtk.VBox()
        self.all.pack_start(self.info, expand=False)
        self.all.pack_start(self.big, expand=True)
        self.window.add(self.all)
        self.window.show_all()
        self.window.connect('destroy',gtk.main_quit)
        self.window.resize(600,200)
        
        self.pos = CPosition()
        cg.step_callback = self.step_callback
        self.stop = False

    def show(self, s):
        p = self.info.get_text()
        self.info.set_text(p + '\n' + s)
        self.window.window.process_updates(True)

    def show_new(self,s):
        self.info.set_text(s)
        self.window.window.process_updates(True)

    def end_game(self,p):
        c = p.calah_comp + sum(p.luns_comp)
        h = p.calah_hum + sum(p.luns_hum)
        self.show_new("Score: Comp %s. Human %s" % (c,h))
        if h > c:
            self.show("Human win.")
        elif h == c:
            self.show("Nobody win.")
        else:
            self.show("Comp win.")
        self.stop = True
#         gtk.main_quit()
#         sys.exit()

    def step_callback(self,cell_type,idx,val):
        val = str(val)
        if cell_type == 'calah_hum':
            self.c_hum.value = val
            self.c_hum.blink()
        elif cell_type == 'calah_comp':
            self.c_comp.value = val
            self.c_comp.blink()
        elif cell_type == 'luns_hum':
            self.buttons[idx].value = val
            self.buttons[idx].blink()
        elif cell_type == 'luns_comp':
            self.luns_comp[idx].value = val
            self.luns_comp[idx].blink()

    def refresh(self):
        for b in self.buttons:
            b.queue_draw()
        self.c_hum.queue_draw() 
        for b in self.luns_comp:
            b.queue_draw()
        self.c_comp.queue_draw()

    def show_pos(self):
        self.c_comp.set_text(str(self.pos.calah_comp))
        self.c_hum.set_text(str(self.pos.calah_hum))
        for i in range(6):
            self.buttons[i].set_text(str(self.pos.luns_hum[i]))
            self.luns_comp[i].set_text(str(self.pos.luns_comp[i]))

    def user_clicked(self,n):
        if self.stop:
            return
        self.show_new("User clicked: %s" % n)
        if self.pos.comp:
            self.show_new("Comp's turn now")
            return
        pm = self.pos.possible_moves()
        if pm == []:
            self.show_new("You have not moves.")
            self.end_game(self.pos)
            return
        if not n in pm:
            self.show_new("This cell is empty.")
            return
        cg.ENABLE_CALLBACK = True
        self.pos,r = self.pos.move(n)
        cg.ENABLE_CALLBACK = False
        self.show_pos()

        self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.window.window.process_updates(True)
        while self.pos.comp:
            pm =  self.pos.possible_moves()
            if not pm:
                self.show_new("Comp has not moves.")
                self.end_game(self.pos)
                return
            self.show_new("Comp is thinking...")
            self.info.queue_draw()
            self.window.window.process_updates(True)
            self.pos.estimate_moves()
            try:
                n = self.pos.best_move()
            except HaveNotMoves:
                self.show_new("Comp has not moves.")
                self.end_game(self.pos)
                return
            self.show_new("Comp move: %s [%s]" % (n, self.pos.luns_comp[n]))
            cg.ENABLE_CALLBACK = True
            self.pos,r = self.pos.move(n)
            cg.ENABLE_CALLBACK = False
            self.show_pos()
        self.window.window.set_cursor(None)
        self.window.window.process_updates(True)
        time.sleep(1)
        self.show_new("Your turn.")

g = GUI()
gtk.main()
