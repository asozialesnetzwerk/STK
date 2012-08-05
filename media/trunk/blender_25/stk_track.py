#!BPY

"""
Name: 'STK Track Exporter (.track)...'
Blender: 259
Group: 'Export'
Tooltip: 'Export a SuperTuxKart track scene'
"""
__author__ = ["Joerg Henrichs (hiker), Marianne Gagnon (Auria)"]
__url__ = ["supertuxkart.sourceforge.net"]
__version__ = "$Revision$"
__bpydoc__ = """\
"""

# From Supertuxkart SVN revision $Revision$

# Copyright (C) 2010 Joerg Henrichs
# Copyright (C) 2012 Marianne Gagnon
# INSERT (C) here!

#If you get an error here, it might be
#because you don't have Python installed.
import bpy
import sys, os, os.path, struct, math, string, re


bl_info = {
    "name": "SuperTuxKart Track Exporter",
    "description": "Exports a blender scene to the SuperTuxKart track format",
    "author": "Joerg Henrichs, Marianne Gagnon",
    "version": (1,0),
    "blender": (2, 5, 9),
    "api": 31236,
    "location": "File > Export",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://supertuxkart.sourceforge.net/Get_involved",
    "tracker_url": "https://sourceforge.net/apps/trac/supertuxkart/",
    "category": "Import-Export"}

from mathutils import *

operator = None
the_scene = None

log = []

def log_info(msg):
    print("INFO:", msg)
    log.append( ('INFO', msg) )
def log_warning(msg):
    print("WARNING:", msg)
    log.append( ('WARNING', msg) )
def log_error(msg):
    print("ERROR:", msg)
    log.append( ('ERROR', msg) )
    
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
# Gets an id property of an object, returning the default if the id property
# is not set. If set_value_if_undefined is set and the property is not
# defined, this function will also set the property to this default value.
def getIdProperty(obj, name, default="", set_value_if_undefined=1):
    import traceback
    try:
        prop = obj[name]
        if isinstance(prop, str):
            from xml.sax.saxutils import escape
            # + "" is used to force a copy of the string AND to convert from binary format to string format
            # escape formats the string for XML
            return (escape(prop + "") + "").encode('ascii', 'xmlcharrefreplace').decode("ascii")
        else:
            return prop
    except:
        if default!=None and set_value_if_undefined:
            obj[name] = default
    return default

# ------------------------------------------------------------------------------
# Returns a game logic property
def getProperty(obj, name, default=""):
    try:
        return obj[name]
    except:
        return default

# ------------------------------------------------------------------------------
# Returns a string 'x="1" y="2" z="3" h="4"', where 1, 2, ...are the actual
# location and rotation of the given object. The location has a swapped
# y and z axis (so that the same coordinate system as in-game is used).
def getXYZHString(obj):
    loc     = obj.location
    hpr     = obj.rotation_euler
    rad2deg = 180.0/3.1415926535;
    s="x=\"%.2f\" y=\"%.2f\" z=\"%.2f\" h=\"%f\"" %\
       (loc[0], loc[2], loc[1], hpr[2]*rad2deg)
    return s

