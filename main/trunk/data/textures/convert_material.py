#!/usr/bin/env python

def output_material(l):
    s="<material name=%s"%l[0]
    if(l[ 1].lower()!="n")  : s="%s clampU=\"%s\""       % (s, l[ 1])
    if(l[ 2].lower()!="n")  : s="%s clampV=\"%s\""       % (s, l[ 2])
    if(l[ 3].lower()!="n")  : s="%s transparency=\"%s\"" % (s, l[ 3])
    if(l[ 4].lower()!="0.1"): s="%s alpha=\"%s\""        % (s, l[ 4])
    if(l[ 5].lower()!="y")  : s="%s light=\"%s\""        % (s, l[ 5])
    if(l[ 6].lower()!="n")  : s="%s sphere=\"%s\""       % (s, l[ 6])
    # Friction is not used anymore, see slowdown etc.
    if(l[ 8].lower()!="n")  : s="%s ignore=\"%s\""       % (s, l[ 8])
    if(l[ 9].lower()!="n")  : s="%s zipper=\"%s\""       % (s, l[ 9])
    if(l[10].lower()!="n")  : s="%s reset=\"%s\""        % (s, l[10]) 
    if(l[11].lower()!="y")  : s="%s collide=\"%s\""      % (s, l[11])
    if len(l)!=12:
        s="%s maxSpeed=\"%s\""      % (s, l[12])
        s="%s slowdownTime=\"%s\""      % (s, l[13])
    s=s+"/>"
    print s
    
    
    
import sys

f = open(sys.argv[1], "r")

for i in f.readlines():
    if(i[0]=="#"): continue
    i=i[:-1]
    l = i.split()
    # For empty lines
    if len(l)!=12 and len(l)!=14: continue
    output_material(l)

