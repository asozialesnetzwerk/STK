#!BPY

"""
Name: 'STK Track Exporter (.track)...'
Blender: 248a
Group: 'Export'
Tooltip: 'Export a SuperTuxKart track scene'
"""
__author__ = ["Joerg Henrichs (hiker)"]
__url__ = ["supertuxkart.sourceforge.net"]
__version__ = "$Revision$"
__bpydoc__ = """\
"""

# From Supertuxkart SVN revision $Revision$

# Copyright (C) 2009 Joerg Henrichs
# INSERT (C) here!

#If you get an error here, it might be
#because you don't have Python installed.
import Blender
import BPyMesh
import sys, os, os.path, struct, math, string, re
import b3d_export

from Blender import Mathutils, IpoCurve, Constraint
from Blender.Mathutils import *
from Blender import Draw, BGL
from Blender.BGL import *
from Blender import sys as bsys

if not hasattr(sys, "argv"):
    sys.argv = m["???"]

def getScriptVersion():
    try:
        m = re.search('(\d+)', __version__)
        return str(m.group(0))
    except:
        return "Unknown"

# ------------------------------------------------------------------------------
def Round(f):
    r = round(f,6) # precision set to 10e-06
    if r == int(r):
        return str(int(r))
    else:
        return str(r)

# ------------------------------------------------------------------------------
# Gets an id property of an objects, returning the default if the id property
# is not set. If set_value_if_undefined is set and the property is not
# defined, this function will also set the property to this default value.
def getIdProperty(obj, name, default="", set_value_if_undefined=1):
    try:
        return obj.properties[name]
    except:
        if default!=None and set_value_if_undefined:
            obj.properties[name]=default
    return default

# ------------------------------------------------------------------------------
# Returns a game logic property
def getProperty(obj, name, default=""):
    try:
        return obj.getProperty(name).getData()
    except:
        return default

# ------------------------------------------------------------------------------
# Returns a string 'x="1" y="2" z="3" h="4"', where 1, 2, ...are the actual
# location and rotation of the given object. The location has a swapped
# y and z axis (so that the same coordinate system as in-game is used).
def getXYZHString(obj):
    loc     = obj.loc
    hpr     = obj.rot
    rad2deg = 180.0/3.1415926535;
    s="x=\"%f\" y=\"%f\" z=\"%f\" h=\"%f\"" %\
       (loc[0], loc[2], loc[1], hpr[2]*rad2deg)
    return s

# ------------------------------------------------------------------------------
# Returns a string 'xyz="1 2 3" hpr="4 5 6"' where 1,2,... are the actual
# location and rotation of the given object. The location has a swapped
# y and z axis (so that the same coordinate system as in-game is used), and
# rotations are multiplied by 10 (since bullet stores the values in units
# of 10 degrees.)
def getXYZHPRString(obj):
    loc     = obj.loc
    hpr     = obj.rot
    si      = obj.size
    rad2deg = 180.0/3.1415926535;
    s="xyz=\"%f %f %f\" hpr=\"%f %f %f\" scale=\"%f %f %f\"" %\
       (loc[0], loc[2], loc[1], -hpr[0]*rad2deg, -hpr[2]*rad2deg,
        -hpr[1]*rad2deg, si[0], si[2], si[1])
    return s
