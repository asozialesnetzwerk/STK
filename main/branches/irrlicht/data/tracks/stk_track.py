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

def savescene_callback(filename):
    global flag_stack
    b3d_export.flag_stack = []
    b3d_export.flag_stack.append(0) #All Objects
    b3d_export.flag_stack.append(0) #Selected Only
    b3d_export.flag_stack.append(0) #Vertex Normals
    b3d_export.flag_stack.append(0) #Vertex Colors
    b3d_export.flag_stack.append(0) #Cameras
    b3d_export.flag_stack.append(0) #Lights
    lObj = Blender.Object.Get()
    lWater = []
    lTrack = []
    for obj in lObj:
        if obj.type!="Mesh": continue
        try:
            p = obj.getProperty("type")
            type = p.getData()
            if type=="water":
                lWater.append(obj)
            else:
                lTrack.append(obj)
        except:
            lTrack.append(obj)
    sBase = os.path.basename(filename)
    f = open(filename+".irrtrack", 'wb')
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
</track>
""" % (sBase, sBase))
    f.close()
    f = open(filename+".scene", 'wb')
    f.write("""<?xml version="1.0"?>\n""")
    f.write("""<scene>\n""")
    f.write("""  <track model="%s_track.b3d" x="0" y="0" z="0"/>\n"""%sBase)
    b3d_export.write_b3d_file(filename+"_track.b3d", lTrack)
    if lWater:
        f.write("""  <waster model="%s_water.b3d" x="0" y="0" z="0"/>\n"""%sBase)
        b3d_export.write_b3d_file(filename+"_water.b3d", lWater)
    f.write("</scene>""")
    f.close() 


#Main
def main():
    tmp_filename = Blender.sys.makename(ext = ".track")
    Blender.Window.FileSelector(savescene_callback,"Export STK track",tmp_filename)

if __name__ == "__main__":
    main()
