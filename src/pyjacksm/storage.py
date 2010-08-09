
""" This module contains a Basic Storage on Filesystem implementation"""

import os
import shutil


class Store( object ):
    """a single session store"""

    def __init__( self, sdir, name ):
	self._sdir = sdir
	self._name = name

    @property
    def name( self ):
	return self._name

    @property
    def session_xml( self ):
	return os.path.join( self._sdir, self._name, "session.xml" )

    @property
    def path( self ):
	return os.path.join( self._sdir, self._name ) + "/"

    def commit( self ):
	pass

class NewStore( Store ):
    """This creates a new session Store"""

    def __init__( self, sdir, name ):
	"""create the store name,
	   TODO: check for overwrite"""

	super(NewStore,self).__init__( sdir, name )
	os.mkdir( self.path )



class OverwriteStore( Store ):
    """this store is for overwriting an old store.
       the new data is written to a tmp location, 
       and the old stuff is only deleted upon commit"""

    def __init__( self, sdir, over_name ):
	"""construct OverwriteStore which overwrites over_name in sdir"""

	super(OverwriteStore,self).__init__( sdir, "tmpname" )
	self._over_name = over_name

    @property
    def name( self ):
	return self._over_name

    def commit( self ):
	shutil.rmtree( os.path.join( self._sdir, self._over_name ) )
	shutil.move( os.path.join( self.path ), os.path.join( self._sdir, self._over_name ) )



class Storage( object ):
    """This class represents the storage backend, that holds the sessions"""

    def __init__( self, sdir ):
	"""constructor, and feed it with a config"""

	self.sessiondir  = sdir

        if not os.path.exists( self.sessiondir ):
            print "Sessiondir %s does not exist. Creating it..."%self.sessiondir
            os.mkdir( self.sessiondir )

    def list_projects( self ):
	"""return a list of str with all known projects"""

        files = os.listdir( self.sessiondir )
        files = filter( lambda x: os.path.isdir( os.path.join( self.sessiondir, x ) ), files )
        return files

    def open( self, name ):
	"""return an open session Store"""

	if not self.session_exists( name ):
            print "Session %s does not exist"%name
            return None
	return Store( self.sessiondir, name )

    def open_new( self, name ):
	"""return an open session Store"""

	if self.session_exists( name ):
            print "Session %s already exists"%name
            return None

	return NewStore( self.sessiondir, name )

    
    def open_overwrite( self, name ):
	"""returns a Store which overwrites name"""

	if not self.session_exists( name ):
            print "Session %s does not exist"%name
            return None
	return OverwriteStore( self.sessiondir, name )


    def session_exists( self, name ):
	return os.path.exists( self.sessiondir+name+"/session.xml" )

