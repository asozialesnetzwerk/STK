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
__version__ = "0.1"
__email__ = "asciimonster@myrealbox.com"
__bpydoc__ = """\

Inspired by Joe Edgar's ID Property browser, this Blender
script is tailored for the SuperTuxKart project.

Allows browsing, creating and editing of ID Properties
for various ID block types such as mesh, scene, object,
etc.
"""

import Blender

from Blender import *
from Blender.BGL import *

###
# Needed: Licence block here
###

# Define Property Types
type_STRING = 0
type_INTEGER = 1
type_FLOAT = 2
type_COLOUR = 3
type_PICKLIST = 10
type_STATIC = 11
type_TYPELIST = 12 
type_URL = 14
type_IMAGEURL = 15
type_DELETE = 20
type_RESET  = 21


# Definition of all available object types. Also translates the Blender names to
# names that make sense to humans ;)
# ATTENTION: If you change something here, don't forget to update  "type" item in lSTK_Picklist, below. 
lObjectType = {"None":"None",\
               "Scene":"Track",\
               "Image":"Texture",\
               "Lamp":"Sun",\
               "Camera":"EndCamera",\
               "Driveline":"Driveline",\
               "Maindriveline":"Main Driveline",\
               "Lap":"Lap",\
               "Check":"Check",\
               "Ignore":"Ignore",\
               "Object":"Object",\
               "Banana":"Banana",\
               "Item":"Item",\
               "Nitro-Small":"Nitro-small",\
               "Nitro-Big":"Nitro-big",\
               "Water":"Water"}

