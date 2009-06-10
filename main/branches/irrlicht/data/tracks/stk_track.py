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
import sys,os,os.path,struct,math,string,re
import b3d_export

from Blender import Mathutils
from Blender.Mathutils import *
from Blender import Draw,BGL
from Blender.BGL import *
from Blender import sys as bsys

if not hasattr(sys,"argv"): sys.argv = ["???"]

# ------------------------------------------------------------------------------
def Round(f):
    r = round(f,6) # precision set to 10e-06
    if r == int(r):
        return str(int(r))
    else:
        return str(r)

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
# Finds the closest quad to two given vertices which belong to a different id.
# The parameters vl and vr are the two vertices, id the id of the drivelines to
# which vl/vr belong. dDrivelines is the dictionary of all drivelines.
def findClosestQuad(target_left, target_right, target_id, dSortedVertices, lAllKeys):
    for id in lAllKeys:
        # ignore vertices which are in the same part 
        if target_id == id: continue
        left_verts  = dSortedVertices[id][0]
        right_verts = dSortedVertices[id][1]
        min_d       = 1000000
        min_indx    = -1
        for i in range(len(left_verts)):
            l = left_verts[i]
            r = right_verts[i]
            d = (target_left[0] - l[0])**2 + (target_left[1] - l[1])**2 + (target_left[2] - l[2])**2
            if d<min_d:
                min_d    = d
                min_indx = i
            d = (target_left[0] - r[0])**2 + (target_left[1] - r[1])**2 + (target_left[2] - r[2])**2
            if d<min_d:
                min_d    = d
                min_indx = i
            d = (target_right[0] - l[0])**2 + (target_right[1] - l[1])**2 + (target_right[2] - l[2])**2
            if d<min_d:
                min_d    = d
                min_indx = i
            d = (target_right[0] - r[0])**2 + (target_right[1] - r[1])**2 + (target_right[2] - r[2])**2
            if d<min_d:
                min_d    = d
                min_indx = i
        return min_indx
    
# ------------------------------------------------------------------------------
# The blender data structures might not be sorted, i.e. mesh.verts[0] might not
# be at all connected to mesh.verts[1]. So to re-created the right order, the
# edges have to be taken into account. This subroutine sorts the vertices
# in the order specified by the meshes. If the mesh is a loop, the point closest
# to 0,0,0 is used as a starting point. 
def sortVertices(mesh):
    # Create a dictorionary with all successors, to speed up the lookup later:
    dSucc   = {}
    for edge in mesh.edges:
        if dSucc.has_key(edge.v1):
            dSucc[edge.v1].append(edge.v2)
        else:
            dSucc[edge.v1]=[edge.v2]
        if dSucc.has_key(edge.v2):
            dSucc[edge.v2].append(edge.v1)
        else:
            dSucc[edge.v2]=[edge.v1]

    # Collect all points with a single successor only:
    l_endpoints = []
    for i in dSucc.keys():
        if len(dSucc[i])==1:
            l_endpoints.append(i)

    l_sorted_vertices = []
    # Find start point and first successor:
    if len(l_endpoints)==0:
        # closed loop, find point closest to 0
        min_dist    = 1000000
        start_index = -1
        v_min       = None
        for i in range(len(mesh.verts)):
            v = mesh.verts[i]
            d=v[0]**2 + v[1]**2 + v[2]**2
            if d<min_dist:
                min_dist    = d
                start_index = i
                v_min       = v
        if v_min==None: return []
        # Now find which of the two successors are going forward along the Yaxis:
        l_succ=dSucc[v_min]
        if l_succ[0][1] > l_succ[1][1]:
            l_sorted_vertices = [v_min, l_succ[0]]
        else:
            l_sorted_vertices = [v_min, l_succ[1]]
    elif len(l_endpoints)==2:
        # How do we pick a start point here??? For now use the one with the
        # lower index, since the user probably started with the start point
        if l_endpoints[0].index<l_endpoints[1].index:
            v_start = l_endpoints[0]
        else:
            v_start = l_endpoints[1]
        # Use v_start and its only successor (with index 0):
        l_sorted_vertices = [v_start, dSucc[v_start][0] ]

    while len(l_sorted_vertices)!=len(mesh.verts):
        # Stop if we reach a vertices with only a single successor - which is the
        # the node we are coming from (except for the very first node in case
        # of a non-loop).
        if len(dSucc[ l_sorted_vertices[-1] ])==1: break
        n1 = dSucc[ l_sorted_vertices[-1] ][0]  # first successor
        n2 = dSucc[ l_sorted_vertices[-1] ][1]  # second successor
        if l_sorted_vertices[-2] == n1:
            l_sorted_vertices.append(n2)
        else:
            l_sorted_vertices.append(n1)

    return l_sorted_vertices
        
