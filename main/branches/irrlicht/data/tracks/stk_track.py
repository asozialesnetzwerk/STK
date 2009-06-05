#!BPY

"""
Name: 'STK Track Exporter (.track)...'
Blender: 248a
Group: 'Export'
Tooltip: 'Export a SuperTuxKart track scene'
"""
__author__ = ["Joerg Henrichs (hiker)"]
__url__ = ["supertuxkart.sourceforge.net"]
__version__ = "0.01"
__bpydoc__ = """\
"""

# Copyright (C) 2009 Joerg Henrichs
# INSERT (C) here!

#If you get an error here, it might be
#because you don't have Python installed.
import Blender
import BPyMesh
import sys,os,os.path,struct,math,string
import b3d_export

from Blender import Mathutils
from Blender.Mathutils import *
from Blender import Draw,BGL
from Blender.BGL import *

if not hasattr(sys,"argv"): sys.argv = ["???"]

# ------------------------------------------------------------------------------
def writeTrackFile(sFilename, sBase):
    f = open(sFilename+".irrtrack", 'wb')
    f.write("""<?xml version="1.0"?>
<track  name        = "Name"
        version     = "1"
        groups      = "standard"
        description = "By ..."
        music       = "ChillCarrier-Druckverlust.music"
        screenschot = "shot-lighthouse.png
        driveline   = "%s.driveline"
        mapping     = "%s.mapping"
        camera-final-position  ="-10 25 3"
        camera-final-hpr       ="-140 -7 0"
>
  <!-- Parameters for a sky dome:
       texture:  the name of the texture to use
       horizontal: Number of vertices of a horizontal layer of the sphere.
       vertical: Number of vertices of a vertical layer of the sphere.
       texture-percent: How much of the height of the texture is used. 
                        Should be between 0 and 1.
       sphere-percent: How much of the sphere is drawn. Value should be 
                       between 0 and 2, where 1 is an exact half-sphere
                       and 2 is a full sphere.  -->
  <sky-dome texture="lighthouse_sky.jpg"
            horizontal="16" vertical="16" 
            texture-percent="0.5" sphere-percent="1.3"/>
            "
</track>
""" % (sBase, sBase))
    f.close()
    
# ------------------------------------------------------------------------------
def writeQuadAndGraph(sFilename, dDrivelines):
    print "stk_track: Writing quad file"
    if not dDrivelines.has_key(""):
        print "No main driveline defines, no driveline information exported!!!"
        return
    
    # Some more consistency test: check that we have left/right pairs, and that
    # the curves have the same size:
    lAllKeys= dDrivelines.keys()
    for id in lAllKeys:
        if len(dDrivelines[id])!=2:
            # More than two is already checked, so it must be only one driveline here.
            print "For driveline '%s' only %d mesh is defined, must be 2."%(id, len(dDrivelines[id]))
            print "Driveline is ignored."
            del dDrivelines[id]
            continue
        if dDrivelines[id].keys()[0]==dDrivelines[id].keys()[1]:
            print "For driveline '%s' only side '%s' is specifed (twice)"%(id, dDrivelines[id].keys()[0])
            print "Driveline is ignored."
            del dDrivelines[id]
            continue
        meshLeft  = dDrivelines[id]["left"].getData()
        meshRight = dDrivelines[id]["right"].getData()
        if len(meshLeft.verts)!=len(meshRight.verts):
            print "For driveline '%s' the number of points must be the same for both sides."%\
                  (id)
            print "Driveline is ignored."
            del dDrivelines[id]
            continue
        if len(meshLeft.verts)<3:
            print "Driveliens '%s' have not enough points (%d), ignored."%(id, len(meshLeft.verts))
            del dDrivelines[id]
            continue
        
    # Now we have only valid drivelines left. Now write them to the quad file
    lAllKeys= dDrivelines.keys()
    lAllKeys.sort()  # Guarantees that the main driveline ("") is first
    f = open(sFilename+".quads", "w")
    f.write("<?xml version=\"1.0\"?>\n")
    f.write("<quads>\n")
    # Stores the first quad number (and since quads = graph nodes the node number) of
    # each section of the track. I.e. the main track starts with quad 0, then the
    # first alternative way, ...
    lStartQuad         = [0]
    dSuccessor         = {}
    last_main_lap_quad = 0
    for id in lAllKeys:
        objl = dDrivelines[id]["left"]
        objr = dDrivelines[id]["right"]
        meshl = objl.getData()
        meshr = objr.getData()
        meshl.transform(objl.getMatrix())
        meshr.transform(objr.getMatrix())
        ldl = meshl.verts
        rdl = meshr.verts
        l   = ldl[0]
        r   = rdl[0]
        l1  = ldl[1]
        r1  = rdl[1]
        f.write("<quad p0=\"%f,%f,%f\" p1=\"%f,%f,%f\" p2=\"%f,%f,%f\" p3=\"%f,%f,%f\"/>\n" \
            %(l[0],l[1],l[2], r[0],r[1],r[2],  \
                r1[0],r1[1],r1[2], l1[0],l1[1],l1[2]) )
        count = 1   # counts number of quads
        for i in range(1, len(ldl)-1):
            l1  = ldl[i+1]
            r1  = rdl[i+1]
            f.write("<quad p0=\"%d:3\" p1=\"%d:2\" p2=\"%f,%f,%f\" p3=\"%f,%f,%f\"/>\n" \
                %(lStartQuad[-1]+i-1, lStartQuad[-1]+i-1, \
                  r1[0],r1[1],r1[2], l1[0],l1[1],l1[2]) )
            count = count + 1
        if id=="":   # main loop, which needs to be closed:
            f.write("<quad p0=\"%d:3\" p1=\"%d:2\" p2=\"0:1\" p3=\"0:0\"/>\n" \
                %(i, i))  # well, lStartQuad[-1] - but this is always 0 for main lap
            last_main_lap_quad = count
            count = count + 1
        lStartQuad.append(lStartQuad[-1]+count)
    f.write("</quads>\n")
    f.close()
    print "stk_track: Writing graph file",lStartQuad
    f=open(sFilename+".graph", "w")
    f.write("<?xml version=\"1.0\"?>\n")
    f.write("<graph>\n")
    f.write("  <!-- First define all nodes of the graph, and what quads they represent -->\n")
    f.write("  <node-list from-quad=\"%d\" to-quad=\"%d\"/>  <!-- map each quad to a node  -->\n"\
            %(0, lStartQuad[1]))
    f.write("  <edge-loop from=\"%d\" to=\"%d\"/>            <!-- main loop of track       -->\n"\
              %(0, last_main_lap_quad))
    for i in range(len(lAllKeys)):
        if lAllKeys[i]=="": continue    # main loop was already done
        f.write("  <edge-line from=\"%d\" to=\"%d\"/>          <!-- shortcut %d              -->\n"\
                  %(lStartQuad[i], lStartQuad[i+1]-1, i))
        # 
    f.close()
      
