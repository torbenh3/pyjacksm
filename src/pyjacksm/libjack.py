
import bpjack

JACK_DEFAULT_AUDIO_TYPE="32 bit float mono audio"
JACK_DEFAULT_MIDI_TYPE="8 bit raw midi"

JackPortIsInput = 0x1
JackPortIsOutput = 0x2
JackPortIsPhysical = 0x4
JackPortCanMonitor = 0x8
JackPortIsTerminal = 0x10

JackSessionSave = 1
JackSessionQuit = 2



class Port( object ):
    def __init__( self, client, name ):
	self.client = client
	self.name = name
	self.portname = name.split(':')[1]
	self.port_p = client.port_by_name( name )
	self.conns = []
        for p in self.port_p.get_all_connections():
            self.conns.append( p )

    def get_connections( self ):
	return self.conns

    def connect( self, other ):
	self.client.connect( self.name, other )

    def disconnect( self, other ):
	self.client.disconnect( self.name, other )

    def is_input( self ):
	return (self.port_p.flags() & JackPortIsInput) != 0

    def is_output( self ):
	return (self.port_p.flags() & JackPortIsOutput) != 0

    def is_audio( self ):
	return (self.port_p.type() == JACK_DEFAULT_AUDIO_TYPE)

    def is_midi( self ):
	return (self.port_p.type() == JACK_DEFAULT_MIDI_TYPE)


class Client( object ):
    def __init__( self, client, name ):
	self.client = client
	self.name = name
	self.ports = []
	self.commandline = None
	self.isinfra = False
	self.uuid = None

    def get_commandline( self ):
	if self.commandline:
	    return self.commandline
	else:
	    return ""

    def set_commandline( self, cmdline ):
	self.commandline = cmdline

    def get_uuid( self ):
	return self.uuid

    def set_uuid( self, uuid ):
	self.uuid = uuid

    def add_port( self, portname ):
	self.ports.append( Port( self.client, portname ) )

    def set_infra( self, cmdline ):
	self.isinfra = True
	self.commandline = cmdline



class JackGraph( object ):
    def __init__( self, client, ports, uuids=[] ):
	self.client = client
	self.clients = {}
	self.reserved_names = []

        for p in ports:
	    port_split = p.split(':')
	    if not self.clients.has_key(port_split[0]):
		self.clients[port_split[0]] = Client( client, port_split[0] )

	    self.clients[port_split[0]].add_port( p )

    def get_client( self, name ):
        if not self.clients.has_key(name):
            self.clients[name] = Client( self.client, name )
        return self.clients[name]

    def get_port_list( self ):
	retval = []
	for c in self.clients.values():
	    for p in c.ports:
		retval.append( p.name )
	return retval



    def check_client_name( self, client ):
	if not client.name in self.reserved_names:
	    return

	oldname = client.name
	newname = self.get_free_name( client.name )

	client.rename( newname )
	del self.clients[oldname]
	self.clients[newname] = client

    def get_free_name( self, oldname, other_names=[] ):
	cname_split = oldname.split('-')
	if len(cname_split) == 1:
	    cname_prefix = cname_split[0]
	else:
	    cname_prefix = string.join( cname_split[:-1], '-' )

	num = 1
	while ("%s-%d"%(cname_prefix,num)) in (self.clients.keys()+self.reserved_names+other_names):
		num+=1

	return ("%s-%d"%(cname_prefix,num))



    def remove_client( self, name ):
	del self.clients[name]
	for c in self.clients.values():
	    for p in c.ports:
		for conn in p.get_connections():
		    if conn.startswith(name+":"):
			p.conns.remove( conn )

    def remove_client_only( self, name ):
	del self.clients[name]

    def ensure_clientnames( self, names ):
	self.reserved_names = names
	for c in self.clients.values():
	    self.check_client_name( c )

    def get_taken_names( self ):
	return self.clients.keys() + self.reserved_names

    def reserve_name( self, uuid, name ):
	if self.client.reserve_client_name( str(name), str(uuid) ):
	    raise Exception( "reservation failure" )
	self.reserved_names.append( name )


class JackClient(object):
    def __init__( self, name, monitor ):
	self.client = bpjack.create_client( name )

    def get_graph( self ):
	ports = self.client.get_ports( )
	retval = JackGraph( self.client, ports )
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





	    
	    