# --------------------------------------------------------------------------
# Write several ways of writing true/false as Y/N
def convertTextToYN(sText):
    sTemp = sText.strip().upper()
    if sTemp=="0" or sTemp[0]=="N" or sTemp=="FALSE":
        return "N"
    else:
        return "Y"
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
        self.from_driveline=None
        self.to_driveline=None
        self.is_last_main = 0
        # Invisible drivelines are not shown in the minimap
        self.invisible = getProperty(driveline, "invisible", 0)
        self.ai_ignore = getProperty(driveline, "ai-ignore", "no")
        self.enabled   = not getProperty(driveline, "disable",   0)
        self.activate  = getProperty(driveline, "activate", None)
        self.strict_lap = convertTextToYN(getProperty(driveline,
                                                      "strict-lapline", "N") ) \
                           == "Y"
        
    # --------------------------------------------------------------------------
    # Returns the name of the driveline
    def getName(self):
        return self.name
    # --------------------------------------------------------------------------
    # Returns if this is a main driveline or not.
    def isMain(self):
        return self.is_main
    # --------------------------------------------------------------------------
    # Returns if this driveline is disabled.
    def isEnabled(self): 
        return self.enabled
    # --------------------------------------------------------------------------
    # Returns the 'activate' property of the driveline object.
    def getActivate(self):
        return self.activate
    # --------------------------------------------------------------------------
    # Returns if this driveline requests strict lap counting (i.e. exactly
    # crossing the line between the start vertices)
    def isStrictLapline(self):
        return self.strict_lap
    # --------------------------------------------------------------------------
    # Stores that the start quad of this driveline is connected to quad
    # quad_index of quad driveline. 
    def setFromQuad(self, driveline, quad_index):
        # Convert the relative to driveline quad index to the global index:
        self.from_quad      = driveline.getFirstQuadIndex()+quad_index
        self.from_driveline = driveline
    # --------------------------------------------------------------------------
    def setToDriveline(self, driveline):
        self.to_driveline = driveline
    # --------------------------------------------------------------------------
    # Returns the global index of the quad this start point is connected to.
    def getFromQuad(self):
        return self.from_quad
    # --------------------------------------------------------------------------
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
    # Returns the start edge, which is the lap counting line for the main
    # drivelines. See defineStartVertex() for setting self.start_line.
    def getStartEdge(self):
        return self.start_line
    # --------------------------------------------------------------------------
    # This driveline is the last main driveline. This means that it will get
    # one additional quad added to connect this to the very first quad. Since
    # the values are not actually needed (see write function), the arrays have
    # to be made one element larger to account for this additional quad (e.g.
    # in calls to getNumberOfQuads etc).
    def setIsLastMain(self, first_driveline):
        self.is_last_main = 1
        cp=[]
        for i in range(3):
            cp.append((self.lLeft [-1][i]+first_driveline.lLeft [0][i]+
                       self.lRight[-1][i]+first_driveline.lRight[0][i])*0.25)

        self.lCenter.append(cp)
        self.lLeft.append(None)
        self.lRight.append(None)

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

    # --------------------------------------------------------------------------
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
            print "Driveline '%s' is incorrect formed, it does not have" \
                  % self.name
            print "exactly two vertices with only one neighbour."
            return

        # Save the middle of the first quad, which is used later for neareast
        # quads computations.
        self.start_point =(  (self.lStart[0][0]+self.lStart[1][0])*0.5,
                             (self.lStart[0][1]+self.lStart[1][1])*0.5,
                             (self.lStart[0][2]+self.lStart[1][2])*0.5 )

    # --------------------------------------------------------------------------
    # Returns the startline of this driveline
    def getStartPoint(self):
        return self.start_point
    # --------------------------------------------------------------------------
    # Returns the distance of the start point from a given point
    def getStartDistanceTo(self, p):
        dx=self.start_point[0]-p[0]
        dy=self.start_point[1]-p[1]
        dz=self.start_point[2]-p[2]
        return dx*dx+dy*dy+dz*dz
    # --------------------------------------------------------------------------
    # Convert the dictionary of list of neighbours to two lists - one for the
    # left side, one for the right side.
    def convertToLists(self):
        self.lLeft   = [self.lStart[0], self.dNext[self.lStart[0]][0]]
        self.lRight  = [self.lStart[1], self.dNext[self.lStart[1]][0]]
        self.lCenter = []
        
        # The quads can be either clockwise or counter-clockwise oriented. STK
        # expectes counter-clockwise, so if the orientation is wrong, swap
        # left and right side.
        if (self.lRight[1][0]-self.lLeft[0][0])*(self.lRight[0][1]-self.lLeft[0][1]) \
         - (self.lRight[1][1]-self.lLeft[0][1])*(self.lRight[0][0]-self.lLeft[0][0]) > 0:
            r   = self.lRight
            self.lRight = self.lLeft
            self.lLeft  = r
        
        # Save start edge, which will become the main lap counting line
        # (on the main driveline). This must be done here after potentially 
        # switching since STK assumes that the first point of a check line (to 
        # which the first line of the main driveline is converted) is on the 
        # left side (this only applies for the lap counting line, see
        # Track::setStartCoordinates/getStartTransform).
        self.start_line = (self.lLeft[1], self.lRight[1])
        
        count=0
        # Just in case that we have an infinite loop due to a malformed graph:
        # stop after 10000 vertices
        max_count=10000
        warning_printed = 0
        while count<max_count:
            count = count + 1
            # Get all neighbours. One is the previous point, one
            # points to the opposite side - we need the other one.
            neighb = self.dNext[self.lLeft[-1]]
            next_left = []
            for i in neighb:
                if i==self.lLeft[-2]: continue   # pointing backwards
                if i==self.lRight[-1]: continue  # to opposite side
                next_left.append(i)
            if len(next_left)==0:
                # No new element found --> this must be the end
                # of the list!!
                break
            
            if len(next_left)!=1 and not warning_printed:
                print "Warning: More than one potential succesor found for left driveline point"
                print self.lLeft[-1][0],self.lLeft[-1][1],self.lLeft[-1][2],":"
                for i in range(len(next_left)):
                    print "Successor %d: %f %f %f" % \
                          (i,next_left[i][0],next_left[i][1],next_left[i][2])
                print "It might also possible that the corresponding right driveline point"
                print self.lRight[-1][0],self.lRight[-1][1],self.lRight[-1][2]
                print "has some inconsistencies."
                print "The drivelines will most certainly not be useable."
                print "Further warnings are likely and will be suppressed."
                warning_printed = 1
                Blender.Draw.PupMenu("Problems with driveline detected, check console for details!")
                
            self.lLeft.append(next_left[0])

            
            # Same for other side:
            neighb = self.dNext[self.lRight[-1]]
            next_right = []
            for i in neighb:
                if i==self.lRight[-2]: continue   # pointing backwards
                # Note lLeft has already a new element appended,
                # so we have to check for the 2nd last element!
                if i==self.lLeft[-2]: continue  # to opposite side
                next_right.append(i)
            if len(next_right)==0:
                print "No more vertices on right side of quad line, but there are"
                print "still points on the left side. Check the points:"
                print "left: ", self.lLeft[-1][0],self.lLeft[-1][1],self.lLeft[-1][2]
                print "right: ", self.lRight[-1][0],self.lRight[-1][1],self.Right[-1][2]
                print "Last left point is ignored."
                break
            if len(next_right)!=1 and not warning_printed:
                print "Warning: More than one potential succesor found for right driveline point"
                print self.lRight[-1][0],self.lRight[-1][1],self.lRight[-1][2],":"
                for i in range(len(next_right)):
                    print "Successor %d: %f %f %f" % \
                          (i,next_right[i][0],next_right[i][1],next_right[i][2])
                print "It might also possible that the corresponding left driveline point"
                print self.lLeft[-1][0],self.lLeft[-1][1],self.lLeft[-1][2]
                print "has some inconsistencies."
                print "The drivelines will most certainly not be useable."
                print "Further warnings are likely and will be suppressed."
                warning_printed = 1
                Blender.Draw.PupMenu("Problems with driveline detected, check console for details!")
                
            self.lRight.append(next_right[0])

            cp=[]
            for i in range(3):
                cp.append((self.lLeft[-2][i]+self.lLeft[-1][i]+
                           self.lRight[-2][i]+self.lRight[-1][i])*0.25)
            self.lCenter.append(cp)

        if count>=max_count:
            print "Warning, Only the first %d vertices of driveline '%s' are exported" %\
                  (max_count, self.name)
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

    # --------------------------------------------------------------------------
    # Determine the driveline from lSorted which is closest to this driveline's
    # endpoint (closest meaning: having a quad that is closest).
    def computeSuccessor(self, lSorted):
        (dist, driveline_index, quad_index)=self.getDistanceTo(self.end_point,
                                                               lSorted)
        return quad_index+lSorted[driveline_index].getFirstQuadIndex()

    # --------------------------------------------------------------------------
    # Writes the quads into a file.
    def writeQuads(self, f):
        l   = self.lLeft[0]
        r   = self.lRight[0]
        l1  = self.lLeft[1]
        r1  = self.lRight[1]

        if self.invisible:
            sInv = " invisible=\"yes\" "
        else:
            sInv = " "
        if self.ai_ignore and self.ai_ignore!="no":
            sAIIgnore = "ai-ignore=\"yes\" "
        else:
            sAIIgnore = " "
        max_index = len(self.lLeft)-1
        # If this is the last main driveline, the last quad is a dummy element
        # added by setLastMain(). So the number of elements is decreased by
        # one.
        if self.is_last_main:
            max_index = max_index - 1
            
        f.write("  <!-- Driveline: %s -->\n"%self.name)
        # Note that only the first quad must be marked with ai-ignore
        # (this results that the AI will not go to the first quad, but
        # if it should end up somewhere on the shortcut, it will
        # continue to drive on the shortcut.
        f.write("  <quad%s%sp0=\"%f %f %f\" p1=\"%f %f %f\" p2=\"%f %f %f\" p3=\"%f %f %f\"/>\n" \
            %(sInv, sAIIgnore, l[0],l[2],l[1], r[0],r[2],r[1], r1[0],r1[2],r1[1], l1[0],l1[2],l1[1]) )
        for i in range(1, max_index):
            l1  = self.lLeft[i+1]
            r1  = self.lRight[i+1]
            f.write("  <quad%sp0=\"%d:3\" p1=\"%d:2\" p2=\"%f %f %f\" p3=\"%f %f %f\"/>\n" \
                    %(sInv,self.global_quad_index_start+i-1, self.global_quad_index_start+i-1, \
                  r1[0],r1[2],r1[1], l1[0],l1[2],l1[1]) )
        if self.is_last_main:
            f.write("  <quad%sp0=\"%d:3\" p1=\"%d:2\" p2=\"0:1\" p3=\"0:0\"/>\n"\
                    % (sInv, max_index-1, max_index-1))