# Definition of the STK context-sensitive menu. Please define arrays here with items 
# of form [parameter_name,object_type,property_type,initial value]
# Important: If you mark something as type_PICKLIST, make sure a corresponding line
# is in lSTK_Picklist 
lSTK_Properties = [["stk-browser-version","Track",type_STATIC,__version__],\
                ["name","Track",type_STRING,""],\
                ["version","Track",type_FLOAT,1],\
                ["groups","Track",type_STRING,""],\
                ["designer","Track",type_STRING,""],\
                ["music","Track",type_URL,""],\
                ["screenshot","Track",type_IMAGEURL,""],\
                ["arena","Track",type_PICKLIST,"no"],\
                ["sky-type","Track",type_PICKLIST,"dome"],\
                ["sky-texture","Track",type_IMAGEURL,""],\
                ["sky-texture1","","Track",type_IMAGEURL],\
                ["sky-texture2","","Track",type_IMAGEURL],\
                ["sky-texture3","","Track",type_IMAGEURL],\
                ["sky-texture4","","Track",type_IMAGEURL],\
                ["sky-texture5","","Track",type_IMAGEURL],\
                ["sky-texture6","","Track",type_IMAGEURL],\
                ["sky-horizontal","Track",type_FLOAT,float(16)],\
                ["sky-vertical","Track",type_FLOAT,float(16)],\
                ["sky-texture-percent","Track",type_FLOAT,float(0.5)],\
                ["sky-sphere-percent","Track",type_FLOAT,float(1.3)],\
                ["sky-color","Track",type_COLOUR,(0.0,0.0,0.0)],\
                ["ambient-color","Track",type_COLOUR,(0.0,0.0,0.0)],\
                ["camera-far","Track",type_INTEGER,float(200.00000)],\
                ["fog","Track",type_PICKLIST,"no"],\
                ["fog-color","Track",type_COLOUR,(0.0,0.0,0.0)],\
                ["fog-density","Track",type_FLOAT,16],\
                ["fog-start","Track",type_STRING,""],\
                ["fog-end","Track",type_STRING,""],\
                ["start-karts-per-row","Track",type_INTEGER,int(2)],\
                ["start-forwards-distance","Track",type_INTEGER,int(1.1)],\
                ["start-sidewards-distance","Track",type_INTEGER,int(1.1)],\
                ["start-upwards-distance","Track",type_INTEGER,int(1.1)],\
#For Textures                
                ["clampU","Texture",type_PICKLIST,"no"],\
                ["clampV","Texture",type_PICKLIST,"no"],\
                ["transparency","Texture",type_PICKLIST,"no"],\
                ["alpha","Texture",type_PICKLIST,"no"],\
                ["light","Texture",type_PICKLIST,"yes"],\
                ["sphere","Texture",type_PICKLIST,"no"],\
                ["slowdown","Texture",type_FLOAT,1],\
                ["anisotropic","Texture",type_PICKLIST,"yes"],\
                ["max-speed","Texture",type_STRING,float(1.0)],\
                ["friction","Texture",type_FLOAT,float(1.0)],\
                ["backface-culling","Texture",type_PICKLIST,"yes"],\
                ["ignore","Texture",type_PICKLIST,"no"],\
                ["zipper","Texture",type_PICKLIST,"no"],\
                ["zipper-duration","Texture",type_FLOAT,float(3.5)],\
                ["zipper-max-speed-increase","Texture",type_FLOAT,float(15)],\
                ["zipper-fade-out-time","Texture",type_FLOAT,float(3)],\
                ["zipper-speed-gain","Texture",type_FLOAT,float(4.5)],\
                ["reset","Texture",type_PICKLIST,"no"],\
                ["graphical-effect","Texture",type_PICKLIST,"none"],\
                ["sfx:filename","Texture",type_STRING,""],\
                ["sfx:name","Texture",type_STRING,""],\
                ["sfx:rolloff","Texture",type_FLOAT,float(0.1)],\
                ["sfx:min-speed","Texture",type_FLOAT,float(0.0)],\
                ["sfx:max-speed","Texture",type_FLOAT,float(30.0)],\
                ["sfx:min-pitch","Texture",type_FLOAT,float(1.0)],\
                ["sfx:max-pitch","Texture",type_FLOAT,float(1.0)],\
                ["sfx:positional","Texture",type_PICKLIST,"no"],\
                ["sfx:volume","Texture",type_FLOAT,float(1.0)],\
#For Lights (doesn't work yet)                
                ["ambient","Sun",type_COLOUR,"0.0 0.0 0.0"],\
                ["diffuse","Sun",type_COLOUR,"0.0 0.0 0.0"],\
                ["specular","Sun",type_COLOUR,"0.0 0.0 0.0"],\
#For Waters
                ["name","Water",type_STRING,""],\
                ["height","Water",type_FLOAT,1],\
                ["length","Water",type_FLOAT,1],\
                ["speed","Water",type_FLOAT,1],\
#For Objects
                ["name","Object",type_STRING,""],\
                ["interaction","Object",type_PICKLIST,"none"],\
                ["shape","Object",type_PICKLIST,"cone"],\
                ["mass","Object",type_FLOAT,225],\
#For Anims (anim-texture)               
#                [anim-dx,"Anim",type_FLOAT,0],\
#                [anim-dy,"Anim",type_FLOAT,0],\
#For checklines
                ["activate","Check",type_STRING,""],\
                ["toggle","Check",type_STRING,""],\
                ["inner-radius","Check",type_FLOAT,1],\
                ["color","Check",type_COLOUR,"0.0 0.0 0.0"],\
                ]

# For picklist, add <name>:<valuelist> to lSTK_Picklist. The valuelist items are |-separated...
lSTK_Picklist = {"type": "None|Driveline|Maindriveline|Lap|Check|Ignore|Object|Banana|Item|Nitro-small|Nitro-big|Water",\
                "arena": "yes|no",\
                "sky-type": "dome|box",\
                "fog": "yes|no",\
                "clampU": "yes|no" ,\
                "clampV": "yes|no" ,\
                "transparency": "yes|no",\
                "backface-culling":"yes|no",\
                "alpha": "yes|no",\
                "light": "yes|no",\
                "anisotropic": "yes|no",\
                "ignore": "yes|no",\
                "zipper": "yes|no",\
                "reset": "yes|no",\
                "graphical-effect": "none|water|smoke",\
                "sfx:positional": "yes|no",\
                "interaction": "none|ghost|static|move",\
                "shape": "cone|coneX|coneZ|box|sphere"
}

