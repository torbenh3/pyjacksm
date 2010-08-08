
from ConfigParser import SafeConfigParser
import os

defaults = { "jackclientname": "sessionmanager", "sessiondir": "~/jackSessions", "templatedir": "~/.jackSession_templates" }

class Config( object ):
    def __init__( self ):
        config = SafeConfigParser( defaults )
        config.read( os.path.expanduser( "~/.pyjacksmrc" ) )
        self.jackname = config.get( "DEFAULT", "jackclientname" )
        if config.has_section( "infra" ):
            self.infra_clients = {}
            for inf in config.items( "infra" ):
                self.infra_clients[inf[0]] = inf[1]
        else:
            self.infra_clients = { "a2j": "a2jmidid" }

        self.implicit_clients = [ "system" ]

        self.sessiondir = os.path.expanduser( config.get( "DEFAULT", "sessiondir" ) ) + "/" 
        self.templatedir = os.path.expanduser( config.get( "DEFAULT", "templatedir" ) ) + "/" 


