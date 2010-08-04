
from libjack  import JackClient
from domgraph import FileGraph

import monitors

class Session (object):
    """Object representing a Session.
       
       it only loads the session from disk, and makes sure, that
       clientnames dont conflict.
       then it creates a set of procmons, and the connmon, which
       will replicate the session, when they are started.

       So a session is basically a set of reservations, initialised procmons,
       and the connmon.

       >>> s = Session( "/home/torbenh/jackSessions/jr01", "bls" ) 
       
    """

    def __init__( self, sessiondir, name ):
        self.sessiondir = sessiondir
        self.name = name

        self.cl = JackClient( "sessionmanager" )

        sd = FileGraph( sessiondir+"/session.xml" )

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


        #print sd.get_client_names()

        # rewrite names... so that there will be no conflicts.
	# TODO: JackClient object needs a method to reserve a Client.
	#       it will rename it, when the current name cant be reserved.

	#for c in sd.iter_normal_clients():
	#    self.cl.make_reservations( c )

        # build up list of port connections
	conns = list( sd.iter_connections() )

        print conns

        # create procmons for the clients
        for c in sd.iter_normal_clients():
            cmd = c.get_commandline( self.sessiondir + "/" )
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
