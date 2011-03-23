#!BPY

"""
Name: 'STK Browser'
Blender: 242
Group: 'Help'
Tooltip: 'Browse STK properties'
"""
from symbol import except_clause
from string import uppercase

__author__ = "Asciimonster"
__version__ = "0.1.6"
__email__ = "asciimonster@myrealbox.com"
__bpydoc__ = """\

Inspired by Joe Edgar's ID Property browser, this Blender
script is tailored for the SuperTuxKart project.

Allows browsing, creating and editing of ID Properties
for various ID block types such as mesh, scene, object,
etc.
"""

import Blender
import os
import stk_track

from Blender import *
from Blender.BGL import *

###
# Needed: License block here
###

# Define Property Types
type_STRING = 0
type_INTEGER = 1
type_FLOAT = 2
type_COLOUR = 3
type_BOOLEAN = 4
type_PICKLIST = 10
type_STATIC = 11
type_TYPELIST = 12 
type_URL = 14
type_IMAGEURL = 15
type_CHOICELIST = 17
#type_DELETE = 20
type_RESET  = 21

# Define Button Events
# (Remember: In Blender-speak any active control is called a button)
btn_SCROLLBAR   = 100
btn_TYPEFILTER  = 101 
btn_OBJFILTER   = 102
btn_STK         = 103
btn_CHANGETYPE  = 104
btn_UP          = 105
btn_DOWN        = 106
btn_USECURRENT  = 107
btn_STARTEXPORT = 108
# N.B. Events 500 and upwards are reserved for all temporary buttons

textheight = 20
pad = 5
lObjects = []
lScenes = []
lImages = []
lLamps = []

# *** INSTRUCTIONS ***
#
# This tool is programmed in 4 layers:
# 1. Define which STK Types belong to what Blender Types
# 2. Define which properties belong to the STK Type
# 3. Define the properties themselves
# 4. Is a property is a Picklist, what are the values in the picklist?

# Define which STK types correspond to which Blender types 
# *** Mental note: ***
# All Blender Object types: 'Armature', 'Camera', 'Curve', 'Lamp', 'Lattice', 'Mball',
#             'Mesh', 'Surf', 'Empty', 'Wave' (deprecated) or 'unknown'
# Additional Blender types: "Scene" and "Image" 
lBlender2STKTypes = {
    "Camera":["Ignore","Ahead","Fixed"],\
    "Empty":["Ignore","Banana","Item","Nitro-Big","Nitro-Small"],\
    "Image":["Texture"],\
    "Lamp":["Ignore","Sun"],\
    "Mesh":["Ignore","Billboard","Check","Driveline","Lap",\
            "Maindriveline","Particle-Emitter","Object","Water"],\
    "Scene":["Track"],\
    "Other":["Ignore"] # All Blender types that cannot be used in STK
}

# Define what properties are coupled with what STK types
# Also determines property order
# The notation "aaa|bbb=ccc" means: show aaa only when bbb equals ccc 
lSTKTypes2Properties = {
    "Ahead":["start"],\
    "Banana":[],\
    "Billboard":[],\
    "Check":["name","activate","toggle","inner-radius","color"],\
    "Driveline":["invisible", "ai-ignore"],\
    "Empty":[],\
    "Fixed":["start"],\
    "Ignore":[],\
    "Item":[],\
    "Lap":["activate","toggle","inner-radius","color"],\
    "Maindriveline":["activate"],\
    "Nitro-Big":[],\
    "Nitro-Small":[],\
    "Object":["animated",\
                "anim-texture|animated=yes",\
                "anim-dx|animated=yes",\
                "anim-dy|animated=yes",\
               "name",\
               "interaction",\
                "shape|interaction=static",
                "shape|interaction=move",
                "mass|interaction=move"],\
    "Particle-Emitter":[],\
    "Sun":["ambient","diffuse","specular"],\
    "Texture":["anisotropic","backface-culling","clampU","clampV","compositing","disable-z-write",\
               "friction","ignore","light","max-speed","reset","slowdown-time","sphere",\
               "graphical-effect","surface","below-surface",\
               "falling-effect","sound-effect", \
                "sfx:filename|sound-effect=yes",\
                "sfx:name|sound-effect=yes",\
                "sfx:rolloff|sound-effect=yes",\
                "sfx:min-speed|sound-effect=yes",\
                "sfx:max-speed|sound-effect=yes",\
                "sfx:min-pitch|sound-effect=yes",\
                "sfx:max-pitch|sound-effect=yes",\
                "sfx:positional|sound-effect=yes",\
               "zipper",\
                "zipper:duration|zipper=yes",\
                "zipper:max-speed-increase|zipper=yes",\
                "zipper:fade-out-time|zipper=yes",\
                "zipper:speed-gain|zipper=yes",\
               "particle",\
                "particle:base|particle=yes",\
                "particle:condition|particle=yes"],\
    "Track":["stk-browser-version","name","groups","designer","music","screenshot","arena",\
             "sky-type",\
              "sky-texture|sky-type=dome",\
              "sky-texture1|sky-type=box",\
              "sky-texture2|sky-type=box",\
              "sky-texture3|sky-type=box",\
              "sky-texture4|sky-type=box",\
              "sky-texture5|sky-type=box",\
              "sky-texture6|sky-type=box",\
              "sky-horizontal|sky-type=dome",\
              "sky-vertical|sky-type=dome",\
              "sky-texture-percent|sky-type=dome",\
              "sky-sphere-percent|sky-type=dome",\
              "sky-color|sky-type=simple",\
             "ambient-color","camera-far",\
             "fog",\
              "fog-color|fog=yes",\
#             "fog-density|fog=yes",\
              "fog-start|fog=yes",\
              "fog-end|fog=yes",\
             "start-karts-per-row","start-forwards-distance","start-sidewards-distance",\
              "start-upwards-distance",\
             "weather"],\
    "Water":["name",\
             "height",\
             "length",\
             "speed",\
             "animated",\
              "anim-texture|animated=yes",\
              "anim-dx|animated=yes",\
              "anim-dy|animated=yes"],\
}