# ==============================================================================
# The actual exporter. It is using a class mainly to store some information
# between calls to different functions, e.g. a cache of exported objects.
class TrackExport:
    
    # Exports the models as b3d object in local coordinate, i.e. with the object
    # center at (0,0,0).
    def exportLocalB3D(self, obj, sPath, name):
        # If the name contains a ".b3d" the model is assumed to be part of
        # the standard objects included in STK, so there is no need to
        # export the model.
        if re.search("\.b3d$", name): return name
        
        name=name+".b3d"
        # If the object was already exported, we don't have to do it again.
        if self.dExportedObjects.has_key(name): return name
        
        old_space = b3d_export.b3d_parameters.get("local-space")
        
        b3d_export.b3d_parameters["local-space"] = 1  # Export in local space
        b3d_export.write_b3d_file(sPath+"/"+name, [obj])
        b3d_export.b3d_parameters["local-space"] = old_space
        
        self.dExportedObjects[name]=1
        
        return name

    # ----------------------------------------------------------------------
    def writeTrackFile(self, sPath, sBase):
        print "Writing track file --> \t",
        start_time  = bsys.time()
        scene       = Blender.Scene.GetCurrent()
        name        = getIdProperty(scene, "name",       "Name of Track")
        groups      = getIdProperty(scene, "groups",     "standard"     )
        is_arena    = getIdProperty(scene, "arena",      "n"            )
        if not is_arena:
            is_arena="n"
        is_arena = not (is_arena[0]=="n" or is_arena[0]=="N" or \
                        is_arena[0]=="f" or is_arena[0]=="F"      )
        designer    = getIdProperty(scene, "designer",   ""             )
        # Support for multi-line descriptions:
        designer    = designer.replace("\\n", "\n")
        if not designer:
            designer    = getIdProperty(scene, "description", "")
            if designer:
                print "Warning: using 'description' instead of designer."
                print "Please use designer only"
            else:
                designer="Designer"
                
        music       = getIdProperty(scene, "music", "")
        screenshot  = getIdProperty(scene, "screenshot", "")
        # Add default settings for sky-dome so that the user is aware of
        # can be set.
        getIdProperty(scene, "sky-type", "dome")
        getIdProperty(scene, "sky-texture", "" )
        getIdProperty(scene, "sky-speed-x", "0")
        getIdProperty(scene, "sky-speed-y", "0")
        # Not sure if these should be added - if the user wants a sky
        # box they are quiet annoying.
        #getIdProperty(scene, "sky-color","")
        #getIdProperty(scene, "sky-horizontal","")
        #getIdProperty(scene, "sky-vertical", "")
        #getIdProperty(scene, "sky-texture-percent","")
        #getIdProperty(scene, "sky-sphere-percent", "")
        
        f = open(sPath+"/track.xml", 'wb')
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<!-- Generated with script from SVN rev %s -->\n"%getScriptVersion())
        f.write("<track  name        = \"%s\"\n"%name)
        f.write("        version     = \"5\"\n")
        f.write("        groups      = \"%s\"\n"%groups)
        f.write("        designer    = \"%s\"\n"%designer)
        if music:
            f.write("        music       = \"%s\"\n"%music)
        else:
            print "No music file defined, ignored."
        if is_arena:
            f.write("        arena       = \"Y\"\n")
        if screenshot:
            f.write("        screenshot  = \"%s\"\n"%screenshot)
        else:
            print "No screenshot defined, ignored"
        f.write(">\n")
        f.write("</track>\n")
        f.close()
        print bsys.time()-start_time, "seconds"
        
    # --------------------------------------------------------------------------
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
                    f.write("    <%s curvetype=\"nurb\" name=\"%s\">\n" \
                            % (type, curves.name))
                    for i in nu:
                        v=Vector(i[0],i[1],i[2]) * matrix
                        f.write("      <p=\"%f %f %f\"/>\n"%(v[0], v[1], v[2]))
                    f.write("    </%s>\n"%type)
                elif nu.type==1:
                    f.write("    <%s curvetype=\"bezier\" name=\"%s\">\n" \
                            % (type, curves.name))
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
    # Additionally, this function sorts the end cameras according to distance
    # to the main driveline - so the first end camera will be the camera
    # closest to the start line etc.
    def convertDrivelinesAndSortEndCameras(self, lDrivelines, lSorted,
                                           lEndCameras):
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

        # Create a new list for all cameras, which also stores the
        # quad index to which the camera is closest to, the distance
        # to the quad, and the camera object. The order is important
        # since this list is later sorted by quad index, so that the
        # first camera is the first in the list.
        lCamerasDistance = []
        for i in range(len(lEndCameras)):
            cam = lEndCameras[i]
            try:
                (distance, driveline_index, quad_index_camera) = \
                           lSorted[0].getDistanceTo(cam.loc, lSorted)
                # Each list contains the index of the closest quad, the
                # distance, and then the camera
                lEndCameras[i] = (driveline_index, quad_index_camera, cam)
            except:
                print "Problem with the end camera - likely the cameras will not"
                print "be exported correctly. Check if the main driveline is"
                print "properly defined (check warning messages), and the"
                print "settings of the camera '%s'."%cam.name
                
        lEndCameras.sort()
        # After sorting remove the unnecessary distance and quad index
        for i in range(len(lEndCameras)):
            # Avoid crash in case that some problem with the camera happened,
            # and lEndCameras is just the blender camera, not the tuple
            if type(lEndCameras[i])==type(()):
                lEndCameras[i] = lEndCameras[i][2]

        # There were already two warning messages printed at this stage, so just
        # ignore this to avoid further crashes
        if len(lSorted)<1:
            return
        # The last main driveline needs to be closed to the first quad.
        # So set a flag in that driveline that it is the last one.
        lSorted[-1].setIsLastMain(lSorted[0])
        quad_index = quad_index + 1
        # Now add the remaining drivelines one at a time. From all remaining
        # drivelines we pick the one closest to the drivelines contained in
        # lSorted.
        while lRemain:
            t = self.findClosestDrivelineToDrivelines(lRemain, lSorted)
            (remain_index, sorted_index, quad_to_index) = t
            lRemain[remain_index].setFromQuad(lSorted[sorted_index],
                                              quad_to_index)
            lSorted.append(lRemain[remain_index])
            del lRemain[remain_index]

            # Set the start quad index for all quads.
            lSorted[-1].setStartQuadIndex(quad_index)
            quad_index = quad_index + lSorted[-1].getNumberOfQuads()

    # --------------------------------------------------------------------------
    # Writes the track.quad file with the list of all quads, and the track.graph
    # file defining a graph node for each quad and a basic connection between
    # all graph nodes.
    def writeQuadAndGraph(self, sPath, lDrivelines, lEndCameras):
        start_time = bsys.time()
        print "Writing quad file --> \t",
        if not lDrivelines:
            print "No main driveline defined, no driveline information exported!!!"
            return
    
        lSorted = []
        self.convertDrivelinesAndSortEndCameras(lDrivelines, lSorted,
                                                lEndCameras)

        # That means that there were some problems with the drivelines, and
        # it doesn't make any sense to continue anyway
        if not lSorted:
            return
        # Stores the first quad number (and since quads = graph nodes the node
        # number) of each section of the track. I.e. the main track starts with
        # quad 0, then the first alternative way, ...
        lStartQuad         = [0]
        dSuccessor         = {}
        last_main_lap_quad = 0
        count              = 0
        
        f = open(sPath+"/quads.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<!-- Generated with script from SVN rev %s -->\n"%getScriptVersion())
        f.write("<quads>\n")

        for driveline in lSorted:
            driveline.writeQuads(f)

        f.write("</quads>\n")
        f.close()
        print bsys.time()-start_time,"seconds. "

        start_time = bsys.time()
        print "Writing graph file --> \t",
        f=open(sPath+"/graph.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<!-- Generated with script from SVN rev %s -->\n"%getScriptVersion())
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
                f.write("  <edge from=\"%d\" to=\"%d\"/>\n" %(fr, to))
                #if to.isEnabled() and fr.isEnabled():
                #    f.write("  <edge from=\"%d\" to=\"%d\"/>\n" %(fr, to))
                #elif to.isEnabled():
                #    f.write("  <!-- %s disabled <edge from=\"%d\" to=\"%d\"/> -->\n" \
                #            %(fr.getName(), fr, to))
                #else:
                #    f.write("  <!-- %s disabled <edge from=\"%d\" to=\"%d\"/> -->\n"
                #            %(to.getName(), fr, to))
                dWrittenEdges[ (fr, to) ] = 1
            if driveline.getFirstQuadIndex()< driveline.getLastQuadIndex():
                f.write("  <edge-line from=\"%d\" to=\"%d\"/>\n" \
                        %(driveline.getFirstQuadIndex(),
                          driveline.getLastQuadIndex()))
            fr = driveline.getLastQuadIndex()
            to = driveline.computeSuccessor(lSorted)
            if not dWrittenEdges.has_key( (fr, to) ):
                f.write("  <edge from=\"%d\" to=\"%d\"/>\n" %(fr, to))
                dWrittenEdges[ (fr, to) ] = 1
        f.write("</graph>\n")
        f.close()
        print bsys.time()-start_time,"seconds. "
          
    # --------------------------------------------------------------------------
    def writeIPO(self, f, ipo ):
        dInterp = {IpoCurve.InterpTypes.BEZIER:        "bezier",
                   IpoCurve.InterpTypes.LINEAR:        "linear",
                   IpoCurve.InterpTypes.CONST:         "const"          }
        dExtend = {IpoCurve.ExtendTypes.CONST:         "const",
                   IpoCurve.ExtendTypes.EXTRAP:        "extrap",
                   IpoCurve.ExtendTypes.CYCLIC_EXTRAP: "cyclic_extrap",
                   IpoCurve.ExtendTypes.CYCLIC:        "cyclic"         }
        for curve in ipo:
            # Swap Y and Z axis
            if   curve.name=="LocZ":   name="LocY"
            elif curve.name=="LocY":   name="LocZ"
            elif curve.name=="RotY":   name="RotZ"
            elif curve.name=="RotZ":   name="RotY"
            elif curve.name=="ScaleY": name="ScaleZ"
            elif curve.name=="ScaleZ": name="ScaleY"
            else:                      name=curve.name
            # Rotations are stored in units of 10 degrees, and we
            # have to reverse the sign
            if name[:3]=="Rot":
                factor=-10
            else:
                factor=1
            f.write("    <curve channel=\"%s\" interpolation=\"%s\" extend=\"%s\">\n"% \
                    (name, dInterp[curve.interpolation], dExtend[curve.extend]))
            
            for bez in curve.bezierPoints:
                if curve.interpolation==IpoCurve.InterpTypes.BEZIER:
                    f.write("      <p c=\"%f %f\" h1=\"%f %f\" h2=\"%f %f\"/>\n"%\
                            (bez.vec[1][0],factor*bez.vec[1][1], bez.vec[0][0],
                             factor*bez.vec[0][1], bez.vec[2][0],
                             factor*bez.vec[2][1]))
                else:
                    f.write("      <p c=\"%f %f\"/>\n"%(bez.vec[1][0],
                                                        factor*bez.vec[1][1]))
            f.write("    </curve>\n")
        
    # --------------------------------------------------------------------------
    # Writes the animation for objects using IPOs:
    def writeAnimationWithIPO(self, f, name, obj, ipo):
        # An animated object can set the 'name' property, then this name will
        # be used to name the exported object (instead of the python name
        # which might be a default name with a number). Additionally, names
        # are cached so it can be avoided to export two or more identical
        # objects.
        parent = obj.getParent()
        # For now: armature animations are assumed to be looped
        if parent and parent.type=="Armature":
            looped =" looped=\"y\" "
        else:
            looped = ""
        shape = getProperty(obj, "shape", "")
        if shape:
            shape="shape=\"%s\""%shape
        if not ipo: ipo=[]
        # Note: Y and Z are swapped!
        f.write("  <object type=\"animation\" model=\"%s\" %s %s%s>\n"% \
                (name, getXYZHPRString(obj), shape, looped))
        self.writeIPO(f, ipo)
        f.write("  </object>\n")
            
        
    # --------------------------------------------------------------------------
    # Writes an animation that uses a path constrained.
    def writeAnimationsWithPaths(self, f, sPath, obj):
        #print "b3d export", obj.name
        print "'%s' is using path '%s'"%(obj.name, \
                               obj.constraints[0][Constraint.Settings.TARGET].name)
    
    # --------------------------------------------------------------------------
    def writeAnimatedTextures(self, f, lAnimTextures):
        for (name, dx, dy) in lAnimTextures:
            sdx=""
            if dx: sdx = " dx=\"%s\" "%dx
            sdy=""
            if dy: sdy = " dy=\"%s\" "%dy
            f.write("    <animated-texture name=\"%s\"%s%s/>\n"%(name, sdx, sdy) )
        
    # --------------------------------------------------------------------------
    # Write the objects that are part of the track (but not animated or
    # physical).
    def writeStaticObjects(self, f, sPath, lStaticObjects, lAnimTextures):
        for obj in lStaticObjects:
            # An object can set the 'name' property, then this name will
            # be used to name the exported object (instead of the python name
            # which might be a default name with a number). Additionally, names
            # are cached so it can be avoided to export two or more identical
            # objects.
            lAnim    = self.checkForAnimatedTextures([obj])
            name     = getProperty(obj, "name", obj.name)
            b3d_name = self.exportLocalB3D(obj, sPath, name)
            kind     = getProperty(obj, "kind", "")
            if lAnim:
                f.write("    <static-object model=\"%s\" %s>\n"% \
                        (b3d_name, getXYZHPRString(obj)) )
                self.writeAnimatedTextures(f, lAnim)
                f.write("    </static-object>\n")
            else:
                f.write("    <static-object model=\"%s\" %s/>\n"% \
                        (b3d_name, getXYZHPRString(obj)) )
        self.writeAnimatedTextures(f, lAnimTextures)

    # --------------------------------------------------------------------------
    # billboard section (check if the billboard is correct and write in the file)
    def writeBillboard(self,f, obj):
        data = obj.getData(mesh=True)
        # check the face
        if len(data.faces) > 1:
            print "\nerror: the billboard <" + getProperty(obj, "name", obj.name) \
                  + "> has more than ONE texture"
            return
        
        # check the points
        if len(data.verts) > 4:
            print "\nerror: the billboard <" + getProperty(obj, "name", obj.name)\
                  + "> has more than 4 points"
            return
        
        try:
            # write in the XML
            # calcul the size and the position
            x_min = data.verts[0].co[0]
            x_max = x_min
            y_min = data.verts[0].co[2]
            y_max = y_min
            for i in range(1, 4):
                x_min = min(x_min, data.verts[i].co[0])
                x_max = max(x_max, data.verts[i].co[0])
                y_min = min(y_min, data.verts[i].co[2])
                y_max = max(y_max, data.verts[i].co[2])
                

            f.write('  <object type="billboard" texture="%s" xyz="%f %f %f" \n'%
                    (Blender.sys.basename(data.faces[0].image.getFilename()),
                     obj.loc[0], obj.loc[2], obj.loc[1]) )
            f.write('             width="%f" height="%f">\n' %(x_max-x_min, y_max-y_min) )
            if obj.getIpo():
                self.writeIPO(f, obj.getIpo())
            f.write('  </billboard>\n')

        except ValueError:
            print "\nerror unknow: check the billboard <" + getProperty(obj, "name", obj.name) + "> " , sys.exc_info()[0]

    # --------------------------------------------------------------------------
    # Particle emitter 
    def writeParticleEmitters(self,f, lParticleEmitters):
        for obj in lParticleEmitters:
            try:
                # origin
                originXYZ = getXYZHString(obj)
                f.write('  <particle-emitter kind="%s" %s/>\n' %\
                        (getProperty(obj, "kind", 0) ,originXYZ))
            except:
                print "\nerror unknow: check the particle-emitter <" + getProperty(obj, "name", obj.name) + "> " , sys.exc_info()[0]
    # --------------------------------------------------------------------------
    # Writes out all checklines.
    # \param lChecks All check meshes
    # \param mainDriveline The main driveline, from which the lap
    #        counting check line is determined.
    def writeChecks(self, f, lChecks, mainDriveline):
        f.write("  <checks>\n")

        # A dictionary containing a list of indices of check structures
        # that belong to this group.
        dGroup2Indices = {"lap":[0]}
        # Collect the indices of all check structures for all groups
        ind = 1
        for obj in lChecks:
            name = getProperty(obj, "type", obj.name.lower())
            if name!="lap":
                name = getProperty(obj, "name", obj.name.lower())
            if dGroup2Indices.has_key(name):
                dGroup2Indices[name].append(ind)
            else:
                dGroup2Indices[name] = [ ind ]
            ind = ind + 1

        if mainDriveline:
            lap = mainDriveline.getStartEdge()
            min_h = lap[0][2]
            if lap[1][2]<min_h: min_h = lap[1][2]

            # The main driveline is always the first entry, so remove
            # only the first entry to get the list of all other lap lines
            l = dGroup2Indices["lap"]
            sSameGroup = reduce(lambda x,y: str(x)+" "+str(y), l, "")
            activate = mainDriveline.getActivate()
            if activate:
                group = activate.lower()
            else:
                group = ""
            if not group or not dGroup2Indices.has_key(group):
                print "Activate group '%s' not found!"%group
                print "Ignored - but lap counting might not work correctly."
                print "Make sure there is an object of type 'check' with"
                print "the name '%s' defined."%group
                activate = ""
            else:
                activate = reduce(lambda x,y: str(x)+" "+str(y), dGroup2Indices[group])
        else:
            # No main drive defined, print a warning and add some dummy
            # driveline (makes the rest of this code easier)
            print "Warning - no main driveline defined, adding dummy driveline"
            lap        = [ [-1, 0], [1, 0] ]
            min_h      = 0
            sSameGroup = ""
            activate = ""

        if sSameGroup:
            sSameGroup="same-group=\"%s\""%sSameGroup.strip()

        if activate:
            activate = "other-ids=\"%s\""%activate
        strict_lapline = mainDriveline.isStrictLapline()
        if not strict_lapline:
            f.write("    <check-lap kind=\"lap\" %s %s />\n"%(sSameGroup, activate))
        else:
            f.write("    <check-line kind=\"lap\" p1=\"%f %f\" p2=\"%f %f\"\n"% \
                    (lap[0][0], lap[0][1],
                     lap[1][0], lap[1][1] )  )
            f.write("                min-height=\"%f\" %s %s/>\n"% (min_h, sSameGroup, activate) )

        ind = 1
        for obj in lChecks:
            mesh=obj.getData()
            # Convert to world space
            mesh.transform(obj.getMatrix())
            # One of lap, activate, toggle, ambient
            activate = getProperty(obj, "activate", "")
            kind=" "
            if activate:
                group = activate.lower()
                if not dGroup2Indices.has_key(group):
                    print "Activate group '%s' not found!"%group
                    print "Ignored - but lap counting might not work correctly."
                    print "Make sure there is an object of type 'check' with"
                    print "the name '%s' defined."%group
                    continue
                s = reduce(lambda x,y: str(x)+" "+str(y), dGroup2Indices[group])
                kind = " kind=\"activate\" other-ids=\"%s\" "% s

            toggle = getProperty(obj, "toggle", "")
            if toggle:
                group = toggle.lower()
                if not dGroup2Indices.has_key(group):
                    print "Toggle group '%s' not found!"%group
                    print "Ignored - but lap counting might not work correctly."
                    print "Make sure there is an object of type 'check' with"
                    print "the name '%s' defined."%group
                    continue
                s = reduce(lambda x,y: str(x)+" "+str(y), dGroup2Indices[group])
                kind = " kind=\"toggle\" other-ids=\"%s\" "% s

            lap = getProperty(obj, "type", obj.name).upper()
            if lap[:3]=="LAP":
                kind = " kind=\"lap\" "  # xml needs a value for an attribute
                activate = getProperty(obj, "activate", "")
                if activate:
                    group = activate.lower()
                    if not dGroup2Indices.has_key(group):
                        print "Activate group '%s' not found for lap line!"%group
                        print "Ignored - but lap counting might not work correctly."
                        print "Make sure there is an object of type 'check' with"
                        print "the name '%s' defined."%group
                        continue
                    s = reduce(lambda x,y: str(x)+" "+str(y), dGroup2Indices[group])
                    kind = "%sother-ids=\"%s\" "% (kind, s)
            
            ambient = getProperty(obj, "ambient", "").upper()
            if ambient:
                kind=" kind=\"ambient-light\" "

            # Get the group name this object belongs to. If the objects
            # is of type lap then 'lap' is the group name, otherwise
            # it's taken from the name property (or the object name).
            name = getProperty(obj, "type", obj.name.lower())
            if name!="lap":
                name = getProperty(obj, "name", obj.name.lower())
                
            # Get the list of indices of this group, excluding
            # the index of the current object. So create a copy
            # of the list and remove the current index
            l = dGroup2Indices[name][:]
            sSameGroup = reduce(lambda x,y: str(x)+" "+str(y), l, "")
            ind = ind + 1

            if len(mesh.verts)==2:   # Check line
                min_h = mesh.verts[0][2]
                if mesh.verts[1][2]<min_h: min_h = mesh.verts[1][2]
                f.write("    <check-line%sp1=\"%f %f\" p2=\"%f %f\"\n" %
                        (kind, mesh.verts[0][0], mesh.verts[0][1],
                         mesh.verts[1][0], mesh.verts[1][1]   )  )

                f.write("                min-height=\"%f\" same-group=\"%s\"/>\n" \
                        % (min_h, sSameGroup.strip())  )
            else:
                radius = 0
                for v in mesh.verts:
                    r = (obj.loc[0]-v[0])*(obj.loc[0]-v[0]) + \
                        (obj.loc[1]-v[1])*(obj.loc[1]-v[1]) + \
                        (obj.loc[2]-v[2])*(obj.loc[2]-v[2])
                    if r>radius:
                        radius=r
                radius = math.sqrt(radius)
                inner_radius = getProperty(obj, "inner-radius", radius)
                color = getProperty(obj, "color", "255 120 120 120")
                f.write("    <check-sphere%sxyz=\"%f %f %f\" radius=\"%f\"\n" % \
                        (kind, obj.loc[0], obj.loc[2], obj.loc[1], radius) )
                f.write("                  same-group=\"%s\"\n"%sSameGroup.strip())
                f.write("                  inner-radius=\"%f\" color=\"%s\"/>\n"% \
                        (inner_radius, color) )
                        
        f.write("  </checks>\n")
            
    # --------------------------------------------------------------------------
    # Checks if there are any animated textures in any of the objects in the
    # list l.
    def checkForAnimatedTextures(self, lObjects):
        lAnimTextures = []
        for obj in lObjects:
            anim_texture = getProperty(obj, "anim-texture", None)
            if not anim_texture: continue
            dx = getProperty(obj, "anim-dx", 0)
            dy = getProperty(obj, "anim-dy", 0)
            lAnimTextures.append( (anim_texture, dx, dy) )
        return lAnimTextures
            
    # --------------------------------------------------------------------------
    # Writes a non-static track object. The objects can be animated or
    # non-animated meshes, and physical or non-physical.
    # Type is either 'movable' or 'nophysics'.
    def writeObject(self, f, sPath, obj):
        name     = getProperty(obj, "name", obj.name)
        b3d_name = self.exportLocalB3D(obj, sPath, name)

        # First kind of object: ipo. There is one or
        # more IPOs define controlling this object.
        # Second kind of object: no ipo, and no physics.
        # So it's a visual-only object. This is exported
        # as an animation object without an IPO attached.
        # -----------------------------------------------
        interact = getProperty(obj, "interaction", "none")
        # An object that can be moved by the player. This object
        # can not have an IPO, so no need to test this here.
        if interact=="move":
            ipo      = obj.getIpo()
            if ipo:
                print "Warning: Movable object %s has an ipo - ipo is ignored." \
                      %obj.name
            shape = getProperty(obj, "shape", "")
            if not shape:
                print "Warning: Movable object %s has no shape - box assumed!" \
                      % obj.name
                shape="box"
            mass  = getProperty(obj, "mass", 10)
            f.write("  <object type=\"movable\" %s\n"%(getXYZHPRString(obj)))
            f.write("          model=\"%s\" shape=\"%s\" mass=\"%s\"/>\n"\
                    % (b3d_name, shape, mass))
            
        # Now the object either has an IPO, or is a 'ghost' object.
        # Either can have an IPO. Even if the objects don't move
        # they are saved as animations (with 0 IPOs).
        elif interact=="ghost" or interact=="none":
            ipo      = obj.getIpo()
            # In objects with skeletal animations the actual armature (which
            # is a parent) contains the IPO. So check for this:
            if not ipo:
                parent = obj.getParent()
                if parent:
                    ipo = parent.getIpo()
            self.writeAnimationWithIPO(f, b3d_name, obj, ipo)
        elif interact=="static":
            ipo      = obj.getIpo()
            # In objects with skeletal animations the actual armature (which
            # is a parent) contains the IPO. So check for this:
            if not ipo:
                parent = obj.getParent()
                if parent:
                    ipo = parent.getIpo()
            self.writeAnimationWithIPO(f, b3d_name, obj, ipo)
        else:
            print "Unknown interaction '%s' - ignored!"%interact

    # --------------------------------------------------------------------------
    # Writes all start positions
    def writeStartPositions(self, f, lStart):
        scene = Blender.Scene.GetCurrent()
        karts_per_row      = getIdProperty(scene, "start-karts-per-row",      "2"  )
        distance_forwards  = getIdProperty(scene, "start-forwards-distance",  "1.5")
        distance_sidewards = getIdProperty(scene, "start-sidewards-distance", "3"  )
        distance_upwards   = getIdProperty(scene, "start-upwards-distance",   "0.1")
        f.write("  <default-start karts-per-row     =\"%s\"\n"%karts_per_row     )
        f.write("                 forwards-distance =\"%s\"\n"%distance_forwards )
        f.write("                 sidewards-distance=\"%s\"\n"%distance_sidewards)
        f.write("                 upwards-distance  =\"%s\"/>\n"%distance_upwards)
        
        dId2Obj     = {}
        count = 1
        for obj in lStart:
            stktype = getProperty(obj, "type", obj.name).upper()
            try:
                id = int(getProperty(obj, "position", ""))
            except:
                id=None
            if not id:
                try:
                    id = int(stktype[5:])
                except ValueError:
                    print "No valid id in '%s' - using %d\n"%(stktype, count)
                    id    = count
                    count = count + 1
            dId2Obj[id] = obj
        l = dId2Obj.keys()
        l.sort()
        for i in l:
            f.write("  <start %s/>\n"%getXYZHString(dId2Obj[i]))
                
    # --------------------------------------------------------------------------
    # Writes all special water nodes.
    def writeWaterNodes(self, f, sPath, lWater):
        start_time = bsys.time()
        print "Exporting water -->",
        for obj in lWater:
            name     = getProperty(obj, "name",   obj.name )
            height   = getProperty(obj, "height", None     )
            speed    = getProperty(obj, "speed",  None     )
            length   = getProperty(obj, "length", None     )
            lAnim    = self.checkForAnimatedTextures([obj])
            b3d_name = self.exportLocalB3D(obj, sPath, name)
            s="  <water model=\"%s\" %s" % \
                (b3d_name, getXYZHPRString(obj))
            if height: s="%s height=\"%s\""%(s, height)
            if speed:  s="%s speed=\"%s\"" %(s, speed )
            if length: s="%s length=\"%s\""%(s, length)
            if lAnim:
                f.write("%s>\n" % s)
                self.writeAnimatedTextures(f, lAnim)
                f.write("  </water>\n")
            else:
                f.write("%s/>\n" % s);

        print bsys.time()-start_time,"seconds."
        
    # --------------------------------------------------------------------------
    # Writes the scene files, which includes all models, animations, and items
    def writeSceneFile(self, sPath, sTrackName, lWater, lTrack, lItems,
                       lObjects, lBillboards, lParticleEmitters,  lChecks, lSun, mainDriveline, lStart,
                       lEndCameras, lCameraCurves):

        start_time = bsys.time()
        print "Writing scene file --> \t",

        f = open(sPath+"/scene.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<!-- Generated with script from SVN rev %s -->\n"%getScriptVersion())
        f.write("<scene>\n")

        # Extract all static objects (which will be merged into one
        # bullet objects in stk):
        lStaticObjects = []
        lOtherObjects  = []
        for obj in lObjects:
            interact = getProperty(obj, "interaction", "static")
            if interact=="static":
                ipo      = obj.getIpo()
                # If an static object has an IPO, it will be moved, and
                # can't be merged with the physics model of the track
                if ipo:
                    lOtherObjects.append(obj)
                else:
                    lStaticObjects.append(obj)
            else:
                lOtherObjects.append(obj)
                
        lAnimTextures  = self.checkForAnimatedTextures(lTrack)
        if lStaticObjects or lAnimTextures:
            f.write("  <track model=\"%s\" x=\"0\" y=\"0\" z=\"0\">\n"%sTrackName)
            self.writeStaticObjects(f, sPath, lStaticObjects, lAnimTextures)
            f.write("  </track>\n")
        else:
            f.write("  <track model=\"%s\" x=\"0\" y=\"0\" z=\"0\"/>\n"%sTrackName)
        self.writeWaterNodes(f, sPath, lWater)
        
        if lParticleEmitters:
            self.writeParticleEmitters(f, lParticleEmitters)
        for obj in lOtherObjects:
            self.writeObject(f, sPath, obj)
        for obj in lBillboards:
            self.writeBillboard(f, obj)
        
        # Assemble all sky/fog related parameters
        # ---------------------------------------
        if len(lSun)>1:
            print "Warning: more than one Sun defined, only the first will be used."            
        sSky=""
        scene = Blender.Scene.GetCurrent()
        s=getIdProperty(scene, "fog", 0)
        if s=="yes":
            sSky="%s fog=\"true\""%sSky
            s=getIdProperty(scene, "fog-color", 0)
            if s: sSky="%s fog-color=\"%s\""%(sSky, s)
            s=getIdProperty(scene, "fog-density", 0)
            if s: sSky="%s fog-density=\"%s\""%(sSky, s)
            s=getIdProperty(scene, "fog-start", 0)
            if s: sSky="%s fog-start=\"%s\""%(sSky, s)
            s=getIdProperty(scene, "fog-end", 0)
            if s: sSky="%s fog-end=\"%s\""%(sSky, s)

        # If there is a sun:
        if len(lSun)>0:
            sun = lSun[0]
            xyz=sun.loc
            sSky="%s xyz=\"%s %s %s\""%(sSky, xyz[0],xyz[2],xyz[1])
            s=getProperty(sun, "color", 0)
            if s: sSky="%s sun-color=\"%s\""%(sSky, s)
            s=getProperty(sun, "specular", 0)
            if s: sSky="%s sun-specular=\"%s\""%(sSky, s)
            s=getProperty(sun, "diffuse", 0)
            if s: sSky="%s sun-diffuse=\"%s\""%(sSky, s)
            s=getProperty(sun, "ambient", 0)
            if s: sSky="%s ambient=\"%s\""%(sSky, s)

        if sSky:
            f.write("  <sun %s/>\n"%sSky)
            
        sky_color=getIdProperty(scene, "sky-color", None)
        if sky_color:
            f.write("  <sky-color rgb=\"%s\"/>\n"%sky_color)

        weather = getIdProperty(scene, "weather", None)
        # Apparently the browser uses the string "none" to indicate
        # that no weather is set. So we have to check for this string
        # as well (ticket #159).
        if weather and weather!="none":
            if weather=="rain":
                f.write("  <weather type=\"rain\" />\n")
            else:
                if weather[:4]!=".xml":
                    weather=weather+".xml"
                f.write("  <weather particles=\"%s\" />\n"%weather)

        rad2deg = 180.0/3.1415926
        for obj in lItems:
            name     = getProperty(obj, "type", "").lower()
            if name=="":
                # If the type is not specified in the property,
                # assume it's an old style item, which means the
                # blender object name is to be used
                l = obj.name.split(".")
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
                if name=="YHERRING": name="big-nitro"
                if name=="SHERRING": name="small-nitro"
            else:
                if name=="nitro-big": name="big-nitro"
                if name=="nitro-small": name="small-nitro"

            # Get the position of the item - first check if the item should
            # be dropped on the track, or stay at the position indicated.
            rx,ry,rz = map(lambda x: rad2deg*x, obj.rot)
            h,p,r    = map(str, map(Round, [rz,rx,ry])  )
            x,y,z    = map(str, map(Round, obj.loc     )  )
            drop     = getProperty(obj, "drop", "y").lower()
            # Swap y and z axis to have the same coordinate system used in game.
            s        = "%s x=\"%s\" y=\"%s\" z=\"%s\"" % (name, x, z, y)
            if h and h!="0": s = "%s h=\"%s\""%(s, h)
            if drop=="n":
                # Pitch and roll will be set automatically if dropped
                if p and p!="0": s="%s p=\"%s\""%(s, p)
                if r and r!="0": s="%s r=\"%s\""%(s, r)
                s="%s drop=\"n\""%s

            f.write("  <%s />\n"%s)

        if lChecks or mainDriveline:
            if not lChecks:
                print "No check defined, lap counting will not work properly!"
            self.writeChecks(f, lChecks, mainDriveline)
        scene   = Blender.Scene.GetCurrent()
        sky     = getIdProperty(scene, "sky-type", None)
        # Note that there is a limit to the length of id properties,
        # which can easily be exceeded by 6 sky textures for a full sky box.
        # Therefore also check for sky-texture1 and sky-texture2.
        texture = getIdProperty(scene, "sky-texture", "")
        s       = getIdProperty(scene, "sky-texture1", "")
        if s: texture = "%s %s"%(texture, s)
        s       = getIdProperty(scene, "sky-texture2", "")
        if s: texture = "%s %s"%(texture, s)
        if sky and texture:
            if sky=="dome":
                hori           = getIdProperty(scene, "sky-horizontal",     16  )
                verti          = getIdProperty(scene, "sky-vertical",       16  )
                tex_percent    = getIdProperty(scene, "sky-texture-percent", 0.5)
                sphere_percent = getIdProperty(scene, "sky-sphere-percent",  1.3)
                speed_x        = getIdProperty(scene, "sky-speed-x",         0.0)
                speed_y        = getIdProperty(scene, "sky-speed-y",         0.0)
                f.write("""
  <sky-dome texture=\"%s\"
            horizontal=\"%s\" vertical=\"%s\" 
            texture-percent=\"%s\" sphere-percent=\"%s\"
            speed-x=\"%s\" speed-y=\"%s\" />
""" %(texture, hori, verti, tex_percent, sphere_percent, speed_x, speed_y))
            elif sky=="box":
                lTextures = string.split(texture)
                if len(lTextures)==5:
                    # Append a dummy 6th element
                    lTextures.append(lTextures[4])
                if len(lTextures)==6:
                    f.write("  <sky-box texture=\"%s\"/>\n" % \
                            " ".join(lTextures))
                else:
                    print "Found %d textures for sky box, must be 5 or 6 space separated texture names.\n" \
                          %len(lTextures)
                
        camera_far  = getIdProperty(scene, "camera-far", ""             )
        if camera_far:            
            f.write("  <camera far=\"%s\"/>\n"%camera_far)
        self.writeStartPositions(f, lStart)
        if lEndCameras:
            f.write("  <end-cameras>\n")
            for i in lEndCameras:
                type = getProperty(i, "type", "ahead").lower()
                if type=="ahead":
                    type="ahead_of_kart"
                elif type=="fixed":
                    type="static_follow_kart"
                else:
                    print "Unknown camera type %s - ignored." % type
                    continue
                xyz = "%f %f %f" % (i.loc[0], i.loc[2], i.loc[1])
                start = getProperty(i, "start", 5)
                f.write("    <camera type=\"%s\" xyz=\"%s\" distance=\"%s\"/>\n"%
                        (type, xyz, start) )
            f.write("  </end-cameras>\n")

        # Write camera curves (unused atm)
        self.writeCurve(f, lCameraCurves)
        f.write("</scene>\n")
        f.close()
        print bsys.time()-start_time,"seconds"

    # --------------------------------------------------------------------------
    # Writes the materials files, which includes all texture definitions 
    # (remember: Blenders "image" objects are STK's "material" objects)
    # Please use the STKProperty browser!!!
    def writeMaterialsFile(self, sPath):
        # Read & Write the materials to the file
        limage = Blender.Image.Get()
        
        materfound = False
        for i in limage:
            for sAttrib,sValue in i.properties.iteritems():
                materfound = True
                break
        if not materfound:
            print "No Materials defined."
            return

        ### Below a rewrite due to the problems with default values detected by Auria ###

        #Shape and form of things to write
        #-> this is basically an extract of the stk_browser datamodel... Perhaps go for intergation?
        
        # The list of all attributes that should always be written, even if
        # they are set to the default. For now this list is empty, but I left
        # the code in place in case that it might be needed later.
        lTextureDefaults = [
            #["anisotropic","yes"],\
            #["backface-culling","yes"],\
            #["clampU","no"],\
            #["clampV","no"],\
            #["compositing","none"],\
            #["disable-z-write","no"],\
            #["friction",1.0],\
            #["graphical-effect","none"],\
            #["ignore","no"],\
            #["light","yes"],\
            #["max-speed",1.0],\
            #["reset","no"],\
            #["slowdown-time",1.0],\
            #["sphere","no"],\
            #["surface","no"],\
            #["below-surface","no"],\
            #["falling-effect","no"],\
            #
            #["sfx:filename",""],\
            #["sfx:name",""],\
            #["sfx:rolloff",0.1],\
            #["sfx:min-speed",0.0],\
            #["sfx:max-speed",30.0],\
            #["sfx:min-pitch",1.0],\
            #["sfx:max-pitch",1.0],\
            #["sfx:positional","no"],\
            #
            #["zipper:duration",3.5],\
            #["zipper:max-speed-increase",15],\
            #["zipper:fade-out-time",3],\
            #["zipper:speed-gain",4.5],\
            #
            #["particle:base",""],\
            #["particle:condition","skid"]
        ]

        lBooleanAttributes = ["clampU","clampV","light","sphere","surface","below-surface",\
                              "falling-effect", \
                              "anisotropic","backface-culling","ignore","disable-z-write","reset",\
                              "sfx:positional"]
        
        start_time = bsys.time()
        print "Writing material file --> \t",

        f = open(sPath+"/materials.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<!-- Generated with script from SVN rev %s -->\n"%getScriptVersion())
        f.write("<materials>\n")

        for i in limage:
            #iterate through material definitions and collect data
            sImage = ""
            sSFX = ""
            sParticle = ""
            sZipper = ""
            hasSoundeffect = (convertTextToYN(getIdProperty(i, "sound-effect", "no")) == "Y")
            hasParticle = (convertTextToYN(getIdProperty(i, "particle", "no")) == "Y")
            hasZipper = (convertTextToYN(getIdProperty(i, "zipper", "no")) == "Y")

            # Create a copy of the list of defaults so that it can be modified. Then add
            # all properties of the current image
            l = lTextureDefaults[:]
            for sAttrib, sValue in i.properties.iteritems():
                if sAttrib not in l:
                    l.append( (sAttrib, sValue) )
            for AProperty,ADefault in l:
                # Don't add the (default) values to the property list
                currentValue = getIdProperty(i, AProperty, ADefault,
                                             set_value_if_undefined=0)
                #Correct for all the ways booleans can be represented (true/false;yes/no;zero/not_zero) 
                if AProperty in lBooleanAttributes:
                    currentValue = convertTextToYN(currentValue)
                
                #These items pertain to the soundeffects (starting with sfx:)
                if AProperty.strip().upper().startswith("SFX:"):
                    strippedName = AProperty.strip().split(":")[1]
                    sSFX = "%s %s=\"%s\""%(sSFX,strippedName,currentValue)
                elif AProperty.strip().upper().startswith("PARTICLE:"):
                    #These items pertain to the particles (starting with sfx:)
                    strippedName = AProperty.strip().split(":")[1]
                    sParticle = "%s %s=\"%s\""%(sParticle,strippedName,currentValue)   
                elif AProperty.strip().upper().startswith("ZIPPER:"):
                    #These items pertain to the particles (starting with sfx:)
                    strippedName = AProperty.strip().split(":")[1]
                    sZipper = "%s %s=\"%s\""%(sZipper,strippedName,currentValue)   
                else:
                    #These items are standard items
                    if AProperty.strip().upper() not in ["PARTICLE","SOUND-EFFECT","ZIPPER"]:
                        sImage = "%s %s=\"%s\""%(sImage,AProperty,currentValue)

            # Now write the main content of the materials.xml file
            if sImage or hasSoundeffect or hasParticle or hasZipper:
                #Get the filename of the image.
                s = i.getFilename()
                sImage="  <material name=\"%s\"%s" % (Blender.sys.basename(s),sImage)                
                if hasSoundeffect:
                    sImage="%s>\n    <sfx%s/" % (sImage,sSFX)
                if hasParticle:
                    sImage="%s>\n    <particles%s/" % (sImage,sParticle)
                if hasZipper:
                    sImage="%s>\n    <zipper%s/" % (sImage,sZipper)
                if not hasSoundeffect and not hasParticle and not hasZipper:
                    sImage="%s/>\n" % (sImage)
                else:
                    sImage="%s>\n  </material>\n" % (sImage)
          
                f.write(sImage)
            
        f.write("</materials>\n")

        f.close()
        print bsys.time()-start_time,"seconds"
        # ----------------------------------------------------------------------

    def __init__(self, sFilename):
        self.dExportedObjects = {}
        
        # Collect the different kind of meshes this exporter handles
        # ----------------------------------------------------------
        lObj                 = Blender.Object.Get()  # List of all objects
        lWater               = []                    # List of all water objects
        lTrack               = []                    # All main track objects
        lDrivelines          = []                    # All drivelines
        found_main_driveline = 0
        lItems               = []                    # All track items
        lEndCameras          = []                    # List of all end cameras
        lCameraCurves        = []                    # Camera curves (unused atm)
        lObjects             = []                    # All special objects
        lBillboards          = []                    # All billboards
        lParticleEmitters    = []                    # All particle emitters
        lChecks              = []                    # All check structures
        lSun                 = []
        lStart               = []                    # All start positions
        for obj in lObj:
            # Try to get the supertuxkart type field. If it's not defined,
            # use the name of the objects as type.
            stktype = getProperty(obj, "type", "").strip().upper()
            
            # Make it possible to ignore certain objects, e.g. if you keep a
            # selection of 'templates' (ready to go models) around to be
            # copied into the main track.
            if stktype=="IGNORE": continue
            
            if obj.type=="Empty":
                # For backward compatibility test for the blender name
                # in case that there is no type property defined. This makes
                # it easier to port old style tracks without having to
                # add the property for all items.
                stktype = getProperty(obj, "type", obj.name).upper()
                # Check for old and new style names
                if stktype[:8] in ["GHERRING", "RHERRING", "YHERRING", "SHERRING"] \
                   or stktype[: 6]== "BANANA"     or stktype[:4]=="ITEM"           \
                   or stktype[:11]=="NITRO-SMALL" or stktype[:9]=="NITRO-BIG"      \
                   or stktype[:11]=="SMALL-NITRO" or stktype[:9]=="BIG-NITRO"      \
                   or stktype[: 6]=="ZIPPER":
                    lItems.append(obj)
                    continue
                elif stktype[:5]=="START":
                    # Start empties are called start1, start2, ...
                    lStart.append(obj)
                elif stktype=="PARTICLE-EMITTER":
                    lParticleEmitters.append(obj)
                else:
                    print "Empty '%s' has type '%s' which is not valid - ignored."%\
                          (obj.name, stktype)
            elif obj.type=="Curve":
                # Only append camera, other curves will be handled in animations
                if stktype[:6]=="CAMERA": lCameraCurves.append(obj)
            elif obj.type=="Lamp":
                lSun.append(obj)
                continue
            elif obj.type=="Camera":
                lEndCameras.append(obj)
                continue
            elif obj.type!="Mesh":
                #print "Non-mesh object '%s' (type: '%s') is ignored!"%(obj.name, stktype)
                continue
            
            if stktype=="WATER":
                lWater.append(obj)
            elif stktype=="CHECK" or stktype=="LAP":
                lChecks.append(obj)
            # Check for new drivelines
            elif stktype=="MAIN-DRIVELINE" or \
                 stktype=="MAINDRIVELINE"  or \
                 stktype=="MAINDL":
                # Main driveline must be the first entry in the list
                lDrivelines.insert(0, Driveline(obj, 1))
                found_main_driveline = 1
            elif stktype=="DRIVELINE":
                lDrivelines.append(Driveline(obj, 0))
            elif stktype=="OBJECT" or stktype=="SPECIAL_OBJECT":
                lObjects.append(obj)
            # for billboard
            elif stktype=="BILLBOARD":
                lBillboards.append(obj)
            else:
                s = getProperty(obj, "type", None)
                if s:
                    print "Warning: object", obj.name,  \
                          " has type property '%s', which is not supported.\n"%s
                lTrack.append(obj)

        if not found_main_driveline:
            print "Main driveline missing, using first driveline as main!"
            
        # Now export the different parts: track file
        # ------------------------------------------
        sBase = os.path.basename(sFilename)
        sPath = os.path.dirname(sFilename)
        self.writeTrackFile(sPath, sBase)
    
        # Quads and mapping files
        # -----------------------
        scene    = Blender.Scene.GetCurrent()
        is_arena = getIdProperty(scene, "arena", "n")
        if not is_arena: is_arena="n"
        is_arena = not (is_arena[0]=="n" or is_arena[0]=="N" or \
                        is_arena[0]=="f" or is_arena[0]=="F"     )
        if not is_arena:
            self.writeQuadAndGraph(sPath, lDrivelines, lEndCameras)
        start_time = bsys.time()
        print "Exporting track -->",
        sTrackName = sBase+"_track.b3d"
        b3d_export.write_b3d_file(sFilename+"_track.b3d", lTrack)
        print bsys.time()-start_time,"seconds."
    
        # scene file
        # ----------
        if len(lDrivelines)==0:
            lDrivelines=[None]
        self.writeSceneFile(sPath, sTrackName, lWater, lTrack, lItems,
                            lObjects, lBillboards, lParticleEmitters, lChecks, lSun, lDrivelines[0],
                            lStart, lEndCameras, lCameraCurves)
        # materials file
        # ----------
        self.writeMaterialsFile(sPath)

        print "Finished."