# ------------------------------------------------------------------------------
# Returns a string 'xyz="1 2 3" hpr="4 5 6"' where 1,2,... are the actual
# location and rotation of the given object. The location has a swapped
# y and z axis (so that the same coordinate system as in-game is used), and
# rotations are multiplied by 10 (since bullet stores the values in units
# of 10 degrees.)
def getXYZHPRString(obj):
    loc     = obj.location
    # irrlicht uses XZY
    hpr     = obj.rotation_euler.to_quaternion().to_euler('XZY')
    si      = obj.scale
    rad2deg = 180.0/3.1415926535;
    s="xyz=\"%.2f %.2f %.2f\" hpr=\"%.1f %.1f %.1f\" scale=\"%.2f %.2f %.2f\"" %\
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
        self.mesh      = driveline.data.copy()
        self.mesh.transform(driveline.matrix_world)
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
        self.invisible = getProperty(driveline, "invisible", "false")
        self.ai_ignore = getProperty(driveline, "ai_ignore", "false")
        self.direction = getProperty(driveline, "direction", "both")
        self.enabled   = not getProperty(driveline, "disable",   0)
        self.activate  = getProperty(driveline, "activate", None)
        self.strict_lap = convertTextToYN(getProperty(driveline,
                                                      "strict_lapline", "N") ) \
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
          
            if self.lRight[-1] is None or self.lLeft[-1] is None:
                return # Invalid driveline (an error message will have been printed)
            
            cp.append((self.mesh.vertices[self.lLeft[-1]].co[i] + 
                       first_driveline.mesh.vertices[first_driveline.lLeft[0]].co[i]+
                       self.mesh.vertices[self.lRight[-1]].co[i] +
                       first_driveline.mesh.vertices[first_driveline.lRight[0]].co[i])*0.25)

        self.lCenter.append(cp)
        self.lLeft.append(None)
        self.lRight.append(None)

    # --------------------------------------------------------------------------
    # This creates a dictionary for a mesh which contains for each vertex a list
    # of all its neighbours.
    def createNeighbourDict(self):
        self.dNext = {}
        for e in self.mesh.edges:
            if e.vertices[0] in self.dNext:
                self.dNext[e.vertices[0]].append(e.vertices[1])
            else:
                self.dNext[e.vertices[0]] = [e.vertices[1]]
            
            if e.vertices[1] in self.dNext:
                self.dNext[e.vertices[1]].append(e.vertices[0])
            else:
                self.dNext[e.vertices[1]] = [e.vertices[0]]

    # --------------------------------------------------------------------------
    # This helper function determines the start vertex for a driveline.
    # Details are documented in convertDrivelines. It returns as list with
    # the two starting lines.
    def defineStartVertex(self):
        # Find all vertices with exactly two neighbours
        self.lStart = []
        for i in self.dNext.keys():
            if len(self.dNext[i])==1:
                self.lStart.append( i )

        if len(self.lStart)!=2:
            log_error("Driveline '%s' is incorrectly formed, cannot find the two 'antennas' that indicate where the driveline starts." % self.name)
            self.start_point = (0,0,0)
            return

        print("self.lStart[0] =", self.lStart[0])
        print("self.lStart[1] =", self.lStart[1])

        start_coord_1 = self.mesh.vertices[self.lStart[0]].co
        start_coord_2 = self.mesh.vertices[self.lStart[1]].co

        # Save the middle of the first quad, which is used later for neareast
        # quads computations.
        self.start_point = ((start_coord_1[0] + start_coord_2[0])*0.5,
                            (start_coord_1[1] + start_coord_2[1])*0.5,
                            (start_coord_1[2] + start_coord_2[2])*0.5 )

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
      
        if len(self.lStart) < 2:
            self.lLeft = [None, None]
            self.lRight = [None, None]
            self.start_line = (None, None)
            self.end_point = (0,0,0)
            self.lCenter = []
            return
      
        self.lLeft   = [self.lStart[0], self.dNext[self.lStart[0]][0]]
        self.lRight  = [self.lStart[1], self.dNext[self.lStart[1]][0]]
        self.lCenter = []
        
        # this is for error handling only
        processed_vertices = {}
        processed_vertices[self.lStart[0]] = True
        processed_vertices[self.lStart[1]] = True

        # The quads can be either clockwise or counter-clockwise oriented. STK
        # expectes counter-clockwise, so if the orientation is wrong, swap
        # left and right side.
        
        left_0_coord = self.mesh.vertices[self.lLeft[0]].co
        #left_1_coord = self.mesh.vertices[self.lLeft[1]].co
        right_0_coord = self.mesh.vertices[self.lRight[0]].co
        right_1_coord = self.mesh.vertices[self.lRight[1]].co
        
        if (right_1_coord[0] - left_0_coord[0])*(right_0_coord[1] - left_0_coord[1]) \
         - (right_1_coord[1] - left_0_coord[1])*(right_0_coord[0] - left_0_coord[0]) > 0:
            r   = self.lRight
            self.lRight = self.lLeft
            self.lLeft  = r
        
        # Save start edge, which will become the main lap counting line
        # (on the main driveline). This must be done here after potentially 
        # switching since STK assumes that the first point of a check line (to 
        # which the first line of the main driveline is converted) is on the 
        # left side (this only applies for the lap counting line, see
        # Track::setStartCoordinates/getStartTransform).
        self.start_line = (self.mesh.vertices[self.lLeft[1]].co, self.mesh.vertices[self.lRight[1]].co)
        
        count=0
        # Just in case that we have an infinite loop due to a malformed graph:
        # stop after 10000 vertices
        max_count = 10000
        warning_printed = 0

        while count < max_count:
            count = count + 1

            processed_vertices[self.lLeft[-1]] = True

            # Get all neighbours. One is the previous point, one
            # points to the opposite side - we need the other one.
            neighb = self.dNext[self.lLeft[-1]]
            next_left = []
            for i in neighb:
                if i==self.lLeft[-2]: continue   # pointing backwards
                if i==self.lRight[-1]: continue  # to opposite side
                next_left.append(i)
            
            if len(next_left) == 0:
                # No new element found --> this must be the end
                # of the list!!
                break
            
            if len(next_left)!=1 and not warning_printed:
                lcoord = self.mesh.vertices[self.lLeft[-1]].co
                rcoord = self.mesh.vertices[self.lRight[-1]].co
                log_warning("Broken driveline at or around point ({0}, {1}, {2})".format\
                            (lcoord[0], lcoord[1], lcoord[2]))
                print("Potential successors :")
                for i in range(len(next_left)):
                    nextco = self.mesh.vertices[next_left[i]].co
                    print ("Successor %d: %f %f %f" % \
                          (i, nextco[0], nextco[1], nextco[2]))
                print ("It might also possible that the corresponding right driveline point")
                print (rcoord[0],rcoord[1],rcoord[2])
                print ("has some inconsistencies.")
                print ("The drivelines will most certainly not be useable.")
                print ("Further warnings are likely and will be suppressed.")
                warning_printed = 1
                operator.report({'ERROR'}, "Problems with driveline detected, check console for details!")
                # Blender.Draw.PupMenu("Problems with driveline detected, check console for details!")
                
            self.lLeft.append(next_left[0])

            
            processed_vertices[self.lRight[-1]] = True

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
                lcoord = self.mesh.vertices[self.lLeft[-1]].co
                rcoord = self.mesh.vertices[self.lRight[-1]].co
                log_warning("Malformed driveline at or around points ({0}, {1}, {2}) and ({3}, {4}, {5})".format\
                             (lcoord[0],lcoord[1],lcoord[2],
                              rcoord[0],rcoord[1],rcoord[2]))
                print ("No more vertices on right side of quad line, but there are")
                print ("still points on the left side. Check the points:")
                print ("left: ", lcoord[0],lcoord[1],lcoord[2])
                print ("right: ", rcoord[0],rcoord[1],rcoord[2])
                print ("Last left point is ignored.")
                break
            
            if len(next_right)!=1 and not warning_printed:
                lcoord = self.mesh.vertices[self.lLeft[-1]].co
                rcoord = self.mesh.vertices[self.lRight[-1]].co
                
                log_error("Invalid driveline at or around point ({0}, {1}, {2})".format\
                          (rcoord[0],rcoord[1],rcoord[2]))
                print ("Warning: More than one potential succesor found for right driveline point")
                print (rcoord[0],rcoord[1],rcoord[2],":")
                #for i in range(len(next_right)):
                #    print ("Successor %d: %f %f %f" % \
                #          (i,next_right[i][0],next_right[i][1],next_right[i][2]))
                print ("It might also possible that the corresponding left driveline point")
                print (lcoord[0],lcoord[1],lcoord[2])
                print ("has some inconsistencies.")
                print ("The drivelines will most certainly not be useable.")
                print ("Further warnings are likely and will be suppressed.")
                warning_printed = 1
                operator.report({'ERROR'}, "Problems with driveline detected!")
                break                
            self.lRight.append(next_right[0])

            processed_vertices[self.lRight[-1]] = True
            processed_vertices[self.lLeft[-1]] = True
            processed_vertices[self.lRight[-2]] = True
            processed_vertices[self.lLeft[-2]] = True

            cp=[]
            for i in range(3):
                cp.append((self.mesh.vertices[self.lLeft[-2]].co[i] + 
                           self.mesh.vertices[self.lLeft[-1]].co[i] +
                           self.mesh.vertices[self.lRight[-2]].co[i] +
                           self.mesh.vertices[self.lRight[-1]].co[i])*0.25)
            self.lCenter.append(cp)

        if count>=max_count and not warning_printed:
            log_warning("Warning, Only the first %d vertices of driveline '%s' are exported" %\
                        (max_count, self.name))
        
        if warning_printed != 1:
            
            not_connected = None
            not_connected_distance = 99999
            
            for v in self.dNext:
                if not v in processed_vertices:
                    
                    # find closest connected vertex (this is only to improve the error message)
                    for pv in processed_vertices:
                        dist = (self.mesh.vertices[v].co - self.mesh.vertices[pv].co).length
                        if dist < not_connected_distance:
                            not_connected_distance = dist
                            not_connected = v
            
            if not_connected:
                log_warning("Warning, driveline '%s' appears to be broken in separate sections. Vertex at %f %f %f is not connected with the rest" % \
                                    (self.name,
                                     self.mesh.vertices[not_connected].co[0],
                                     self.mesh.vertices[not_connected].co[1],
                                     self.mesh.vertices[not_connected].co[2]))

        
        # Now remove the first two points, which are only used to indicate
        # the starting point:
        del self.lLeft[0]
        del self.lRight[0]
        self.end_point =((self.mesh.vertices[self.lLeft[-1]].co[0] +
                          self.mesh.vertices[self.lRight[-1]].co[0])*0.5,
                         (self.mesh.vertices[self.lLeft[-1]].co[1] +
                          self.mesh.vertices[self.lRight[-1]].co[1])*0.5,
                         (self.mesh.vertices[self.lLeft[-1]].co[2] +
                          self.mesh.vertices[self.lRight[-1]].co[2])*0.5 )

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
        return quad_index + lSorted[driveline_index].getFirstQuadIndex()

    # --------------------------------------------------------------------------
    # Writes the quads into a file.
    def writeQuads(self, f):
      
        if self.lLeft[0] is None or self.lRight[0] is None:
            return # Invalid driveline (a message will have been printed)
        if self.lLeft[1] is None or self.lRight[1] is None:
            return # Invalid driveline (a message will have been printed)
      
        l   = self.mesh.vertices[self.lLeft[0]].co
        r   = self.mesh.vertices[self.lRight[0]].co
        l1  = self.mesh.vertices[self.lLeft[1]].co
        r1  = self.mesh.vertices[self.lRight[1]].co

        if self.invisible and self.invisible=="true":
            sInv = " invisible=\"yes\" "
        else:
            sInv = " "
        
        if self.ai_ignore and self.ai_ignore=="true":
            sAIIgnore = "ai-ignore=\"yes\" "
        else:
            sAIIgnore = " "
        
        if self.direction and self.direction != "both":
            sDirection = "direction=\"" + self.direction + "\" "
        else:
            sDirection = " "
            
        max_index = len(self.lLeft) - 1
        
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
        f.write("  <quad%s%s%sp0=\"%f %f %f\" p1=\"%f %f %f\" p2=\"%f %f %f\" p3=\"%f %f %f\"/>\n" \
            %(sInv, sAIIgnore, sDirection, l[0],l[2],l[1], r[0],r[2],r[1], r1[0],r1[2],r1[1], l1[0],l1[2],l1[1]) )
        for i in range(1, max_index):
            if self.lRight[i+1] is None: return # broken driveline (messages will already have been printed)
          
            l1  = self.mesh.vertices[self.lLeft[i+1]].co
            r1  = self.mesh.vertices[self.lRight[i+1]].co
            f.write("  <quad%s%sp0=\"%d:3\" p1=\"%d:2\" p2=\"%f %f %f\" p3=\"%f %f %f\"/>\n" \
                    %(sInv,sDirection,self.global_quad_index_start+i-1, self.global_quad_index_start+i-1, \
                  r1[0],r1[2],r1[1], l1[0],l1[2],l1[1]) )
        if self.is_last_main:
            f.write("  <quad%sp0=\"%d:3\" p1=\"%d:2\" p2=\"0:1\" p3=\"0:0\"/>\n"\
                    % (sInv, self.global_quad_index_start+max_index-1, \
                             self.global_quad_index_start+max_index-1))

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
        
        name = name + ".b3d"
        # If the object was already exported, we don't have to do it again.
        if name in self.dExportedObjects: return name
        
        if 'b3d_export' not in dir(bpy.ops.screen):
            log_error("Cannot find the B3D exporter, make sure you installed it properly")
            return
        
        # FIXME: silly and ugly hack, the list of objects to export is passed through
        #        a custom scene property
        global the_scene
        the_scene.obj_list = [obj]
        bpy.ops.screen.b3d_export(localsp=True, mipmap=True, lights=False, vcolors=True,
                                  vnormals=True, cameras=False, filepath=sPath+"/"+name,
                                  overwrite_without_asking=True)
        the_scene.obj_list = []
        #bpy.ops.screen.b3d_export.skip_dialog = False
        #setObjList([])
        
        #b3d_export.b3d_parameters["local-space"] = old_space
        
        self.dExportedObjects[name]=1
        
        return name

    # ----------------------------------------------------------------------
    def writeTrackFile(self, sPath, nsBase):
        print("Writing track file --> \t")

        global the_scene

        #start_time  = bsys.time()
        scene       = the_scene
        name        = getIdProperty(scene, "name",       "Name of Track")
        groups      = getIdProperty(scene, "groups",     "standard"     )
        is_arena    = getIdProperty(scene, "arena",      "n"            )
        if not is_arena:
            is_arena="n"
        is_arena = not (is_arena[0]=="n" or is_arena[0]=="N" or \
                        is_arena[0]=="f" or is_arena[0]=="F"      )

        is_cutscene = getIdProperty(scene, "cutscene",  "false") == "true"
        is_internal = getIdProperty(scene, "internal",   "n"            )
        is_internal = (is_internal == "true")
        
        designer    = getIdProperty(scene, "designer",   ""             )
        
        # Support for multi-line descriptions:
        designer    = designer.replace("\\n", "\n")
        
        if not designer:
            designer    = getIdProperty(scene, "description", "")
            if designer:
                log_warning("The 'Description' field is deprecated, please use 'Designer'")
            else:
                designer="?"
        
        music       = getIdProperty(scene, "music", "")
        screenshot  = getIdProperty(scene, "screenshot", "")

        smooth_normals = getIdProperty(scene, "smooth_normals", "false")

        # Add default settings for sky-dome so that the user is aware of
        # can be set.
        getIdProperty(scene, "sky_type", "dome")
        getIdProperty(scene, "sky_texture", "" )
        getIdProperty(scene, "sky_speed_x", "0")
        getIdProperty(scene, "sky_speed_y", "0")
        # Not sure if these should be added - if the user wants a sky
        # box they are quiet annoying.
        #getIdProperty(scene, "sky-color","")
        #getIdProperty(scene, "sky-horizontal","")
        #getIdProperty(scene, "sky-vertical", "")
        #getIdProperty(scene, "sky-texture-percent","")
        #getIdProperty(scene, "sky-sphere-percent", "")
        
        f = open(sPath+"/track.xml", mode='w', encoding='utf-8')
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<!-- Generated with script from SVN rev %s -->\n"%getScriptVersion())
        f.write("<track  name           = \"%s\"\n"%name)
        f.write("        version        = \"5\"\n")
        f.write("        groups         = \"%s\"\n"%groups)
        f.write("        designer       = \"%s\"\n"%designer)
        if music:
            f.write("        music          = \"%s\"\n"%music)
        else:
            log_warning("No music file defined.")
        
        if is_arena:
            f.write("        arena          = \"Y\"\n")

        if is_cutscene:
            f.write("        cutscene       = \"Y\"\n")

        if is_internal:
            f.write("        internal       = \"Y\"\n")
        
        if screenshot:
            f.write("        screenshot     = \"%s\"\n"%screenshot)
        else:
            log_warning("No screenshot defined")

        f.write("        smooth-normals = \"%s\"\n" % smooth_normals)
        
        f.write(">\n")
        f.write("</track>\n")
        f.close()
        #print bsys.time() - start_time, "seconds"
     
    # --------------------------------------------------------------------------
    
    def writeBezierCurve(self, f, curve, speed):
        matrix = curve.matrix_world
        if len(curve.data.splines) > 1:
            log_warning(curve.name + " contains multiple curves, will only export the first one")
        
        f.write('    <curve channel="LocXYZ" speed="%.2f" curvetype="bezier">\n'%speed)
        if curve.data.splines[0].type != 'BEZIER':
            log_warning(curve.name + " should be a bezier curve, not a " + curve.data.splines[0].type)
        else:
            for pt in curve.data.splines[0].bezier_points:
                v0 = matrix*pt.handle_left
                v1 = matrix*pt.co*matrix 
                v2 = matrix*pt.handle_right
                f.write("      <point c=\"%f %f %f\" h1=\"%f %f %f\" h2=\"%f %f %f\" />\n"% \
                        ( v1[0],v1[2],v1[1],
                          v0[0],v0[2],v0[1],
                          v2[0],v2[2],v2[1] ) )
        f.write("    </curve>\n")
    
    # --------------------------------------------------------------------------
    def writeCurves(self, f, lCurves):
        count = 0
        for curves in lCurves:
            type=getProperty(curves, "type").lower()
            if not type in ["camera", "anim2d", "anim3d"]: continue
            count = count + 1
        if count==0: return
        f.write("  <curves>\n")
        for curve in lCurves:
            type=getProperty(curve, "type").lower()
            if not type in ["camera", "anim2d", "anim3d"]: continue
            matrix = curve.getMatrix()
        for nu in curve.data:
            # 0:"poly", 1:"bezier", 4:"nurbs"
            if nu.type==4:
                f.write("    <%s curvetype=\"nurb\" name=\"%s\">\n" \
                        % (type, curve.name))
                for i in nu:
                    v=Vector(i[0],i[1],i[2]) * matrix
                    f.write("      <p=\"%.3f %.3f %.3f\"/>\n"%(v[0], v[1], v[2]))
                f.write("    </%s>\n"%type)
            elif nu.type==1:
                f.write("    <%s curvetype=\"bezier\" name=\"%s\">\n" \
                        % (type, curve.name))
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
                           lSorted[0].getDistanceTo(cam.location, lSorted)
                # Each list contains the index of the closest quad, the
                # distance, and then the camera
                lEndCameras[i] = (driveline_index, quad_index_camera, cam)
            except:
                log_warning("Problem with the end camera '%s'. Check if the main driveline is " +\
                            "properly defined (check warning messages), and the " +\
                            "settings of the camera."%cam.name)
                
        lEndCameras.sort()
        
        # After sorting remove the unnecessary distance and quad index
        for i in range(len(lEndCameras)):
            # Avoid crash in case that some problem with the camera happened,
            # and lEndCameras is just the blender camera, not the tuple
            if type(lEndCameras[i])==type(()):
                lEndCameras[i] = lEndCameras[i][2]

        # There were already two warning messages printed at this stage, so just
        # ignore this to avoid further crashes
        if len(lSorted) < 1:
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
        #start_time = bsys.time()
        print("Writing quad file --> \t")
        if not lDrivelines:
            print("No main driveline defined, no driveline information exported!!!")
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
        #print bsys.time() - start_time,"seconds. "

        #start_time = bsys.time()
        print("Writing graph file --> \t")
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
            if (fr,to) not in dWrittenEdges:
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
            if (fr, to) not in dWrittenEdges:
                f.write("  <edge from=\"%d\" to=\"%d\"/>\n" %(fr, to))
                dWrittenEdges[ (fr, to) ] = 1
        f.write("</graph>\n")
        f.close()
        #print bsys.time()-start_time,"seconds. "
          
    # --------------------------------------------------------------------------
    def writeIPO(self, f, anim_data ):
        #dInterp = {IpoCurve.InterpTypes.BEZIER:        "bezier",
        #           IpoCurve.InterpTypes.LINEAR:        "linear",
        #           IpoCurve.InterpTypes.CONST:         "const"          }
        #dExtend = {IpoCurve.ExtendTypes.CONST:         "const",
        #           IpoCurve.ExtendTypes.EXTRAP:        "extrap",
        #           IpoCurve.ExtendTypes.CYCLIC_EXTRAP: "cyclic_extrap",
        #           IpoCurve.ExtendTypes.CYCLIC:        "cyclic"         }
        
        if anim_data and anim_data.action:
            ipo = anim_data.action.fcurves
        else:
            return
        
        # ==== Possible values returned by blender ====
        # fcurves[0].data_path
        #    location, rotation_euler, scale
        # fcurves[0].extrapolation
        #    CONSTANT, LINEART
        # fcurves[0].keyframe_points[0].interpolation
        #    CONSTANT, LINEAR, BEZIER
        
        # Swap Y and Z axis
        axes = ['X', 'Z', 'Y']
        
        for curve in ipo:
          
            if curve.data_path == 'location':
                name = "Loc" + axes[curve.array_index]
            elif curve.data_path == 'rotation_euler':
                name = "Rot" + axes[curve.array_index]
            elif curve.data_path == 'scale':
                name = "Scale" + axes[curve.array_index]
            else:
                if "pose.bones" not in curve.data_path: # we ignore bone curves
                    log_warning("Unknown curve type " + curve.data_path)
                continue
            
            extrapolation = "const"
            
            for modifier in curve.modifiers:
                if modifier.type == 'CYCLES':
                    extrapolation = "cyclic"
                    break
            
            # If any point is bezier we'll export as Bezier
            interpolation = "linear"
            for bez in curve.keyframe_points:
                if bez.interpolation=='BEZIER':
                    interpolation = "bezier"
                    break
            
            # Rotations are stored in randians
            if name[:3]=="Rot":
                factor=-57.29577951 # 180/PI
            else:
                factor=1
            f.write("    <curve channel=\"%s\" interpolation=\"%s\" extend=\"%s\">\n"% \
                    (name, interpolation, extrapolation))
                    #(name, dInterp[curve.interpolation], dExtend[curve.extend]))
            
            warning_shown = False
            
            for bez in curve.keyframe_points:
                if interpolation=="bezier":
                    if bez.interpolation=='BEZIER':
                        f.write("      <p c=\"%.3f %.3f\" h1=\"%.3f %.3f\" h2=\"%.3f %.3f\"/>\n"%\
                                (bez.co[0],factor*bez.co[1],
                                 bez.handle_left[0], factor*bez.handle_left[1],
                                 bez.handle_right[0], factor*bez.handle_right[1]))
                    else:
                        # point with linear IPO in bezier curve
                        f.write("      <p c=\"%.3f %.3f\" h1=\"%.3f %.3f\" h2=\"%.3f %.3f\"/>\n"%\
                                (bez.co[0], factor*bez.co[1],
                                 bez.co[0] - 1, factor*bez.co[1],
                                 bez.co[0] + 1, factor*bez.co[1]))
                        
                        if not warning_shown:
                            log_warning("You have an animation curve which contains a mix of mixture of Bezier and " +
                                        "linear interpolation, please convert everything to Bezier for best results")
                            warning_shown = True
                else:
                    f.write("      <p c=\"%.3f %.3f\"/>\n"%(bez.co[0],
                                                            factor*bez.co[1]))
            f.write("    </curve>\n")
    
    # --------------------------------------------------------------------------
    # Writes the animation for objects using IPOs:
    def writeAnimationWithIPO(self, f, name, obj, ipo, objectType="animation"):
        # An animated object can set the 'name' property, then this name will
        # be used to name the exported object (instead of the python name
        # which might be a default name with a number). Additionally, names
        # are cached so it can be avoided to export two or more identical
        # objects.
        parent = obj.parent
        # For now: armature animations are assumed to be looped
        if parent and parent.type=="ARMATURE":
            looped =" looped=\"y\" "
        else:
            looped = ""
        shape = getProperty(obj, "shape", "")
        if shape:
            shape="shape=\"%s\""%shape
        if not ipo: ipo=[]

        lodstring = self.getLODString(obj)
        
        type = getProperty(obj, "type", "")
        if type == "lod_instance":
            model_string = ""
        else:
            model_string = "model=\"%s\" " % name
        
        interaction = getProperty(obj, "interaction", 'static')
        if interaction == 'reset':
            reset_string = " reset=\"y\""
        else:
            reset_string = ""
        
        interaction_string = ' interaction="' + interaction + '"'
        
        tangent_string = ""
        if getProperty(obj, "tangents", "false") == "true":
            tangent_string="tangents=\"true\" "
            
        if parent and parent.type=="ARMATURE":
            f.write("  <object type=\"%s\" %s%s %s%s%s%s%s%s>\n"% \
                    (objectType, model_string, getXYZHPRString(parent), shape, looped,
                     lodstring, reset_string, tangent_string, interaction_string))
        else:
            f.write("  <object type=\"%s\" %s%s %s%s%s%s%s%s>\n"% \
                    (objectType, model_string, getXYZHPRString(obj), shape, looped,
                     lodstring, reset_string, tangent_string, interaction_string))
        self.writeIPO(f, ipo)
        f.write("  </object>\n")
            
        
    # --------------------------------------------------------------------------
    # Writes an animation that uses a path constrained.
    def writeAnimationsWithPaths(self, f, sPath, obj):
        #print "b3d export", obj.name
        print("'%s' is using path '%s'"%(obj.name,
                               obj.constraints[0][Constraint.Settings.TARGET].name))
    
    # --------------------------------------------------------------------------
    def writeAnimatedTextures(self, f, lAnimTextures):
        for (name, dx, dy) in lAnimTextures:
            sdx=""
            if dx: sdx = " dx=\"%.3f\" "%float(dx)
            sdy=""
            if dy: sdy = " dy=\"%.3f\" "%float(dy)
            f.write("    <animated-texture name=\"%s\"%s%s/>\n"%(name, sdx, sdy) )
        
    # --------------------------------------------------------------------------
    # Write the objects that are part of the track (but not animated or
    # physical).
    def writeStaticObjects(self, f, sPath, lStaticObjects, lAnimTextures):
        for obj in lStaticObjects:
            
            lodstring = self.getLODString(obj)

            # An object can set the 'name' property, then this name will
            # be used to name the exported object (instead of the python name
            # which might be a default name with a number). Additionally, names
            # are cached so it can be avoided to export two or more identical
            # objects.
            lAnim    = self.checkForAnimatedTextures([obj])
            name     = getProperty(obj, "name", obj.name)
            if len(name) == 0: name = obj.name
            
            type = getProperty(obj, "type", "X")
            
            if type != "lod_instance":
                b3d_name = self.exportLocalB3D(obj, sPath, name)
            kind = getProperty(obj, "kind", "")
            
            if type == "lod_instance":
                model_string = ""
            elif type == "single_lod":
                # single_lod is a shortcut that generates both a lod_instance and a lod_model
                model_string2 =  " model=\"%s\""%b3d_name
                lodstring2 = ' lod_distance="' + str(getProperty(obj, "lod_distance", 60.0)) + '" lod_group="_single_lod_' + name + '"'
                f.write("    <static-object%s%s %s interaction\"%s\"/> <!-- writeStaticObjects -->\n" % (lodstring2, model_string2, getXYZHPRString(obj), getProperty(obj, "interaction", "static")) )
                model_string = ""
            else:
                model_string =  " model=\"%s\""%b3d_name

            condition_if = getProperty(obj, "if", "")
            if len(condition_if) > 0:
                condition_if_str = " if=\"%s\""%condition_if
            else:
                condition_if_str = ""
            
            condition_ifnot = getProperty(obj, "ifnot", "")
            if len(condition_ifnot) > 0:
                condition_ifnot_str = " ifnot=\"%s\""%condition_ifnot
            else:
                condition_ifnot_str = ""
            
            challenge_val = getProperty(obj, "challenge", "")
            if len(challenge_val) > 0:
                challenge_str = " challenge=\"%s\""% challenge_val
            else:
                challenge_str = ""
                
            interaction = getProperty(obj, "interaction", '??')
            if interaction == 'reset':
                reset_string = " reset=\"y\""
            else:
                reset_string = ""
            
            tangent_string = ""
            if getProperty(obj, "tangents", "false") == "true":
                tangent_string=" tangents=\"true\""
            
            if lAnim:
                f.write("    <static-object%s%s %s%s%s%s%s> <!-- writeStaticObjects 2 -->\n"% \
                        (lodstring, model_string, getXYZHPRString(obj), reset_string,
                         condition_if_str, condition_ifnot_str, tangent_string) )
                self.writeAnimatedTextures(f, lAnim)
                f.write("    </static-object>\n")
            else:
                f.write("    <static-object%s%s %s%s%s%s%s%s/> <!-- writeStaticObjects 3 -->\n"% \
                        (lodstring, model_string, getXYZHPRString(obj), reset_string,
                         condition_if_str, condition_ifnot_str, challenge_str, tangent_string) )
        self.writeAnimatedTextures(f, lAnimTextures)

    # --------------------------------------------------------------------------
    # Get LOD string for a given object (returns an empty string if object is not LOD)
    def getLODString(self, obj):
        lodstring = ""
        type = getProperty(obj, "type", "object")
        if type == "lod_model":
            dist = type = getProperty(obj, "lod_distance", None)
            if dist is None:
                log_warning("LOD model " + obj.name + " has no distance property")
            group = type = getProperty(obj, "lod_name", "")
            if len(group) == 0:
                log_warning("LOD model " + obj.name + " has no group property")
            lodstring = ' lod_distance="' + str(dist) + '" lod_group="' + group + '"'
        elif type == "lod_instance":
            group = type = getProperty(obj, "lod_name", "")
            if len(group) == 0:
                log_warning("LOD instance " + obj.name + " has no group property")
            lodstring = ' lod_instance="true" lod_group="' + group + '"'
        elif type == "single_lod":
            lodstring = ' lod_instance="true" lod_group="_single_lod_' + getProperty(obj, "name", obj.name) + '"'
        return lodstring

    # --------------------------------------------------------------------------
    # billboard section (check if the billboard is correct and write in the file)
    def writeBillboard(self,f, obj):
        data = obj.data
        
        # check the face
        if len(data.faces) > 1:
            log_error("Billboard <" + getProperty(obj, "name", obj.name) \
                  + "> has more than ONE face")
            return
        
        # check the points
        if len(data.vertices) > 4:
            log_error("Billboard <" + getProperty(obj, "name", obj.name)\
                       + "> has more than 4 points")
            return
        
        if len(data.uv_textures) < 1 or len(data.uv_textures[0].data) < 1:
            log_error("Billboard <" + getProperty(obj, "name", obj.name)\
                       + "> has no UV texture")
            return
        
        
        try:
            # write in the XML
            # calcul the size and the position
            x_min = data.vertices[0].co[0]
            x_max = x_min
            y_min = data.vertices[0].co[2]
            y_max = y_min
            z_min = data.vertices[0].co[1]
            z_max = z_min
            for i in range(1, 4):
                x_min = min(x_min, data.vertices[i].co[0])
                x_max = max(x_max, data.vertices[i].co[0])
                y_min = min(y_min, data.vertices[i].co[2])
                y_max = max(y_max, data.vertices[i].co[2])
                z_min = min(z_min, data.vertices[i].co[1])
                z_max = max(z_max, data.vertices[i].co[1])
            
            fadeout_str = ""
            fadeout = getProperty(obj, "fadeout", "false")
            if fadeout == "true":
                start = float(getProperty(obj, "start", 1.0))
                end = float(getProperty(obj, "end", 15.0))
                fadeout_str = "fadeout=\"true\" start=\"" + str(start) + "\" end=\"" + str(end) + "\""
            
            f.write('  <object type="billboard" texture="%s" xyz="%f %f %f" \n'%
                    (os.path.basename(data.uv_textures[0].data[0].image.filepath),
                     obj.location[0], obj.location[2], obj.location[1]) )
            f.write('             width="%f" height="%f" %s>\n' %(max(x_max-x_min, z_max-z_min), y_max-y_min, fadeout_str) )
            if obj.animation_data and obj.animation_data.action and obj.animation_data.action.fcurves and len(obj.animation_data.action.fcurves) > 0:
                self.writeIPO(f, obj.animation_data)
            f.write('  </object>\n')

        except ValueError:
            log_error("Invalid value for billboard <" + getProperty(obj, "name", obj.name) + "> ",
                    sys.exc_info()[0])

    # --------------------------------------------------------------------------
    # Particle emitter 
    def writeParticleEmitters(self,f, lParticleEmitters):
        for obj in lParticleEmitters:
            try:
                # origin
                originXYZ = getXYZHString(obj)
                
                if getProperty(obj, "clip_distance", 0) > 0 :
                    f.write('  <particle-emitter kind="%s" %s clip_distance="%i">\n' %\
                            (getProperty(obj, "kind", 0), originXYZ, getProperty(obj, "clip_distance", 0)))
                else:
                    f.write('  <particle-emitter kind="%s" %s>\n' %\
                        (getProperty(obj, "kind", 0), originXYZ))
                
                if obj.animation_data and obj.animation_data.action and obj.animation_data.action.fcurves and len(obj.animation_data.action.fcurves) > 0:
                    self.writeIPO(f, obj.animation_data)
                
                f.write('  </particle-emitter>\n')
            except:
                log_error("Invalid particle emitter <" + getProperty(obj, "name", obj.name) + "> ",
                    sys.exc_info()[0])

    # --------------------------------------------------------------------------
    # Sound emitter 
    def writeSoundEmitters(self,f, lSoundEmitters):
        for obj in lSoundEmitters:
            try:
                # origin
                originXYZ = getXYZHPRString(obj)
                
                play_near_string = ""
                if getProperty(obj, "play_when_near", "false") == "true":
                    dist = getProperty(obj, "play_distance", 1.0)
                    play_near_string = " play-when-near=\"true\" distance=\"%.1f\"" % dist
                
                conditions_string = ""
                if len(getProperty(obj, "sfx_conditions", "")) > 0:
                    conditions_string = ' conditions="' + getProperty(obj, "sfx_conditions", "") + '"'
                
                
                f.write('  <object type="sfx-emitter" sound="%s" rolloff="%.3f" volume="%s" max_dist="%.1f" %s%s%s>\n' %\
                        (getProperty(obj, "sfx_filename", "some_sound.ogg"),
                         getProperty(obj, "sfx_rolloff", 0.05),
                         getProperty(obj, "sfx_volume", 0),
                         getProperty(obj, "sfx_max_dist", 500.0), originXYZ, play_near_string, conditions_string))
                
                if obj.animation_data and obj.animation_data.action and obj.animation_data.action.fcurves and len(obj.animation_data.action.fcurves) > 0:
                    self.writeIPO(f, obj.animation_data)
                
                f.write('  </object>\n')
            except:
                log_error("Invalid sound emitter <" + getProperty(obj, "name", obj.name) + "> ",
                    sys.exc_info()[0])
        
    # --------------------------------------------------------------------------
    # Action Triggers
    def writeActionTriggers(self, f, lActionEmitters):
        for obj in lActionEmitters:
            try:
                # origin
                originXYZ = getXYZHPRString(obj)
                
                f.write('  <object type="action-trigger" action="%s" distance="%s" %s/>\n' %\
                        (getProperty(obj, "action", ""),
                         getProperty(obj, "trigger_distance", 5.0),
                         originXYZ))
            except:
                log_error("Invalid action <" + getProperty(obj, "name", obj.name) + "> ",
                    sys.exc_info()[0])

    # --------------------------------------------------------------------------
    # Writes out all checklines.
    # \param lChecks All check meshes
    # \param mainDriveline The main driveline, from which the lap
    #        counting check line is determined.
    def writeCannon(self, f, cannon):
    
        start = cannon
        
        endSegmentName = getProperty(start, "cannonend", "")
        if len(endSegmentName) == 0 or endSegmentName not in bpy.data.objects:
            log_error("Cannon " + cannon.name + " end is not defined")
            return
        
        end = bpy.data.objects[endSegmentName]
        
        if len(start.data.vertices) != 2:
            log_warning("Cannon start " + start.name + " is not a line made of 2 vertices as expected")
        if len(end.data.vertices) != 2:
            log_warning("Cannon end " + end.name + " is not a line made of 2 vertices as expected")
        
        startloc = start.location
        endloc = end.location
        
        start_matrix = start.rotation_euler.to_matrix()
        end_matrix = end.rotation_euler.to_matrix()
        
        curvename = getProperty(start, "cannonpath", "")
        
        start_pt1 = start.data.vertices[0].co*start_matrix + startloc
        start_pt2 = start.data.vertices[1].co*start_matrix + startloc
        end_pt1 = end.data.vertices[0].co*end_matrix + endloc
        end_pt2 = end.data.vertices[1].co*end_matrix + endloc
        

        f.write('    <cannon p1="%.2f %.2f" p2="%.2f %.2f" min-height="%f" target-p1="%.2f %.2f %.2f" target-p2="%.2f %.2f %.2f">\n'%\
                (start_pt1[0], start_pt1[1],
                 start_pt2[0], start_pt2[1],
                 min(start_pt1[2], start_pt2[2]),
                 end_pt1[0],   end_pt1[2],   end_pt1[1],
                 end_pt2[0],   end_pt2[2],   end_pt2[1]))
        
        if len(curvename) > 0:
            self.writeBezierCurve(f, bpy.data.objects[curvename], \
                                  getProperty(start, "cannonspeed", 50.0) )
        
        f.write('    </cannon>\n')
        
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
            name = getProperty(obj, "type", obj.name.lower()).lower()
            if len(name) == 0: name = obj.name.lower()
            
            type = getProperty(obj, "type", "")
            if type == "cannonstart" or type == "cannonend":
                continue
                
            if name!="lap":
                name = getProperty(obj, "name", obj.name.lower()).lower()
            if name in dGroup2Indices:
                dGroup2Indices[name].append(ind)
            else:
                dGroup2Indices[name] = [ ind ]
            ind = ind + 1

        if mainDriveline:
            lap = mainDriveline.getStartEdge()
            
            if lap[0] is None:
                return # Invalid driveline (a message will have been printed)
            
            coord = lap[0]
            min_h = coord[2]
            if coord[2] < min_h: min_h = coord[2]

            # The main driveline is always the first entry, so remove
            # only the first entry to get the list of all other lap lines
            l = dGroup2Indices["lap"]
            
            from functools import reduce
            sSameGroup = reduce(lambda x,y: str(x)+" "+str(y), l, "")
            
            activate = mainDriveline.getActivate()
            if activate:
                group = activate.lower()
                
                if not group or group not in dGroup2Indices:
                    log_warning("Activate group '%s' not found!"%group)
                    print("Ignored - but lap counting might not work correctly.")
                    print("Make sure there is an object of type 'check' with")
                    print("the name '%s' defined."%group)
                    activate = ""
                else:
                    activate = reduce(lambda x,y: str(x)+" "+str(y), dGroup2Indices[group])
            else:
                group = ""
                activate = ""
                log_warning("Warning : the main driveline does not activate any checkline. Lap counting and kart rescue will not work correctly.")
        else:
            # No main drive defined, print a warning and add some dummy
            # driveline (makes the rest of this code easier)
            log_warning("no main driveline defined, adding dummy driveline")
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
        
            try:
                type = getProperty(obj, "type", "")
                if type == "cannonstart":
                    self.writeCannon(f, obj)
                    continue
                elif type == "cannonend":
                    continue
                
                mesh = obj.data.copy()
                # Convert to world space
                mesh.transform(obj.matrix_world)
                # One of lap, activate, toggle, ambient
                activate = getProperty(obj, "activate", "")
                kind=" "
                if activate:
                    group = activate.lower()
                    if group not in dGroup2Indices:
                        log_warning("Activate group '%s' not found!"%group)
                        print("Ignored - but lap counting might not work correctly.")
                        print("Make sure there is an object of type 'check' with")
                        print("the name '%s' defined."%group)
                        continue
                    s = reduce(lambda x,y: str(x)+" "+str(y), dGroup2Indices[group])
                    kind = " kind=\"activate\" other-ids=\"%s\" "% s

                toggle = getProperty(obj, "toggle", "")
                if toggle:
                    group = toggle.lower()
                    if group not in dGroup2Indices:
                        log_warning("Toggle group '%s' not found!"%group)
                        print("Ignored - but lap counting might not work correctly.")
                        print("Make sure there is an object of type 'check' with")
                        print("the name '%s' defined."%group)
                        continue
                    s = reduce(lambda x,y: str(x)+" "+str(y), dGroup2Indices[group])
                    kind = " kind=\"toggle\" other-ids=\"%s\" "% s

                lap = getProperty(obj, "type", obj.name).upper()
                if lap[:3]=="LAP":
                    kind = " kind=\"lap\" "  # xml needs a value for an attribute
                    activate = getProperty(obj, "activate", "")
                    if activate:
                        group = activate.lower()
                        if group not in dGroup2Indices:
                            log_warning("Activate group '%s' not found for lap line!"%group)
                            print("Ignored - but lap counting might not work correctly.")
                            print("Make sure there is an object of type 'check' with")
                            print("the name '%s' defined."%group)
                            continue
                        s = reduce(lambda x,y: str(x)+" "+str(y), dGroup2Indices[group])
                        kind = "%sother-ids=\"%s\" "% (kind, s)
                
                ambient = getProperty(obj, "ambient", "").upper()
                if ambient:
                    kind=" kind=\"ambient-light\" "

                # Get the group name this object belongs to. If the objects
                # is of type lap then 'lap' is the group name, otherwise
                # it's taken from the name property (or the object name).
                name = getProperty(obj, "type", obj.name.lower()).lower()
                if name!="lap":
                    name = getProperty(obj, "name", obj.name.lower()).lower()
                    if len(name) == 0: name = obj.name.lower()
                    
                # Get the list of indices of this group, excluding
                # the index of the current object. So create a copy
                # of the list and remove the current index
                l = dGroup2Indices[name][:]
                sSameGroup = reduce(lambda x,y: str(x)+" "+str(y), l, "")
                ind = ind + 1

                if len(mesh.vertices)==2:   # Check line
                    min_h = mesh.vertices[0].co[2]
                    if mesh.vertices[1].co[2] < min_h: min_h = mesh.vertices[1].co[2]
                    f.write("    <check-line%sp1=\"%f %f\" p2=\"%f %f\"\n" %
                            (kind, mesh.vertices[0].co[0], mesh.vertices[0].co[1],
                             mesh.vertices[1].co[0], mesh.vertices[1].co[1]   )  )

                    f.write("                min-height=\"%f\" same-group=\"%s\"/>\n" \
                            % (min_h, sSameGroup.strip())  )
                else:
                    radius = 0
                    for v in mesh.vertices:
                        r = (obj.location[0]-v[0])*(obj.location[0]-v[0]) + \
                            (obj.location[1]-v[1])*(obj.location[1]-v[1]) + \
                            (obj.location[2]-v[2])*(obj.loc[2]-v[2])
                        if r > radius:
                            radius = r
                    
                    radius = math.sqrt(radius)
                    inner_radius = getProperty(obj, "inner_radius", radius)
                    color = getProperty(obj, "color", "255 120 120 120")
                    f.write("    <check-sphere%sxyz=\"%f %f %f\" radius=\"%f\"\n" % \
                            (kind, obj.location[0], obj.location[2], obj.location[1], radius) )
                    f.write("                  same-group=\"%s\"\n"%sSameGroup.strip())
                    f.write("                  inner-radius=\"%f\" color=\"%s\"/>\n"% \
                            (inner_radius, color) )
            except Exception as exc:
                log_error("Error exporting checkline " + obj.name + ", make sure it is properly formed")
                
                from traceback import format_tb
                print(format_tb(exc.__traceback__)[0])
        f.write("  </checks>\n")
            
    # --------------------------------------------------------------------------
    # Checks if there are any animated textures in any of the objects in the
    # list l.
    def checkForAnimatedTextures(self, lObjects):
        lAnimTextures = []
        for obj in lObjects:
            use_anim_texture = getProperty(obj, "enable_anim_texture", "false")
            if use_anim_texture != 'true': continue
            
            anim_texture = getProperty(obj, "anim_texture", None)
            dx = getProperty(obj, "anim_dx", 0)
            dy = getProperty(obj, "anim_dy", 0)
            lAnimTextures.append( (anim_texture, dx, dy) )
        return lAnimTextures
    
    # --------------------------------------------------------------------------
    # Writes a non-static track object. The objects can be animated or
    # non-animated meshes, and physical or non-physical.
    # Type is either 'movable' or 'nophysics'.
    def writeObject(self, f, sPath, obj):
        name     = getProperty(obj, "name", obj.name)
        if len(name) == 0: name = obj.name
        
        type = getProperty(obj, "type", "X")
        
        if obj.type != "CAMERA":
            if type == "lod_instance":
                b3d_name = None
            else:
                b3d_name = self.exportLocalB3D(obj, sPath, name)

            
        # First kind of object: ipo. There is one or
        # more IPOs define controlling this object.
        # Second kind of object: no ipo, and no physics.
        # So it's a visual-only object. This is exported
        # as an animation object without an IPO attached.
        # -----------------------------------------------
        interact = getProperty(obj, "interaction", "none")
        
        if obj.type=="CAMERA":
            ipo  = obj.animation_data
            self.writeAnimationWithIPO(f, "", obj, ipo, objectType="cutscene_camera")
        # An object that can be moved by the player. This object
        # can not have an IPO, so no need to test this here.
        elif interact=="move":
            ipo      = obj.animation_data
            if ipo and ipo.action:
                log_warning("Movable object %s has an ipo - ipo is ignored." \
                            %obj.name)
            shape = getProperty(obj, "shape", "")
            if not shape:
                log_warning("Movable object %s has no shape - box assumed!" \
                            % obj.name)
                shape="box"
            mass  = getProperty(obj, "mass", 10)
            lodstring = self.getLODString(obj)
            
            type = getProperty(obj, "type", "?")
            
            if type == "lod_instance":
                model_string = ""
            else:
                model_string = "model=\"%s\" " % b3d_name
            
            tangent_string = ""
            if getProperty(obj, "tangents", "false") == "true":
                tangent_string=" tangents=\"true\" "
            
            f.write("  <object type=\"movable\" %s\n"%(getXYZHPRString(obj)))
            f.write("          %sshape=\"%s\" mass=\"%s\"%s%s/>\n"\
                    % (model_string, shape, mass, lodstring, tangent_string))
            
        # Now the object either has an IPO, or is a 'ghost' object.
        # Either can have an IPO. Even if the objects don't move
        # they are saved as animations (with 0 IPOs).
        elif interact=="ghost" or interact=="none":
            
            ipo      = obj.animation_data
            
            # In objects with skeletal animations the actual armature (which
            # is a parent) contains the IPO. So check for this:
            if not ipo or not ipo.action:
                parent = obj.parent
                if parent:
                    ipo = parent.animation_data
            self.writeAnimationWithIPO(f, b3d_name, obj, ipo)
            
        elif interact=="static" or interact=="reset":            
            ipo      = obj.animation_data
            # In objects with skeletal animations the actual armature (which
            # is a parent) contains the IPO. So check for this:
            if not ipo or not ipo.action:
                parent = obj.parent
                if parent:
                    ipo = parent.animation_data
            self.writeAnimationWithIPO(f, b3d_name, obj, ipo)
        else:
            log_warning("Unknown interaction '%s' - ignored!"%interact)

    # --------------------------------------------------------------------------
    # Writes all start positions
    def writeStartPositions(self, f, lStart):
        global the_scene
        scene = the_scene
        karts_per_row      = int(getIdProperty(scene, "start_karts_per_row",      2))
        distance_forwards  = float(getIdProperty(scene, "start_forwards_distance",  1.5))
        distance_sidewards = float(getIdProperty(scene, "start_sidewards_distance", 3.0))
        distance_upwards   = float(getIdProperty(scene, "start_upwards_distance",   0.1))
        f.write("  <default-start karts-per-row     =\"%i\"\n"%karts_per_row     )
        f.write("                 forwards-distance =\"%.2f\"\n"%distance_forwards )
        f.write("                 sidewards-distance=\"%.2f\"\n"%distance_sidewards)
        f.write("                 upwards-distance  =\"%.2f\"/>\n"%distance_upwards)
        
        dId2Obj     = {}
        count = 1
        for obj in lStart:
            stktype = getProperty(obj, "type", obj.name).upper()
            id = int(getProperty(obj, "start_index", "-1"))
            if id == "-1":
                log_warning("Invalid start position " + id)

            dId2Obj[id] = obj
        l = dId2Obj.keys()
        
        if len(l) < 4 and getIdProperty(scene, "arena",  "false") == "true":
            log_warning("You should define at least 4 start positions")
        
        #l.sort() # sorting not needed AFAICT, the dictionary keeps the keys sorted
        for i in l:
            f.write("  <start %s/>\n"%getXYZHString(dId2Obj[i]))
                
    # --------------------------------------------------------------------------
    # Writes all special water nodes.
    def writeWaterNodes(self, f, sPath, lWater):
        #start_time = bsys.time()
        print ("Exporting water -->")
        for obj in lWater:
            name     = getProperty(obj, "name",   obj.name )
            if len(name) == 0:
                name = obj.name
            height   = getProperty(obj, "height", None     )
            speed    = getProperty(obj, "speed",  None     )
            length   = getProperty(obj, "length", None     )
            lAnim    = self.checkForAnimatedTextures([obj])
            b3d_name = self.exportLocalB3D(obj, sPath, name)
            s="  <water model=\"%s\" %s" % \
                (b3d_name, getXYZHPRString(obj))
            if height: s="%s height=\"%.2f\""%(s, float(height))
            if speed:  s="%s speed=\"%.2f\"" %(s, float(speed))
            if length: s="%s length=\"%.2f\""%(s, float(length))
            if lAnim:
                f.write("%s>\n" % s)
                self.writeAnimatedTextures(f, lAnim)
                f.write("  </water>\n")
            else:
                f.write("%s/>\n" % s);

        #print bsys.time()-start_time,"seconds."
        
    # --------------------------------------------------------------------------
    # Writes the scene files, which includes all models, animations, and items
    def writeSceneFile(self, sPath, sTrackName, lWater, lTrack, lItems, lObjects, lBillboards,
                       lParticleEmitters, lSoundEmitters, lActionTriggers, lChecks, lSun, mainDriveline,
                       lStart, lEndCameras, lCameraCurves):

        #start_time = bsys.time()
        print("Writing scene file --> \t")

        f = open(sPath+"/scene.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<!-- Generated with script from SVN rev %s -->\n"%getScriptVersion())
        f.write("<scene>\n")

        # Extract all static objects (which will be merged into one
        # bullet objects in stk):
        lStaticObjects = []
        lOtherObjects  = []
        for obj in lObjects:
            type = getProperty(obj, "type", "??")
            interact = getProperty(obj, "interaction", "static")
            #if type == "lod_instance" or type == "lod_model" or type == "single_lod":
            #    interact = "static"
            
            if interact=="static" or interact=="reset":
                
                ipo      = obj.animation_data
                if obj.parent is not None and obj.parent.type=="ARMATURE" and obj.parent.animation_data is not None:
                    ipo = obj.parent.animation_data
                
                # If an static object has an IPO, it will be moved, and
                # can't be merged with the physics model of the track
                # BUT 'reset' objects must NOT be static objects otherwise then we can't detect
                # collisions against it in bullet
                if (ipo and ipo.action) or interact=="reset":
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
        if lSoundEmitters:
            self.writeSoundEmitters(f, lSoundEmitters)
        if lActionTriggers:
            self.writeActionTriggers(f, lActionTriggers)
            
        for obj in lOtherObjects:
            self.writeObject(f, sPath, obj)
        for obj in lBillboards:
            self.writeBillboard(f, obj)
        
        # Subtitles
        subtitles = []
        end_time = bpy.data.scenes[0].frame_end
        for marker in reversed(bpy.data.scenes[0].timeline_markers):
            if marker.name.startswith("subtitle"):
                subtitle_text = bpy.data.scenes[0][marker.name]
                subtitles.insert(0, [marker.frame, end_time - 1, subtitle_text])
            end_time = marker.frame
        
        if len(subtitles) > 0:
            f.write("  <subtitles>\n")
            
            for subtitle in subtitles:
                f.write("        <subtitle from=\"%i\" to=\"%i\" text=\"%s\"/>\n" % (subtitle[0], subtitle[1], subtitle[2]))
            
            f.write("  </subtitles>\n")
        
        
        # Assemble all sky/fog related parameters
        # ---------------------------------------
        if len(lSun) > 1:
            log_warning("Warning: more than one Sun defined, only the first will be used."   )         
        sSky=""
        global the_scene
        scene = the_scene
        s = getIdProperty(scene, "fog", 0)
        if s == "yes" or s == "true":
            sSky="%s fog=\"true\""%sSky
            s=getIdProperty(scene, "fog_color", 0)
            if s: sSky="%s fog-color=\"%s\""%(sSky, s)
            s=getIdProperty(scene, "fog_density", 0)
            if s: sSky="%s fog-density=\"%s\""%(sSky, s)
            s=getIdProperty(scene, "fog_start", 0)
            if s: sSky="%s fog-start=\"%s\""%(sSky, s)
            s=getIdProperty(scene, "fog_end", 0)
            if s: sSky="%s fog-end=\"%s\""%(sSky, s)

        # If there is a sun:
        if len(lSun) > 0:
            sun = lSun[0]
            xyz=sun.location
            sSky="%s xyz=\"%.2f %.2f %.2f\""%(sSky, float(xyz[0]), float(xyz[2]), float(xyz[1]))
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
            
        sky_color=getIdProperty(scene, "sky_color", None)
        if sky_color:
            f.write("  <sky-color rgb=\"%s\"/>\n"%sky_color)

        weather = getIdProperty(scene, "weather", None)
        if weather and weather != "none":
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
                if name=="GHERRING": name="banana"
                if name=="RHERRING": name="item"
                if name=="YHERRING": name="big-nitro"
                if name=="SHERRING": name="small-nitro"
            else:
                if name=="nitro-big": name="big-nitro"
                if name=="nitro_big": name="big-nitro"
                if name=="nitro-small": name="small-nitro"
                if name=="nitro_small": name="small-nitro"

            # Get the position of the item - first check if the item should
            # be dropped on the track, or stay at the position indicated.
            rx,ry,rz = map(lambda x: rad2deg*x, obj.rotation_euler)
            h,p,r    = map(str, map(Round, [rz,rx,ry])  )
            x,y,z    = map(str, map(Round, obj.location )  )
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
                log_warning("No check defined, lap counting will not work properly!")
            self.writeChecks(f, lChecks, mainDriveline)
        
        scene   = the_scene
        sky     = getIdProperty(scene, "sky_type", None)
        # Note that there is a limit to the length of id properties,
        # which can easily be exceeded by 6 sky textures for a full sky box.
        # Therefore also check for sky-texture1 and sky-texture2.
        texture = getIdProperty(scene, "sky_texture", "")
        s       = getIdProperty(scene, "sky_texture1", "")
        if s: texture = "%s %s"%(texture, s)
        s       = getIdProperty(scene, "sky_texture2", "")
        if s: texture = "%s %s"%(texture, s)
        if sky and texture:
            if sky=="dome":
                hori           = getIdProperty(scene, "sky_horizontal",     16  )
                verti          = getIdProperty(scene, "sky_vertical",       16  )
                tex_percent    = getIdProperty(scene, "sky_texture_percent", 0.5)
                sphere_percent = getIdProperty(scene, "sky_sphere_percent",  1.3)
                speed_x        = getIdProperty(scene, "sky_speed_x",         0.0)
                speed_y        = getIdProperty(scene, "sky_speed_y",         0.0)
                f.write("""
  <sky-dome texture=\"%s\"
            horizontal=\"%s\" vertical=\"%s\" 
            texture-percent=\"%s\" sphere-percent=\"%s\"
            speed-x=\"%s\" speed-y=\"%s\" />
""" %(texture, hori, verti, tex_percent, sphere_percent, speed_x, speed_y))
            elif sky=="box":
                lTextures = [getIdProperty(scene, "sky_texture2", ""),
                             getIdProperty(scene, "sky_texture3", ""),
                             getIdProperty(scene, "sky_texture4", ""),
                             getIdProperty(scene, "sky_texture5", ""),
                             getIdProperty(scene, "sky_texture6", ""),
                             getIdProperty(scene, "sky_texture1", "")]
                f.write("  <sky-box texture=\"%s\"/>\n" % \
                            " ".join(lTextures))
                
        camera_far  = getIdProperty(scene, "camera_far", ""             )
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
                    log_warning ("Unknown camera type %s - ignored." % type)
                    continue
                xyz = "%f %f %f" % (i.location[0], i.location[2], i.location[1])
                start = getProperty(i, "start", 5)
                f.write("    <camera type=\"%s\" xyz=\"%s\" distance=\"%s\"/>\n"%
                        (type, xyz, start) )
            f.write("  </end-cameras>\n")

        # Write camera curves (unused atm)
        self.writeCurves(f, lCameraCurves)
        f.write("</scene>\n")
        f.close()
        #print bsys.time()-start_time,"seconds"

    def __init__(self, sFilename):
        self.dExportedObjects = {}
        
        # Collect the different kind of meshes this exporter handles
        # ----------------------------------------------------------
        lObj                 = bpy.data.objects      # List of all objects
        lWater               = []                    # List of all water objects
        lTrack               = []                    # All main track objects
        lDrivelines          = []                    # All drivelines
        found_main_driveline = False
        lItems               = []                    # All track items
        lEndCameras          = []                    # List of all end cameras
        lCameraCurves        = []                    # Camera curves (unused atm)
        lObjects             = []                    # All special objects
        lBillboards          = []                    # All billboards
        lParticleEmitters    = []                    # All particle emitters
        lSoundEmitters       = []
        lActionTriggers      = []
        lChecks              = []                    # All check structures
        lSun                 = []
        lStart               = []                    # All start positions
        
        for obj in lObj:
            # Try to get the supertuxkart type field. If it's not defined,
            # use the name of the objects as type.
            stktype = getProperty(obj, "type", "").strip().upper()
            
            #print("Checking object",obj.name,"which has type",stktype)

            # Make it possible to ignore certain objects, e.g. if you keep a
            # selection of 'templates' (ready to go models) around to be
            # copied into the main track.
            if stktype=="IGNORE": continue
            
            
            if obj.type=="EMPTY":
                # For backward compatibility test for the blender name
                # in case that there is no type property defined. This makes
                # it easier to port old style tracks without having to
                # add the property for all items.
                stktype = getProperty(obj, "type", obj.name).upper()
                # Check for old and new style names
                if stktype[:8] in ["GHERRING", "RHERRING", "YHERRING", "SHERRING"] \
                   or stktype[: 6]== "BANANA"     or stktype[:4]=="ITEM"           \
                   or stktype[:11]=="NITRO-SMALL" or stktype[:9]=="NITRO-BIG"      \
                   or stktype[:11]=="NITRO_SMALL" or stktype[:9]=="NITRO_BIG"      \
                   or stktype[:11]=="SMALL-NITRO" or stktype[:9]=="BIG-NITRO"      \
                   or stktype[: 6]=="ZIPPER":
                    lItems.append(obj)
                    continue
                elif stktype[:5]=="START":
                    lStart.append(obj)
                    continue
                elif stktype=="PARTICLE_EMITTER":
                    lParticleEmitters.append(obj)
                    continue
                elif stktype=="SFX_EMITTER":
                    lSoundEmitters.append(obj)
                    continue
                elif stktype=="ACTION_TRIGGER":
                    lActionTriggers.append(obj)
                    continue
                else:
                    log_warning("Empty '%s' has type '%s' which is not valid - ignored."%(obj.name, stktype))
            elif obj.type=="CURVE":
                # Only append camera, other curves will be handled in animations
                if stktype[:6]=="CAMERA": lCameraCurves.append(obj)
            elif obj.type=="LAMP" and stktype == "SUN":
                lSun.append(obj)
                continue
            elif obj.type=="CAMERA" and stktype in ['fixed', 'ahead']:
                lEndCameras.append(obj)
                continue
            elif obj.type=="CAMERA" and stktype == 'CUTSCENE_CAMERA':
                lObjects.append(obj)
                continue
            elif obj.type!="MESH":
                #print "Non-mesh object '%s' (type: '%s') is ignored!"%(obj.name, stktype)
                continue
            
            if stktype=="WATER":
                lWater.append(obj)
            elif stktype=="CHECK" or stktype=="LAP" or stktype=="CANNONSTART":
                lChecks.append(obj)
            # Check for new drivelines
            elif stktype=="MAIN-DRIVELINE" or \
                 stktype=="MAINDRIVELINE"  or \
                 stktype=="MAINDL":
                # Main driveline must be the first entry in the list
                lDrivelines.insert(0, Driveline(obj, 1))
                found_main_driveline = True
            elif stktype=="DRIVELINE":
                lDrivelines.append(Driveline(obj, 0))
            elif stktype=="OBJECT" or stktype=="SPECIAL_OBJECT" or stktype=="LOD_MODEL" or stktype=="LOD_INSTANCE" or stktype=="SINGLE_LOD":
                lObjects.append(obj)
            # for billboard
            elif stktype=="BILLBOARD":
                lBillboards.append(obj)
            elif stktype=="CANNONEND":
                pass # cannon ends are handled with cannon start objects
            elif stktype=="NONE":
                lTrack.append(obj)
            else:
                s = getProperty(obj, "type", None)
                if s:
                    log_warning("object " + obj.name + " has type property '%s', which is not supported.\n"%s)
                lTrack.append(obj)

        is_arena = getIdProperty(bpy.data.scenes[0], "arena",      "n"            )
        is_cutscene = getIdProperty(bpy.data.scenes[0], "cutscene",  "false") == "true"
        if not found_main_driveline and not is_arena and not is_cutscene:
            log_warning("Main driveline missing, using first driveline as main!")
            
        # Now export the different parts: track file
        # ------------------------------------------
        sBase = os.path.basename(sFilename)
        sPath = os.path.dirname(sFilename)
        self.writeTrackFile(sPath, sBase)
    
        # Quads and mapping files
        # -----------------------
        global the_scene
        scene    = the_scene
        is_arena = getIdProperty(scene, "arena", "n")
        if not is_arena: is_arena="n"
        is_arena = not (is_arena[0]=="n" or is_arena[0]=="N" or \
                        is_arena[0]=="f" or is_arena[0]=="F"     )
                        
        if not is_arena and not is_cutscene:
            self.writeQuadAndGraph(sPath, lDrivelines, lEndCameras)
        #start_time = bsys.time()

        sTrackName = sBase+"_track.b3d"

        # FIXME: silly and ugly hack, the list of objects to export is passed through
        #        a custom scene property
        scene.obj_list = lTrack
        
        if 'b3d_export' not in dir(bpy.ops.screen):
            log_error("Cannot find the B3D exporter, make sure you installed it properly")
            return
        
        bpy.ops.screen.b3d_export(localsp=False, mipmap=True, lights=False, vcolors=True,
                                  vnormals=True, cameras=False, filepath=sPath+"/"+sTrackName,
                                  overwrite_without_asking=True)
        scene.obj_list = []
        
        #write_b3d_file(sFilename+"_track.b3d")
        
        #b3d_export.write_b3d_file(sFilename+"_track.b3d", lTrack)
        #print bsys.time()-start_time,"seconds."
    
        # scene file
        # ----------
        if len(lDrivelines)==0:
            lDrivelines=[None]
        self.writeSceneFile(sPath, sTrackName, lWater, lTrack, lItems,
                            lObjects, lBillboards, lParticleEmitters, lSoundEmitters, lActionTriggers,
                            lChecks, lSun, lDrivelines[0], lStart, lEndCameras, lCameraCurves)
        # materials file
        # ----------
        if 'stk_material_exporter' not in dir(bpy.ops.screen):
            log_error("Cannot find the material exporter, make sure you installed it properly")
            return
        
        bpy.ops.screen.stk_material_exporter(filepath=sPath)

        import datetime
        now = datetime.datetime.now()
        log_info("Export completed on " + now.strftime("%Y-%m-%d %H:%M"))
        print("Finished.")

