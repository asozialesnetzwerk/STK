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

from Blender import Mathutils, IpoCurve, Constraint
from Blender.Mathutils import *
from Blender import Draw,BGL
from Blender.BGL import *
from Blender import sys as bsys

if not hasattr(sys,"argv"): sys.argv =m ["???"]

# ------------------------------------------------------------------------------
def Round(f):
    r = round(f,6) # precision set to 10e-06
    if r == int(r):
        return str(int(r))
    else:
        return str(r)

# ------------------------------------------------------------------------------
# Gets an id property of an objects, returning the default if the id property
# is not set.
def getIdProperty(obj, name, default=""):
    try:
        return obj.properties[name]
    except:
        pass
    return default

# ------------------------------------------------------------------------------
# Returns a game logic property
def getProperty(obj, name, default=""):
    try:
        return obj.getProperty(name).getData()
    except:
        return default

# ------------------------------------------------------------------------------
# Returns a string 'xyz="1 2 3" hpr="4 5 6"' where 1,2,... are the actual
# location and rotation of the given object. The location has a swapped
# y and z axis (so that the same coordinate system as in-game is used), and
# rotations are multiplied by 10 (since bullet stores the values in units
# if 10 degrees.)
def getXYZHPRString(obj):
    loc   = obj.loc
    hpr   = obj.rot
    s="xyz=\"%f %f %f\" hpr=\"%f %f %f\"" %\
       (loc[0], loc[2], loc[1], hpr[0]*10.0, hpr[1]*10.0, hpr[2]*10.0)
    return s
    
# ------------------------------------------------------------------------------
# Exports the models as b3d object in local coordinate, i.e. with the object
# center at (0,0,0).
def exportLocalB3D(obj, name):
    oldLoc = obj.loc
    oldRot = obj.rot
    obj.loc=(0,0,0)
    obj.rot=(0,0,0)
    b3d_export.write_b3d_file(name, [obj])
    obj.loc = oldLoc
    obj.rot = oldRot

