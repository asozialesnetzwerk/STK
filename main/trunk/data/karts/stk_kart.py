#!BPY

#(setq tab-width 4)
#(setq py-indent-offset `4)

"""
Name: 'STK Kart Exporter (.irrkart)...'
Blender: 248a
Group: 'Export'
Tooltip: 'Export a SuperTuxKart kart'
"""
__author__ = ["Joerg Henrichs (hiker)/xapantu"]
__url__ = ["supertuxkart.sourceforge.net"]
__version__ = "$Revision$"
__bpydoc__ = """\
"""

# Copyright (C) 2009-2010 Joerg Henrichs / Xapantu

#If you get an error here, it might be
#because you don't have Python installed.
import Blender
import BPyMesh
import sys,os,os.path,struct,math,string,re
import b3d_export

from Blender import Mathutils
from Blender.Mathutils import *
from Blender import Draw,BGL

ARG = __script__['arg']

# Assign event numbers to buttons
eventQuit = 0
eventExport = 1
eventkartName = 2
eventkartGroup = 4
eventkartShadow = 5
eventkartIcon = 6
eventBrowse = 7
eventBrowseShadow = 8
eventBrowseIcon = 9
eventPath = 10
eventSound = 11
kartName =Draw.Create("")
kartGroup = Draw.Create("standard")
scene =""
targetShadow =""
targetShadowAll =""
targetIcon =""
targetIconAll =""
kartShadow = Draw.Create("")
kartIcon = Draw.Create("")
pathExport =""
pathExportTxt = Draw.Create("")
pathExportShadow =""
pathExportIcon =""
kartSoundHorn = Draw.Create("")
kartSoundCrash = Draw.Create("")
kartSoundShoot = Draw.Create("")
kartSoundWin = Draw.Create("")
kartSoundExplode = Draw.Create("")
kartSoundGoo = Draw.Create("")
kartSoundPass = Draw.Create("")
kartSoundZiper = Draw.Create("")
kartSoundName = Draw.Create("")
kartSoundAttach = Draw.Create("")


# ------------------------------------------------------------------------------
# Returns a game logic property
def getProperty(obj, name, default=""):
    try:
        return obj.getProperty(name).getData()
    except:
        return default
# ------------------------------------------------------------------------------


def getScriptVersion():
    m = re.search('(\d+)', __version__)
    if m:
            return str(m.group(0))
    return "0.1"