# Finally define the properties of each property
#
# Formatting is:
# BOOLEAN  - default
# COLOUR   - default(r,g,b)
# FLOAT    - default, min, max, step
# IMAGEURL - default, max_length
# INTEGER  - default, min, max
# PICKLIST - default ==> Please don't forget to update lSTK_Picklist, below.
# STATIC   - value 
# STRING   - default, max_length
# URL      - default, max_length
lPropertyDef = {
# General use                
    "activate":[type_STRING,"", 50],\
    "color":[type_COLOUR,0.0,0.0,0.0],\
    "inner-radius":[type_FLOAT,1, 0, 10000, 0.1],\
    "name":[type_STRING,"",50],\
    "start":[type_FLOAT,25,1,2000,1],\
    "toggle":[type_STRING,"", 50],\
# Driveline
    "invisible":[type_BOOLEAN,"no"],
    "ai-ignore":[type_BOOLEAN,"no"],
# Scene only
    "ambient-color":[type_COLOUR,0.0,0.0,0.0],\
    "arena":[type_BOOLEAN,"no"],\
    "camera-far":[type_INTEGER,200,10,100000],\
    "designer":[type_STRING,"",200],\
    "fog":[type_BOOLEAN,"no"],\
    "fog-color":[type_COLOUR,0.0,0.0,0.0],\
#    "fog-density":[type_FLOAT,16,0,1000,0.1],\
    "fog-start":[type_FLOAT,1000,0,1000000,0.1],\
    "fog-end":[type_FLOAT,1000,0,1000000,0.1],\
    "groups":[type_STRING,"",200],\
    "music":[type_URL,"",200],\
    "screenshot":[type_IMAGEURL,"",200],\
    "sky-type":[type_PICKLIST,"dome"],\
    "sky-color":[type_COLOUR,0.0,0.0,0.0],\
    "sky-texture":[type_IMAGEURL,"",200],\
    "sky-texture1":[type_IMAGEURL,"",200],\
    "sky-texture2":[type_IMAGEURL,"",200],\
    "sky-texture3":[type_IMAGEURL,"",200],\
    "sky-texture4":[type_IMAGEURL,"",200],\
    "sky-texture5":[type_IMAGEURL,"",200],\
    "sky-texture6":[type_IMAGEURL,"",200],\
    "sky-texture-percent":[type_FLOAT,0.5,0,1,0.1],\
    "sky-sphere-percent":[type_FLOAT,1.3,0,2,0.1],\
    "sky-horizontal":[type_INTEGER,16,0,1000],\
    "sky-vertical":[type_INTEGER,16,0,1000],\
    "start-karts-per-row":[type_INTEGER,2,1,10],\
    "start-forwards-distance":[type_FLOAT,1.1,0,1000,0.1],\
    "start-sidewards-distance":[type_FLOAT,1.1,0,1000,0.1],\
    "start-upwards-distance":[type_FLOAT,1.1,0,1000,0.1],\
    "stk-browser-version":[type_STATIC,__version__,""],\
    "weather":[type_PICKLIST,"none"],\
#For Textures  
    "clampU":[type_BOOLEAN,"no"],\
    "clampV":[type_BOOLEAN,"no"],\
    "compositing":[type_PICKLIST,"none"],\
    "light":[type_BOOLEAN,"yes"],\
    "sphere":[type_BOOLEAN,"no"],\
    "slowdown-time":[type_FLOAT,1.0, 0, 100, 0.1],\
    "anisotropic":[type_BOOLEAN,"no"],\
    "max-speed":[type_FLOAT,1.0, 0, 1.0, 0.1],\
    "friction":[type_FLOAT,1.0,0.0,50000,0.1],\
    "particle":[type_BOOLEAN,"no"],\
    "particle:base":[type_URL,"",200],\
    "particle:condition":[type_CHOICELIST,"none"],\
    "backface-culling":[type_BOOLEAN,"yes"],\
    "ignore":[type_BOOLEAN,"no"],\
    "disable-z-write":[type_BOOLEAN,"no"],\
    "zipper":[type_BOOLEAN,"no"],\
    "zipper:duration":[type_FLOAT,3.5, 0, 10, 0.1],\
    "zipper:max-speed-increase":[type_FLOAT,15, 0, 100, 0.1],\
    "zipper:fade-out-time":[type_FLOAT,3, 0, 100, 0.1],\
    "zipper:speed-gain":[type_FLOAT,4.5, 0, 100, 0.1],\
    "reset":[type_BOOLEAN,"no"],\
    "surface":[type_BOOLEAN,"no"],\
    "falling-effect":[type_BOOLEAN,"no"], \
    "below-surface":[type_BOOLEAN,"no"],\
    "graphical-effect":[type_PICKLIST,"none"],\
    "sound-effect":[type_BOOLEAN,"no"],\
    "sfx:filename":[type_STRING,"", 200],\
    "sfx:name":[type_STRING,"", 50],\
    "sfx:rolloff":[type_FLOAT,0.1, 0, 100, 0.1],\
    "sfx:min-speed":[type_FLOAT,0.0, 0, 500, 0.1],\
    "sfx:max-speed":[type_FLOAT,30.0, 0, 500, 0.1],\
    "sfx:min-pitch":[type_FLOAT,1.0, 0.5, 2, 0.1],\
    "sfx:max-pitch":[type_FLOAT,1.0, 0.5, 2, 0.1],\
    "sfx:positional":[type_BOOLEAN,"no"],\
#For Lights
    "ambient":[type_COLOUR,0.0,0.0,0.0],\
    "diffuse":[type_COLOUR,0.0,0.0,0.0],\
    "specular":[type_COLOUR,0.0,0.0,0.0],\
#For Waters
    "height":[type_FLOAT,2, 0, 100, 0.1],\
    "length":[type_FLOAT,10, 0, 100, 0.1],\
    "speed":[type_FLOAT,300, 0, 1000, 0.1],\
#For Objects
    "animated":[type_BOOLEAN,"no"],\
    "anim-texture":[type_IMAGEURL,"",200],\
    "anim-dx":[type_FLOAT,0, 0, 1000, 10],\
    "anim-dy":[type_FLOAT,0, 0, 1000, 10],\
    "interaction":[type_PICKLIST,"none"],\
    "shape":[type_PICKLIST,"box"],\
    "mass":[type_FLOAT,225, 0, 10000, 0.1],\
}
             
