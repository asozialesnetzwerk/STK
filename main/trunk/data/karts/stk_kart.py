#!BPY

#(setq tab-width 4)
#(setq py-indent-offset `4)

"""
Name: 'STK Kart Exporter (.irrkart)...'
Blender: 248a
Group: 'Export'
Tooltip: 'Export a SuperTuxKart kart'
"""
__author__  = ["Joerg Henrichs (hiker)/xapantu"]
__url__     = ["supertuxkart.sourceforge.net"]
__version__ = "$Revision$"
__bpydoc__  = """\
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


# Assign event numbers to buttons
event_quit          =  0
event_export        =  1
event_kart_name     =  2
event_color         =  3
event_kart_group    =  4
event_kart_shadow   =  5
event_kart_icon     =  6
event_browse        =  7
event_browse_shadow =  8
event_browse_icon   =  9
event_path          = 10
event_sound         = 11
event_kart_map_icon = 12
event_browse_map_icon=13
event_center_shift  = 14
event_engine_sfx    = 15
event_browse_engine_sfx = 16
target_map_icon     = ""
path_export         = ""
kart_name           = Draw.Create("")
kart_color          = Draw.Create("")
kart_group          = Draw.Create("")
kart_shadow         = Draw.Create("")
kart_icon           = Draw.Create("")
kart_map_icon       = Draw.Create("")
kart_engine_sfx     = Draw.Create("")
path_export_text    = Draw.Create("")
kart_sound_horn     = Draw.Create("")
kart_sound_crash    = Draw.Create("")
kart_sound_shoot    = Draw.Create("")
kart_sound_win      = Draw.Create("")
kart_sound_explode  = Draw.Create("")
kart_sound_goo      = Draw.Create("")
kart_sound_pass     = Draw.Create("")
kart_sound_zipper   = Draw.Create("")
kart_sound_name     = Draw.Create("")
kart_sound_attach   = Draw.Create("")
center_shift        = Draw.Create("")

# ------------------------------------------------------------------------------
# Returns a game logic property
def getProperty(obj, name, default=""):
    try:
        return obj.getProperty(name).getData()
    except:
        return default
# ------------------------------------------------------------------------------
# Gets an id property of an objects, returning the default if the id property
# is not set.
def getIdProperty(obj, name, default=""):
    try:
        return obj.properties[name]
    except:
        if default!=None:
            obj.properties[name]=default
    return default

# ------------------------------------------------------------------------------
# Returns the version of this script
def getScriptVersion():
    m = re.search('(\d+)', __version__)
    if m:
            return str(m.group(0))
    return "0.1"

# ------------------------------------------------------------------------------
def gui():
    global eventPush, event_quit, kart_name, event_kart_name, event_color,              \
           event_kart_group, kart_group, event_kart_map_icon, event_browse_map_icon,    \
           kart_shadow, kart_icon, kart_color, event_browse_icon, event_browse_shadow,  \
           event_export, path_export_text, event_path,kart_sound_horn, kart_sound_crash,\
           kart_sound_shoot, kart_sound_win, kart_sound_explode, kart_sound_goo,        \
           kart_sound_pass, kart_sound_zipper, kart_sound_name, kart_sound_attach,      \
           event_sound, kart_map_icon, center_shift, kart_engine_sfx
    
    BGL.glClearColor(0.4,0.5,0.8,1)
    BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)
    BGL.glColor3f(1,1,1)
    scene = Blender.Scene.GetCurrent()
    BGL.glRasterPos2i(10, 250)

    
    Draw.Text("Kart Exporter for STK Irrlicht version")
    button             = Draw.Button("Quit",             event_quit,          5, 0,
                                     160, 20, "Quit")
    button_export      = Draw.Button("Export",           event_export,        5, 30,
                                     160, 20, "export")


    line = 230
    kart_name          = Draw.String("Kart Name : ",     event_kart_name,     5,line,
                                     310, 20, kart_name.val, 320, "Kart Name")
    line = line - 20
    kart_color         = Draw.String("Color : ",         event_color,         5,line,
                                     310, 20, kart_color.val, 320, "Kart Color")
    
    line = line - 20
    kart_group         = Draw.String("Kart Group : ",    event_kart_group,    5,line,
                                     310, 20, kart_group.val, 320, "Kart Group")
    line = line - 20
    center_shift       = Draw.String("Center-shift : ",  event_center_shift,  5,line,
                                     310, 20, center_shift.val, 320, "Center Shift")
    line = line - 20
    button_shadow      = Draw.Button("Select a shadow",  event_browse_shadow,315,line,
                                     160, 20, "shadow")
    kart_shadow        = Draw.String("Kart Shadow : ",   event_kart_shadow,   5, line,
                                     310, 20, kart_shadow.val, 320, "Kart Shadow")
    line = line - 20
    kart_icon          = Draw.String("Kart Icon : ",     event_kart_icon,     5,line,
                                     310, 20, kart_icon.val, 320, "Kart Icon")
    button_icon        = Draw.Button("Select an icon",   event_browse_icon, 315,line,
                                     160, 20, "icon")
    line = line - 20
    kart_map_icon      = Draw.String("Minimap Icon : ",     event_kart_map_icon,5,line,
                                     310, 20, kart_map_icon.val, 320, "Minimap Icon")
    button_map_icon    = Draw.Button("Select a map icon",event_browse_map_icon,315,line,
                                     160, 20, "icon")
    line = line - 20
    kart_engine_sfx    = Draw.String("Engine SFX : ",     event_engine_sfx,5,line,
                                     310, 20, kart_engine_sfx.val, 320, "Engine SFX")
    button_engine_sfx  = Draw.Button("Select engine SFX",event_browse_engine_sfx,315,line,
                                     160, 20, "Engine SFX")
    line = line - 20
    
    path_export_text   = Draw.String("Path : ",          event_path,          5, line,
                                     310, 20, path_export_text.val, 320, "Path")
    buttonPath         = Draw.Button("Select Path",      event_browse,      315, line,
                                     160, 20, "path")
    line = line - 20
        
    #kart_sound_horn    = Draw.String("Sound Horn : ",    event_sound,       500, 0,
    #                                 310, 20, kart_sound_horn.val, 320, "Kart Sounds")
    #kart_sound_crash   = Draw.String("Sound Crash : ",   event_sound,       500, 30,
    #                                 310, 20, kart_sound_crash.val, 320, "Kart Sounds")
    #kart_sound_shoot   = Draw.String("Sound Shoot : ",   event_sound,       500, 60,
    #                                 310, 20, kart_sound_shoot.val, 320, "Kart Sounds")
    #kart_sound_win     = Draw.String("Sound Win : ",     event_sound,       500, 90,
    #                                 310, 20, kart_sound_win.val, 320, "Kart Sounds")
    #kart_sound_explode = Draw.String("Sound Explode : ", event_sound,       500, 120,
    #                                 310, 20, kart_sound_explode.val, 320, "Kart Sounds")
    #kart_sound_goo     = Draw.String("Sound Goo : ",     event_sound,       500, 150,
    #                                 310, 20, kart_sound_goo.val, 320, "Kart Sounds")
    #kart_sound_pass    = Draw.String("Sound Pass : ",    event_sound,       500, 180,
    #                                 310, 20, kart_sound_pass.val, 320, "Kart Sounds")
    #kart_sound_zipper  = Draw.String("Sound Ziper : ",   event_sound,       500, 210,
    #                                 310, 20, kart_sound_zipper.val, 320, "Kart Sounds")
    #kart_sound_name    = Draw.String("Sound Name: ",     event_sound,       500, 240,
    #                                 310, 20, kart_sound_name.val, 320, "Kart Sounds")
    #kart_sound_attach  = Draw.String("Sound Attach : ",  event_sound,       500, 270,
    #                                 310, 20, kart_sound_attach.val, 320, "Kart Sounds")
    
# ------------------------------------------------------------------------------
def event(evt, val):
    if evt == Draw.ESCKEY:
        Draw.Exit()
             
# ------------------------------------------------------------------------------
def butt_evt(evt):  # function that handles keyboard and mouse events
    global event_quit, kart_engine_sfx
    if evt == event_quit:
        writeIDProperties()
        Draw.Exit()
    elif evt == event_export:
        exportKart()
    elif evt == event_browse:
        Blender.Window.FileSelector(selectPath,"Export STK kart",
                                    Blender.sys.makename(ext = ".xml"))
    elif evt == event_browse_shadow:
        Blender.Window.FileSelector(selectPathShadow,"Select a shadow",
                                    Blender.sys.makename(ext = ".png"))
    elif evt == event_browse_icon:
        Blender.Window.FileSelector(selectPathIcon,"Select an icon",
                                    Blender.sys.makename(ext = ".png"))             
    elif evt == event_browse_map_icon:
        Blender.Window.FileSelector(selectPathMapIcon,"Select an icon",
                                    Blender.sys.makename(ext = ".png"))             
    elif evt == event_browse_engine_sfx:
        result = Draw.PupTreeMenu( [ ("small", 1), ("large", 2) ] )
        if result==1:
            kart_engine_sfx.val = "small"
        elif result==2:
            kart_engine_sfx.val = "large"
        Draw.Redraw(1)

# ------------------------------------------------------------------------------
def selectPath(filename):
    global path_export_text
    path_export_text.val = Blender.sys.dirname(filename)

# ------------------------------------------------------------------------------
def selectPathShadow(filename):
    global kart_shadow
    kart_shadow.val = Blender.sys.basename(filename)
# ------------------------------------------------------------------------------
def selectPathIcon(filename):
    global kart_icon
    kart_icon.val = Blender.sys.basename(filename)
# ------------------------------------------------------------------------------
def selectPathMapIcon(filename):
    global kart_map_icon
    kart_map_icon.val = Blender.sys.basename(filename)

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

# ------------------------------------------------------------------------------
# Saves any defined animations to the kart.xml file.
def saveAnimations(f):
    scene       = Blender.Scene.GetCurrent()
    context     = scene.getRenderingContext()
    first_frame = context.startFrame()
    last_frame  = context.endFrame()
    # search for animation
    lAnims = []
    for i in range(first_frame, last_frame+1):
        try:
            marker = scene.timeline.getName(i).lower()
            if  marker in \
               ["straight", "right", "left", "start-winning", "start-winning-loop",
                "end-winning", "start-losing", "start-losing-loop", "end-losing",
                "start-explosion", "end-explosion",
                "turning-l", "center", "turning-r", "repeat-losing", "repeat-winning"]:
                if marker=="turning-l": marker="left"
                if marker=="turning-r": marker="right"
                if marker=="center": marker="straight"
                if marker=="repeat-losing": marker="start-losing-loop"
                if marker=="repeat-winning": marker="start-winning-loop"
                lAnims.append( (marker, i-1) )
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
def saveSounds(f, engine_sfx):
    lSounds = []
    if  engine_sfx:                 lSounds.append( ("engine",     engine_sfx) );
    #if kart_sound_horn.val  != "": lSounds.append( ("horn-sound", kart_sound_horn.val ))
    #if kart_sound_crash.val != "": lSounds.append( ("crash-sound",kart_sound_crash.val))
    #if kart_sound_shoot.val != "" :lSounds.append( ("shoot-sound",kart_sound_shoot.val))
    #if kart_sound_win.val   != "" :lSounds.append( ("win-sound",  kart_sound_win.val  ))
    #if kart_sound_explode.val!="" :lSounds.append( ("explode-sound",kart_sound_explode.val))
    #if kart_sound_goo.val   != "" :lSounds.append( ("goo-sound",  kart_sound_goo.val))
    #if kart_sound_pass.val  != "" :lSounds.append( ("pass-sound", kart_sound_pass.val))
    #if kart_sound_zipper.val!= "" :lSounds.append( ("zipper-sound",kart_sound_zipper.val))
    #if kart_sound_name.val  != "" :lSounds.append( ("name-sound", kart_sound_name.val))
    #if kart_sound_attach.val!= "" :lSounds.append( ("attach-sound",kart_sound_attach.val))

    if lSounds:
        f.write('  <sounds %s = "%s"'%(lSounds[0][0], lSounds[0][1]))
        for (name, sound) in lSounds[1:]:
            f.write('\n          %s = "%s"'%(name, sound))
        f.write('/>\n')
    
# ------------------------------------------------------------------------------
# Exports the actual kart.
def exportKart():
    global kart_name, kart_group, kart_icon, kart_shadow, path_export_text, \
           kart_color, kart_engine_sfx
    path = path_export_text.val
    kart_name_string = kart_name.val
    if not kart_name_string:
        Blender.Draw.PupBlock("No kart name specified",["No kart name specified!"])
        return
    lColor = kart_color.val.split()
    if len(lColor)!=3:
        Blender.Draw.PupBlock("Incorrect kart color", ["Incorrect kart color",
                                                       "must be an RGB value!"])
        return
    
    b3d_export.b3d_parameters["vertex-normals" ] = 1  # Vertex normals.
    b3d_export.b3d_parameters["vertex-colors"  ] = 1  # Vertex colors
    b3d_export.b3d_parameters["cameras"        ] = 0  # Cameras
    b3d_export.b3d_parameters["lights"         ] = 0  # Lights
    b3d_export.b3d_parameters["mipmap"         ] = 1  # Enable mipmap
    b3d_export.b3d_parameters["local-space"    ] = 0  # Export in world space

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
            # Due to limitations with the b3d exporter animated
            # objects must be first in the list of objects to export:
            if obj.getParent() and obj.getParent().type=="Armature":
                lKart.insert(0, obj)
            else:
                lKart.append(obj)


    # Write the xml file
    # ------------------
    if not kart_shadow.val:   kart_shadow.val   = kart_name_string.lower() + "_shadow.png"
    if not kart_icon.val:     kart_icon.val     = kart_name_string.lower() + "_icon.png"
    if not kart_map_icon.val: kart_map_icon.val = kart_name_string.lower() + "_map_icon.png"
    if not kart_group.val:    kart_group.val    = "default"
    if not kart_engine_sfx.val: kart_engine_sfx.val = "small"
        
    f = open(Blender.sys.join(path,"kart.xml"), 'wb')    
    f.write('<?xml version="1.0"?>\n')
    f.write('<!-- Generated with script from SVN rev %s -->\n'\
            % getScriptVersion())
    rgb = (0.7, 0.0, 0.0)
    model_file = kart_name_string.lower()+".b3d"
    f.write('<kart name              = "%s"\n' % kart_name_string)
    f.write('      version           = "2"\n' )
    f.write('      model-file        = "%s"\n' % model_file)
    f.write('      icon-file         = "%s"\n' % kart_icon.val)
    f.write('      minimap-icon-file = "%s"\n' % kart_map_icon.val)
    f.write('      shadow-file       = "%s"\n' % kart_shadow.val)
    if center_shift.val:
        f.write('      center-shift      = "%s"\n' % center_shift.val)
        
    f.write('      groups            = "%s"\n' % kart_group.val)
    f.write('      rgb               = "%s %s %s" >\n' % tuple(lColor))
    
    saveSounds(f, kart_engine_sfx.val)
    saveAnimations(f)
    saveWheels(f, lWheels, path)
    f.write('</kart>\n')
    f.close()

    # Export the actual kart (the wheels are already exported in saveWheels)
    b3d_export.write_b3d_file(Blender.sys.join(path, model_file), lKart)
    
    writeIDProperties()
    Draw.PupMenu("Successful")


# ------------------------------------------------------------------------------
# This saves all entered values in the ID properties of this model
def writeIDProperties():
    global kart_name, kart_group, kart_icon, kart_shadow, path_export_text,        \
           kart_sound_horn, kart_sound_crash, kart_sound_shoot, kart_sound_win,    \
           kart_sound_explode, kart_sound_goo, kart_sound_pass, kart_sound_zipper, \
           kart_sound_name, kart_sound_attach, event_sound, kart_minimap_icon,     \
           center_shift, kart_engine_sfx
    
    scene = Blender.Scene.GetCurrent()
    scene.properties['name'            ] = kart_name.val
    scene.properties['color'           ] = kart_color.val
    scene.properties['group'           ] = kart_group.val
    scene.properties['icon'            ] = kart_icon.val
    scene.properties['minimap-icon'    ] = kart_map_icon.val
    scene.properties['center-shift'    ] = center_shift.val
    scene.properties['shadow'          ] = kart_shadow.val
    scene.properties['engine-sfx'      ] = kart_engine_sfx.val
    scene.properties['kartPath'        ] = path_export_text.val
    scene.properties['kartSoundHorn'   ] = kart_sound_horn.val
    scene.properties['kartSoundCrash'  ] = kart_sound_crash.val
    scene.properties['kartSoundShoot'  ] = kart_sound_shoot.val
    scene.properties['kartSoundWin'    ] = kart_sound_win.val
    scene.properties['kartSoundExplode'] = kart_sound_explode.val
    scene.properties['kartSoundGoo'    ] = kart_sound_goo.val
    scene.properties['kartSoundPass'   ] = kart_sound_pass.val
    scene.properties['kartSoundZiper'  ] = kart_sound_zipper.val
    scene.properties['kartSoundName'   ] = kart_sound_name.val
    scene.properties['kartSoundAttach' ] = kart_sound_attach.val

# ==============================================================================
def main():
    scene = Blender.Scene.GetCurrent()

    kart_name.val          = getIdProperty(scene, 'name'            , "")
    kart_color.val         = getIdProperty(scene, 'color'           , "0.7 0 0")
    kart_group.val         = getIdProperty(scene, 'group'           , "standard")
    kart_icon.val          = getIdProperty(scene, 'icon'            , "")
    kart_map_icon.val      = getIdProperty(scene, 'minimap-icon'    , "")
    center_shift.val       = getIdProperty(scene, 'center-shift'    , "")
    kart_shadow.val        = getIdProperty(scene, 'shadow'          , "")
    kart_engine_sfx.val    = getIdProperty(scene, 'engine-sfx'      , "")
    path_export_text.val   = getIdProperty(scene, 'kartPath'        , "")
    kart_sound_horn.val    = getIdProperty(scene, 'kartSoundHorn'   , "")
    kart_sound_crash.val   = getIdProperty(scene, 'kartSoundCrash'  , "")
    kart_sound_shoot.val   = getIdProperty(scene, 'kartSoundShoot'  , "")
    kart_sound_win.val     = getIdProperty(scene, 'kartSoundWin'    , "")
    kart_sound_explode.val = getIdProperty(scene, 'kartSoundExplode', "")
    kart_sound_goo.val     = getIdProperty(scene, 'kartSoundGoo'    , "")
    kart_sound_pass.val    = getIdProperty(scene, 'kartSoundPass'   , "")
    kart_sound_zipper.val  = getIdProperty(scene, 'kartSoundZiper'  , "")
    kart_sound_name.val    = getIdProperty(scene, 'kartSoundName'   , "")
    kart_sound_attach.val  = getIdProperty(scene, 'kartSoundAttach' , "")

    Draw.Register(gui, event, butt_evt)

# ==============================================================================
main()