# ==============================================================================
def savescene_callback(sFilename):
    global log
    log = []
    
    exporter = TrackExport(sFilename)

thelist = []
def getlist(self):
    global thelist
    return thelist
def setlist(self, value):
    global thelist
    thelist = value
     

# ==== EXPORT OPERATOR ====
class STK_Track_Export_Operator(bpy.types.Operator):
    bl_idname = ("screen.stk_track_export")
    bl_label = ("SuperTuxKart Track Export")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        if bpy.context.mode != 'OBJECT':
            self.report({'ERROR'}, "You must be in object mode")
            log_error("You must be in object mode")
            return {'FINISHED'}
        
        if 'is_stk_track' not in context.scene or context.scene['is_stk_track'] != 'true':
            log_error("Not a STK track!")
            return {'FINISHED'}
        
        blend_filepath = context.blend_data.filepath
        if not blend_filepath:
            blend_filepath = "Untitled"
        else:
            import os
            blend_filepath = os.path.splitext(blend_filepath)[0]
        self.filepath = blend_filepath
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            self.report({'ERROR'}, "You msut be in object mode")
            return {'FINISHED'}
        
        if self.filepath == "" or 'is_stk_track' not in context.scene or context.scene['is_stk_track'] != 'true':
            return {'FINISHED'}

        global operator
        operator = self
        
        # FIXME: silly and ugly hack, the list of objects to export is passed through
        #        a custom scene property
        bpy.types.Scene.obj_list = property(getlist, setlist)
        
        savescene_callback(self.filepath)
        return {'FINISHED'}


