from phidias.Types import *
from phidias.Main import *
from phidias.Lib import *
from phidias.Agent import *

class connected(Belief): pass
class item(Belief): pass
class goto(Belief): pass

class connect(Procedure): pass
class pick(Procedure): pass

class item_picked(Reactor): pass


def phidias_client():

    def_vars('X', 'Y', 'F')

    class main(Agent):
        def main(self):
            
            connect() >> [ +connected()[{'to': 'robot@127.0.0.1:6566'}] ]
            
            pick() / item(X, Y) >> [ +goto(X, Y)[{'to': 'robot@127.0.0.1:6566'}] ] 
            
            pick() >> [ show_line('every item has been picked.') ]
            
            +item_picked(X, Y)[{'from':F}] / item(X, Y) >> [ -item(X, Y), show_line(X, ' ', Y), pick() ]
            

    ag = main()
    ag.start()

    PHIDIAS.run_net(globals(), 'http')
    PHIDIAS.shell(globals())