def gui():
    global eventPush, eventQuit, kartName, eventkartName, eventkartGroup, kartGroup, scene, eventfileShadow, eventfileIcon, kartShadow, kartIcon, eventBrowseIcon, eventBrowseShadow, eventExport, pathExportTxt, eventPath,kartSoundHorn, kartSoundCrash, kartSoundShoot, kartSoundWin, kartSoundExplode, kartSoundGoo, kartSoundPass, kartSoundZiper, kartSoundName, kartSoundAttach, eventSound
    BGL.glClearColor(0.4,0.5,0.8,1)
    BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)
    BGL.glColor3f(1,1,1)
    scene = Blender.Scene.getCurrent()
    BGL.glRasterPos2i(10, 250)
    try:
            kartName.val = scene.properties['name']
            print "getting kartName",kartName.val
            kartGroup.val = scene.properties['group']
            kartIcon.val = scene.properties['icon']
            kartShadow.val = scene.properties['shadow']
            pathExportTxt.val = scene.properties['kartPath']
            kartSoundHorn.val = scene.properties['kartSoundHorn']
            kartSoundCrash.val = scene.properties['kartSoundCrash']
            kartSoundShoot.val = scene.properties['kartSoundShoot']
            kartSoundWin.val = scene.properties['kartSoundWin']
            kartSoundExplode.val = scene.properties['kartSoundExplode']
            kartSoundGoo.val = scene.properties['kartSoundGoo']
            kartSoundPass.val = scene.properties['kartSoundPass']
            kartSoundZiper.val = scene.properties['kartSoundZiper']
            kartSoundName.val = scene.properties['kartSoundName']
            kartSoundAttach.val = scene.properties['kartSoundAttach']
    except:
            scene.properties['name'] = kartName.val
            print "setting except kartName",kartName.val
            scene.properties['group'] = kartGroup.val
            scene.properties['icon'] = kartIcon.val
            scene.properties['shadow'] = kartShadow.val
            scene.properties['kartPath'] = pathExportTxt.val
            scene.properties['kartSoundHorn'] = kartSoundHorn.val
            scene.properties['kartSoundCrash'] = kartSoundCrash.val
            scene.properties['kartSoundShoot'] = kartSoundShoot.val
            scene.properties['kartSoundWin'] = kartSoundWin.val
            scene.properties['kartSoundExplode'] = kartSoundExplode.val
            scene.properties['kartSoundGoo'] = kartSoundGoo.val
            scene.properties['kartSoundPass'] = kartSoundPass.val
            scene.properties['kartSoundZiper'] = kartSoundZiper.val
            scene.properties['kartSoundName'] = kartSoundName.val
            scene.properties['kartSoundAttach'] = kartSoundAttach.val

    Draw.Text("Kart Exporter for STK Irrlicht version")
    button = Draw.Button("Quit", eventQuit, 5, 0, 160, 20, "Quit")
    buttonexport = Draw.Button("Export", eventExport, 5, 30, 160, 20, "export")
    buttonPath = Draw.Button("Select Path", eventBrowse, 315, 90, 160, 20, "path")
    pathExportTxt = Draw.String("Path : ", eventPath, 5, 80, 310, 20, pathExportTxt.val, 320, "Path")
    kartShadow = Draw.String("Kart Shadow : ", eventkartShadow, 5, 140, 310, 20, kartShadow.val, 320, "Kart Shadow")
    kartIcon = Draw.String("Kart Icon : ", eventkartIcon, 5, 120, 310, 20, kartIcon.val, 320, "Kart Icon")
    buttonicon = Draw.Button("Select an icon", eventBrowseIcon, 315, 120, 160, 20, "icon")
    buttonShadow = Draw.Button("Select a shadow", eventBrowseShadow, 315, 140, 160, 20, "shadow")
    kartName = Draw.String("Kart Name : ", eventkartName, 5, 200, 310, 20, kartName.val, 320, "Kart Name")
    kartGroup = Draw.String("Kart Group : ", eventkartGroup, 5, 160, 310, 20, kartGroup.val, 320, "Kart Group")
    kartSoundHorn = Draw.String("Sound Horn : ", eventSound, 500, 0, 310, 20, kartSoundHorn.val, 320, "Kart Sounds")
    kartSoundCrash = Draw.String("Sound Crash : ", eventSound, 500, 30, 310, 20, kartSoundCrash.val, 320, "Kart Sounds")
    kartSoundShoot = Draw.String("Sound Shoot : ", eventSound, 500, 60, 310, 20, kartSoundShoot.val, 320, "Kart Sounds")
    kartSoundWin = Draw.String("Sound Win : ", eventSound, 500, 90, 310, 20, kartSoundWin.val, 320, "Kart Sounds")
    kartSoundExplode = Draw.String("Sound Explode : ", eventSound, 500, 120, 310, 20, kartSoundExplode.val, 320, "Kart Sounds")
    kartSoundGoo = Draw.String("Sound Goo : ", eventSound, 500, 150, 310, 20, kartSoundGoo.val, 320, "Kart Sounds")
    kartSoundPass = Draw.String("Sound Pass : ", eventSound, 500, 180, 310, 20, kartSoundPass.val, 320, "Kart Sounds")
    kartSoundZiper = Draw.String("Sound Ziper : ", eventSound, 500, 210, 310, 20, kartSoundZiper.val, 320, "Kart Sounds")
    kartSoundName = Draw.String("Sound Name: ", eventSound, 500, 240, 310, 20, kartSoundName.val, 320, "Kart Sounds")
    kartSoundAttach = Draw.String("Sound Attach : ", eventSound, 500, 270, 310, 20, kartSoundAttach.val, 320, "Kart Sounds")
    
def event(evt, val):
    if evt == Draw.ESCKEY:
        Draw.Exit()
             