# -----------------------------------------------------------------------------------------
def savescene_callback(sFilename):
	# FIXME: for testing only
    sFilename="c:/cygwin/home/joerg/currentSVN/data/tracks/jungle/test"
    # Settings for the b3d exporter:
    global flag_stack
    b3d_export.flag_stack = []
    b3d_export.flag_stack.append(0) #All Objects
    b3d_export.flag_stack.append(0) #Selected Only
    b3d_export.flag_stack.append(0) #Vertex Normals
    b3d_export.flag_stack.append(0) #Vertex Colors
    b3d_export.flag_stack.append(0) #Cameras
    b3d_export.flag_stack.append(0) #Lights

    # Collect the different kind of meshes this exporter handles
    # ----------------------------------------------------------
    lObj = Blender.Object.Get()
    lWater      = []
    lTrack      = []
    dDrivelines = {}
    lEmpties    = []
    for obj in lObj:
        if obj.type=="Empty":
            lEmpties.append(obj)
            continue
        if obj.type!="Mesh": continue
        try:
            p    = obj.getProperty("type")
            type = p.getData().upper()
        except RuntimeError:
            type = obj.name.upper()
        if type=="WATER":
            lWater.append(obj)
        elif type[:9]=="DRIVELINE":
            if type[:14]=="DRIVELINE_LEFT":
                id   = type[14:]
                side = "left"
            elif type[:15]=="DRIVELINE_RIGHT":
                id   = type[15:]
                side = "right"
            else:
                print "Unknown driveline: name '%s' type '%s'"%(name, type)
                print "Driveline is ignored."
                continue
            if dDrivelines.has_key(id):
                # Do some consistency tests
                if len(dDrivelines[id].keys())>1:
                    print "Too many drivelines for '%s' specified - ignored."%id
                    del dDriveliens[id]
                    continue
                k = dDrivelines[id].keys()[0]
                if k==side:
                    print "Side '%s' for driveline '%s' specified twice - ignored." %\
                          (side, id)
                    del dDrivelines[id]
                    continue
                dDrivelines[id][side] = obj
            else:
                dDrivelines[id] = {side:obj}
        elif obj.getType()=="Empty":
            lEmpties.append(obj)
        else:
            lTrack.append(obj)

    # Now export the different parts: track file
    # ------------------------------------------
    sBase = os.path.basename(sFilename)
    writeTrackFile(sFilename, sBase)

    # Quads and mapping files
    # -----------------------
    print "quads",dDrivelines
    writeQuadAndGraph(sFilename, dDrivelines)

    # scene file
    # ----------
    f = open(sFilename+".scene", 'wb')
    f.write("""<?xml version="1.0"?>\n""")
    f.write("""<scene>\n""")
    f.write("""  <track model="%s_track.b3d" x="0" y="0" z="0"/>\n"""%sBase)
    b3d_export.write_b3d_file(sFilename+"_track.b3d", lTrack)
    if lWater:
        f.write("""  <waster model="%s_water.b3d" x="0" y="0" z="0"/>\n"""%sBase)
        b3d_export.write_b3d_file(sFilename+"_water.b3d", lWater)
    f.write("</scene>""")
    f.close() 


#Main
def main():
    tmp_filename = Blender.sys.makename(ext = ".track")
    Blender.Window.FileSelector(savescene_callback,"Export STK track",tmp_filename)

if __name__ == "__main__":
    main()
