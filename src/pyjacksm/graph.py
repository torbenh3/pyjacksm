
JACK_DEFAULT_AUDIO_TYPE="32 bit float mono audio"
JACK_DEFAULT_MIDI_TYPE="8 bit raw midi"

JackPortIsInput = 0x1
JackPortIsOutput = 0x2
JackPortIsPhysical = 0x4
JackPortCanMonitor = 0x8
JackPortIsTerminal = 0x10


class PortName(str):
    """ A PortName basically just a string...
	
	>>> a = PortName( 'client:port' )
	>>> a.get_clientname()
	'client'
	>>> a.get_shortname()
	'port'

	>>> a = PortName( 'client', 'port' )
	>>> a.get_clientname()
	'client'
	>>> a.get_shortname()
	'port'
	>>> a
	'client:port'
    """

    def __new__( cls, part1, part2 = None ):
	""" Create a PortName, if passed only one Parameter it needs to be a complete PortName,
	    with 2 Parameters, it needs to be client and portname...
	"""
	if part2:
	    return super(PortName,cls).__new__( cls, part1 + ":" + part2 )
	else:
	    return super(PortName,cls).__new__( cls, part1 )

    def get_clientname( self ):
	"""the clientname part of the PortName"""
	return self[:self.find(":")]

    def get_shortname( self ):
	"""the shortname part of the PortName"""
	return self[self.find(":")+1:]


class Port( object ):
    """the baseclass for a Port."""

    def __init__( self, client, name, typ, flags ):
	self.portname = PortName(name).get_shortname()
	self.typ = typ
	self.flags = flags
	self.client = client

	self.conns = []


    def get_name( self ):
	"""return the full name built from clientname and portname"""
	return PortName( self.client.name, self.portname )

    def get_connections( self ):
	return self.conns

    def is_input( self ):
	return (self.flags & JackPortIsInput) != 0

    def is_output( self ):
	return (self.flags & JackPortIsOutput) != 0

    
    def is_audio( self ):
	return (self.typ == JACK_DEFAULT_AUDIO_TYPE)

    def is_midi( self ):
	return (self.typ == JACK_DEFAULT_MIDI_TYPE)



class LivePort( Port ):
    """A live port which can be connected and such"""

    def __init__( self, jserver, client, name ):
	"""Create the port coresponding to name, which needs to be a valid jack port"""

	self.port_p = jserver.port_by_name( name )
	super(LivePort,self).__init__( client, name, self.port_p.type(), self.port_p.flags() )


class DomPort( Port ):
    """A Port which was loaded from a dom"""

    def __init__( self, client, node ):
	"""Create a Port from the Dom node..."""
	super(DomPort,self).__init__( client, node.getAttribute("name"), JACK_DEFAULT_AUDIO_TYPE, 0 )

	# put all connection names into named_connections
	self.named_connections = [ i.getAttribute( "dst" ) for i in node.getElementsByTagName( "conn" ) ]



class Client( object ):
    """Baseclass for all Clients"""

    def __init__( self, name ):
	self.name = name
	self.ports = []
	self.commandline = None
	self.isinfra = False
	self.uuid = None
	self.hide = False

    def get_commandline( self ):
	if self.commandline:
	    return self.commandline
	else:
	    return ""

    def add_port( self, portname, typ, flags ):
	"""adds a Port... this is probably not useful in the basclass"""
	self.ports.append( Port( self, portname, typ, flags ) )

    def get_port( self, portname ):
	"""get a Port..."""
	for p in self.ports:
	    if p.portname == portname:
		return p
	raise KeyError


class LiveClient( Client ):
    """a live client, from the jackgraph..."""

    def __init__( self, jserver, name ):
	"""Create the LiveClient, ports are added afterwards"""
	super(LiveClient,self).__init__( name )
	self.jserver = jserver
	
    def add_port( self, portname ):
	"""adds a Port... """
	self.ports.append( LivePort( self.jserver, self, portname ) )


class DomClient( Client ):
    """Client created from a DomNode"""

    def __init__( self, node ):
	"""Create DomClient from a DomNode..."""
	super(LiveClient,self).__init__( node.getAttribute( "jackname" ) )
	self.uuid = node.getAttribute( "uuid" )
	self.cmdline = node.getAttribute( "cmdline" )

	for p in node.getElementsByTagName( "port" ):
	    self.ports.append( DomPort( self, p ) )


class Graph( object ):
    """Baseclass for all Graphs"""
    def __init__( self ):
	self.clients = []

    def get_client( self, name ):
	"""get the client object with name"""
	for i in self.clients:
	    if i.name == name:
		return i
	raise KeyError


    def get_port( self, portname ):
	pn = PortName( portname )
	return self.get_client( pn.get_clientname() ).get_port( pn.get_shortname() )

    def get_port_list( self ):
	"""return a list with all portnames"""
	retval = []
	for c in self.clients:
	    for p in c.ports:
		retval.append( p.name )
	return retval

    def iter_clients( self ):
	"""iterator over all valid clients"""
	for c in self.clients:
	    if not c.hide:
		yield c

    def iter_ports( self ):
	"""iterator over all ports"""
	for c in self.iter_clients():
	    for p in c.ports:
		yield p

    def iter_connections( self ):
	for p in self.iter_ports():
	    for dst in p.get_connections():
		if not dst.client.hide:
		    yield (p, dst)

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


class DomGraph( Graph ):
    """A Graph from a dom"""

    def __init__( self, domdoc ):
	"""create graph from domdoc"""

	super(DomGraph, self).__init__()

	doc = domdoc.documentElement
	for c in doc.getElementsByTagName( "jackclient" ):
	    self.clients.append( DomClient( c ) )

	for port in self.iter_ports():
	    for dst in port.named_connections:
		port.conns.append( self.get_port( dst ) )
	


if __name__ == "__main__":
    import doctest
    doctest.testmod()

