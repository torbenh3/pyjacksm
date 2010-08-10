
from pyjacksm.session import Session, save_session
from pyjacksm.config  import Config
from pyjacksm.storage import Storage


class SessionManager( object ):
    def __init__( self ):
	self.config = Config()
	self.session_storage = Storage( self.config.sessiondir )
	self.template_storage = Storage( self.config.templatedir )

	self.current_session = None

    def list_projects( self ):
	return self.session_storage.list_projects()

    def list_templates( self ):
	return self.template_storage.list_projects()

    def get_current_session( self ):
	if self.current_session:
	    return self.current_session
	else:
	    return ""

    def session_exists( self, name ):
	return self.session_storage.session_exists( name )

    def load_session( self, name, template=False ):
        if template:
	    storage = self.template_storage
        else:
            storage = self.session_storage

	if not storage.session_exists( name ):
            print "Session %s does not exist"%name
            return None

	store = storage.open( name )
        return Session( store )

    def get_storage( self, template=False ):
        if template:
	    return self.template_storage
        else:
            return self.session_storage

    def update_current( self, name, quit, template ):
	if quit:
	    self.current_session = None
	elif not template:
	    self.current_session = name


    def save_as( self, name, quit=False, template=False ):
	sto = self.get_storage( template )
	save_session( sto.open_new( name ), quit, template )
	self.update_current( name, quit, template )


    def save_over( self, name, quit=False ):
	sto = self.get_storage()
	save_session( sto.open_overwrite( name ), quit )
	self.update_current( name, quit, template=False )

    def save( self, quit=False ):
	sto = self.get_storage()
	save_session( sto.open_overwrite( self.current_session ), quit )