# ==============================================================================
# The actual exporter. It is using a class mainly to store some information
# between calls to different functions, e.g. a cache of exported objects.
class TrackExport:

    
    def writeTrackFile(self, sPath, sBase, lCurves):
        print "Writing track.xml file",
        start_time  = bsys.time()
        scene       = Blender.Scene.getCurrent()
        name        = getIdProperty(scene, "name", "Name of Track")
        version     = getIdProperty(scene, "version", "1")
        groups      = getIdProperty(scene, "groups", "standard")
        description = getIdProperty(scene, "description", "Description")
        # Support for multi-line descriptions:
        description = description.replace("\\n", "\n")
        music       = getIdProperty(scene, "music", "musicfile.music")
        screenshot  = getIdProperty(scene, "screenshot", "ssot-%s.jpg"%name)
        f = open(sPath+"/track.xml", 'wb')
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<track  name        = \"%s\"\n"%name)
        f.write("        version     = \"%s\"\n"%version)
        f.write("        groups      = \"%s\"\n"%groups)
        f.write("        description = \"%s\"\n"%description)
        f.write("        music       = \"%s\"\n"%music)
        f.write("        screenschot = \"%s\"\n"%screenshot)
        f.write("        driveline   = \"%s.driveline\"\n"%sBase)
        f.write("        mapping     = \"%s.mapping\"\n"%sBase)
        f.write("        camera-final-position  =\"-10 25 3\"\n")
        f.write("        camera-final-hpr       =\"-140 -7 0\"\n")
        f.write("""
      <!-- Parameters for a sky dome:
           texture:  the name of the texture to use
           horizontal: Number of vertices of a horizontal layer of the sphere.
           vertical: Number of vertices of a vertical layer of the sphere.
           texture-percent: How much of the height of the texture is used. 
                            Should be between 0 and 1.
           sphere-percent: How much of the sphere is drawn. Value should be 
                           between 0 and 2, where 1 is an exact half-sphere
                           and 2 is a full sphere.  -->
      <sky-dome texture=\"lighthouse_sky.jpg\"
                horizontal=\"16\" vertical=\"16\" 
                texture-percent=\"0.5\" sphere-percent=\"1.3\"/>
    """ )
        self.writeCurve(f, lCurves)
        f.write("</track>\n")
        f.close()
        print bsys.time()-start_time, "seconds"
        
    # -----------------------------------------------------------------------------------------
    def writeCurve(self, f, lCurves):
        count = 0
        for curves in lCurves:
            type=getProperty(curves, "type").lower()
            if not type in ["camera", "anim2d", "anim3d"]: continue
            count = count + 1
        if count==0: return
        f.write("  <curves>\n")
        for curves in lCurves:
            type=getProperty(curves, "type").lower()
            if not type in ["camera", "anim2d", "anim3d"]: continue
            matrix = curves.getMatrix()
            for nu in curves.data:
                # 0:"poly", 1:"bezier", 4:"nurbs"
                if nu.type==4:
                    f.write("    <%s curvetype=\"nurb\" name=\"%s\">\n"%(type, curves.name))
                    for i in nu:
                        v=Vector(i[0],i[1],i[2]) * matrix
                        f.write("      <p=\"%f %f %f\"/>\n"%(v[0], v[1], v[2]))
                    f.write("    </%s>\n"%type)
                elif nu.type==1:
                    f.write("    <%s curvetype=\"bezier\" name=\"%s\">\n"%(type, curves.name))
                    for i in list(nu):
                        # v0/v2 = hanldes, v1 = control point
                        v0 = Vector(i.vec[0][0],i.vec[0][1],i.vec[0][2])
                        v1 = Vector(i.vec[1][0],i.vec[1][1],i.vec[1][2])
                        v2 = Vector(i.vec[2][0],i.vec[2][1],i.vec[2][2])
                        v0 = v0*matrix
                        v1 = v1*matrix
                        v2 = v2*matrix
                        f.write("      <point c=\"%f %f %f\" h1=\"%f %f %f\" h2=\"%f %f %f\" />\n"% \
                                ( v1[0],v1[1],v1[2],
                                  v0[0],v0[1],v0[2],
                                  v2[0],v2[1],v2[2] ) )
                    f.write("    </%s>\n"%type)
        f.write("  </curves>\n")
                    
        
    # ------------------------------------------------------------------------------
    # Finds the closest quad to two given vertices which belong to a different id.
    # The parameters vl and vr are the two vertices, id the id of the drivelines to
    # which vl/vr belong. dDrivelines is the dictionary of all drivelines.
    def findClosestQuad(self, target_left, target_right, target_id, lAllDrivelines):
        for (id, left_verts, right_verts) in lAllDrivelines:
            # ignore vertices which are in the same part 
            if target_id == id: continue
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
    # This creates a dictionary for a mesh which contains for each vertex a list
    # with all its neighbours.
    def createNeighbourDict(self, mesh):
        dNext = {}
        for e in mesh.edges:
            if dNext.has_key(e.v1):
                dNext[e.v1].append(e.v2)
            else:
                dNext[e.v1] = [e.v2]
            if dNext.has_key(e.v2):
                dNext[e.v2].append(e.v1)
            else:
                dNext[e.v2] = [e.v1]
        return dNext
        
    # ------------------------------------------------------------------------------
    # The blender data structures might not be sorted, i.e. mesh.verts[0] might not
    # be at all connected to mesh.verts[1]. So to re-created the right order, the
    # edges have to be taken into account. This subroutine sorts the vertices
    # in the order specified by the meshes. If the mesh is a loop, the point closest
    # to 0,0,0 is used as a starting point. 
    def sortVerticesOldDrivelines(self, mesh):
        # Create a dictorionary with all successors, to speed up the lookup later:
        dSucc   = self.createNeighbourDict(mesh)
    
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
    
    
        while len(l_sorted_vertices)!=len(mesh.verts):
            # Stop if we reach a vertices with only a single successor - which is the
            # the node we are coming from
            if len(dSucc[ l_sorted_vertices[-1] ])==1: break
            n1 = dSucc[ l_sorted_vertices[-1] ][0]  # first successor
            n2 = dSucc[ l_sorted_vertices[-1] ][1]  # second successor
            # Append the node that's not already in the list:
            if l_sorted_vertices[-2] == n1:
                l_sorted_vertices.append(n2)
            else:
                l_sorted_vertices.append(n1)
    
        return l_sorted_vertices
            
    # ------------------------------------------------------------------------------
    # Converts the old driveline structure:
    def convertOldDrivelines(self, dOldDrivelines, lAllDrivelines):
        lAllKeys= dOldDrivelines.keys()
        lAllKeys.sort()  # Guarantees that the main driveline ("") is first
        for id in lAllKeys:
            objl  = dOldDrivelines[id]["left"]
            objr  = dOldDrivelines[id]["right"]
            meshl = objl.getData()
            meshr = objr.getData()
            meshl.transform(objl.getMatrix())
            meshr.transform(objr.getMatrix())
            ldl = self.sortVerticesOldDrivelines(meshl)
            rdl = self.sortVerticesOldDrivelines(meshr)
            lAllDrivelines.append( (id, ldl, rdl) )
        
    # ------------------------------------------------------------------------------
    # This helper function determines the start vertex for a driveline.
    # Details are documented in convertNewDrivelines. It returns as list with
    # the two starting lines.
    def findStartVertex(self, dNext):
        # Find all vertices with exactly two neighbours
        lOneNeighbour = []
        for i in dNext.keys():
            if len(dNext[i])==1:
                lOneNeighbour.append(i)

        if len(lOneNeighbour)!=2:
            return None

        l=[]
        for v in lOneNeighbour:
            l.append( [v,dNext[v][0]] )
        return l

        
    # ------------------------------------------------------------------------------
    # Converts a new drivelines. New drivelines have the following structure:
    #   +---+---+--+--...--+--
    #   |   |      |       |  
    #   +---+------+--...--+--
    # The starting quad of the drivelines is marked by two edges ending in a
    # single otherwise unconnected vertex. These two vertices (and edges) are
    # not used in the actual driveline, they are only used to indicate where
    # the drivelines starts.
    def convertNewDrivelines(self, lNewDrivelines, lAllDrivelines):
        # Create a dictionary with all neighbours for each vertex:
    
        # Find the begin of the drivelines:
        for driveline in lNewDrivelines:
            mesh = driveline.getData()
            mesh.transform(driveline.getMatrix())
            dNext = self.createNeighbourDict(mesh)
            start = self.findStartVertex(dNext)
            if not start:
                print "Driveline '%s' is incorrect formed, it does not have"%driveline.name
                print "exactly two vertices with only one neighbour."
                return
            # Left and right are actually arbitrary, since it doesn't matter if
            # the quads created from them are clockwise or counter-clockwise. The
            # start vector is removed later, it simplifies whe while loop.
            lLeft  = start[0]
            lRight = start[1]
            count=0
            # Just in case that we have an infinite loop due to a malformed graph:
            # stop after 10000 vertices
            while count<10000:
                count = count + 1
                # Get all neighbours. One is the previous point, one
                # points to the opposite side - we need the other one.
                neighb = dNext[lLeft[-1]]
                for i in neighb:
                    if i==lLeft[-2]: continue   # pointing backwards
                    if i==lRight[-1]: continue  # to opposite side
                    lLeft.append(i)
                    break
                else:
                    # No new element found --> this must be the end
                    # of the list!!
                    break
                # Same for other side:
                neighb = dNext[lRight[-1]]
                for i in neighb:
                    if i==lRight[-2]: continue   # pointing backwards
                    # Note lLeft has already a new element appended,
                    # so we have to check for the 2nd last element!
                    if i==lLeft[-2]: continue  # to opposite side
                    lRight.append(i)
                    break
            if count>=10000:
                print "Warning, Only the first 10000 vertices of driveline '%s' are exported" %\
                      (driveline.name)
            lAllDrivelines.append( ( driveline.name, lLeft[1:], lRight[1:] ) )
    
            
    # ------------------------------------------------------------------------------
    # Writes the track.quad file with the list of all quads, and the track.graph
    # file defining a graph node for each quad and a basic connection between all
    # graph nodes.
    def writeQuadAndGraph(self, sPath, lNewDrivelines, dOldDrivelines):
        start_time = bsys.time()
        print "stk_track: Writing quad file --> ",
        if not dOldDrivelines.has_key("") and not lNewDrivelines:
            print "No main driveline defined, no driveline information exported!!!"
            return
    
        # No consistency tests for old drivelines, since they should be removed!
    
        lAllDrivelines = []
        self.convertOldDrivelines(dOldDrivelines, lAllDrivelines)
        self.convertNewDrivelines(lNewDrivelines, lAllDrivelines)
        
        f = open(sPath+"/quads.xml", "w")
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
        count              = 0
        for (name, lLeft, lRight) in lAllDrivelines:
            l   = lLeft[0]
            r   = lRight[0]
            l1  = lLeft[1]
            r1  = lRight[1]
            if count==0:
                f.write("<!-- Main driveline -->\n")
            else:
                f.write("<!-- Driveline: %s -->\n"%name)
            count = count + 1
            f.write("  <quad p0=\"%f,%f,%f\" p1=\"%f,%f,%f\" p2=\"%f,%f,%f\" p3=\"%f,%f,%f\"/>\n" \
                %(l[0],l[1],l[2], r[0],r[1],r[2], r1[0],r1[1],r1[2], l1[0],l1[1],l1[2]) )
            count = 1   # counts number of quads
            for i in range(1, len(lLeft)-1):
                l1  = lLeft[i+1]
                r1  = lRight[i+1]
                f.write("  <quad p0=\"%d:3\" p1=\"%d:2\" p2=\"%f,%f,%f\" p3=\"%f,%f,%f\"/>\n" \
                    %(lStartQuad[-1]+i-1, lStartQuad[-1]+i-1, \
                      r1[0],r1[1],r1[2], l1[0],l1[1],l1[2]) )
                count = count + 1
            if name=="":   # main loop, which needs to be closed:
                f.write("  <quad p0=\"%d:3\" p1=\"%d:2\" p2=\"0:1\" p3=\"0:0\"/>\n" \
                    %(i, i))  # +lStartQuad[-1] - but this is always 0 for main lap
                last_main_lap_quad = count
                count = count + 1
            lStartQuad.append(lStartQuad[-1]+count)
        f.write("</quads>\n")
        f.close()
        print bsys.time()-start_time,"seconds. "
        start_time = bsys.time()
        print "stk_track: Writing graph file -->",
        f=open(sPath+"/graph.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<graph>\n")
        f.write("  <!-- First define all nodes of the graph, and what quads they represent -->\n")
        f.write("  <node-list from-quad=\"%d\" to-quad=\"%d\"/>  <!-- map each quad to a node  -->\n"\
                %(0, lStartQuad[-1]))
        f.write("  <!-- Define the main loop -->\n");
        f.write("  <edge-loop from=\"%d\" to=\"%d\"/>\n" % (0, last_main_lap_quad) )
        for i in range(1, len(lAllDrivelines)):
            id     = lAllDrivelines[i][0]
            f.write("  <!-- Shortcut %s -->\n"%id)
            lLeft   = lAllDrivelines[i][1]
            lRight  = lAllDrivelines[i][2]
            nBegin = self.findClosestQuad(lLeft[0],  lRight[0],  id, lAllDrivelines)
            nEnd   = self.findClosestQuad(lLeft[-1], lRight[-1], id, lAllDrivelines)
    
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
    # Writes the animation for objects using IPOs:
    def writeAnimationWithIPO(self, f, sPath, obj, ipo):
        # An animated object can set the 'name' property, then this name will
        # be used to name the exported object (instead of the python name
        # which might be a default name with a number). Additionally, names
        # are cached so it can be avoided to export two or more identical
        # objects.
        b3d_name = getProperty(obj, "name", obj.name)+".b3d"
        if not self.dExportedObjects.has_key(b3d_name):
            exportLocalB3D(obj, sPath+"/"+b3d_name)
            
        shape = getProperty(obj, "shape", "")
        if shape:
            shape="shape=\"%s\""%shape
    
        # Note: Y and Z are swapped!
        f.write("    <animations-IPO obj=\"%s\" %s %s>\n"% \
                (b3d_name, getXYZHPRString(obj), shape),)
        dInterp = {IpoCurve.InterpTypes.BEZIER:        "bezier",
                   IpoCurve.InterpTypes.LINEAR:        "linear",
                   IpoCurve.InterpTypes.CONST:         "const"          }
        dExtend = {IpoCurve.ExtendTypes.CONST:         "const",
                   IpoCurve.ExtendTypes.EXTRAP:        "extrap",
                   IpoCurve.ExtendTypes.CYCLIC_EXTRAP: "cyclic_extrap",
                   IpoCurve.ExtendTypes.CYCLIC:        "cyclic"         }
        for curve in ipo:
            # Swap Y and Z axis
            if   curve.name=="LocZ": name="LocY"
            elif curve.name=="LocY": name="LocZ"
            elif curve.name=="RotY": name="RotZ"
            elif curve.name=="RotZ": name="RotY"
            else:                    name=curve.name
            # Rotations are stored in units of 10 degrees!
            if name[:3]=="Rot": factor=10
            else:               factor=1
            f.write("      <curve channel=\"%s\" interpolation=\"%s\" extend=\"%s\">\n"% \
                    (name, dInterp[curve.interpolation], dExtend[curve.extend]))
            
            for bez in curve.bezierPoints:
                if curve.interpolation==IpoCurve.InterpTypes.BEZIER:
                    f.write("        <p c=\"%f %f\" h1=\"%f %f\" h2=\"%f %f\"/>\n"%\
                            (bez.vec[1][0],factor*bez.vec[1][1], bez.vec[0][0],factor*bez.vec[0][1],
                             bez.vec[2][0],factor*bez.vec[2][1]))
                else:
                    f.write("        <p c=\"%f %f\"/>\n"%(bez.vec[1][0],f*bez.vec[1][1]))
            f.write("      </curve>\n")
            
        f.write("    </animations-IPO>\n")
            
        
    # -----------------------------------------------------------------------------------------
    # Writes an animation that uses a path constrained.
    def writeAnimationsWithPaths(self, f, sPath, obj):
        #print "b3d export", obj.name
        print "'%s' is using path '%s'"%(obj.name, \
                               obj.constraints[0][Constraint.Settings.TARGET].name)
    
    # -----------------------------------------------------------------------------------------
    # Writes out all animations (be it animations with IPO or animations with path
    # constraints).
    def writeAnimations(self, f, sPath, lAnimations):
        scene       = Blender.Scene.getCurrent()
        f.write("  <animations fps=\"%d\">\n"%scene.getRenderingContext().fps)
        for obj in lAnimations:
            ipo = obj.getIpo()
            if ipo:
                self.writeAnimationWithIPO(f, sPath, obj, ipo)
            else:
                self.writeAnimationsWithPaths(f, sPath, obj)
        f.write("  </animations>\n")
                
    # -----------------------------------------------------------------------------------------
    # Writes out all checklines.
    def writeChecks(self, f, lChecklines):
        f.write("  <checks>\n")
        for obj in lChecklines:
            mesh=obj.getData()
            # Convert to world space
            mesh.transform(obj.getMatrix())
            subtype = getProperty(obj, "kind", "new-lap")
            if len(mesh.verts)!=2:
                print "Mesh '%s' has '%d', not 2 vertices - ignored."%\
                      (obj.name, len(mesh.verts))
                continue
            min_h = mesh.verts[0][2]
            if mesh.verts[1][2]<min_h: min_h = mesh.verts[1][2]
            f.write("    <checkline type=\"%s\" p1=\"%f %f\" p2=\"%f %f\" min-height=\"%f\"/>\n"% \
                    (subtype, mesh.verts[0][0], mesh.verts[0][1],mesh.verts[1][0], mesh.verts[1][1],
                     min_h))
        f.write("  </checks>\n")
            
    # -----------------------------------------------------------------------------------------
    # Writes the scene files, which includes all models, animations, and items
    def writeSceneFile(self, sPath, sTrackName, sWaterName, lItems, lAnimations,
                       lPhysical, lChecklines):
        start_time = bsys.time()
        print "Writing scene file -->",
        f = open(sPath+"/scene.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<scene>\n")
        
        f.write("  <track model=\"%s\" x=\"0\" y=\"0\" z=\"0\"/>\n"%sTrackName)
        if sWaterName:
            f.write("  <water model=\"%s\" x=\"0\" y=\"0\" z=\"0\"/>\n"""%sWaterName)
            
        rad2deg = 180.0/3.1415926
        for obj in lItems:
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
            # FIXME: what about zipper??
            if name=="GHERRING": name="banana"
            if name=="RHERRING": name="item"
            if name=="YHERRING": name="nitro-big"
            if name=="SHERRING": name="nitro-small"
            s="%s x=\"%s\" y=\"%s\""%(name, x, y)
            if z: s="%s z=\"%s\""%(s, z)
            if p and p!="0": s="%s p=\"%s\""%(s, p)
            if r and r!="0": s="%s r=\"%s\""%(s, r)
            f.write("  <%s />\n"%s)

        for obj in lPhysical:
            name=getProperty(obj, "name", obj.name)
            # If the name ends with ".b3d", don't export this model anymore and
            # assume it's a standard model included in STK
            if not re.search("\.b3d$", name):
                name=name+".b3d"
                exportLocalB3D(obj, sPath+"/"+name)
            shape = getProperty(obj, "shape", "box")
            mass  = getProperty(obj, "mass", 10)
            f.write("  <physical-object %s\n"%(getXYZHPRString(obj)))
            f.write("                   model=\"%s\" shape=\"%s\" mass=\"%f\"/>\n"% \
                    (name, shape, mass))
            
        if lAnimations:
            self.writeAnimations(f, sPath, lAnimations)
        if lChecklines:
            self.writeChecks(f, lChecklines)
        f.write("</scene>\n")
        f.close()
        print bsys.time()-start_time,"seconds"
    # -----------------------------------------------------------------------------------------
    def storeOldDriveline(self, type, obj, dDrivelines):
        # Check for old drivelines:
        if type[:8]=="DRV_LEFT":
            id   = type[8:]
            side = "left"
        elif type[:9]=="DRV_RIGHT":
            id   = type[9:]
            side = "right"
        else:
            print "Unknown driveline: '%s' - ignored."%type
            return
        if dDrivelines.has_key(id):
            # Do some consistency tests
            if len(dDrivelines[id].keys())>1:
                print "Too many drivelines for '%s' specified - ignored."%id
                del dDrivelines[id]
                return
            k = dDrivelines[id].keys()[0]
            if k==side:
                print "Side '%s' for driveline '%s' specified twice - ignored." %\
                      (side, id)
                del dDrivelines[id]
                return
            dDrivelines[id][side] = obj
        else:
            dDrivelines[id] = {side:obj}
        
    # -----------------------------------------------------------------------------------------

    def __init__(self, sFilename):
        self.dExportedObjects = {}
        
        # Collect the different kind of meshes this exporter handles
        # ----------------------------------------------------------
        lObj           = Blender.Object.Get()
        lWater         = []
        lTrack         = []
        dOldDrivelines = {}
        lNewDrivelines = []
        main_driveline = None
        lItems         = []
        lCameraCurves  = []
        lAnimations    = []
        lPhysical      = []
        lChecklines    = []
        for obj in lObj:
            # Try to get the supertuxkart type field. If it's not defined,
            # use the name of the objects as type.
            stktype = getProperty(obj, "type", obj.name).upper()
            # Make it possible to ignore certain objects, e.g. if you keep a
            # selection of 'templates' (ready to go models) around to be
            # copied into the main track.
            if stktype=="IGNORE": continue
            
            if obj.type=="Empty" and \
               stktype[:8] in ["GHERRING", "RHERRING", "YHERRING", "SHERRING",  # backw. comp.
                               "BANANA", "ITEM", "NITRO-SM", "NITRO-BI"]:
                lItems.append(obj)
                continue
            elif obj.type=="Curve":
                # Only append camera, other curves will be handled in animations
                if stktype=="CAMERA": lCameraCurves.append(obj)
            elif stktype[:6]=="PHYSIC":
                lPhysical.append(obj)
            elif obj.type!="Mesh":
                #print "Non-mesh object '%s' (type: '%s') is ignored!"%(obj.name, stktype)
                continue
            
            if stktype=="WATER":
                lWater.append(obj)
            elif stktype=="CHECKLINE":
                lChecklines.append(obj)
            # Check for new drivelines
            elif stktype[:14]=="MAIN-DRIVELINE":
                # The main driveline must be the first driveline in the list
                main_driveline = obj
            elif stktype[:9]=="DRIVELINE":
                lNewDrivelines.append(obj)
            # Backwards compatibility:
            elif stktype[:4]=="DRV_":
                self.storeOldDriveline(stktype, obj, dOldDrivelines)
            elif stktype[:4]=="ANIM":
                lAnimations.append(obj)
            else:
                lTrack.append(obj)

        if not main_driveline:
            print "Main driveline missing, using first driveline as main!"
        else:
            lNewDrivelines.insert(0, main_driveline)
            
        # Now export the different parts: track file
        # ------------------------------------------
        sBase = os.path.basename(sFilename)
        sPath = os.path.dirname(sFilename)
        self.writeTrackFile(sPath, sBase, lCameraCurves)
    
        # Quads and mapping files
        # -----------------------
        self.writeQuadAndGraph(sPath, lNewDrivelines, dOldDrivelines)
    
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
            b3d_export.write_b3d_file(sFilename+"_water.b3d", lWater)
            print bsys.time()-start_time,"seconds."
    
        # scene file
        # ----------
        self.writeSceneFile(sPath, sTrackName, sWaterName, lItems, lAnimations,
                            lPhysical, lChecklines)

# =============================================================================================
def savescene_callback(sFilename):
    # FIXME: for testing only
    sFilename="c:/cygwin/home/jh235117/local/supertuxkart/supertuxkart/data/tracks/jungle/test"
    print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    # Settings for the b3d exporter:
    global flag_stack
    b3d_export.flag_stack = []
    b3d_export.flag_stack.append(0) #All Objects
    b3d_export.flag_stack.append(0) #Selected Only
    b3d_export.flag_stack.append(1) #Vertex Normals
    b3d_export.flag_stack.append(0) #Vertex Colors
    b3d_export.flag_stack.append(0) #Cameras
    b3d_export.flag_stack.append(0) #Lights

    exporter = TrackExport(sFilename)

# =============================================================================================
def main():
    tmp_filename = Blender.sys.makename(ext = ".track")
    Blender.Window.FileSelector(savescene_callback,"Export STK track",tmp_filename)

if __name__ == "__main__":
    main()