# Define Buttons
# (Remember: In Blender-speak any active control is called a button)
btn_SCROLLBAR   = 100
btn_TYPEFILTER  = 101 
btn_OBJFILTER   = 102
btn_STK         = 103
btn_CHANGETYPE  = 104
btn_UP          = 105
btn_DOWN        = 106
#Events 500 and upwards are reserved for all temporary buttons
#The list below enumerates them, items are formatted as [ObjectName,ButtonName,ButtonType] 
lButtonList = []

textheight = 20
lObjects = []
lScenes = []
lImages = []
lLamps = []

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
        for (obj_type,obj_name,obj_index) in self.lObjectList:
            if obj_name == current_object:
                if obj_type == lObjectType["Scene"]:
                    lScenes = Blender.Scene.Get() # I don't understand why I need to reread this...
                    del lScenes[obj_index].properties[property_name]
                elif obj_type == lObjectType["Image"]:
                    lImages = Blender.Image.Get()
                    del lImages[obj_index].properties[property_name]
                else: 
                    #"Normal" object
                    lObjects = Blender.Object.Get()
                    lObjects[obj_index].removeProperty(property_name)
                     
                break    
        
    def GetCurrentType(self):
        selected_type = self.GetSTKTypes().split("|")[self.currenttype-1]
        if selected_type == "All":
            #All can be any type => look at the object
            selected_object = self.GetSTKObjects(selected_type).split("|")[self.currentobject-1]
            for (obj_type,obj_name,obj_index) in self.lObjectList:
                if obj_name == selected_object:
                    selected_type = obj_type
                    break 

        return selected_type

    def GetCurrentObject(self):
        return self.GetSTKObjects(self.GetCurrentType()).split("|")[self.currentobject-1]
        
    def GetProperties(self,ObjectName):
        #Get the Properties of the current object
         
        my_props = [] # Fill with [prop_name,prop_type,current_value] 
        for (obj_type,obj_name,obj_index) in self.lObjectList:
            if ObjectName == obj_name:
                if obj_type == lObjectType["Scene"]:
                    lScenes = Blender.Scene.Get() # I don't understand why I need to reread this...