class STK_Copy_Log_Operator(bpy.types.Operator):
    bl_idname = ("screen.stk_track_copy_log")
    bl_label = ("Copy Log")

    def execute(self, context):
        global log
        context.window_manager.clipboard = str(log)
        return {'FINISHED'}

class STK_Clean_Log_Operator(bpy.types.Operator):
    bl_idname = ("screen.stk_track_clean_log")
    bl_label = ("Clean Log")

    def execute(self, context):
        global log
        log = []
        print("Log cleaned")
        return {'FINISHED'}

# ==== PANEL ====
class STK_Track_Exporter_Panel(bpy.types.Panel):
    bl_label = "Track Exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
    def draw(self, context):
        global the_scene
        the_scene = context.scene
        
        layout = self.layout
        
        # ==== Types group ====
        row = layout.row()
        
        row.operator("screen.stk_track_export", "Export", icon='BLENDER')
        
        if bpy.context.mode != 'OBJECT':
            row.enabled = False
        
        # ==== Output Log ====
        
        global log
        
        if len(log) > 0:
            box = layout.box()
            row = box.row()
            row.label("Log")
            
            for type,msg in log:
                if type == 'INFO':
                  row = box.row()
                  row.label(msg, icon='INFO')
                elif type == 'WARNING':
                  row = box.row()
                  row.label("WARNING: " + msg, icon='ERROR')
                elif type == 'ERROR':
                  row = box.row()
                  row.label("ERROR: " + msg, icon='CANCEL')
            
            row = box.row()
            row.operator("screen.stk_track_clean_log", text="Clear Log", icon='X')
            row.operator("screen.stk_track_copy_log",  text="Copy Log", icon='COPYDOWN')


# Add to a menu
def menu_func_export(self, context):
    global the_scene
    the_scene = context.scene
    self.layout.operator(STK_Track_Export_Operator.bl_idname, text="STK Track")

def register():
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()

