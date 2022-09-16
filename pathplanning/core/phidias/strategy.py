from phidias.Types import *
from phidias.Main import *
from phidias.Lib import *
from phidias.Agent import *

from pathplanning.core.const import PHIDIAS_HANDLER_PORT

class connected(Belief): pass
class item(Belief): pass
class goto(Belief): pass

class connect(Procedure): pass
class pick(Procedure): pass

class item_picked(Reactor): pass
class item_released(Reactor): pass


def phidias_client():

    remote_dest = { 'to': f'robot@127.0.0.1:{PHIDIAS_HANDLER_PORT}'  }

    def_vars('X', 'Y', 'F')

    class main(Agent):
        
        def main(self):
            
            connect() / item(X, Y) >> [ -item(X, Y), connect() ]
            
            connect() >> [ +connected()[remote_dest] ]
            
            pick() / item(X, Y) >> [ +goto(X, Y)[remote_dest] ] 
            
            pick() >> [ show_line('every item has been picked.') ]
            
            +item_released(X, Y)[{'from': F}] / item(X, Y) >> [ -item(X, Y), show_line(X, ' ', Y), pick() ]

            +item_released(X, Y)[{'from': F}] >> [ show_line(X, ' ', Y, ' not recognized in kb.')]
            
            +item_picked(X, Y)[{'from': F}] / item(X, Y) >> [ show_line("robot picked (", X, " ", Y, ")") ]


    ag = main()
    ag.start()

    PHIDIAS.run_net(globals(), 'http')
    PHIDIAS.shell(globals())