# ==============================================================================
def savescene_callback(sFilename):
    # Settings for the b3d exporter:
    b3d_export.b3d_parameters["vertex-normals" ] = 1  # Vertex normals.
    b3d_export.b3d_parameters["vertex-colors"  ] = 1  # Vertex colors
    b3d_export.b3d_parameters["cameras"        ] = 0  # Cameras
    b3d_export.b3d_parameters["lights"         ] = 0  # Lights
    b3d_export.b3d_parameters["mipmap"         ] = 1  # Enable mipmap
    b3d_export.b3d_parameters["local-space"    ] = 0  # Export in world space

    exporter = TrackExport(sFilename)

# ==============================================================================
def main():
    print "\n\n-- supertuxkart exporter | SVN version:" + getScriptVersion() + " | (c) Joerg Henrichs (hiker)--"
    ok = 1
    try:
        b3d_version = b3d_export.__version__
        # Will be e.g. 2.06 or 3.0
        if int(b3d_version.split(".")[0])<3:
            ok = 0
    except:
        ok = 0
        
    if not ok:
        Blender.Draw.PupMenu("B3d exporter too old! Please install a new version from STK SVN.")
    else:
        # Make sure to leave edit mode, since otherwise the mesh before
        # entering edit mode is exported.
        if Blender.Window.EditMode():
            Blender.Window.EditMode(0)

        tmp_filename = Blender.sys.makename(ext = "")
        Blender.Window.FileSelector(savescene_callback,"Export STK track",tmp_filename)

        # Note that we can't go back to edit mode (if it was selected before)
        # since this line is executed by blender before any callback is done,
        # i.e. when the script actually runs, it is still in edit mode.
        # if was_edit_mode:  Blender.Window.EditMode(1)
        
if __name__ == "__main__":
    main()
