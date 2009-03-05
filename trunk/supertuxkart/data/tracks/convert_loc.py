#!/usr/bin/env python

import sys

def do_coordinates(l):
    s=""
    for i in range(len(l)):
        if l[i]=="{}":
            l[i]=""
    if len(l)>=1 and l[0]:
        s="x=\"%s\""%l[0]
    # The axis must be swapped for irrlicht
    if len(l)>=2 and l[1]:
        s="%s y=\"%s\""%(s, l[1])

    if len(l)>=3 and l[2]:
        s="%s z=\"%s\""%(s,l[2])
    return s

if __name__=="__main__":
    filename = sys.argv[1]
    f        = open(filename,"r")
    first    = 1
    for i in f.readlines():
        if(i[0]=="#"): continue
        i = i[:-1]
        l = i.split(",")
        type = l[0].lower()
        if type=="gherring":
            print "<banana %s/>" % do_coordinates(l[1:])
        elif type=="rherring":
            print "<item %s/>" % do_coordinates(l[1:])
        elif type=="sherring":
            print "<small-nitro %s/>" % do_coordinates(l[1:])
        elif type=="yherring":
            print "<big-nitro %s/>" % do_coordinates(l[1:])
        else:
            if first:
                # Note: l[0] contains "" from the .loc file!
                print "<track model=%s %s/>"%(l[0], do_coordinates(l[1:]))
            else:
                print "<object model=%s %s/>"%(l[0], do_coordinates(l[1:]))
