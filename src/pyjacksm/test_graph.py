
from StringIO import StringIO

from state import FileGraph
import unittest


def get_test_session():
	test_session = """<?xml version="1.0" ?>
	<jacksession>
		<jackclient cmdline="a2jmidid" infra="True" jackname="a2j">
			<port name="a2j:port1">
				<conn dst="jack_rack:out_1"/>
			</port>
			<port name="a2j:port2"/>
		</jackclient>
		<jackclient cmdline="jack-rack --jack-session-uuid 4 &quot;/home/torbenh/jackSessions/jr01/jack_rack/rack.xml&quot;" infra="False" jackname="jack_rack" uuid="4">
			<port name="jack_rack:out_1" shortname="out_1">
				<conn dst="a2j:port1"/>
			</port>
			<port name="jack_rack:in_1" shortname="in_1">
				<conn dst="system:out_1"/>
			</port>
		</jackclient>
	</jacksession>
	"""
	return StringIO( test_session )

class TestDomGraph( unittest.TestCase ):

	def setUp( self ):
		self.graph = FileGraph( get_test_session() )

	def test_client_iter( self ):
		self.assertEqual( len(list(self.graph.iter_clients())), 2 )

	def test_port_iter( self ):
		self.assertEqual( len(list(self.graph.iter_ports())), 4 )

	def test_conn_iter( self ):
		self.assertEqual( len(list(self.graph.iter_connections())), 3 )

	def test_hide_client( self ):
		self.graph.get_client( "a2j" ).hide = True
		self.assertEqual( len(list(self.graph.iter_ports())), 2 )
		self.assertEqual( len(list(self.graph.iter_clients())), 1 )
		self.assertEqual( len(list(self.graph.iter_connections())), 1 )

if __name__ == '__main__':
	unittest.main()