def butt_evt(evt):  # function that handles keyboard and mouse events
    global eventQuit, targetShadow
    if evt == eventQuit:
        Draw.Exit()
        print "The Quit button was pushed."
    if evt == eventExport:
        saveKart()
        print "The Export button was pushed"
    if evt == eventBrowse:
        Blender.Window.FileSelector(selectPath,"Export STK kart", Blender.sys.makename(ext = ".xml"))
    if evt == eventBrowseShadow:
        Blender.Window.FileSelector(selectPathShadow,"Select a shadow", Blender.sys.makename(ext = ".png"))
    if evt == eventBrowseIcon:
        Blender.Window.FileSelector(selectPathIcon,"Select an icon", Blender.sys.makename(ext = ".png"))             

def selectPath(filename):
    global scene
    scene.properties['kartPath'] = Blender.sys.dirname(filename)
    print filename

def selectPathShadow(filename):
    global scene
    scene.properties['shadow']  =   Blender.sys.basename(filename)
    print filename

def selectPathIcon(filename):
    global scene
    scene.properties['icon'] = Blender.sys.basename(filename)
    print filename

# ------------------------------------------------------------------------------
def saveWheels(f, lWheels, path):
    if len(lWheels)!=4:
        print "Warning - %d wheels specified" % len(lWheels)

    lWheelNames = ("wheel-front-right.b3d", "wheel-front-left.b3d",
                   "wheel-rear-right.b3d",  "wheel-rear-left.b3d"   )
    lSides      = ('front-right', 'front-left', 'rear-right', 'rear-left')

    f.write('  <wheels>\n')
    for wheel in lWheels:
        name = wheel.name.upper()
        # If old stylen names are given, use them to determine
        # which wheel is which.
        if name=="WHEELFRONT.R":
            index=0
        elif name=="WHEELFRONT.L":
            index=1
        elif name=="WHEELREAR.R":
            index=2
        elif name=="WHEELREAR.L":
            index=3
        else:
            # Otherwise the new style 'type=wheel' is used. Use the x and
            #  y coordinates to determine where the wheel belongs to.
            x = wheel.LocX
            y = wheel.LocY
            index = 0
            if y<0:
                index=index+2
            if x>0: index=index+1
        
        f.write('    <%s position = "%f %f %f"\n' \
                % ( lSides[index], wheel.LocX, wheel.LocZ, wheel.LocY))
        f.write('                 model    = "%s"       />\n'%lWheelNames[index])
        lOldPos = Mathutils.Vector(wheel.LocX,wheel.LocY,wheel.LocZ)
        wheel.setLocation(0, 0, 0)
        b3d_export.write_b3d_file(Blender.sys.join(path, lWheelNames[index]),
                                  [wheel])
        wheel.setLocation(lOldPos)
                                  
    f.write('  </wheels>\n')
    f.write('</kart>\n')

# ------------------------------------------------------------------------------
# Saves any defined animations to the kart.xml file.
def saveAnimations(f):
    # search for animation
    lAnims = []
    for i in range(1, 300):
        try:
            marker = scene.timeline.getName(i)
            if  marker in \
               ["straight", "right", "left", "start-winning", "end-winning",
                "start-losing", "end-losing", "start-explosion",
                "end-explosion"]:
                lAnims.append( (marker, i) )
        except:
            pass

    if lAnims:
        f.write('  <animations %s = "%s"' % (lAnims[0][0], lAnims[0][1]))
        for (marker, frame) in lAnims[1:]:
                f.write('\n              %s = "%s"'%(marker, frame))
        f.write('/>\n')
    
# ------------------------------------------------------------------------------
# Code for saving kart specific sounds. This is not yet supported, but for
# now I'll leave the code in plase
def saveSounds(f):
    return

    lSounds = []
    if kartSoundHorn.val  != "": lSounds.append( ("horn-sound", kartSoundHorn.val ))
    if kartSoundCrash.val != "": lSounds.append( ("crash-sound",kartSoundCrash.val))
    if kartSoundShoot.val != "" :lSounds.append( ("shoot-sound",kartSoundShoot.val))
    if kartSoundWin.val   != "" :lSounds.append( ("win-sound",  kartSoundWin.val  ))
    if kartSoundExplode.val!="" :lSounds.append( ("explode-sound",kartSoundExplode.val))
    if kartSoundGoo.val   != "" :lSounds.append( ("goo-sound",  kartSoundGoo.val))
    if kartSoundPass.val  != "" :lSounds.append( ("pass-sound", kartSoundPass.val))
    if kartSoundZiper.val != "" :lSounds.append( ("zipper-sound",kartSoundZiper.val))
    if kartSoundName.val  != "" :lSounds.append( ("name-sound", kartSoundName.val))
    if kartSoundAttach.val!= "" :lSounds.append( ("attach-sound",kartSoundAttach.val))

    if lSounds:
        f.write('  <sounds %s = "%s"'%(lSounds[0][0], lSounds[0][1]))
        for (name, sound) in lSounds[1:]:
            f.write('\n          %s = "%s"'%(name, sound))
        f.write('/>\n')
    