# For picklist, add <name>:<valuelist> to lSTK_Picklist. The valuelist items are |-separated...
lSTK_Picklist = {"sky-type": "dome|box|simple",\
                "graphical-effect": "none|water",\
                "compositing": "none|blend|test|additive",\
                "particle:condition": "skid|drive",\
                "interaction": "none|ghost|static|move",\
                "shape": "box|sphere|coneX|coneY|coneZ",\
                "weather": "none|rain|snow"
}

class STKData:
    #Data wrapper class to conceal Blender's complexity
    currenttype = 1
    currentobject = 1
    
    #ObjectList is filled as: [ObjectType,ObjectName,Index]
    # - ObjectType is a mix of Blender and STK types 
    # - Index is the index of the object in the lObjects, lScenes, or lImages list 
    lObjectList = []
    
    def __init__(self):
        self.ReloadObjects()
        
    def DeleteProperty(self,property_name):
        #Delete the requested property of the current object
        current_object = self.GetCurrentObject()
        for (bl_type,stk_type,obj_name,obj_index) in self.lObjectList:
            if obj_name == current_object:
                if bl_type == "Scene":
                    lScenes = Blender.Scene.Get() # I don't understand why I need to reread this...
                    del lScenes[obj_index].properties[property_name]
                elif bl_type == "Image":
                    lImages = Blender.Image.Get()
                    del lImages[obj_index].properties[property_name]
                else: 
                    #"Normal" object
                    lObjects = Blender.Object.Get()
                    lObjects[obj_index].removeProperty(property_name)
                     
                break    
    
    def GetBlenderType(self,object_name):
        for (bl_type,stk_type,obj_name,obj_index) in self.lObjectList:
            if obj_name == object_name:
                return bl_type
        return "Other"
        
    def GetCurrentType(self):
        selected_type = self.GetSTKTypes().split("|")[self.currenttype-1]
        if selected_type == "All":
            #All can be any type => look at the object
            selected_object = self.GetSTKObjects(selected_type).split("|")[self.currentobject-1]
            for (bl_type,stk_type,obj_name,obj_index) in self.lObjectList:
                if obj_name == selected_object:
                    selected_type = stk_type
                    break 

        return selected_type

    def GetCurrentObject(self):
        if self.GetSTKTypes().split("|")[self.currenttype-1] == "All":
            return self.GetSTKObjects("All").split("|")[self.currentobject-1]
        else:    
            return self.GetSTKObjects(self.GetCurrentType()).split("|")[self.currentobject-1]
        
    def GetProperties(self,ObjectName):
        #Get the Properties of the current object
         
        my_props = [] # Fill with [prop_name,prop_type,current_value] 
        
        cur_obj_index = -1
        for (bl_type,stk_type,obj_name,obj_index) in self.lObjectList:
            if ObjectName.title() == obj_name.title():
                cur_obj_index = obj_index
                cur_blendertype = bl_type
                cur_stktype = stk_type 
                if bl_type == "Scene":
                    # Showing a Scene? Write version number
                    lScenes = Blender.Scene.Get() 
                    lScenes[obj_index].properties["stk-browser-version"] = __version__
                elif bl_type == "Image":
                    lImages = Blender.Image.Get()
                else:
                    lObjects = Blender.Object.Get()
                    # Draw option to change STK type  
                    my_props.append(["type",type_TYPELIST,stk_type])
                break

        if cur_obj_index < 0:
            Draw.PupMenu("Error%t|Object " + ObjectName + " not listed!")
            return []

        AllProperties = []        
        try:
            AllProperties = lSTKTypes2Properties[cur_stktype]
        except:
            # If try fails: An object type was defined that is not defined above
            # -> Do a soft fail: print an error to the log then change it to an Ignore type
            print "Error for object %s: Type %s not defined. Implicit coversion to 'Ignore'" % (ObjectName,cur_stktype)

        for prop in AllProperties:
            cur_prop = prop.split("|")[0]
            
            #Get default value of property 
            cur_default = lPropertyDef[cur_prop][1]
            if lPropertyDef[cur_prop][0] == type_COLOUR:
                cur_default = "%i %i %i" % (lPropertyDef[cur_prop][1],\
                                            lPropertyDef[cur_prop][2],\
                                            lPropertyDef[cur_prop][3])
            
            #Get current value of property
            try:
                if cur_blendertype == "Scene":
                    cur_value = lScenes[cur_obj_index].properties[cur_prop]
                elif cur_blendertype == "Image":
                    cur_value = lImages[cur_obj_index].properties[cur_prop]
                else:
                    cur_value = lObjects[cur_obj_index].getProperty(cur_prop).getData()
            except:
                #If no current value... Insert default  
                cur_value = cur_default
            
            #Check if this property should be shown
            try:
                temp = prop.split("|")[1]
                test_name = temp.split("=")[0]
                test_value = temp.split("=")[1]
                try: 
                    if cur_blendertype == "Scene":
                        if lScenes[cur_obj_index].properties[test_name] != test_value:
                            continue
                    elif cur_blendertype == "Image":
                        if lImages[cur_obj_index].properties[test_name] != test_value:
                            continue
                    else:
                        if lObjects[cur_obj_index].getProperty(test_name).getData() != test_value:
                            continue
                except:
                    # Property is not yet there... Use default for comparison
                    if lPropertyDef[test_name][1] != test_value:
                        continue
            except:
                temp = "Do nothing"
            
            if cur_blendertype in ["Scene","Image"]:
                my_props.append(self.ProcessProperty(cur_prop,0,cur_value))
            else:
                try: 
                    my_props.append(self.ProcessProperty(cur_prop,\
                          lObjects[cur_obj_index].getProperty(cur_prop).getType(),cur_value))
                except:
                    my_props.append(self.ProcessProperty(cur_prop,0,cur_value))
        
        return my_props

    def GetSTKTypes(self):
        #Give back all object types currently present in Blender

        tmp_type = []
        for (bl_type,stk_type,obj_name,obj_index) in self.lObjectList:
            #Add Blender type
            if bl_type not in tmp_type:
                if bl_type not in ["Image","Scene"]: #No sense in showing Blender types with only one STK Type
                    tmp_type.append(bl_type)
            #Add STK type
            if stk_type not in tmp_type:
                tmp_type.append(stk_type)

        tmp_type.sort()
        output = "All" # All is a standard option
        for objtype2 in tmp_type:
            output = "%s|%s" % (output,objtype2)
                
        return output
    
    def GetSTKObjects(self,filter):
        #Give back all object names currently present in Blender, matching current filter
        
        output = "" # Here there is no standard option since a valid object name must be returned
        for (bl_type,stk_type,obj_name,obj_index) in self.lObjectList:
            if filter == bl_type or filter == stk_type or filter == "All":
                if output == "":
                    output = obj_name
                else:
                    output = "%s|%s" % (output,obj_name)
        
        return output 

    def ProcessProperty(self,prop_name,prop_type,prop_val):
        #Take the raw blender property and return a [name,type,value pair]
        tmp_prop = [prop_name,type_STATIC,prop_val] #Default is static 
        
        #First, determine defaults
        if prop_type == 0:
            tmp_prop = [prop_name,type_STRING,prop_val]
        elif prop_type.title() == "Int":    
            tmp_prop = [prop_name,type_INTEGER,prop_val]
        elif prop_type.title() == "Float":    
            tmp_prop = [prop_name,type_FLOAT,prop_val]
                
        #Second, look through lPropertyDef for the correct type
        try:
            tmp_type = lPropertyDef[prop_name][0]
            tmp_prop = [prop_name,tmp_type,prop_val]
        except:
            #Do nothing
            print "Unknown property %s" % prop_name                      

        return tmp_prop      
    
    def ReloadObjects(self):
        #Read Objects from Blender
        #Fill lObjectList with [Blender-Type,STK-Type,Object-Name,Object-Index] items.
        lObjects = Blender.Object.Get()
        lScenes = Blender.Scene.Get()
        lImages = Blender.Image.Get()
        self.lObjectList = []

        #Now to sort them
        x = 0
        for Scene in lScenes:
            #Scene only has Track as an STK type
            self.lObjectList.append(["Scene","Track",Scene.getName(),x])
            x += 1
        
        x = 0
        for Image in lImages:
            #Image only has Texture as an STK type
            self.lObjectList.append(["Image","Texture",Image.getName(),x])
            x += 1
            
        x = -1        
        for Object in lObjects:
            x += 1

            #Get Blender Type
            blend_type = Object.getType().title()
            #Get STK type 
            tux_type = ""
            try:
                tux_type = Object.getProperty("type").getData().title()
            except:
                # No STK type given, hence ignore
                tux_type = "Ignore"
            
            if blend_type in lBlender2STKTypes.keys():
                self.lObjectList.append([blend_type,tux_type,Object.getName(),x])
            else:
                #Unhandled Blender type
                self.lObjectList.append(["Other","Ignore",Object.getName(),x])
   
    def SetChoiceListProperty(self,prop_name, but_name):
        # Set one of the choicelist options
        # First, check if some of the helper buttons are pressed
        if but_name == "None":
            self.SetProperty(prop_name, "")
            return
        if but_name == "All":
            self.SetProperty(prop_name, lSTK_Picklist[prop_name].replace("|"," "))
            return
        
        # 1. Get current list
        tmp = ""
        tmp2 = ""
        for (prop_name2,prop_type,current_value) in self.GetProperties(self.GetCurrentObject()):
            if prop_name == prop_name2:
                tmp = current_value

        #2. Add the value to list
        for listitem in lSTK_Picklist[prop_name].split("|"):
            if listitem in tmp.split():
                if but_name != listitem:
                    if tmp2 == "":
                        tmp2 = listitem
                    else:
                        tmp2 = "%s %s" % (tmp2,listitem)