# ------------------------------------------------------------------------------
# Writes the track.quad file with the list of all quads, and the track.graph
# file defining a graph node for each quad and a basic connection between all
# graph nodes.
def writeQuadAndGraph(sFilename, dDrivelines):
    start_time = bsys.time()
    print "stk_track: Writing quad file --> ",
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
    # For each vertex this mapping contains all neighbours
    dVertex2Neighb     = {}
    dSortedVertices    = {}
    for id in lAllKeys:
        objl  = dDrivelines[id]["left"]
        objr  = dDrivelines[id]["right"]
        meshl = objl.getData()
        meshr = objr.getData()
        meshl.transform(objl.getMatrix())
        meshr.transform(objr.getMatrix())
        ldl = sortVertices(meshl)
        rdl = sortVertices(meshr)
        dSortedVertices[id]=[ldl, rdl]   # save sorted vertices for later
        l   = ldl[0]
        r   = rdl[0]
        l1  = ldl[1]
        r1  = rdl[1]
        if id=="":
            f.write("<!-- Main driveline -->\n")
        else:
            f.write("<!-- Driveline: %s -->\n"%id)
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
                %(i, i))  # +lStartQuad[-1] - but this is always 0 for main lap
            last_main_lap_quad = count
            count = count + 1
        lStartQuad.append(lStartQuad[-1]+count)
    f.write("</quads>\n")
    f.close()
    print bsys.time()-start_time,"seconds. "
    start_time = bsys.time()
    print "stk_track: Writing graph file -->",
    f=open(sFilename+".graph", "w")
    f.write("<?xml version=\"1.0\"?>\n")
    f.write("<graph>\n")
    f.write("  <!-- First define all nodes of the graph, and what quads they represent -->\n")
    f.write("  <node-list from-quad=\"%d\" to-quad=\"%d\"/>  <!-- map each quad to a node  -->\n"\
            %(0, lStartQuad[-1]))
    f.write("  <!-- Define the main loop -->\n");
    f.write("  <edge-loop from=\"%d\" to=\"%d\"/>\n" % (0, last_main_lap_quad) )
    for i in range(1, len(lAllKeys)):
        id     = lAllKeys[i]
        f.write("<!-- Shortcut %s -->\n"%id)
        objl   = dDrivelines[id]["left"]
        objr   = dDrivelines[id]["right"]
        vl     = dSortedVertices[id][0]    # left side
        vr     = dSortedVertices[id][1]    # right side
        nBegin = findClosestQuad(vl[0],  vr[0],  id, dSortedVertices, lAllKeys)
        nEnd   = findClosestQuad(vl[-1], vr[-1], id, dSortedVertices, lAllKeys)

        f.write("  <edge      from=\"%d\" to=\"%d\"/>          <!-- Enter shortcut %s  -->\n"\
                %(nBegin, lStartQuad[i], id))
        f.write("  <edge-line from=\"%d\" to=\"%d\"/>          <!-- Shortcut %s        -->\n"\
                  %(lStartQuad[i], lStartQuad[i+1]-1, id))
        f.write("  <edge      from=\"%d\" to=\"%d\"/>          <!-- Leave shortcut %s  -->\n"\
                %(lStartQuad[i+1]-1, nEnd, id))
        #
    f.write("</graph>\n")
    f.close()
    print bsys.time()-start_time,"seconds. "
      
# -----------------------------------------------------------------------------------------
def writeSceneFile(sFilename, sTrackName, sWaterName, lEmpties):
    start_time = bsys.time()
    print "Writing scene file -->",
    f = open(sFilename+".scene", "w")
    f.write("<?xml version=\"1.0\"?>\n")
    f.write("<scene>\n")
    
    f.write("  <track model=\"%s\" x=\"0\" y=\"0\" z=\"0\"/>\n"%sTrackName)
    if sWaterName:
        f.write("  <waster model=\"%s\" x=\"0\" y=\"0\" z=\"0\"/>\n"""%sWaterName)
        
    rad2deg = 180.0/3.1415926
    for obj in lEmpties:
        rx,ry,rz = map(lambda x: rad2deg*x, obj.rot)
        h,p,r    = map(str, map(Round, [rz,rx,ry])  )
        x,y,z    = map(str, map(Round, obj.loc     )  )
        l        = obj.name.split(".")
        if len(l)!=1:
            if l[-1].isdigit():   # Remove number appended by blender
                l = l[:-1]
            name = ".".join(l)
        else:
            name = obj.name
        # Portability for old models:
        g=re.match("(.*) *{(.*)}", name)
        if g:
            name  = g.group(1)
            specs = g.group(2).lower()
            if specs.find("z")>=0: z=None
            if specs.find("p")>=0: p=None
            if specs.find("r")>=0: r=None
        if name=="GHERRING": name="banana"
        if name=="RHERRING": name="item"
        if name=="YHERRING": name="nitro-big"
        if name=="SHERRING": name="nitro-small"
        s="%s x=\"%s\" y=\"%s\""%(name, x, y)
        if z: s="%s z=\"%s\""%(s, z)
        if p and p!="0": s="%s p=\"%s\""%(s, p)
        if r and r!="0": s="%s r=\"%s\""%(s, r)
        # FIXME: do we have other items?
        # FIXME: what about zipper??
        if name in ["banana", "item", "nitro-big", "nitro-small", "zipper.ac"]:
            f.write("  <%s />\n"%s)
        else:
            print "Unknown item: '%s' --> '%s'"%(obj.name, name)
    f.write("</scene>\n")
    f.close()
    print bsys.time()-start_time,"seconds"
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
    writeQuadAndGraph(sFilename, dDrivelines)

    start_time = bsys.time()
    print "Exporting track -->",
    sTrackName = sBase+"_track.b3d"
    #FIXME for now to save time: b3d_export.write_b3d_file(sFilename+"_track.b3d", lTrack)
    print bsys.time()-start_time,"seconds."
    sWaterName = ""
    if lWater:
        start_time=bsys.time()
        sWaterName = sBase+"_water.b3d"
        print "Exporting water -->",
        # FIXME for now to save time: b3d_export.write_b3d_file(sFilename+"_water.b3d", lWater)
        print bsys.time()-start_time,"seconds."

    # scene file
    # ----------
    writeSceneFile(sFilename, sTrackName, sWaterName, lEmpties)

#Main
def main():
    tmp_filename = Blender.sys.makename(ext = ".track")
    Blender.Window.FileSelector(savescene_callback,"Export STK track",tmp_filename)

if __name__ == "__main__":
    main()