# ------------------------------------------------------------------------------
def saveKart():
    global kartName, kartGroup, scene, kartIcon, kartShadow, pathExportTxt
    path = pathExportTxt.val
    kart_name = kartName.val
    print "saving",kartName.val

    global flag_stack
    b3d_export.flag_stack = []
    b3d_export.flag_stack.append(0) #All Objects
    b3d_export.flag_stack.append(1) #Selected Only
    b3d_export.flag_stack.append(1) #Vertex Normals
    b3d_export.flag_stack.append(1) #Vertex Colors
    b3d_export.flag_stack.append(0) #Cameras
    b3d_export.flag_stack.append(0) #Lights
    b3d_export.flag_stack.append(1) #Mipmap

    # Get the kart and all wheels
    # ---------------------------
    lObj    = Blender.Object.Get()
    lWheels = []
    lKart   = []
    for obj in lObj:
        stktype = getProperty(obj, "type", "").strip().upper()
        name    = obj.name.upper()
        if stktype=="WHEEL":
            lWheels.append(obj)
        elif stktype=="IGNORE":
            pass
        # For backward compatibility
        elif name in ["WHEELFRONT.R","WHEELFRONT.L", \
                      "WHEELREAR.R", "WHEELREAR.L"     ]:
            lWheels.append(obj)
        else:
            lKart.append(obj)


    # Write the xml file
    # ------------------
    if kartShadow.val == "":
        kartShadow.val = kart_name.lower() + "_shadow.png"
    if kartIcon.val == "":
        kartIcon.val = kart_name.lower() + "_icon.png"
    if kartGroup.val == "":
        kartGroup.var = "default"
        
    f = open(Blender.sys.join(path,"kart.xml"), 'wb')    
    f.write('<!-- Generated with script from SVN rev %s -->\n'\
            % getScriptVersion())
    rgb = (0.7, 0.0, 0.0)
    f.write('<?xml version="1.0"?>\n')
    f.write('<kart name        = "%s"\n' % kartName.val)
    f.write('      version     = "2"\n' )
    f.write('      model-file  = "%s.b3d"\n' % name)
    f.write('      icon-file   = "%s"\n' % kartIcon.val)
    f.write('      shadow-file = "%s"\n' % kartShadow.val)
    f.write('      groups      = "%s"\n' % kartGroup.val)
    f.write('      rgb         = "%f %f %f" >\n' % rgb)
    
    saveSounds(f)
    saveAnimations(f)
    saveWheels(f, lWheels, path)
    f.write('</kart>\n')
    f.close()

    # Export the actual kart (the wheels are already exported in saveWheels)
    b3d_export.write_b3d_file(Blender.sys.join(path, kartName.val + ".b3d"), lKart)
    
    print "writing back",kartName.val
    scene.properties['name'] = kartName.val
    scene.properties['group'] = kartGroup.val
    scene.properties['icon'] = kartIcon.val
    scene.properties['shadow'] = kartShadow.val
    scene.properties['kartPath'] = pathExportTxt.val
    scene.properties['kartSoundHorn'] = kartSoundHorn.val
    scene.properties['kartSoundCrash'] = kartSoundCrash.val
    scene.properties['kartSoundShoot'] = kartSoundShoot.val
    scene.properties['kartSoundWin'] = kartSoundWin.val
    scene.properties['kartSoundExplode'] = kartSoundExplode.val
    scene.properties['kartSoundGoo'] = kartSoundGoo.val
    scene.properties['kartSoundPass'] = kartSoundPass.val
    scene.properties['kartSoundZiper'] = kartSoundZiper.val
    scene.properties['kartSoundName'] = kartSoundName.val
    scene.properties['kartSoundAttach'] = kartSoundAttach.val
    Draw.PupMenu("Successful")


Draw.Register(gui, event, butt_evt)