#                    print listitem,"*",tmp,"*",tmp2 
            else:
                if but_name == listitem:
                    if tmp2 == "":
                        tmp2 = listitem
                    else:
                        tmp2 = "%s %s" % (tmp2,listitem)
        
        #3. Store List
        self.SetProperty(prop_name, tmp2)
         
    def SetProperty(self,property_name,new_value):
        #Set the properties of the current object
        current_object = self.GetCurrentObject()
        for (bl_type,stk_type,obj_name,obj_index) in self.lObjectList:
            if obj_name == current_object:
                if bl_type == "Scene":
                    lScenes = Blender.Scene.Get() # I don't understand why I need to reread this...
                    lScenes[obj_index].properties[property_name] = new_value
                elif bl_type == "Image":
                    lImages = Blender.Image.Get()
                    lImages[obj_index].properties[property_name] = new_value
                else: 
                    #"Normal" object
                    lObjects = Blender.Object.Get()
                    myprop = []
                    try:
                        myprop = lObjects[obj_index].getProperty(property_name)
                    except:
                        lObjects[obj_index].addProperty(property_name,new_value,"STRING")
                        myprop = lObjects[obj_index].getProperty(property_name)
                         
                    myprop.setData(new_value)
                     
                break
            
class STKBrowser:
    menu_type = []
    menu_object = []
    property_cursor = 1 #use this one to move through properties
    property_items = 0 #total number of property items
    lButtonIndex = 500
    lButtons = []
    lButtonList = []

    temp_property_name = ""
    
    def __init__(self):
        self.lButtonIndex = 500
        
    def ButtonIn(self,button_id):  # the function to handle Draw Button events
        if button_id == btn_TYPEFILTER:
            data.currenttype = self.menu_type.val 
            data.currentobject = 1 
            self.property_cursor = 1
        elif button_id == btn_OBJFILTER:
            data.currentobject = self.menu_object.val
            self.property_cursor = 1
        elif button_id == btn_UP:
            if self.property_cursor > 1: 
                self.property_cursor -= 1        
        elif button_id == btn_DOWN:
            if self.property_cursor < self.property_items:
                self.property_cursor += 1   
        elif button_id == btn_USECURRENT:
            try:
                current_object = Blender.Object.GetSelected()[0].getName()
                data.currenttype = 1
                data.currentobject = 1
                i = 0
                for o in data.GetSTKObjects("All").split("|"):
                    i += 1
                    if o == current_object:
                        data.currentobject = i
                        break
                if data.currentobject == 1:
                    Draw.PupMenu("Error%t|Object not Found")
            except:
                Draw.PupMenu("Error%t|Cannot determine object!")
        elif button_id == btn_STARTEXPORT:
            try:
                stk_track.main()
            except:
                Draw.PupMenu("Error%t|Could not start exporter!")
            
        elif button_id >= 500:
            #Handle button that has been used in property list
            (prop_name,but_name,but_type) = self.lButtonList[button_id-500]
            if but_type == type_STRING:
                data.SetProperty(prop_name, self.lButtons[button_id-500].val)
            if but_type == type_INTEGER:
                data.SetProperty(prop_name, self.lButtons[button_id-500].val)
            if but_type == type_FLOAT:
                data.SetProperty(prop_name, self.lButtons[button_id-500].val)
            if but_type == type_COLOUR:
                r,b,g = self.lButtons[button_id-500].val
                r = int(round(r*256))
                b = int(round(b*256))
                g = int(round(g*256))
                data.SetProperty(prop_name, "%i %i %i" % (r,b,g))
            if but_type == type_PICKLIST:
                #It's a picklist
                data.SetProperty(prop_name, but_name)
            #type_STATIC => Do nothing    
            elif but_type == type_TYPELIST:
                #The object type changed
                
                available_types = lBlender2STKTypes[data.GetBlenderType(data.GetCurrentObject())]
                data.SetProperty(prop_name, available_types[self.lButtons[button_id-500].val-1])
                data.currenttype = 1
                data.currentobject = 1
            elif but_type == type_URL:
                # Unfortunately this works like a two stage rocket
                # 1. Run the file selection window   
                Window.FileSelector(self.SetURL, "Select %s" % prop_name)
                # 2. Store the propertyname for later use in callback function
                self.temp_property_name = prop_name
            elif but_type == type_IMAGEURL:
                # Equal to type_URL, but now as an imagebrowser 
                Window.ImageSelector(self.SetURL, "Select %s" % prop_name)
                self.temp_property_name = prop_name
            elif but_type == type_CHOICELIST:
                #One of the options of a choicelist is activated
                data.SetChoiceListProperty(prop_name, but_name)
            elif but_type == type_RESET:
                #Read the default value and set the property with it.
                if lPropertyDef[prop_name][0] == type_COLOUR:
                    colour_default = "%i %i %i" % (lPropertyDef[prop_name][1],\
                                                lPropertyDef[prop_name][2],\
                                                lPropertyDef[prop_name][3])
                    data.SetProperty(prop_name, colour_default)
                else:  
                    data.SetProperty(prop_name, lPropertyDef[prop_name][1])
                
            
        Draw.Redraw(1)

    def Draw(self):
        size = Window.GetAreaSize()
        width = size[0]
        height = size[1]
        x = 0
        y = height-textheight  #N.B. (0,0) bottomleft, whereas (width,height) = topright
        self.lButtonIndex = 500
        self.lButtonList = []
        self.lButtons = []
        
        data.ReloadObjects()

        #Draw the top bar
        printtext = "Use Current "
        printwidth = Draw.GetStringWidth(printtext)
        Draw.PushButton("Use Current", btn_USECURRENT, x, y, printwidth, textheight, "Opens currently selected object in the 3D view") 
        x += printwidth + pad
        
        printtext = "Create Track "
        printwidth = Draw.GetStringWidth(printtext)
        Draw.PushButton("Create Track", btn_STARTEXPORT, x, y, printwidth, textheight, "Starts the track exporter which create the track") 
        x += printwidth + pad
        
        #Newline
        x = 0
        y -= textheight+pad

        printtext = "Type= "
        printwidth = Draw.GetStringWidth(printtext)
        Draw.Label(printtext, x, y, printwidth, textheight) 
        x += printwidth + pad
        
        stk_types = data.GetSTKTypes()
        self.menu_type = Draw.Menu(stk_types, btn_TYPEFILTER, x, y, 100, textheight, data.currenttype) 
        x += 100 + pad 
        
        printtext = "Object= "
        printwidth = Draw.GetStringWidth(printtext)
        Draw.Label(printtext, x, y, printwidth, textheight) 
        x += printwidth + pad
        
        stk_objects = data.GetSTKObjects(stk_types.split("|")[data.currenttype-1])
        self.menu_object = Draw.Menu(stk_objects, btn_OBJFILTER, x, y, 200, textheight, data.currentobject) 
        x += 100 + pad
        
        printtext = "Down "
        printwidth = Draw.GetStringWidth(printtext)
        Draw.PushButton("Up", btn_UP, width-(printwidth+pad), y, printwidth, textheight) 
        Draw.PushButton("Down", btn_DOWN, width-(printwidth+pad), 0, printwidth, textheight) 

        #Newline
        x = 0
        y -= textheight+pad
        
        cur_prop_nr = 0
        self.property_items = 0
        
        #Print the properties
        cur_objname = stk_objects.split("|")[data.currentobject-1]
        for (prop_name,prop_type,current_value) in data.GetProperties(cur_objname):
            #Skip some properties if you are looking down the list...
            cur_prop_nr += 1
            if cur_prop_nr < self.property_cursor:
                continue
            
            #Apply background striation 
            if (cur_prop_nr % 2) > 0: 
                self.DrawBox(x,y-1,width,textheight+1)
            
            #Apply indentation to conditional properties
            if prop_name not in lSTKTypes2Properties[data.GetCurrentType()]:
                x += pad
            
            #Delete button
            if prop_type not in [type_STATIC,type_TYPELIST]:
                # Delete button no longer necessary
                #printtext = "Del "
                #printwidth = Draw.GetStringWidth(printtext)
                #tmp_but = Draw.PushButton("Del", self.NextButton(),\
                #         width-(printwidth+pad), y, printwidth, textheight) 
                #self.lButtons.append(tmp_but)
                #self.RegisterButton(tmp_but, prop_name, "Del", type_DELETE)
                printtext = "Reset "
                printwidth = Draw.GetStringWidth(printtext)
                tmp_but = Draw.PushButton("Reset", self.NextButton(),\
                         width-(printwidth+pad), y, printwidth, textheight)
                self.lButtons.append(tmp_but)
                self.RegisterButton(prop_name, "Reset", type_RESET) 
            
            if prop_type != type_TYPELIST:
                prop_def = lPropertyDef[prop_name]
            printtext = "%s: " % prop_name
            printwidth = Draw.GetStringWidth(printtext)
            Draw.Label(printtext, x, y, printwidth, textheight) 
            x += printwidth + pad
            if prop_type == type_STRING:
                tmp_but = Draw.String("", self.NextButton(), x, y, 200, textheight,\
                                      str(current_value), int(prop_def[2]))
                self.lButtons.append(tmp_but)
                self.RegisterButton(prop_name, "", type_STRING)
            elif prop_type == type_INTEGER:
                try:
                    tmp_but = Draw.Number("", self.NextButton(), x, y, 100, textheight,\
                                          int(current_value), int(prop_def[2]), int(prop_def[3]))  
                    self.lButtons.append(tmp_but)
                    self.RegisterButton(prop_name, "", type_INTEGER)
                except:
                    printtext = "Value Read Error (press Reset) "
                    printwidth = Draw.GetStringWidth(printtext)
                    Draw.Label(printtext, x, y, printwidth, textheight) 
            elif prop_type == type_FLOAT:
                try:
                    tmp_but = Draw.Number("", self.NextButton(), x, y, 150, textheight,\
                                          float(current_value), float(prop_def[2]), float(prop_def[3]),\
                                          "",self.Dummy, float(prop_def[4])) 
                    self.lButtons.append(tmp_but)
                    self.RegisterButton(prop_name, "", type_FLOAT)
                except:
                    printtext = "Value Read Error (press Reset) "
                    printwidth = Draw.GetStringWidth(printtext)
                    Draw.Label(printtext, x, y, printwidth, textheight) 
            elif prop_type == type_COLOUR:
                try:
                    tmp_but = []
                    r_colour = float(current_value.split()[0]) / 256
                    g_colour = float(current_value.split()[1]) / 256
                    b_colour = float(current_value.split()[2]) / 256
                    tmp_colour = (r_colour,g_colour,b_colour)
                    tmp_but = Draw.ColorPicker(self.NextButton(), x, y, 100, textheight, tmp_colour)
                    self.lButtons.append(tmp_but)
                    self.RegisterButton(prop_name, "", type_COLOUR)
 
                    x += 100 + pad  
                    printtext = "<- Click here to change colour "
                    printwidth = Draw.GetStringWidth(printtext)
                    Draw.Label(printtext, x, y, printwidth, textheight)                
                except:
                    printtext = "Value Read Error (press Reset) "
                    printwidth = Draw.GetStringWidth(printtext)
                    Draw.Label(printtext, x, y, printwidth, textheight)  
            elif prop_type == type_BOOLEAN:
                try:
                    tmp = "%s" % current_value
                    tmp2 = tmp.title()
                    if tmp2[0] == "F" or tmp2[0] == "N" or tmp2[0] == "0":
                        tmp3 = False
                    else:
                        tmp3 = True
                    
                    printtext = "yes"
                    printwidth = Draw.GetStringWidth(printtext+" ")
                    tmp_but = Draw.Toggle(printtext, self.NextButton(),\
                         x, y, printwidth, textheight, tmp3)
                    self.lButtons.append(tmp_but)
                    self.RegisterButton(prop_name, printtext, type_PICKLIST)
                    x += printwidth 
                    
                    printtext = "no"
                    printwidth = Draw.GetStringWidth(printtext+" ")
                    tmp_but = Draw.Toggle(printtext, self.NextButton(),\
                         x, y, printwidth, textheight, tmp3==False)
                    self.lButtons.append(tmp_but)
                    self.RegisterButton(prop_name, printtext, type_PICKLIST)
                except:
                    printtext = "Value Read Error (press Reset) "
                    printwidth = Draw.GetStringWidth(printtext)
                    Draw.Label(printtext, x, y, printwidth, textheight) 
            elif prop_type == type_PICKLIST:
                tmp = 0
                thelist = lSTK_Picklist[prop_name]
                for tmp2 in thelist.split("|"):
                    tmp += 1
                    
                    printtext = "%s " % tmp2
                    printwidth = Draw.GetStringWidth(printtext)
                    tmp_but = Draw.Toggle(tmp2, self.NextButton(),\
                         x, y, printwidth, textheight, tmp2 == current_value)
                    self.lButtons.append(tmp_but)
                    self.RegisterButton(prop_name, tmp2, type_PICKLIST)
                    x += printwidth 
            elif prop_type == type_TYPELIST:
                tmp = 0
                tmp3 = 0
                thelist = lBlender2STKTypes[data.GetBlenderType(cur_objname)]
                tmp4 = ""
                for tmp2 in thelist:
                    tmp += 1
                    tmp4 = "%s|%s" % (tmp4,tmp2)
                    if tmp2 == current_value:
                        tmp3 = tmp 
                    
                tmp_but = Draw.Menu(tmp4, self.NextButton(), x, y, 100, textheight, tmp3)
                self.lButtons.append(tmp_but)
                self.RegisterButton(prop_name, tmp2, type_TYPELIST)     
            elif prop_type in [type_URL, type_IMAGEURL]:
                #An URL is handled as a type_STRING + Pushbutton
                tmp_but = Draw.String("", self.NextButton(), x, y, 200, textheight,\
                                      str(current_value), int(prop_def[2]))
                self.lButtons.append(tmp_but)
                self.RegisterButton(prop_name, "", type_STRING) 
                x += 200 
                
                printtext = "Select File "
                printwidth = Draw.GetStringWidth(printtext)
                tmp_but = Draw.PushButton(printtext, self.NextButton(), x, y, printwidth, textheight)
                self.lButtons.append(tmp_but)
                self.RegisterButton(prop_name, printtext, type_URL)
            elif prop_type == type_CHOICELIST:
                tmp = 0
                thelist = lSTK_Picklist[prop_name]
                tmp3 = current_value.split()
                for tmp2 in thelist.split("|"):
                    tmp += 1
                    
                    printtext = "%s " % tmp2
                    printwidth = Draw.GetStringWidth(printtext)
                    tmp_but = Draw.Toggle(tmp2, self.NextButton(),\
                                          x, y, printwidth, textheight, tmp2 in tmp3)
                    self.lButtons.append(tmp_but)
                    self.RegisterButton(prop_name, tmp2, type_CHOICELIST)
                    x += printwidth
                    
                printtext = "Reset "
                printwidth = Draw.GetStringWidth(printtext)
                tmp_x = width-pad-printwidth
                printtext = "All "
                printwidth = Draw.GetStringWidth(printtext)
                tmp_x -= pad+printwidth
                tmp_but = Draw.PushButton(printtext, self.NextButton(),\
                                          tmp_x, y, printwidth, textheight)
                self.lButtons.append(tmp_but)
                self.RegisterButton(prop_name, "All", type_CHOICELIST)
                printtext = "None "
                printwidth = Draw.GetStringWidth(printtext)
                tmp_x -= printwidth
                tmp_but = Draw.PushButton(printtext, self.NextButton(),\
                                          tmp_x, y, printwidth, textheight)
                self.lButtons.append(tmp_but)
                self.RegisterButton(prop_name, "None", type_CHOICELIST)                
            else: #type_STATIC
                printtext = "%s " % current_value
                printwidth = Draw.GetStringWidth(printtext)
                Draw.Label(printtext, x, y, printwidth, textheight) 
                x += printwidth + pad
            #Newline
            x = 0
            y -= textheight + 2
            
        printtext = "*LIST END* "
        printwidth = Draw.GetStringWidth(printtext)
        Draw.Label(printtext, x, y, printwidth, textheight) 
        x += printwidth + pad
        
        self.property_items = cur_prop_nr
        
    def DrawBox(self, x, y, width, height):
   #                                     glColor3f(0.5, 0.4, 0.3)
   #                             self.DrawBox(GL_POLYGON, x+pad, y, self.width-pad*2, itemhgt)
                                
   #                     glColor3f(0, 0, 0)      
    #                    self.DrawBox(GL_LINE_LOOP, x+pad, y, self.width-pad*2, itemhgt)
                #glColor3f(0.5, 0.5, 0.5)
                glColor3f(0.65, 0.65, 0.65)
                glBegin(GL_POLYGON)# GL_LINE_LOOP)# 
                #glPolygonMode(GL_FRONT, GL_LINE);
                glVertex2f(x, y)
                glVertex2f(x+width, y)
                glVertex2f(x+width, y+height)
                glVertex2f(x, y+height)
                glEnd()
                
    def Dummy(self,a,b):
        a = 0 #Dummy Method            

    def EventIn(self, evt, val):
        if evt == Draw.ESCKEY:
            Draw.Exit()
            return
        elif evt == btn_SCROLLBAR:
            print "%s" % val
        elif evt == Draw.WHEELUPMOUSE:
            self.ButtonIn(btn_UP)    
        elif evt == Draw.WHEELDOWNMOUSE:
            self.ButtonIn(btn_DOWN)    

    def Go(self):
        Draw.Register(self.Draw, self.EventIn, self.ButtonIn)
        
    def NextButton(self):
        return self.lButtonIndex
    
    def RegisterButton(self,property_name,button_name,button_type):
        #IMPORTANT: Also add the button object to self.lButtons
        self.lButtonList.append([property_name,button_name,button_type])
        self.lButtonIndex += 1
        
    def SetURL(self,file_name):
        data.SetProperty(self.temp_property_name, Blender.sys.basename(file_name))
        
data = STKData()
browser = STKBrowser()
browser.Go()
