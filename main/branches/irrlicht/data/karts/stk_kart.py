#!BPY

"""
Name: 'STK Kart Exporter (.irrkart)...'
Blender: 248a
Group: 'Export'
Tooltip: 'Export a SuperTuxKart kart'
"""
__author__ = ["Joerg Henrichs (hiker)/xapantu"]
__url__ = ["supertuxkart.sourceforge.net"]
__version__ = "0.01"
__bpydoc__ = """\
"""

# Copyright (C) 2009 Joerg Henrichs / Xapantu
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

ARG = __script__['arg']


# Assign event numbers to buttons
eventQuit = 0
eventExport = 1
eventkartName = 2
eventkartVersion = 3
eventkartGroup = 4
eventkartShadow = 5
eventkartIcon = 6
eventBrowse = 7
eventBrowseShadow = 8
eventBrowseIcon = 9
eventPath = 10
kartName =Draw.Create("")
kartVersion =Draw.Create("")
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
kartFileName = Draw.Create("")

def gui():
	global eventPush, eventQuit, kartName, eventkartName, eventkartVersion, kartVersion, eventkartGroup, kartGroup, scene, eventfileShadow, eventfileIcon, kartShadow, kartIcon, eventBrowseIcon, eventBrowseShadow, eventExport, pathExportTxt, eventPath, kartFileName
	BGL.glClearColor(0.4,0.5,0.8,1)
	BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)
	BGL.glColor3f(1,1,1)
	scene = Blender.Scene.getCurrent()
	BGL.glRasterPos2i(10, 250)
	try:
			kartName.val = scene.properties['name']
			kartVersion.val = scene.properties['version']
			kartGroup.val = scene.properties['group']
			kartIcon.val = scene.properties['icon']
			kartShadow.val = scene.properties['shadow']
			kartFileName.val = scene.properties['kartFile']
			pathExportTxt.val = scene.properties['kartPath']
	except:
			scene.properties['name'] = kartName.val
			scene.properties['version'] = kartVersion.val
			scene.properties['group'] = kartGroup.val
			scene.properties['icon'] = kartIcon.val
			scene.properties['shadow'] = kartShadow.val
			scene.properties['kartFile'] = kartFileName.val
			scene.properties['kartPath'] = pathExportTxt.val
			pass
	Draw.Text("Kart Exporter for STK Irrlicht version")
	button = Draw.Button("Quit", eventQuit, 5, 0, 160, 20, "Quit")
	buttonexport = Draw.Button("Export", eventExport, 5, 30, 160, 20, "export")
	buttonPath = Draw.Button("Select Path", eventBrowse, 315, 90, 160, 20, "path")
	pathExportTxt = Draw.String("Path : ", eventPath, 5, 80, 310, 20, pathExportTxt.val, 320, "Path")
	kartFileName = Draw.String("Kart File : ", eventPath, 5, 100, 310, 20, kartFileName.val, 320, "kart file")
	kartShadow = Draw.String("Kart Shadow : ", eventkartShadow, 5, 140, 310, 20, kartShadow.val, 320, "Kart Shadow")
	kartIcon = Draw.String("Kart Icon : ", eventkartIcon, 5, 120, 310, 20, kartIcon.val, 320, "Kart Icon")
	buttonicon = Draw.Button("Select an icon", eventBrowseIcon, 315, 120, 160, 20, "icon")
	buttonShadow = Draw.Button("Select a shadow", eventBrowseShadow, 315, 140, 160, 20, "shadow")
	kartName = Draw.String("Kart Name : ", eventkartName, 5, 200, 310, 20, kartName.val, 320, "Kart Name")
	kartVersion = Draw.String("Kart Version : ", eventkartVersion, 5, 180, 310, 20, kartVersion.val, 32, "Kart Version")
	kartGroup = Draw.String("Kart Group : ", eventkartGroup, 5, 160, 310, 20, kartGroup.val, 320, "Kart Group")
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
			Blender.Window.FileSelector(selectPath,"Export STK kart", Blender.sys.makename(ext = ".irrkart"))
	if evt == eventBrowseShadow:
			Blender.Window.FileSelector(selectPathShadow,"Select a shadow", Blender.sys.makename(ext = ".png"))
	if evt == eventBrowseIcon:
			Blender.Window.FileSelector(selectPathIcon,"Select an icon", Blender.sys.makename(ext = ".png"))
			 

