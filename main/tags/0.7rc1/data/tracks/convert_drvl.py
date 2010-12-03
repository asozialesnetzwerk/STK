#!/usr/bin/env python

# Converts two STK driveline files into one xml based questkart file
# convert_drvl race.drvl race.drvr
import sys
import string

# exchange y and z dimensions
# note: dimension swapping for later, when
# STK uses a left handed coordinate system.
def xyz2xzy(s):
    l=s.split(",")
    return "%s %s %s"%(l[0],l[1],l[2])

fL=open(sys.argv[1],"r")
fR=open(sys.argv[2],"r")

print '<?xml version="1.0"?>'
print '<quads>'
i=0
tPrevious=None
while 1:
    l=fL.readline()[:-1]
    if not l: break
    l=xyz2xzy(l)
    r=fR.readline()[:-1]
    r=xyz2xzy(r)
    if tPrevious:
        if(i>0):
            print '<quad p0="%d:3" p1="%d:2" p2="%s" p3="%s"/>' \
                  %(i-1, i-1, r, l)
        else:
            print '<quad p0="%s" p1="%s" p2="%s" p3="%s"/>' \
                  %(tPrevious[0], tPrevious[1], r, l)
        i=i+1
    else:
        tFirst = (l,r)
    tPrevious= (l, r) 

# Now connect the last point with the first point
print '<quad p0="%d:3" p1="%d:2" p2="0:1" p3="0:0"/>' \
      %(i-1, i-1)
fL.close()
fR.close()
print "</quads>"
