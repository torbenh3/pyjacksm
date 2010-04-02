#!/usr/bin/env python

from distutils.core import setup

setup(name='pyjacksm',
	version='0.1',
	description='jack session manager',
	author='Torben Hohn',
	author_email='torbenh@gmx.de',
	url='http://www.jackaudio.org/',
	packages=['pyjacksm'],
	package_dir  = {'pyjacksm': 'src/pyjacksm'},
	package_data = {'pyjacksm': ["data/jacksmpanel.glade", "data/jack_sm_icon.png"] },
	scripts=['src/jacksm'],
	data_files=[('/usr/share/dbus-1/services', ['data/org.jackaudio.sessionmanager.service'])]
	)

