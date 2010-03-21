#!BPY

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

# Copyright (C) 2009 Joerg Henrichs / Xapantu
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
def butt_evt(evt):	# function that handles keyboard and mouse events
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
	global pathExport, pathExportTxt
	scene.properties['kartPath'] = Blender.sys.dirname(filename)
	print filename

def selectPathShadow(filename):
	scene.properties['shadow']	=	Blender.sys.basename(filename)
	print filename

def selectPathIcon(filename):
	scene.properties['icon'] = Blender.sys.basename(filename)
	print filename

def saveKart():
	global kartName, kartGroup, scene, kartIcon, kartShadow, pathExportTxt
	path = pathExportTxt.val
	name = kartName.val.lower()
	print "saving",kartName.val
	ac_filename_kart = ".b3d"
	ac_filename_fr = "wheel-front-right.b3d"
	ac_filename_fl = "wheel-front-left.b3d"
	ac_filename_rr = "wheel-rear-right.b3d"
	ac_filename_rl = "wheel-rear-left.b3d"
	
	if kartShadow.val == "Shadow of Kart":
			kartShadow.val = name + "shadow.png"
	if kartIcon.val == "Icon of Kart":
			kartIcon.val = name + "icone.png"
	
	global flag_stack
	b3d_export.flag_stack = []
	b3d_export.flag_stack.append(0) #All Objects
	b3d_export.flag_stack.append(1) #Selected Only
	b3d_export.flag_stack.append(1) #Vertex Normals
	b3d_export.flag_stack.append(1) #Vertex Colors
	b3d_export.flag_stack.append(0) #Cameras
	b3d_export.flag_stack.append(0) #Lights
	b3d_export.flag_stack.append(1) #Mipmap

	
	o_fr = Blender.Object.Get("WheelFront.R")
	old_locfr = Mathutils.Vector(o_fr.LocX,o_fr.LocY,o_fr.LocZ)
	o_fr.setLocation(0, 0, 0)
	o_frobj = []
	o_frobj.append(o_fr)
	
	o_fl = Blender.Object.Get("WheelFront.L")
	old_locfl = Mathutils.Vector(o_fl.LocX,o_fl.LocY,o_fl.LocZ)
	o_fl.setLocation(0, 0, 0)
	o_flobj = []
	o_flobj.append(o_fl)
	
	o_rr = Blender.Object.Get("WheelRear.R")
	old_locrr = Mathutils.Vector(o_rr.LocX,o_rr.LocY,o_rr.LocZ)
	o_rr.setLocation(0, 0, 0)
	o_rrobj = []
	o_rrobj.append(o_rr)

	o_rl = Blender.Object.Get("WheelRear.L")
	old_locrl = Mathutils.Vector(o_rl.LocX,o_rl.LocY,o_rl.LocZ)
	o_rl.setLocation(0, 0, 0)
	o_rlobj = []
	o_rlobj.append(o_rl)
	
	lObj = Blender.Object.GetSelected()
	lKart = []
	for obj in lObj:
			lKart.append(obj)
	rgb = (0.7, 0.0, 0.0)
	f = open(Blender.sys.join(path,"kart.xml"), 'wb')
	
	f.write('<!-- Generated with script from SVN rev %s -->\n'%getScriptVersion())
	f.write('<?xml version="1.0"?>\n')
	f.write('  <kart name        = "%s"\n' % kartName.val)
	f.write('        version     = "2"\n' )
	f.write('        model-file  = "%s.b3d"\n' % name)
	f.write('        icon-file   = "%s"\n' % kartIcon.val)
	f.write('        shadow-file = "%s"\n' % kartShadow.val)
	f.write('        groups      = "%s"\n' % kartGroup.val)
	f.write('        rgb         = "%f %f %f" >\n' % rgb)
	
	# search for animation
	lAnims = []
	for i in range(1, 300):
		try:
			marker = scene.timeline.getName(i)
			if	marker in \
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
	f.write('  <wheels>\n')
	f.write('    <front-right position = "%f %f %f"\n' % (old_locfr.x, old_locfr.z, old_locfr.y))
	f.write('                 model    = "wheel-front-right.b3d"       />\n')
	f.write('    <front-left  position = "%f %f %f"\n' % (old_locfl.x, old_locfl.z, old_locfl.y))
	f.write('                 model    = "wheel-front-left.b3d"        />\n')
	f.write('    <rear-right  position = "%f %f %f"\n' % (old_locrr.x, old_locrr.z, old_locrr.y))
	f.write('                 model    = "wheel-rear-right.b3d"        />\n')
	f.write('    <rear-left   position = "%f %f %f"\n' % (old_locrl.x, old_locrl.z, old_locrl.y))
	f.write('                 model    = "wheel-rear-left.b3d"         />\n')
	f.write('  </wheels>\n')
	f.write('</kart>\n')
	f.close()
	b3d_export.write_b3d_file(Blender.sys.join(path,name + ac_filename_kart), lKart)
	b3d_export.write_b3d_file(Blender.sys.join(path, ac_filename_fl), o_flobj)
	b3d_export.write_b3d_file(Blender.sys.join(path, ac_filename_fr), o_frobj)
	b3d_export.write_b3d_file(Blender.sys.join(path, ac_filename_rl), o_rlobj)
	b3d_export.write_b3d_file(Blender.sys.join(path, ac_filename_rr), o_rrobj)
	o_fr.setLocation(old_locfr)
	o_fl.setLocation(old_locfl)
	o_rr.setLocation(old_locrr)
	o_rl.setLocation(old_locrl)
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


Draw.Register(gui,event, butt_evt)
