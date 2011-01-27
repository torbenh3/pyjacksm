
from threading import Thread
from subprocess import *

class ProcMon (Thread):
    def __init__ (self, command, name, callback ):
        Thread.__init__(self)
        self.command = command
        self.daemon = True
	self.name = name
	self.callback = callback

        self.log = []

    def run (self):
        self.p = Popen( self.command, bufsize=1, stdout=PIPE, stderr=STDOUT, shell=True, close_fds=True )

        while(True):
            line = self.p.stdout.readline()
            if len(line) == 0:
                break
            if len(self.log) == 100:
                del self.log[0]
            self.log.append(line.strip())
	    self.callback(self.name)

        self.log.append( "*** Program terminated !" )
	self.callback(self.name)


class ConnMon (Thread):
    def __init__ (self, conns, cl, progress_cb, finished_cb):
        Thread.__init__(self)
        self.conns = conns
        self.cl = cl
        self.progress_cb = progress_cb
        self.finished_cb = finished_cb
        self.num_conns = len(conns)

        self.g = self.cl.get_graph()


    def check_port (self, pname):
	to_remove = []
	for c1 in self.conns:
	    if c1[0]==pname:
		if c1[1] in self.avail_ports:
		    self.cl.connect( pname, c1[1] )

		    to_remove.append( c1 )
		    if (c1[1],c1[0]) in self.conns:
			to_remove.append( (c1[1],c1[0]) )

	    if c1[1]==pname:
		if c1[0] in self.avail_ports:
		    self.cl.connect( pname, c1[0] )

		    to_remove.append( c1 )
		    if (c1[1],c1[0]) in self.conns:
			to_remove.append( (c1[1],c1[0]) )

	for r in to_remove:
	    try:
		self.conns.remove( r )
	    except:
		pass

    def run(self):

        self.avail_ports = self.g.get_port_list()

	for p in self.avail_ports:
	    self.check_port( p )

	self.progress_cb( self.num_conns-len(self.conns), self.num_conns )

        while len(self.conns) > 0:
            pname = self.cl.pop_port()
            if len(pname)==0:
                break

	    self.check_port( pname )

            self.avail_ports.append( pname )
            self.progress_cb( self.num_conns-len(self.conns), self.num_conns )

        self.finished_cb()
	self.cl = None

    def abort_monitoring (self):
        self.cl.abort_monitor()
	self.cl = None



