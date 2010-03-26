#/usr/bin/env python

import gtk

sicon = gtk.status_icon_new_from_file( "/home/torbenh/sm.png" )

sicon.connect( "activate", 