#                    my_props.append(["stk-browser-version",type_STATIC,__version__])
                    lScenes[obj_index].properties["stk-browser-version"] = __version__                   
                    my_props.append(["type",type_STATIC,obj_type])
                    for (item_name,item_val) in lScenes[obj_index].properties.iteritems():
                        if item_name.title() != "Type": # I've already added the type
                            my_props.append(self.ProcessProperty(obj_type,item_name,0,item_val))
                elif obj_type == lObjectType["Image"]:
                    lImages = Blender.Image.Get()
                    my_props.append(["type",type_STATIC,obj_type])
                    for (item_name,item_val) in lImages[obj_index].properties.iteritems():
                        if item_name.title() != "Type": # I've already added the type
                            my_props.append(self.ProcessProperty(obj_type,item_name,0,item_val))
                else: 
                    #"Normal" object
                    my_props.append(["type",type_TYPELIST,obj_type])
                    lObjects = Blender.Object.Get()
                    for property_obj in lObjects[obj_index].getAllProperties():
                        if property_obj.getName().title() != "Type": # I've already added the type
                            my_props.append(self.ProcessProperty(obj_type,\
                                property_obj.getName(),property_obj.getType(),property_obj.getData()))
                     
                break

        return my_props

    def GetSTKTypes(self):
        #Give back all object types currently present in Blender
        tmp_type = []
        for (obj_type,obj_name,obj_index) in self.lObjectList:
            if obj_type not in tmp_type:
                tmp_type.append(obj_type)

        output = "All" # All is a standard option
        for objtype2 in tmp_type:
            output = "%s|%s" % (output,objtype2)
                
        return output
    
    def GetSTKObjects(self,filter):
        #Give back all object names currently present in Blender, matching current filter
        lObjects = Blender.Object.Get()
        lScenes = Blender.Scene.Get() # I don't understand why I need to reread this...
        lImages = Blender.Image.Get()
        
        tmp_name = []
        for (obj_type,obj_name,obj_index) in self.lObjectList:
            if obj_type == lObjectType["Scene"]:
                if filter == lObjectType["Scene"] or filter == "All":
                    tmp_name.append(lScenes[obj_index].getName())
            elif obj_type == lObjectType["Image"]:
                if filter == lObjectType["Image"] or filter == "All":
                    tmp_name.append(lImages[obj_index].getName())
            elif obj_type == filter or filter == "All":
                tmp_name.append(lObjects[obj_index].getName())
                
        output = "" # Here there is no standard option since a valid object name must be returned
        for obj_name in tmp_name:
            if output == "":
                output = obj_name
            else:
                output = "%s|%s" % (output,obj_name)
        
        return output 

    def IsChangableType(self,ObjType):
        #Is this object type a Blender or STK Type?
        #CURENTLY UNUSED!!!
        if ObjType == lObjectType["Scene"] or \
            ObjType == lObjectType["Image"]:
            return False
        else:
            return True 
        
    def ProcessProperty(self,obj_type,prop_name,prop_type,prop_val):
        #Take the raw blender property and return a [name,type,value pair]
        tmp_prop = [prop_name,type_STRING,prop_val] #Assume string 
        
        #First, determine defaults
        if prop_type == 0:
            tmp_prop = [prop_name,type_STRING,prop_val]
        elif prop_type.title() == "Int":    
            tmp_prop = [prop_name,type_INTEGER,prop_val]
        elif prop_type.title() == "Float":    
            tmp_prop = [prop_name,type_FLOAT,prop_val]
                
        #Second, look through lSTK_Propertiesthe for the correct type 
        for (p_name,o_type,p_type,init_val) in lSTK_Properties:
                if obj_type.title() == o_type.title() and prop_name.title() == p_name.title():
                        tmp_prop = [prop_name,p_type,prop_val]

        return tmp_prop      
    
    def ReloadObjects(self):
        #Read Objects from Blender
        lObjects = Blender.Object.Get()
        lScenes = Blender.Scene.Get()
        lImages = Blender.Image.Get()
        lLamps = Blender.Lamp.Get()
        self.lObjectList = []

        #Now to sort them
        x = 0
        for Scene in lScenes:
            self.lObjectList.append([lObjectType["Scene"],Scene.getName(),x])
            x += 1
        
        x = 0
        for Image in lImages:
            self.lObjectList.append([lObjectType["Image"],Image.getName(),x])
            x += 1
            
        x = 0
        for Lamp in lLamps:
 #           self.lObjectList.append([lObjectType["Lamp"],Lamp.getName(),x])
            x += 1
            
        x = 0        
        for Object in lObjects:
            try:
                objtype = Object.getProperty("type").getData().title()
                if objtype in lObjectType:
                    self.lObjectList.append([lObjectType[objtype],Object.getName(),x])
                else:
                    self.lObjectList.append([lObjectType["None"],Object.getName(),x])
            except:
                self.lObjectList.append([lObjectType["None"],Object.getName(),x])
            x += 1
            
    def SetProperty(self,property_name,new_value):
        #Set the properties of the current object
        current_object = self.GetCurrentObject()
        for (obj_type,obj_name,obj_index) in self.lObjectList:
            if obj_name == current_object:
                if obj_type == lObjectType["Scene"]:
                    lScenes = Blender.Scene.Get() # I don't understand why I need to reread this...
                    lScenes[obj_index].properties[property_name] = new_value
                elif obj_type == lObjectType["Image"]:
                    lImages = Blender.Image.Get()
                    lImages[obj_index].properties[property_name] = new_value
                else: 
                    #"Normal" object
                    lObjects = Blender.Object.Get()
                    lObjects[obj_index].properties[property_name] = new_value
                     
                break
            
