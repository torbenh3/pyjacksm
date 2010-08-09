
import os

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

    def __init__( self, client, name, typ = JACK_DEFAULT_MIDI_TYPE, flags = 0 ):
	self.portname = PortName(name).get_shortname()
	self.typ = typ
	self.flags = flags
	self.client = client

	self.conns = []
	self.named_connections = []
	self.dummy = False


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




class DummyPort( Port ):
    """A Port which was loaded from a dom"""

    def __init__( self, client, name, typ=JACK_DEFAULT_AUDIO_TYPE, flags=0 ):
	"""Create a Dummy Port"""
	super(DummyPort,self).__init__( client, name, typ, flags )
	self.dummy = True



class Client( object ):
    """Baseclass for all Clients"""

    def __init__( self, name ):
	self.name = name
	self.orig_name = name
	self.ports = []
	self.cmdline = ""
	self.isinfra = False
	self.uuid = ""
	self.hide = False
	self.dummy = False

    def get_commandline( self, store ):
	client_session_dir = os.path.join( store.path, self.orig_name ) + "/"
	if self.cmdline:
	    return self.cmdline.replace( "${SESSION_DIR}", client_session_dir )
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


class DummyClient( Client ):
    def __init__( self, name ):
	super(DummyClient,self).__init__( name )
	self.dummy = True


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

    def has_client( self, name ):
	"""return True if client is part of this graph"""
	for i in self.clients:
	    if i.name == name:
		return True
	return False


    def get_port( self, portname ):
	pn = PortName( portname )
	return self.get_client( pn.get_clientname() ).get_port( pn.get_shortname() )

    def get_port_list( self ):
	"""return a list with all portnames"""
	retval = []
	for c in self.clients:
	    for p in c.ports:
		retval.append( p.portname )
	return retval

    def iter_clients( self ):
	"""iterator over all valid clients"""
	for c in self.clients:
	    if (not c.hide) and (not c.dummy):
		yield c

    def iter_normal_clients( self ):
	"""iterate over normal clients"""
	for c in self.iter_clients():
	    if not c.isinfra:
		yield c

    def iter_infra_clients( self ):
	"""iterate over infra clients"""
	for c in self.iter_clients():
	    if c.isinfra:
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()

