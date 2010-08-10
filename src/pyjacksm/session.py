
from libjack  import JackClient
from state import FileGraph, graph_to_dom
from pyjacksm.config  import Config

import monitors
import string

class Session (object):
    """Object representing a Session.
       
       it only loads the session from disk, and makes sure, that
       clientnames dont conflict.
       then it creates a set of procmons, and the connmon, which
       will replicate the session, when they are started.

       So a session is basically a set of reservations, initialised procmons,
       and the connmon.

       >>> import storage
       >>> store = storage.Store( "/home/torbenh/jackSessions", "jr01" )
       >>> s = Session( store ) 
       
    """

    def __init__( self, store ):

	self.name = store.name

        self.cl = JackClient( "sessionmanager" )

        sd = FileGraph( store.session_xml )

        g=self.cl.get_graph()

        self.procmons = {}

	# check which infra clients are missing from the live graph.
	# and insert the missing ones into the procmons
        for ic in sd.iter_infra_clients():
            if not g.has_client( ic.name ):
                self.procmons[ ic.name ] = monitors.ProcMon( ic.cmdline )

	# set callback defaults
        self.progress_cb = self.progress
        self.finished_cb = self.finished


        # rewrite names... so that there will be no conflicts.
	for c in sd.iter_normal_clients():
	    print c.name
	    self.cl.do_reservation( c )

        # build up list of port connections
	conns = [ (c[0].get_name(), c[1].get_name()) for c in sd.iter_connections() ]

        print conns

        # create procmons for the clients
        for c in sd.iter_normal_clients():
            cmd = c.get_commandline( store )
            self.procmons[c.name] = monitors.ProcMon( cmd )

        self.connmon = monitors.ConnMon( conns, self.cl, self.do_progress_cb, self.do_finished_cb )

    def start_load (self):
        print "start connmon"
        self.connmon.start()
        
        print "start procmons"
        for i in self.procmons.values():
            i.start()
        print "got em"


    def get_clients (self):
        return self.procmons.keys()

    def get_client_log (self, client):
        log = self.procmons[client].log
        return string.join( log, '\n' )

    def abort_load (self):
        self.connmon.abort_monitoring()

    def do_progress_cb (self, num, of):
        print "do_progess %d / %d" % (num, of)
        self.progress_cb( num, of )
        print "done"
        
    def do_finished_cb( self ):
        self.finished_cb()

    # defaults..
    def progress (self, num, of):
        print "progress %d / %d " % (num, of)
        
    def finished( self ):
        print "session loaded"


def save_session( store, quit=False, template=False, cfg=Config() ): 

    jserver = JackClient( "sessionmanager" )

    # snapshot the Graph
    g = jserver.get_graph()

    # now send the notifications...
    if quit:
	notify = jserver.session_save_and_quit( store.path )
    elif template:
	notify = jserver.session_save_template( store.path )
    else:
	notify = jserver.session_save( store.path )

    # weave the notifications into the snapshot graph
    for n in notify:
	c = g.get_client( n.clientname )
	c.cmdline =  n.commandline
	c.uuid = n.uuid

    # special treatment for implicit and infra clients
    for c in g.iter_clients():
	if c.cmdline == "":
	    if not c.name in cfg.infra_clients.keys()+cfg.implicit_clients:
	     	c.hide = True
	    elif c.name in cfg.implicit_clients:
	    	c.dummy = True
	    else:
	    	c.isinfra = True
	    	c.cmdline = cfg.infra_clients[c.name]

    dom = graph_to_dom( g )


    f = file( store.session_xml, "w" )
    f.write( dom.toprettyxml() )
    f.close()
    store.commit()

    return 0



if __name__ == "__main__":
    import doctest
    doctest.testmod()
