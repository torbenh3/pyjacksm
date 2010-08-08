
from pyjacksm import libjack
from pyjacksm import state
from pyjacksm import monitors
import subprocess
from ConfigParser import SafeConfigParser
import os
import time
import shutil
import string

defaults = { "jackclientname": "sessionmanager", "sessiondir": "~/jackSessions", "templatedir": "~/.jackSession_templates" }


class Session (object):
    def __init__( self, sessiondir, name ):
        self.sessiondir = sessiondir
        self.name = name

        self.cl = libjack.JackClient( "sessionmanager", True )

        sd = state.SessionDom( sessiondir+"/session.xml" )

        g=self.cl.get_graph()

        self.procmons = {}

        avail_ports = g.get_port_list()

        for ic in sd.get_infra_clients():
            if not ic[0] in g.clients.keys():
                self.procmons[ic[0]] = monitors.ProcMon( ic[1] )

        self.progress_cb = self.progress
        self.finished_cb = self.finished


        print sd.get_client_names()

        # rewrite names... so that there will be no conflicts.
	sd.fixup_client_names( g )

	# now we have mangled all the names, lets reserve them.
	for (uuid, clientname) in sd.get_uuid_client_pairs():
	    print "reserving name %s"%clientname
	    g.reserve_name( uuid, clientname )

        # build up list of port connections
        conns = []
        for p in sd.get_port_names():
            for c in sd.get_connections_for_port( p ):
                conns.append( (p,c) )
        print conns

        # create procmons for the clients
        for cname in sd.get_reg_client_names():
            cmd = sd.get_commandline_for_client( cname, self.sessiondir + "/" )
            self.procmons[cname] = monitors.ProcMon( cmd )

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


class SessionManager( object ):
    def __init__( self ):
        self.config = SafeConfigParser( defaults )
        self.config.read( os.path.expanduser( "~/.pyjacksmrc" ) )
        self.jackname = self.config.get( "DEFAULT", "jackclientname" )
        if self.config.has_section( "infra" ):
            self.infra_clients = {}
            for inf in self.config.items( "infra" ):
                self.infra_clients[inf[0]] = inf[1]
        else:
            self.infra_clients = { "a2j": "a2jmidid" }
        self.implicit_clients = [ "system" ]

        self.sessiondir = os.path.expanduser( self.config.get( "DEFAULT", "sessiondir" ) ) + "/" 
        if not os.path.exists( self.sessiondir ):
            print "Sessiondir %s does not exist. Creating it..."%self.sessiondir
            os.mkdir( self.sessiondir )

        self.templatedir = os.path.expanduser( self.config.get( "DEFAULT", "templatedir" ) ) + "/" 
        if not os.path.exists( self.templatedir ):
            print "Templatedir %s does not exist. Creating it..."%self.templatedir
            os.mkdir( self.templatedir )

	self.current_session = None

    def list_projects( self ):
        files = os.listdir( self.sessiondir )
        files = filter( lambda x: os.path.isdir( os.path.join( self.sessiondir, x ) ), files )
        return files

    def list_templates( self ):
        files = os.listdir( self.templatedir )
        files = filter( lambda x: os.path.isdir( os.path.join( self.templatedir, x ) ), files )
        return files

    def get_current_session( self ):
	if self.current_session:
	    return self.current_session
	else:
	    return ""

    def move_session( self, old, new ):
	shutil.move( os.path.join( self.sessiondir, old ), os.path.join( self.sessiondir, new ) )

    def rm_session( self, name ):
	shutil.rmtree( os.path.join( self.sessiondir, name ) )

    def session_exists( self, name ):
	return os.path.exists( self.sessiondir+name+"/session.xml" )

    def load_session( self, name, template=False ):
        if template:
            path = self.templatedir
        else:
            path = self.sessiondir

        if not os.path.exists( path+name+"/session.xml" ):
            print "Session %s does not exist"%name
            return None

        s =  Session( path+name, name )

	self.current_session = name

	return s

    def quit_session( self, name ):
	self.current_session = None
	return self.save_session( name, True )

    def save_template( self, name ):
        return self.save_session( name, False, True )

    def save_session( self, name, quit=False, template=False ): 
        if template:
            path = self.templatedir
        else:
            path = self.sessiondir

        if os.path.exists( path+name ):
            print "session %s already exists"%name
            return -1

        self.cl = libjack.JackClient( self.jackname, False )

        os.mkdir( self.sessiondir+name )
        g=self.cl.get_graph()
	if quit:
	    notify = self.cl.session_save_and_quit( path+name+"/" )
        elif template:
	    notify = self.cl.session_save_template( path+name+"/" )
	else:
	    notify = self.cl.session_save( path+name+"/" )

        for n in notify:
            c = g.get_client( n.clientname )
            c.set_commandline( n.commandline )
	    c.set_uuid( n.uuid )

        sd = state.SessionDom()

        for c in g.clients.values():
            if c.get_commandline() == "":
                if not c.name in self.infra_clients.keys()+self.implicit_clients:
                    g.remove_client( c.name )
                elif c.name in self.implicit_clients:
                    g.remove_client_only( c.name )
                else:
                    c.set_infra( self.infra_clients[c.name] )


        for i in g.clients.values():
            sd.add_client(i)

        f = file( path+name+"/session.xml", "w" )
        f.write( sd.get_xml() )
        f.close()

	self.current_session = name

        print sd.get_xml()
        return 0
