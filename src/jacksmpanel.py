#/usr/bin/env python

import gtk
import dbus.service
import pyjacksm
import os

class dialog1(object):
    def __init__( self ):
	builder = gtk.Builder()
	builder.add_from_file( os.path.join( pyjacksm.__path__[0], "data", "jacksmpanel.glade" ))

	self.dialog = builder.get_object( "dialog1" )
	self.treeview = builder.get_object( "treeview1" )
	self.listmodel = builder.get_object( "liststore1" )

	self.treeview.append_column( gtk.TreeViewColumn( "name", gtk.CellRendererText(), text=0 ) )

	projects = sm_iface.list()

	for i in projects:
	    self.listmodel.append( [i] )

	builder.connect_signals( self, None )
	    
    def ok_clicked( self, data ):
	print "ok"
	sel = self.treeview.get_selection()
	(model, it) = sel.get_selected()
	if not it:
	    return

	value = model.get_value( it, 0 )

	sm_iface.load( value )


    def cancel_clicked( self, data ):
	self.dialog.destroy()
	print "cancel"


def icon_activate( icon ):

    d = dialog1() 

    d.dialog.show()


def get_sm_iface():
    session_bus = dbus.SessionBus()
    sm_proxy = session_bus.get_object( "org.jackaudio.sessionmanager", "/org/jackaudio/sessionmanager" )
    sm_iface = dbus.Interface( sm_proxy, "org.jackaudio.sessionmanager" )

    return sm_iface

sm_iface = get_sm_iface()


sicon = gtk.status_icon_new_from_file( os.path.join( pyjacksm.__path__[0], "data", "jack_sm_icon.png" ))

sicon.connect( "activate", icon_activate )

gtk.main()
