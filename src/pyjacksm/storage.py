
import os
import shutil

class Storage( object ):
    """This class represents the storage backend, that holds the sessions"""

    def __init__( self, config ):
	"""constructor, and feed it with a config"""

	self.sessiondir  = config.sessiondir
	self.templatedir = config.templatedir

        if not os.path.exists( self.sessiondir ):
            print "Sessiondir %s does not exist. Creating it..."%self.sessiondir
            os.mkdir( self.sessiondir )

        if not os.path.exists( self.templatedir ):
            print "Templatedir %s does not exist. Creating it..."%self.templatedir
            os.mkdir( self.templatedir )

    def list_projects( self ):
	"""return a list of str with all known projects"""

        files = os.listdir( self.sessiondir )
        files = filter( lambda x: os.path.isdir( os.path.join( self.sessiondir, x ) ), files )
        return files

    def list_templates( self ):
	"""return a list of str with all known templates"""

        files = os.listdir( self.templatedir )
        files = filter( lambda x: os.path.isdir( os.path.join( self.templatedir, x ) ), files )
        return files

    def move_session( self, old, new ):
	"""move a session"""
	shutil.move( os.path.join( self.sessiondir, old ), os.path.join( self.sessiondir, new ) )

    def rm_session( self, name ):
	"""remove a session"""
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

        return Session( path+name, name )

