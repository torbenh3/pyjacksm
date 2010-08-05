
from pyjacksm import bpjack
from graph import Port, Client, Graph, PortName

JACK_DEFAULT_AUDIO_TYPE="32 bit float mono audio"
JACK_DEFAULT_MIDI_TYPE="8 bit raw midi"

JackPortIsInput = 0x1
JackPortIsOutput = 0x2
JackPortIsPhysical = 0x4
JackPortCanMonitor = 0x8
JackPortIsTerminal = 0x10

JackSessionSave = 1
JackSessionQuit = 2


class LivePort( Port ):
    """A live port which can be connected and such"""

    def __init__( self, jserver, client, name ):
	"""Create the port coresponding to name, which needs to be a valid jack port"""

	self.port_p = jserver.port_by_name( name )
	super(LivePort,self).__init__( client, name, self.port_p.type(), self.port_p.flags() )


class LiveClient( Client ):
    """a live client, from the jackgraph..."""

    def __init__( self, jserver, name ):
	"""Create the LiveClient, ports are added afterwards"""
	super(LiveClient,self).__init__( name )
	self.jserver = jserver
	
    def add_port( self, portname ):
	"""adds a Port... """
	self.ports.append( LivePort( self.jserver, self, portname ) )


class LiveGraph(Graph):
    """a live JackGraph"""

    def __init__(self, jserver, ports):
	"""Create a LiveGraph from a list of all ports
	   jserver is the bpjack Client, and ports is a list of Strings or PortNames

	   this constructor also scans all connections...
	"""

	super(LiveGraph, self).__init__()

	self.jserver = jserver
		
        for p in map( PortName, ports ):
	    try:
		client = self.get_client( p.get_clientname() )
	    except KeyError:
		client = LiveClient( jserver, p.get_clientname() )
		self.clients.append( client )

	    client.add_port( p )

	for port in self.iter_ports():
	    for dst in port.port_p.get_all_connections():
		port.conns.append( self.get_port( dst ) )




class JackClient(object):
    def __init__( self, name ):
	self.client = bpjack.create_client( name )

    def get_graph( self ):
	ports = self.client.get_ports( )
	retval = LiveGraph( self.client, ports )
	return retval


    def session_save( self, path ):
	return self.client.session_notify_any( JackSessionSave, str(path) )

    def session_save_and_quit( self, path ):
	return self.client.session_notify_any( JackSessionQuit, str(path) )

    def connect( self, a, b ):
	portA_p = self.client.port_by_name( str(a) )
	
	if( portA_p.flags() & JackPortIsOutput ):
	    self.client.connect( str(a), str(b) )
	else:
	    self.client.connect( str(b), str(a) )

    def pop_port( self ):
        return self.client.pop_port()

    def abort_monitor( self ):
        self.client.abort_monitor()


    def do_reservation( self, cl ):

	num = 0
	while True:
	    if self.client.reserve_client_name( str(cl.name), str(cl.uuid) ) == 0:
		return

	    num += 1
	    cname_split = cl.name.split('-')
	    if len(cname_split) == 1:
		cname_prefix = cname_split[0]
	    else:
		cname_prefix = string.join( cname_split[:-1], '-' )

	    cl.name = ("%s-%02d"%(cname_prefix,num))

	    print "new name: ", cl.name

