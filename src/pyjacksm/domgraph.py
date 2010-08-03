
""" Support for building a Graph from DOM and also
    converting it back to Dom """

from graph import Port, Client, Graph, PortName

#these are not necassary:
from graph import DummyPort, DummyClient

from xml.dom.minidom import getDOMImplementation, parse, Element

class DomPort( Port ):
    """A Port which was loaded from a dom"""

    def __init__( self, client, node ):
	"""Create a Port from the Dom node..."""
	super(DomPort,self).__init__( client, node.getAttribute("name") )

	# put all connection names into named_connections
	self.named_connections = [ i.getAttribute( "dst" ) for i in node.getElementsByTagName( "conn" ) ]


class DomClient( Client ):
    """Client created from a DomNode"""

    def __init__( self, node ):
	"""Create DomClient from a DomNode..."""
	super(DomClient,self).__init__( node.getAttribute( "jackname" ) )
	self.uuid = node.getAttribute( "uuid" )
	self.cmdline = node.getAttribute( "cmdline" )

	for p in node.getElementsByTagName( "port" ):
	    self.ports.append( DomPort( self, p ) )


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
		port.conns.append( self.ensure_port( dst ) )

    def ensure_port( self, portname ):
	pn = PortName( portname )

	try:
	    cl = self.get_client( pn.get_clientname() )
	except KeyError:
	    cl = DummyClient( pn.get_clientname() ) 
	    self.clients.append( cl )

	try:
	    po = cl.get_port( pn.get_shortname() )
	except KeyError:
	    po = DummyPort( cl, pn, "", 0 )
	    cl.ports.append( po )

	return po


class FileGraph( DomGraph ):
    """A Graph built from an xml File"""

    def __init__( self, filename ):
    	dom = parse( filename )
	super(FileGraph, self).__init__( dom )




if __name__ == "__main__":
    import doctest
    doctest.testmod()

