
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
    """A Graph built from an xml File

    >>> import test_graph
    >>> g = FileGraph( test_graph.get_test_session() )
    
    """

    def __init__( self, filename ):
    	dom = parse( filename )
	super(FileGraph, self).__init__( dom )


def client_to_dom( client ):

    cl_elem = Element( "jackclient" )
    cl_elem.setAttribute( "cmdline", client.cmdline )
    cl_elem.setAttribute( "jackname", client.name )
    if client.uuid:
	cl_elem.setAttribute( "uuid", client.uuid )
    if client.isinfra:
	cl_elem.setAttribute( "infra", "True" )
    else:
	cl_elem.setAttribute( "infra", "False" )

    for p in client.ports:
	po_elem = Element( "port" )
	po_elem.setAttribute( "name", p.get_name() )
	po_elem.setAttribute( "shortname", p.portname )
	
	for c in p.get_connections():
	    c_elem = Element( "conn" )
	    c_elem.setAttribute( "dst", c.get_name() )

	    po_elem.appendChild( c_elem )

	cl_elem.appendChild( po_elem )
    
    return cl_elem


def graph_to_dom( graph ):
    """Convert a graph to a DOM..

	>>> import test_graph
	>>> g = FileGraph( test_graph.get_test_session() )
        >>> d = graph_to_dom( g )
    """

    impl = getDOMImplementation()
    dom = impl.createDocument(None,"jacksession",None)

    for c in graph.iter_clients():
	cl_elem = client_to_dom( c )
	dom.documentElement.appendChild( cl_elem )

    return dom



if __name__ == "__main__":
    import doctest
    doctest.testmod()

