# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import datamodel 
import stk_track

# ==== OPERATORS FOR MULTI-CHOICE FIELDS ====

for curr in datamodel.lSTK_Picklist:
    class STK_SetItem(bpy.types.Operator):
           
            bl_idname = ("screen.stk_set_" + curr)
            bl_label = ("STK Object :: set " + curr)
           
  #          value = bpy.props.EnumProperty("values", "values", datamodel.lSTK_Picklist[curr][0],
  #                                         datamodel.lSTK_Picklist[curr])
            
            def execute(self, context):
                scene = context.scene
                scene[curr] = value
               
                return {'FINISHED'}

# ==== OPERATORS ====

class STK_CreateProperties(bpy.types.Operator):
        bl_idname = ("screen.stk_create_props")
        bl_label = ("STK Track : create properties")
       
        def execute(self, context):
            scene = context.scene
            
            for current_property in datamodel.lSTKTypes2Properties["Track"]:
                curprop = current_property.split("|")[0]
                if not curprop in scene:
                    scene[curprop] = datamodel.lPropertyDef[curprop][1]
           
            #if not "camera_far" in scene:
            #    scene["camera_far"] = 200
            #    scene["_RNA_UI"] = {"camera_far": {"min":50, "max":500}}
           
            return {'FINISHED'}
        
# ==== OPERATOR START EXPORT ====

class STK_OPER_StartExport(bpy.types.Operator):
    bl_idname = ("screen.stk_make_track")
    bl_label = ("STK Track: create track")
    
    def execute(self, context):
        try:
            stk_track.main()
        except:
            context.invoke_popup("Error%t|Could not start exporter!")
        return {'FINISHED'}

# ==== PANEL ====
class STK_PANEL_Scene(bpy.types.Panel):
        bl_label = "SuperTuxKart Track Properties"
        bl_space_type = "PROPERTIES"
        bl_region_type = "WINDOW"
        bl_context = "scene"
       
        def draw(self, context):
            layout = self.layout

            scene = context.scene
           
            # ==== Create properties button ====
            row = layout.row()
            row.operator("screen.stk_create_props", "Create SuperTuxKart Attributes")
            
            row = layout.row()
            row.operator("screen.stk_make_track", "Start the track exporter")
           
            # ==== Track attributes ====
            for current_property in datamodel.lSTKTypes2Properties["Track"]:
                try:
                    if current_property in scene:
                        row = layout.row()
                        row.prop(scene, '["%s"]' % current_property, current_property)
                except:
                    pass
            
            row = layout.row()
            row.prop_enum(scene, '[fog]', 'fog')
           
        
           
            # ---- Arena
 #           row = layout.row()
 #           row.label("Arena")
           
 #           try:
 #               row.operator_menu_enum("screen.stk_set_arena", property="value", text=scene["arena"])
 #           except:
#                pass
           
            # ---- Camera-far
 #           row = layout.row()
           
 #           try:
 #               row.prop(scene, '["camera_far"]', slider=True, text="Camera far distance")
 #           except:
  #              pass
   #        
            # ---- Sky-type
  #          row = layout.row()
  #          row.label("Sky Type")
           
  #          try:
  #              row.operator_menu_enum("screen.stk_set_sky_type", property="value", text=scene["sky_type"])
  #          except:
  #              pass
           
lClasses = [STK_PANEL_Scene]           
           
def register():
    pass
#    for cls in lClasses:
#        bpy.types.register(cls)

def unregister():
    for cls in lClasses:
        bpy.types.unregister(cls)

if __name__ == "__main__":
    register()


#!BPY

#"""
#Name: 'STK Browser'
#Blender: 242
#Group: 'Help'
#Tooltip: 'Browse STK properties'
#"""
#from symbol import except_clause
#from string import uppercase

#__author__ = "Asciimonster"
#__version__ = "0.1.6"
#__email__ = "asciimonster@myrealbox.com"
#__bpydoc__ = """\

#Inspired by Joe Edgar's ID Property browser, this Blender
#script is tailored for the SuperTuxKart project.

#Allows browsing, creating and editing of ID Properties
#for various ID block types such as mesh, scene, object,
#etc.
#"""

#import Blender
#import os
#import stk_track

#from Blender import *
#from Blender.BGL import *

###
# Needed: License block here
###

# Define Button Events
# (Remember: In Blender-speak any active control is called a button)
#btn_SCROLLBAR   = 100
#btn_TYPEFILTER  = 101 
#btn_OBJFILTER   = 102
#btn_STK         = 103
#btn_CHANGETYPE  = 104
#btn_UP          = 105
#btn_DOWN        = 106
#btn_USECURRENT  = 107
#btn_STARTEXPORT = 108
# N.B. Events 500 and upwards are reserved for all temporary buttons

#textheight = 20
#pad = 5
#lObjects = []
#lScenes = []
#lImages = []
#lLamps = []
