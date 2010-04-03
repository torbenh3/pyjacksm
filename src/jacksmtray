#!/usr/bin/env python

import gtk
import dbus.service
import pyjacksm
import os

class builder_base( gtk.Builder ):
    def __init__( self, filename ):
	gtk.Builder.__init__( self )
	self.add_from_file( os.path.join( pyjacksm.__path__[0], "data", filename ))


class load_dialog( object ):
    def __init__( self ):
	bb = builder_base( "load_dialog.glade" )

	self.dialog    = bb.get_object( "dialog1" )
	self.treeview  = bb.get_object( "treeview1" )
	self.listmodel = bb.get_object( "liststore1" )

	bb.connect_signals( self, None )

	self.treeview.append_column( gtk.TreeViewColumn( "name", gtk.CellRendererText(), text=0 ) )

	projects = sm_iface.list()
	projects.sort()

	for i in projects:
	    self.listmodel.append( [i] )


	self.dialog.show()
	    

    def ok_clicked( self, data ):
	sel = self.treeview.get_selection()
	(model, it) = sel.get_selected()
	if not it:
	    return

	value = model.get_value( it, 0 )

	sm_iface.load( value )
	self.dialog.destroy()

    def cancel_clicked( self, data ):
	self.dialog.destroy()

class over_dialog( object ):
    def __init__( self ):
	bb = builder_base( "overwrite_dialog.glade" )
	self.dialog    = bb.get_object( "overwrite_dialog" )

class save_dialog( object ):
    def __init__( self ):
	bb = builder_base( "save_dialog.glade" )

	self.dialog    = bb.get_object( "save_dialog" )
	self.treeview  = bb.get_object( "save_tree" )
	self.listmodel = bb.get_object( "liststore1" )
	self.entry     = bb.get_object( "name_entry" )

	bb.connect_signals( self, None )

	self.treeview.append_column( gtk.TreeViewColumn( "name", gtk.CellRendererText(), text=0 ) )

	projects = sm_iface.list()
	projects.sort()

	for i in projects:
	    self.listmodel.append( [i] )


	self.dialog.show()

    def tree_sel( self, data ):
	sel = self.treeview.get_selection()
	(model, it) = sel.get_selected()
	if not it:
	    return

	value = model.get_value( it, 0 )
	print value
	self.entry.set_text( value )


    def ok_clicked( self, data ):
	sname = self.entry.get_text()

	if sm_iface.session_exists( sname ):
	    q = gtk.MessageDialog( type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="Session already exists. Overwrite ?" )
	    r = q.run()
	    q.destroy()
	    if r == gtk.RESPONSE_YES:
		sm_iface.save_over( sname )
	else:
	    sm_iface.save_as( sname )

	self.dialog.destroy()

    def cancel_clicked( self, data ):
	self.dialog.destroy()


class popup_menu(object):
    def __init__( self, button, activate_time ):
	bb = builder_base( "session_popup.glade" )

	self.menu = bb.get_object( "popup_menu" )
	self.quit = bb.get_object( "quit_item" )

	if not sm_iface.current_session():
	    self.quit.set_sensitive( False )

	bb.connect_signals( self, None )

	self.menu.popup ( None, None, None, button, activate_time )

    def save_cb( self, data ):
	if sm_iface.current_session():
	    sm_iface.save()
	else:
	    d = save_dialog()

    def save_as_cb( self, data ):
	d = save_dialog()
	print "save as"

    def load_cb( self, data ):
	d = load_dialog()

    def quit_cb( self, data ):
	if sm_iface.current_session():
	    sm_iface.quit()


def icon_activate( icon ):
    d = dialog1()

def icon_popup( icon, button, activate_time ):
    p = popup_menu( button, activate_time )



def get_sm_iface():
    session_bus = dbus.SessionBus()
    sm_proxy = session_bus.get_object( "org.jackaudio.sessionmanager", "/org/jackaudio/sessionmanager" )
    sm_iface = dbus.Interface( sm_proxy, "org.jackaudio.sessionmanager" )

    return sm_iface

sm_iface = get_sm_iface()

sicon = gtk.status_icon_new_from_file( os.path.join( pyjacksm.__path__[0], "data", "jack_sm_icon.png" ))

#sicon.connect( "activate", icon_activate )
sicon.connect( "popup-menu", icon_popup )

gtk.main()