class STKBrowser:
    menu_type = []
    menu_object = []
    property_cursor = 1 #use this one to move through properties
    lButtonIndex = 500
    lButtons = []
    temp_property_name = ""
    
    def __init__(self):
        self.dirty = False 
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
            if self.property_cursor > 0: 
                self.property_cursor -= 1        
        elif button_id == btn_DOWN:
            self.property_cursor += 1   
        elif button_id == btn_STK:
            current_object_type = data.GetCurrentType() 
            block = []
            lPropertiesList = []
            for (new_prop,obj_group,obj_type,default) in lSTK_Properties:
                if obj_group==current_object_type:
                    t = (new_prop,default,Draw.Create(0))
                    lPropertiesList.append(t)
                    block.append((t[0],t[2]))

            if len(lPropertiesList)==0:
                    Draw.PupMenu("Error%t|No action defined for " + current_object_type + "!")
                    return

            retval = Blender.Draw.PupBlock("Add STK Properties", block)
            if retval == 0: return

            for (new_prop2,default2,thebutton) in lPropertiesList:
                if thebutton.val:
                    data.SetProperty(new_prop2,default2)
        elif button_id > 500:
            #Handle button that has been used in property list
            (cur_button,prop_name,but_name,but_type) = lButtonList[button_id-500]
            if but_type == type_STRING:
                data.SetProperty(prop_name, self.lButtons[button_id-500].val)
            if but_type == type_INTEGER:
                data.SetProperty(prop_name, self.lButtons[button_id-500].val)
            if but_type == type_FLOAT:
                data.SetProperty(prop_name, self.lButtons[button_id-500].val)
            if but_type == type_COLOUR:
                data.SetProperty(prop_name, "%s %s %s" % self.lButtons[button_id-500].val)
            if but_type == type_PICKLIST:
                #It's a picklist
                data.SetProperty(prop_name, but_name)
            #type_STATIC => Do nothing    
            elif but_type == type_TYPELIST:
                #The object type changed
                self.dirty = True #Force a reload of all objects
                data.SetProperty(prop_name, but_name)
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
            elif but_type == type_DELETE:
                #Delete the property
                data.DeleteProperty(prop_name)
            elif but_type == type_RESET:
                #Read the default value and set the property with it. 
                for (p_name,o_type,p_type,default_val) in lSTK_Properties:
                    if prop_name == p_name:
                        data.SetProperty(prop_name, default_val)
            
        Draw.Redraw(1)

    def Draw(self):
        size = Window.GetAreaSize()
        width = size[0]
        height = size[1]
        x = 0
        y = height-textheight  #N.B. (0,0) bottomleft, whereas (width,height) = topright
        pad = 5
        self.lButtonIndex = 500
        lButtonList = []
        self.lButtons = []
        
        #Reload Necessary? 
        if self.dirty:
            data.ReloadObjects()
            self.dirty = False

        #Draw the top bar
        printtext = "STK Menu "
        printwidth = Draw.GetStringWidth(printtext)
        Draw.PushButton(printtext,btn_STK,x,y,printwidth,textheight)
        x += printwidth + pad

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
        Draw.PushButton("Down", btn_DOWN, width-2*(printwidth+pad), y, printwidth, textheight) 
                
        #Newline
        x = 0
        y -= textheight+pad

        cur_prop_nr = 0
        
        #Print the properties
        cur_objname = stk_objects.split("|")[data.currentobject-1]
        for (prop_name,prop_type,current_value) in data.GetProperties(cur_objname):
            #Skip some properties if you are looking down the list...
            cur_prop_nr += 1
            if  cur_prop_nr < self.property_cursor:
                continue
            
            self.DrawBox(x+1,y+1,width-1,textheight-1)
            #Delete button
            if prop_type not in [type_STATIC,type_TYPELIST]:
                printtext = "Del "
                printwidth = Draw.GetStringWidth(printtext)
                tmp_but = Draw.PushButton("Del", self.NextButton(),\
                         width-(printwidth+pad), y, printwidth, textheight) 
                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, "Del", type_DELETE)
                printtext = "Reset "
                printwidth2 = Draw.GetStringWidth(printtext)
                tmp_but = Draw.PushButton("Reset", self.NextButton(),\
                         width-(printwidth+pad)-(printwidth2+pad), y, printwidth2, textheight)
                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, "Reset", type_RESET) 
            
            printtext = "%s: " % prop_name
            printwidth = Draw.GetStringWidth(printtext)
            Draw.Label(printtext, x, y, printwidth, textheight) 
            x += printwidth + pad
            if prop_type == type_STRING:
                tmp_but = Draw.String("", self.NextButton(), x, y, 200, textheight, str(current_value), 200)
                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, "", type_STRING)
            elif prop_type == type_INTEGER:
                tmp_but = Draw.Number("", self.NextButton(), x, y, 100, textheight, int(current_value), 0, 100000000)  
                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, "", type_INTEGER)
            elif prop_type == type_FLOAT:
                tmp_but = Draw.Number("", self.NextButton(), x, y, 150, textheight, float(current_value), 0.0, 100000000.0,"",self.Dummy,0.1) 
                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, "", type_FLOAT)
            elif prop_type == type_COLOUR:
                tmp_but = []
                try:
                    r_colour = float(current_value.split()[0])
                    g_colour = float(current_value.split()[1])
                    b_colour = float(current_value.split()[2])
                    tmp_colour = (r_colour,g_colour,b_colour)
                    tmp_but = Draw.ColorPicker(self.NextButton(), x, y, 100, textheight, tmp_colour)
                except:
                    tmp_but = Draw.ColorPicker(self.NextButton(), x, y, 100, textheight, (0.1,0.1,0.1))

                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, "", type_COLOUR)
 
                x += 100 + pad  
                printtext = "<- Click here to change colour "
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
                    self.RegisterButton(tmp_but, prop_name, tmp2, type_PICKLIST)
                    x += printwidth 
            elif prop_type == type_TYPELIST:
                tmp = 0
                tmp3 = 0
                thelist = lSTK_Picklist[prop_name]
                for tmp2 in thelist.split("|"):
                    tmp += 1
                    if tmp2 == current_value:
                        tmp3 = tmp 
                    
                tmp_but = Draw.Menu(thelist, self.NextButton(),\
                         x, y, 100, textheight, tmp3)
                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, tmp2, type_TYPELIST)
            elif prop_type in [type_URL, type_IMAGEURL]:
                #An URL is handled as a type_STRING + Pushbutton
                tmp_but = Draw.String("", self.NextButton(), x, y, 200, textheight, str(current_value), 200)
                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, "", type_STRING) 
                x += 200 
                
                printtext = "Select File "
                printwidth = Draw.GetStringWidth(printtext)
                tmp_but = Draw.PushButton(printtext, self.NextButton(), x, y, printwidth, textheight)
                self.lButtons.append(tmp_but)
                self.RegisterButton(tmp_but, prop_name, printtext, type_URL)
            else: #type_STATIC
                printtext = "%s " % current_value
                printwidth = Draw.GetStringWidth(printtext)
                Draw.Label(printtext, x, y, printwidth, textheight) 
                x += printwidth + pad
            #Newline
            x = 0
            y -= textheight
            
        printtext = "*LIST END* "
        printwidth = Draw.GetStringWidth(printtext)
        Draw.Label(printtext, x, y, printwidth, textheight) 
        x += printwidth + pad
        
    def DrawBox(self, x, y, width, height):
   #                                     glColor3f(0.5, 0.4, 0.3)
   #                             self.DrawBox(GL_POLYGON, x+pad, y, self.width-pad*2, itemhgt)
                                
   #                     glColor3f(0, 0, 0)      
    #                    self.DrawBox(GL_LINE_LOOP, x+pad, y, self.width-pad*2, itemhgt)
                glColor3f(0.5, 0.5, 0.5)
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
            if self.property_cursor > 0: 
                self.property_cursor -= 1        
                Draw.Redraw(1)     
        elif evt == Draw.WHEELDOWNMOUSE:
            self.property_cursor += 1   
            Draw.Redraw(1)     

    def Go(self):
        Draw.Register(self.Draw, self.EventIn, self.ButtonIn)
        
    def NextButton(self):
        return self.lButtonIndex
    
    def RegisterButton(self,the_button,property_name,button_name,button_type):
        #Assign an event to a button
        lButtonList.append([the_button,property_name,button_name,button_type])
        self.lButtonIndex += 1
        #Ouch! I had to do a workaround here...
        #Button objects are mangled as they are passed as 
        #I fixed it by making a new list self.lButtons, but need a better solution
        
    def SetURL(self,file_name):
        data.SetProperty(self.temp_property_name, Blender.sys.basename(file_name))
        
data = STKData()
browser = STKBrowser()
browser.Go()
