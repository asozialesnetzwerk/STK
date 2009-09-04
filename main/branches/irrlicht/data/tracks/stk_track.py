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
# A special class to store a drivelines.
class Driveline:
    def __init__(self, driveline, is_main):
        self.name      = driveline.name
        self.is_main   = is_main
        # Transform the mesh to the right coordinates.
        self.mesh      = driveline.getData()
        self.mesh.transform(driveline.getMatrix())
        # Convert the mesh into a dictionary: each vertex is a key to a
        # list of neighbours.
        self.createNeighbourDict()
        self.defineStartVertex()
        self.convertToLists()
        self.from_quad=None
        # Invisible drivelines are not shown in the minimap
        self.invisible = getProperty(driveline, "invisible", 0)
        self.disable   = getProperty(driveline, "disable",   0)
    # ------------------------------------------------------------------------------
    # Returns the name of the driveline
    def getName(self):
        return self.name
    # ------------------------------------------------------------------------------
    # Returns if this is a main driveline or not.
    def isMain(self):
        return self.is_main
    # ------------------------------------------------------------------------------
    # Stores that the start quad of this driveline is connected to quad
    # quad_index of quad driveline. 
    def setFromQuad(self, driveline, quad_index):
        # Convert the relative to driveline quad index to the global index:
        self.from_quad = driveline.getFirstQuadIndex()+quad_index
    # ------------------------------------------------------------------------------
    # Returns the global index of the quad this start point is connected to.
    def getFromQuad(self):
        return self.from_quad
    # ------------------------------------------------------------------------------
    # Returns the number of quads of this driveline
    def getNumberOfQuads(self):
        return len(self.lCenter)
    # --------------------------------------------------------------------------
    # Stores the index of the first quad in this driveline in the global
    # quad index.
    def setStartQuadIndex(self, n):
        self.global_quad_index_start = n
    # --------------------------------------------------------------------------
    # Returns the start index for this driveline in the global numbering of
    # all quads
    def getFirstQuadIndex(self):
        return self.global_quad_index_start
    # --------------------------------------------------------------------------
    # Returns the global index of the last quad in this driveline.
    def getLastQuadIndex(self):
        return self.global_quad_index_start+len(self.lCenter)-1
    # --------------------------------------------------------------------------
    # This creates a dictionary for a mesh which contains for each vertex a list
    # of all its neighbours.
    def createNeighbourDict(self):
        self.dNext = {}
        for e in self.mesh.edges:
            if self.dNext.has_key(e.v1):
                self.dNext[e.v1].append(e.v2)
            else:
                self.dNext[e.v1] = [e.v2]
            if self.dNext.has_key(e.v2):
                self.dNext[e.v2].append(e.v1)
            else:
                self.dNext[e.v2] = [e.v1]

    # ------------------------------------------------------------------------------
    # This helper function determines the start vertex for a driveline.
    # Details are documented in convertDrivelines. It returns as list with
    # the two starting lines.
    def defineStartVertex(self):
        # Find all vertices with exactly two neighbours
        self.lStart = []
        for i in self.dNext.keys():
            if len(self.dNext[i])==1:
                self.lStart.append(i)

        if len(self.lStart)!=2:
            print "Driveline '%s' is incorrect formed, it does not have"%self.name
            print "exactly two vertices with only one neighbour."
            return

        self.start_point =(  (self.lStart[0][0]+self.lStart[1][0])*0.5,
                             (self.lStart[0][1]+self.lStart[1][1])*0.5,
                             (self.lStart[0][2]+self.lStart[1][2])*0.5 )

    # ------------------------------------------------------------------------------
    # Returns the startline of this driveline
    def getStartPoint(self):
        return self.start_point
    # ------------------------------------------------------------------------------
    # Returns the distance of the start point from a given point
    def getStartDistanceTo(self, p):
        dx=self.start_point[0]-p[0]
        dy=self.start_point[1]-p[1]
        dz=self.start_point[2]-p[2]
        return dx*dx+dy*dy+dz*dz
    # ------------------------------------------------------------------------------
    # Convert the dictionary of list of neighbours to two lists - one for the
    # left side, one for the right side.
    def convertToLists(self):
        self.lLeft   = [self.lStart[0], self.dNext[self.lStart[0]][0]]
        self.lRight  = [self.lStart[1], self.dNext[self.lStart[1]][0]]
        self.lCenter = []
        count=0
        # Just in case that we have an infinite loop due to a malformed graph:
        # stop after 10000 vertices
        max_count=10000
        while count<max_count:
            count = count + 1
            # Get all neighbours. One is the previous point, one
            # points to the opposite side - we need the other one.
            neighb = self.dNext[self.lLeft[-1]]
            for i in neighb:
                if i==self.lLeft[-2]: continue   # pointing backwards
                if i==self.lRight[-1]: continue  # to opposite side
                self.lLeft.append(i)
                break
            else:
                # No new element found --> this must be the end
                # of the list!!
                break
            # Same for other side:
            neighb = self.dNext[self.lRight[-1]]
            for i in neighb:
                if i==self.lRight[-2]: continue   # pointing backwards
                # Note lLeft has already a new element appended,
                # so we have to check for the 2nd last element!
                if i==self.lLeft[-2]: continue  # to opposite side
                self.lRight.append(i)
                break
            cp=[]
            for i in range(3):
                cp.append((self.lLeft[-2][i]+self.lLeft[-1][i]+
                           self.lRight[-2][i]+self.lRight[-1][i])*0.25)
            self.lCenter.append(cp)

        if count>=max_count:
            print "Warning, Only the first %d vertices of driveline '%s' are exported" %\
                  (max_count, driveline.name)
        # Now remove the first two points, which are only used to indicate
        # the starting point:
        del self.lLeft[0]
        del self.lRight[0]
        self.end_point =(  (self.lLeft[-1][0]+self.lRight[-1][0])*0.5,
                           (self.lLeft[-1][1]+self.lRight[-1][1])*0.5,
                           (self.lLeft[-1][2]+self.lRight[-1][2])*0.5 )

    # --------------------------------------------------------------------------
    # Returns the end point of this driveline
    def getEndPoint(self):
        return self.end_point
    # --------------------------------------------------------------------------
    def getDistanceToStart(self, lDrivelines):
        return self.getDistanceTo(self.start_point, lDrivelines)
    # --------------------------------------------------------------------------
    # Returns the shortest distance to any of the drivelines in the list
    # lDrivelines from the given point p (it's actually a static function).
    # The distance is defined to be the shortest distance from the
    # start point of this driveline to all quads of all drivelines in
    # lDrivelines. This function returns the distance, the index of the
    # driveline in lDrivelines, and the local index of the quad within this
    # driveline as a tuple.
    def getDistanceTo(self, p, lDrivelines):
        if not lDrivelines: return (None, None, None)
        
        (min_dist, min_quad_index) = lDrivelines[0].getMinDistanceToPoint(p)
        min_driveline_index        = 0
        for i in range(1, len(lDrivelines)):
            if lDrivelines[i]==self: continue   # ignore itself
            (dist, quad_index) = lDrivelines[i].getMinDistanceToPoint(p)
            if dist < min_dist:
                min_dist            = dist
                min_quad_index      = quad_index
                min_driveline_index = i
        return (min_dist, min_driveline_index, min_quad_index)

    # --------------------------------------------------------------------------
    # Returns the minimum distance from the center point of each quad to the
    # point p.
    def getMinDistanceToPoint(self, p):
        pCenter   = self.lCenter[0]
        dx        = pCenter[0]-p[0]
        dy        = pCenter[1]-p[1]
        dz        = pCenter[2]-p[2]
        min_dist  = dx*dx+dy*dy+dz*dz
        min_index = 0
        for i in range(1, len(self.lCenter)):
            pCenter = self.lCenter[i]
            dx      = pCenter[0]-p[0]
            dy      = pCenter[1]-p[1]
            dz      = pCenter[2]-p[2]
            d       = dx*dx+dy*dy+dz*dz
            if d<min_dist:
                min_dist  = d
                min_index = i
        return (min_dist, min_index)

    # ------------------------------------------------------------------------------
    # Determine the driveline from lSorted which is closest to this driveline's
    # endpoint (closest meaning: having a quad that is closest).
    def computeSuccessor(self, lSorted):
        (dist, driveline_index, quad_index)=self.getDistanceTo(self.end_point,
                                                               lSorted)
        print "\ncs", self.getName(), dist, driveline_index, \
              quad_index,lSorted[driveline_index].getName()
        return quad_index+lSorted[driveline_index].getFirstQuadIndex()

    # ------------------------------------------------------------------------------
    # Writes the quads into a file.
    def write(self, f):
        l   = self.lLeft[0]
        r   = self.lRight[0]
        l1  = self.lLeft[1]
        r1  = self.lRight[1]
        if self.invisible:
            sInv = " invisible=\"1\" "
        else:
            sInv = " "
        f.write("  <!-- Driveline: %s -->\n"%self.name)
        f.write("  <quad%sp0=\"%f,%f,%f\" p1=\"%f,%f,%f\" p2=\"%f,%f,%f\" p3=\"%f,%f,%f\"/>\n" \
            %(sInv, l[0],l[1],l[2], r[0],r[1],r[2], r1[0],r1[1],r1[2], l1[0],l1[1],l1[2]) )
        for i in range(1, len(self.lLeft)-1):
            l1  = self.lLeft[i+1]
            r1  = self.lRight[i+1]
            f.write("  <quad%sp0=\"%d:3\" p1=\"%d:2\" p2=\"%f,%f,%f\" p3=\"%f,%f,%f\"/>\n" \
                    %(sInv,self.global_quad_index_start+i-1, self.global_quad_index_start+i-1, \
                  r1[0],r1[1],r1[2], l1[0],l1[1],l1[2]) )

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
                    
    # --------------------------------------------------------------------------
    # Finds the closest driveline from the list lDrivelines to the point p (i.e.
    # the driveline for which the distance between p and the drivelines start
    # point is as small as possible. Returns the index of the closest drivelines.
    def findClosestDrivelineToPoint(self, lDrivelines, p):
        min_index = 0
        min_dist  = lDrivelines[0].getStartDistanceTo(p)
        for i in range(1,len(lDrivelines)):
            driveline=lDrivelines[i]
            dist_new = driveline.getStartDistanceTo(p)
            if dist_new<min_dist:
                min_dist  = dist_new
                min_index = i

        return min_index
    
    # --------------------------------------------------------------------------
    # Find the driveline from lRemain that is closest to any of the drivelines
    # in lSorted.
    def findClosestDrivelineToDrivelines(self, lRemain, lSorted):
        remain_index                    = 0
        (min_dist, sorted_index, min_quad) = lRemain[0].getDistanceToStart(lSorted)
        for i in range(1, len(lRemain)):
            (dist, index, quad) = lRemain[i].getDistanceToStart(lSorted)
            if dist<min_dist:
                min_dist     = dist
                sorted_index = index
                min_quad     = quad
                remain_index = i
        return (remain_index, sorted_index, min_quad)
        
    # --------------------------------------------------------------------------
    # Converts a new drivelines. New drivelines have the following structure:
    #   +---+---+--+--...--+--
    #   |   |      |       |  
    #   +---+--+---+--...--+--
    # The starting quad of the drivelines is marked by two edges ending in a
    # single otherwise unconnected vertex. These two vertices (and edges) are
    # not used in the actual driveline, they are only used to indicate where
    # the drivelines starts. This data structure is handled in the Driveline
    # class.
    def convertDrivelines(self, lDrivelines, lSorted):
        # First collect all main drivelines, and all remaining drivelines
        # ---------------------------------------------------------------
        lMain     = []
        lRemain   = []
        for driveline in lDrivelines:
            if driveline.isMain():
                lMain.append(driveline)
            else:
                lRemain.append(driveline)

        # Now collect all main drivelines in one list starting
        # with the closest to 0, then the one closest to the
        # end of the first one, etc
        p          = (0,0,0)
        quad_index = 0
        while lMain:
            min_index = self.findClosestDrivelineToPoint(lMain, p)
            # Move the main driveline with minimal distance to the
            # sorted list.
            lSorted.append(lMain[min_index])
            del lMain[min_index]
            
            # Set the start quad index for all quads.
            lSorted[-1].setStartQuadIndex(quad_index)
            quad_index = quad_index + lSorted[-1].getNumberOfQuads()

            p = lSorted[-1].getEndPoint()

        # Now add the remaining drivelines one at a time. From all remaining
        # drivelines we pick the one closest to the drivelines contained in
        # lSorted.
        while lRemain:
            t = self.findClosestDrivelineToDrivelines(lRemain, lSorted)
            (remain_index, sorted_index, quad_to_index) = t
            print lRemain[remain_index].getName(),t
            lRemain[remain_index].setFromQuad(lSorted[sorted_index], quad_to_index)
            lSorted.append(lRemain[remain_index])
            del lRemain[remain_index]

            # Set the start quad index for all quads.
            lSorted[-1].setStartQuadIndex(quad_index)
            quad_index = quad_index + lSorted[-1].getNumberOfQuads()

    # --------------------------------------------------------------------------
    # Writes the track.quad file with the list of all quads, and the track.graph
    # file defining a graph node for each quad and a basic connection between all
    # graph nodes.
    def writeQuadAndGraph(self, sPath, lDrivelines):
        start_time = bsys.time()
        print "stk_track: Writing quad file --> ",
        if not lDrivelines:
            print "No main driveline defined, no driveline information exported!!!"
            return
    
        lSorted = []
        self.convertDrivelines(lDrivelines, lSorted)
        # Stores the first quad number (and since quads = graph nodes the node number) of
        # each section of the track. I.e. the main track starts with quad 0, then the
        # first alternative way, ...
        lStartQuad         = [0]
        dSuccessor         = {}
        last_main_lap_quad = 0
        count              = 0
        
        f = open(sPath+"/quads.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<quads>\n")
        
        for driveline in lSorted:
            driveline.write(f)

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
                %(0, lSorted[-1].getLastQuadIndex()))

        f.write("  <!-- Define the main loop -->\n");
        last_main = None
        for i in lSorted:
            if i.isMain():
                last_main = i
            else:
                break

        # The main driveline is written as a simple loop
        f.write("  <edge-loop from=\"%d\" to=\"%d\"/>\n" %
                (0, last_main.getLastQuadIndex()) )

        # Each non-main driveline writes potentially three entries in the
        # graph file: connection to the beginning of this driveline, the
        # driveline quads themselves, and a connection from the end of the
        # driveline to another driveline. But this can result in edged being
        # written more than once: consider two non-main drivelines A and B
        # which are connected to each other. Then A will write the edge from
        # A to B as its end connection, and B will write the same connection
        # as its begin connection. To avoid this, we keep track of all
        # written from/to edges, and only write one if it hasn't been written.
        dWrittenEdges={}
        # Now write the remaining drivelines
        for driveline in lSorted:
            # Mainline was already written, so ignore it
            if driveline.isMain(): continue

            f.write("  <!-- Shortcut %s -->\n"%driveline.getName())
            # Write the connection from an already written quad to this
            fr = driveline.getFromQuad()
            to = driveline.getFirstQuadIndex()
            if not dWrittenEdges.has_key( (fr,to) ):
                f.write("  <edge from=\"%d\" to=\"%d\">\n" %(fr, to))
                dWrittenEdges[ (fr, to) ] = 1
            if driveline.getFirstQuadIndex()< driveline.getLastQuadIndex():
                f.write("  <edge-line from=\"%d\" to=\"%d\"/>\n" \
                        %(driveline.getFirstQuadIndex(), driveline.getLastQuadIndex()))
            fr = driveline.getLastQuadIndex()
            to = driveline.computeSuccessor(lSorted)
            if not dWrittenEdges.has_key( (fr, to) ):
                f.write("  <edge from=\"%d\" to=\"%d\"/>\n" %(fr, to))
                dWrittenEdges[ (fr, to) ] = 1
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

    def __init__(self, sFilename):
        self.dExportedObjects = {}
        
        # Collect the different kind of meshes this exporter handles
        # ----------------------------------------------------------
        lObj           = Blender.Object.Get()
        lWater         = []
        lTrack         = []
        lDrivelines    = []
        found_main_driveline = 0
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
            elif stktype[:14]=="MAIN-DRIVELINE" or stktype[:13]=="MAINDRIVELINE" or \
                 stktype[:6]=="MAINDL":
                lDrivelines.append(Driveline(obj, 1))
                found_main_driveline = 1
            elif stktype[:9]=="DRIVELINE":
                lDrivelines.append(Driveline(obj, 0))
            elif stktype[:4]=="ANIM":
                lAnimations.append(obj)
            else:
                lTrack.append(obj)

        if not found_main_driveline:
            print "Main driveline missing, using first driveline as main!"
            
        # Now export the different parts: track file
        # ------------------------------------------
        sBase = os.path.basename(sFilename)
        sPath = os.path.dirname(sFilename)
        self.writeTrackFile(sPath, sBase, lCameraCurves)
    
        # Quads and mapping files
        # -----------------------
        self.writeQuadAndGraph(sPath, lDrivelines)
    
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