def selectPath(filename):
	global pathExport, pathExportTxt, kartFileName
	scene.properties['kartPath'] = Blender.sys.dirname(filename)
	scene.properties['kartFile'] = Blender.sys.basename(filename)
	print filename

def selectPathShadow(filename):
	scene.properties['shadow']	=	Blender.sys.basename(filename)
	print filename

def selectPathIcon(filename):
	scene.properties['icon'] = Blender.sys.basename(filename)
	print filename

def saveKart():
	global kartName, kartVersion, kartGroup, scene, kartIcon, kartShadow, kartFileName, pathExportTxt
	path = pathExportTxt.val
	name = Blender.sys.splitext(kartFileName.val)[0]
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
	b3d_export.flag_stack.append(0) #Vertex Normals
	b3d_export.flag_stack.append(0) #Vertex Colors
	b3d_export.flag_stack.append(0) #Cameras
	b3d_export.flag_stack.append(0) #Lights
	

	
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
	lTrack = []
	for obj in lObj:
			lTrack.append(obj)
	rgb = (0.7, 0.0, 0.0)
	f = open(Blender.sys.join(path,name + ".irrkart"), 'wb')
	f.write('(tuxkart-kart\n')
	f.write('	(version %s)\n' % kartVersion.val)
	f.write('	(name        "%s")\n' % kartName.val)
	f.write('	(model-file  "%s.b3d")\n' % name)
	f.write('	(icon-file   "%s")\n' % kartIcon.val)
	f.write('	(shadow-file "%s")\n' % kartShadow.val)
	f.write('	(groups      "%s")\n' % kartGroup.val)
	f.write('	(rgb         %f %f %f)\n' % rgb)
	# search for animation
	for i in range(1, 300):
			try:
				if scene.timeline.getName(i) == "straight" or scene.timeline.getName(i) == "right" or scene.timeline.getName(i) == "left":
					f.write('	(animations-')
					f.write('%s %s)\n' %(scene.timeline.getName(i), i))
			except:
				pass
	f.write('	(wheel-front-right\n')
	f.write('		(position %f %f %f)\n' %(old_locfr.x, old_locfr.y, old_locfr.z))
	f.write('		(model		"wheel-front-right.b3d")\n')
	f.write('	)\n')
	f.write('	(wheel-front-left\n')
	f.write('		(position %f %f %f)\n' %(old_locfl.x, old_locfl.y, old_locfl.z))
	f.write('		(model		"wheel-front-left.b3d")\n')
	f.write('	)\n')
	f.write('	(wheel-rear-right\n')
	f.write('		(position %f %f %f)\n' %(old_locrr.x, old_locrr.y, old_locrr.z))
	f.write('		(model		"wheel-rear-right.b3d")\n')
	f.write('	)\n')
	f.write('	(wheel-rear-left\n')
	f.write('		(position %f %f %f)\n' %(old_locrl.x, old_locrl.y, old_locrl.z))
	f.write('		(model		"wheel-rear-left.b3d")\n')
	f.write('	)\n')
	f.write(')\n')
	f.close()
	b3d_export.write_b3d_file(Blender.sys.join(path,name + ac_filename_kart), lTrack)
	b3d_export.write_b3d_file(Blender.sys.join(path, ac_filename_fl), o_flobj)
	b3d_export.write_b3d_file(Blender.sys.join(path, ac_filename_fr), o_frobj)
	b3d_export.write_b3d_file(Blender.sys.join(path, ac_filename_rl), o_rlobj)
	b3d_export.write_b3d_file(Blender.sys.join(path, ac_filename_rr), o_rrobj)
	o_fr.setLocation(old_locfr)
	o_fl.setLocation(old_locfl)
	o_rr.setLocation(old_locrr)
	o_rl.setLocation(old_locrl)
	scene.properties['name'] = kartName.val
	scene.properties['version'] = kartVersion.val
	scene.properties['group'] = kartGroup.val
	scene.properties['icon'] = kartIcon.val
	scene.properties['shadow'] = kartShadow.val
	scene.properties['kartFile'] = kartFileName.val
	scene.properties['kartPath'] = pathExportTxt.val
	Draw.PupMenu("Successful")


Draw.Register(gui,event, butt_evt)
