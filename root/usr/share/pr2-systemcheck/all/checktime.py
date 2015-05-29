#!/usr/bin/env python

import sys
from subprocess import Popen, PIPE
import socket
import re

hostnames = ['c1','c2']

ret = 0

for host in hostnames:
    thishost = socket.gethostname()

    p = Popen(["ntpdate", "-q", host], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    res = p.wait()
    (o,e) = p.communicate()

    if (res == 0):
        measured_offset = float(re.search("offset (.*),", o).group(1))
        print "Offset from %s to %s -- %f"%(thishost, host, measured_offset)
        
        if abs(measured_offset) > .0001:
            print >> sys.stderr, "Offset from %s to %s too high."%(thishost,host)
            ret = 2
        
    else:
        print >> sys.stderr, "Problem running ntpdate"
        sys.exit(1)

sys.exit(ret)
