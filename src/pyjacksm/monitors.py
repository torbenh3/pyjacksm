
from threading import Thread
from subprocess import *

class ProcMon (Thread):
    def __init__ (self, command ):
        Thread.__init__(self)
        self.command = command
        self.daemon = True

        self.log = []

    def run (self):
        self.p = Popen( self.command, bufsize=1, stdout=PIPE, shell=True, close_fds=True )

        while(True):
            line = self.p.stdout.readline()
            if len(line) == 0:
                break
            if len(self.log) == 100:
                del self.log[0]
            self.log.append(line.strip())

        self.log.append( "*** Program terminated !" )


class ConnMon (Thread):
    def __init__ (self, conns, cl, progress_cb, finished_cb):
        Thread.__init__(self)
        self.conns = conns
        self.cl = cl
        self.progress_cb = progress_cb
        self.finished_cb = finished_cb
        self.num_conns = len(conns)

        self.g = self.cl.get_graph()

    def run(self):

        avail_ports = self.g.get_port_list()

        while len(self.conns) > 0:
            pname = self.cl.pop_port()
            if len(pname)==0:
                break

            print "---------- got port ", pname
            to_remove = []
            for c1 in self.conns:
                print "check ", c1
                if c1[0]==pname:
                    print "take1"
                    if c1[1] in avail_ports:
                        print "take2"
                        self.cl.connect( pname, c1[1] )

                        to_remove.append( c1 )
                        if (c1[1],c1[0]) in self.conns:
                            to_remove.append( (c1[1],c1[0]) )

                if c1[1]==pname:
                    print "take3"
                    if c1[0] in avail_ports:
                        print "take4"
                        self.cl.connect( pname, c1[0] )

                        to_remove.append( c1 )
                        if (c1[1],c1[0]) in self.conns:
                            to_remove.append( (c1[1],c1[0]) )

            for r in to_remove:
                print "remove ", r
                try:
                    self.conns.remove( r )
                except:
                    print "fail"

            avail_ports.append( pname )
            self.progress_cb( self.num_conns-len(self.conns), self.num_conns )

        self.finished_cb()

    def abort_monitoring (self):
        self.cl.abort_monitor()


if __name__=='__main__':        

    def pline( line ):
        print line


    x = ProcMon( 'for i in `seq 3`; do echo -e "bla \\n"; sleep 1; done', pline )

    x.start()

    x.join( 1 )

    print "main exit"
    import sys

    sys.exit(0)


