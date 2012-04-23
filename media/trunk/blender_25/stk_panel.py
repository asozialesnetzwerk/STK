
bl_info = {
    "name": "SuperTuxKart Panel",
    "description": "Allows editing object, scene and material properties for SuperTuxKart",
    "author": "Joerg Henrichs, Marianne Gagnon, Asciimonster",
    "version": (2,0),
    "blender": (2, 5, 9),
    "api": 31236,
    "location": "Properties Panel",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://supertuxkart.sourceforge.net/Get_involved",
    "tracker_url": "https://sourceforge.net/apps/trac/supertuxkart/",
    "category": "Object"}

import bpy
from collections import OrderedDict
import getpass

CONTEXT_OBJECT = 0
CONTEXT_SCENE  = 1
CONTEXT_MATERIAL  = 2

def getObject(context, contextLevel):
    if contextLevel == CONTEXT_OBJECT:
        return context.object
    if contextLevel == CONTEXT_SCENE:
        return context.scene
    if contextLevel == CONTEXT_MATERIAL:
        if 'selected_image' in context.scene:
            selected_image = context.scene['selected_image']
            if selected_image in bpy.data.images:
                return bpy.data.images[selected_image]
    
    return None

class STK_TypeUnset(bpy.types.Operator):
    bl_idname = ("screen.stk_unset_type")
    bl_label = ("STK Object :: unset type")
    
    def execute(self, context):
        obj = context.object
        obj["type"] = ""
        return {'FINISHED'}

# ------------------------------------------------------------------------------
#! Utility function, creates all properties in a given object
#!
#! object   the object to create properties in
#! props    a list of properties to create
def createProperties(object, props):
    
    if not "_RNA_UI" in object:
        object["_RNA_UI"] = {}
        
    for p in props.keys():
        
        if not p in object:
            
            # create property by setting default value
            v = props[p].default
            object[p] = v
            
            if isinstance(props[p], StkEnumProperty):
                if v in props[p].values:
                    createProperties(object, props[p].values[v].subproperties)
        
        # check the property has the right type
        elif isinstance(props[p], StkFloatProperty) :
            
            if not isinstance(object[p], float):
                try:
                    object[p] = float(object[p])
                except:
                    object[p] = props[p].default
            
        elif isinstance(props[p], StkIntProperty):
            
            if not isinstance(object[p], int):
                try:
                    object[p] = int(object[p])
                except:
                    object[p] = props[p].default
        
        elif isinstance(props[p], StkProperty) and not isinstance(object[p], str):
            try:
                object[p] = str(object[p])
            except:
                object[p] = props[p].default


        rna_ui_dict = {}
        try:
            rna_ui_dict["description"] = props[p].doc
        except:
            pass
        
        try:
            if props[p].min is not None:
                rna_ui_dict["min"] = props[p].min
                rna_ui_dict["soft_min"] = rops[p].min
        except:
            pass
        
        try:
            if props[p].max is not None:
                rna_ui_dict["max"] = props[p].max
                rna_ui_dict["soft_max"] = props[p].max
        except:
            pass
        
        object["_RNA_UI"][p] = rna_ui_dict


# ------------------------------------------------------------------------------
#! The base class for all properties.
#! If you use this property directly (and not a subclass), you get a simple text box
class StkProperty:
    def __init__(self, id, name, default, doc="(No documentation was defined for this item)"):
        self.name = name
        self.id = id
        self.default = default
        self.doc = doc


# ------------------------------------------------------------------------------
#! A text field where you can type a reference to another object (or a property
#! of another object) with an optional dropdown button to see current choices
#!
#! id               the id of the blender id-property
#! name             user-visible name
#! contextLevel     object, scene, material level?
#! default          default value for this property
#! filter           a lambda taking arguments "self" and "object", and that returns
#!                  parameter 'object' is to be displayed in the dropdown of this property
#! doc              documentation to show in the tooltip
#! static_objects   items to append to the menu unconditionally (a list of tuples of
#!                  form 'id', 'visible name')
#! unique_id_suffix if the blender id-property name is not unique, you can append a
#!                  custom suffix here to make sure the 2 same-name properties each have
#!                  their own dropdown (e.g. 'activate' for a checkline object and
#!                  'activate' for a lapline)
#! obj_identifier   a lambda taking arguments "self" and "object", and that returns
#!                  the id (value) of an object that should be put in this property when
#!                  the object is selected
#! obj_text         a lambda taking arguments "self" and "object", and that returns
#!                  the user-visible string to apear in the dropdown for an object
class StkObjectReferenceProperty(StkProperty):
    
    def __init__(self, id, name, contextLevel, default, filter, doc="Select an object",
                 static_objects=[], unique_id_suffix = "",
                 obj_identifier=lambda self, obj: obj.name,
                 obj_text=lambda self, obj: (obj.name + ((" (" + obj["name"] + ")") if "name" in obj else ""))):
        super(StkObjectReferenceProperty, self).__init__(id, name, default)
        self.doc = doc
        self.unique_id_suffix = unique_id_suffix
        
        if filter is None:
            raise Exception("Filter may not be None")
        
        class SelectObjectOperator(bpy.types.Operator):
            bl_idname = "scene.stk_select_object_" + id + unique_id_suffix
            bl_label = "Select Object Operator"
            __doc__ = doc

            m_id = id
            m_context_level = contextLevel
            
            # name of the object to select
            name = bpy.props.StringProperty()

            def execute(self, context):
                object = getObject(context, self.m_context_level)
                object[self.m_id] = self.name
                return {'FINISHED'}

        bpy.utils.register_class(SelectObjectOperator)
        
        class ObjectPickerMenu(bpy.types.Menu):
            m_filter = filter
            m_obj_identifier = obj_identifier
            m_obj_text = obj_text
            m_static_objects = static_objects
            bl_idname = "screen.stk_object_menu_" + id + unique_id_suffix
            bl_label  = ("SuperTuxKart Object Picker Menu (" + id + unique_id_suffix + ")")
            m_property_id = id + unique_id_suffix
            
            def draw(self, context):
                objects = context.scene.objects
                
                seen_objs = {}
                
                layout = self.layout
                for object in objects:
                    if self.m_filter(object):
                        text = self.m_obj_text(object)
                        object_id = self.m_obj_identifier(object)
                        
                        if object_id is not None and object_id not in seen_objs:
                            layout.operator("scene.stk_select_object_"+self.m_property_id, text=text).name = object_id
                            seen_objs[object_id] = True

                for curr in self.m_static_objects:
                    layout.operator("scene.stk_select_object_"+self.m_property_id, text=curr[1]).name=curr[0]

        
        bpy.utils.register_class(ObjectPickerMenu)


# ------------------------------------------------------------------------------
#! One entry in a StkEnumProperty
class StkEnumChoice:
    
    #! @param name          User-visible name for this property
    #! @param subproperties A list of StkProperty's. Contains the properties
    #                       that are to be shown when this enum item is selected
    def __init__(self, name, subproperties, doc="(No documentation was defined for this item)"):
        self.name = name
        
        self.subproperties = OrderedDict([])
        for curr in subproperties:
            self.subproperties[curr.id] = curr
        
        self.doc = doc


# ------------------------------------------------------------------------------
#! An enum property
#!
#! id               the id of the blender id-property
#! name             user-visible name
#! values           the choices offered by this enum, as a list of 'StkEnumChoice' objects
#! contextLevel     object, scene, material level?
#! default          default value for this property
#! unique_prefix    if the blender id-property name is not unique, you can prepend a
#!                  custom prefix here to make sure the 2 same-name properties each have
#!                  their own dropdown (e.g. 'activate' for a checkline object and
#!                  'activate' for a lapline)
class StkEnumProperty(StkProperty):
    
    def getOperatorName(self):
        return self.operator_name
    
    #! @param name   User-visible name for this property
    #! @param values A dictionnary of type { 'value' : StkEnumChoice(...) }
    #! @note         The first value will be used by default
    def __init__(self, id, name, values, contextLevel, default, unique_prefix="", doc="(No documentation for this item)"):
        super(StkEnumProperty, self).__init__(id, name, default)
        self.values = values
        self.operator_name = "screen.stk_set_"   + unique_prefix + id
        self.doc = doc
        default_value = default
        
        values_for_blender_unsorted = []
        for curr_val in values.keys():
            if len(curr_val) > 0:
                curr_obj = values[curr_val]
                values_for_blender_unsorted.append( (curr_val, curr_obj.name, curr_obj.name) )
        
        values_for_blender = sorted(values_for_blender_unsorted, key=lambda k: k[1])
                
        # Create operator for this combo
        class STK_SetComboValue(bpy.types.Operator):
        
            value = bpy.props.EnumProperty(attr="values", name="values", default=default_value + "",
                                           items=values_for_blender)
            
            bl_idname = ("screen.stk_set_"   + unique_prefix + id)
            bl_label  = ("SuperTuxKart set " + unique_prefix + id)
            __doc__ = doc
            
            m_property_id = id
            m_items_val = values_for_blender
            m_values = values
            m_context_type = contextLevel
            
            def execute(self, context):
                
                # Set the property
                object = getObject(context, self.m_context_type)
                if object is None:
                    return
                
                object[self.m_property_id] = self.value
                
                # If sub-properties are needed, create them
                if self.value in self.m_values:
                    createProperties(object, self.m_values[self.value].subproperties)
                
                return {'FINISHED'}
            
        bpy.utils.register_class(STK_SetComboValue)

# ------------------------------------------------------------------------------
#! A combinable enum property (each value can be checked or unchecked, and
#! several values can be selected at once. gives a text property containing
#! the IDs of the selected values, separated by spaces)
#!
#! id               the id of the blender id-property
#! name             user-visible name
#! values           the choices offered by this enum, as a list of 'StkEnumChoice' objects
#! contextLevel     object, scene, material level?
#! default          default value for this property
class StkCombinableEnumProperty(StkProperty):
    
    #! @param name   User-visible name for this property
    #! @param values A dictionnary of type { 'value' : StkEnumChoice(...) }
    #! @note         The first value will be used by default
    def __init__(self, id, name, values, contextLevel, default):
        super(StkCombinableEnumProperty, self).__init__(id, name, default)
        self.values = values
        
        default_value = default
        
        values_for_blender = []
        for curr_val in values.keys():
            curr_obj = values[curr_val]
            values_for_blender.append( curr_val )
        
        for curr in values_for_blender:
            # Create operator for this combo
            class STK_SetEnumComboValue(bpy.types.Operator):
            
                bl_idname = ("screen.stk_set_"+id+"_"+curr)
                bl_label  = ("SuperTuxKart set "+id+" = " + curr)
                
                if values[curr].doc is not None:
                    __doc__ = values[curr].doc + ""
                
                m_property_id = id
                m_items_val = values_for_blender
                m_values = values
                m_context_type = contextLevel
                m_curr = curr
                
                def execute(self, context):
                    
                    # Set the property
                    object = getObject(context, self.m_context_type)
                    if object is None:
                        return
                    
                    if self.m_property_id not in object:
                        object[self.m_property_id] = ""
                    
                    if self.m_curr in object[self.m_property_id]:
                        # Remove selected value
                        l = object[self.m_property_id].split()
                        l.remove( self.m_curr )
                        object[self.m_property_id] = " ".join(l)
                    else:
                        # Add selected value
                        object[self.m_property_id] = object[self.m_property_id] + " " + self.m_curr
                    
                    return {'FINISHED'}
                
            bpy.utils.register_class(STK_SetEnumComboValue)


# ------------------------------------------------------------------------------
#! A floating-point property
#!
#! id               the id of the blender id-property
#! name             user-visible name
#! default          default value for this property
#! doc              documentation shown to the user in a tooltip
#! min              minimum accepted value
#! max              maximum accepted value
class StkFloatProperty(StkProperty):
    
    #! @param name   User-visible name for this property
    def __init__(self, id, name, default=0.0, doc="(No documentation defined for this element)", min = None, max = None):
        super(StkFloatProperty, self).__init__(id, name, default)
        self.default
        self.doc = doc
        self.min = min
        self.max = max


# ------------------------------------------------------------------------------
#! An integer property
#!
#! id               the id of the blender id-property
#! name             user-visible name
#! default          default value for this property
#! doc              documentation shown to the user in a tooltip
#! min              minimum accepted value
#! max              maximum accepted value
class StkIntProperty(StkProperty):
    
    #! @param name   User-visible name for this property
    def __init__(self, id, name, default=0, doc="(No documentation defined for this element)", min=None, max=None):
        super(StkIntProperty, self).__init__(id, name, default)
        self.doc = doc
        self.min = min
        self.max = max


# ------------------------------------------------------------------------------
#! A boolean property (appears as a checkbox)
#!
#! id                   the id of the blender id-property
#! name                 user-visible name
#! contextLevel         object, scene, material level?
#! default              default value for this property
#! @param subproperties A list of StkProperty's. Contains the properties
#                       that are to be shown when this checkbox is checked
#! box                  if True, the properties from 'subproperties' are
#!                      displayed in a box
#! doc                  documentation shown to the user in a tooltip
class StkBoolProperty(StkProperty):
    
    # (self, id, name, values, default):
    box = True
    
    #! A floating-point property
    def __init__(self, id, name, contextLevel, default="false", subproperties=[], box = True, doc="(No documentation defined for this element)"):
        super(StkBoolProperty, self).__init__(id, name, default)
        
        self.box = box
        self.contextLevel = contextLevel
        
        self.subproperties = OrderedDict([])
        for curr in subproperties:
            self.subproperties[curr.id] = curr
        
        self.doc = doc
        super_self = self
        
        # Create operator for this bool
        class STK_ToggleBoolValue(bpy.types.Operator):
        
            bl_idname = ("screen.stk_toggle_bool_"+str(contextLevel)+"_"+id)
            bl_label  = ("SuperTuxKart toggle "+id)
            __doc__ = doc
            
            m_context_level = contextLevel
            m_property_id = id
            m_super_self = super_self
            
            def execute(self, context):
                
                # Set the property
                
                object = getObject(context, self.m_context_level)
                if object is None:
                    return
                
                curr_val = False
                if self.m_property_id in object:
                    curr_val = (object[self.m_property_id] == "true")
                    
                new_val = not curr_val
                
                if curr_val :
                    object[self.m_property_id] = "false"
                else:
                    object[self.m_property_id] = "true"
                
                
                # If sub-properties are needed, create them
                if object[self.m_property_id] == "true":
                    createProperties(object, self.m_super_self.subproperties)
                
                return {'FINISHED'}
        
        bpy.utils.register_class(STK_ToggleBoolValue)


# ------------------------------------------------------------------------------
#! A color property
#!
#! id               the id of the blender id-property
#! name             user-visible name
#! contextLevel     object, scene, material level?
#! default          default value for this property
#! doc              documentation shown to the user in a tooltip
class StkColorProperty(StkProperty):
    
    #! A floating-point property
    def __init__(self, id, name, contextLevel, default="255 255 255", doc="(No documentation defined for this item)"):
        super(StkColorProperty, self).__init__(id, name, default)

        #! Color picker operator (TODO: this operator is mostly for backwards compatibility with our
        #                               blend files that come from 2.4; blender 2.5 has a color property
        #                               type we could use)
        class Apply_Color_Operator(bpy.types.Operator):
            bl_idname = ("screen.apply_color_"+id)
            bl_label = ("Apply Color")
            __doc__ = doc
           
            property_id = id
            
            m_context_level = contextLevel
           
            temp_color = bpy.props.FloatVectorProperty(
               name= "temp_color",
               description= "Temp Color.",
               subtype= 'COLOR',
               min= 0.0,
               max= 1.0,
               soft_min= 0.0,
               soft_max= 1.0,
               default= (1.0,1.0,1.0)
            )
           
            def invoke(self, context, event):
                
                currcol = [1.0, 1.0, 1.0]
                try:
                    
                    object = getObject(context, self.m_context_level)
                    if object is None:
                        return
                    
                    currcol = list(map(eval, object[self.property_id].split()))
                    currcol[0] = currcol[0]/255.0
                    currcol[1] = currcol[1]/255.0
                    currcol[2] = currcol[2]/255.0
                except:
                    pass
                self.temp_color = currcol
                context.window_manager.invoke_props_dialog(self)
                return {'RUNNING_MODAL'}
           
               
            def draw(self, context):
        
                layout = self.layout
               
                # ==== Types group ====
                box = layout.box()
                row = box.row()
                try:
                    row.template_color_wheel(self, "temp_color", value_slider=True, cubic=False)
                except Exception as ex:
                    import sys
                    print("Except :(", type(ex), ex, "{",ex.args,"}")
                    pass
               
                row = layout.row()
                row.prop(self, "temp_color", text="Selected Color")
               
            def execute(self, context):
                
                object = getObject(context, self.m_context_level)
                if object is None:
                    return
                
                object[self.property_id] = "%i %i %i" % (self.temp_color[0]*255, self.temp_color[1]*255, self.temp_color[2]*255)
                return {'FINISHED'}
            
        bpy.utils.register_class(Apply_Color_Operator)


# ------------------------------------------------------------------------------
#                                  THE PROPERTIES
# ------------------------------------------------------------------------------

import xml.dom.minidom

def readEnumValues(valueNodes, contextLevel):
    out = {}
    
    for node in valueNodes:
        if node.localName == None:
            continue
        elif node.localName == "EnumChoice":
            args = dict()
            args["name"] = node.getAttribute("label")
            args["subproperties"] = parseProperties(node, contextLevel)
            
            if node.hasAttribute("doc"):
                args["doc"] = node.getAttribute("doc")
            
            out[node.getAttribute("id")] = StkEnumChoice(**args)
        else:
            print("INTERNAL ERROR : Unexpected tag " + str(node.localName) + " in enum '" + str(node.localName) + "'")
            
    return out

def parseProperties(node, contextLevel):

    props = []

    for e in node.childNodes:
        if e.localName == None:
            continue
        
        elif e.localName == "StringProp":
            defaultval = e.getAttribute("default")
            if defaultval == "$user":
                defaultval = getpass.getuser()
                
            if e.hasAttribute("doc"):
                props.append(StkProperty(id=e.getAttribute("id"), name=e.getAttribute("name"), default=defaultval,
                                         doc=e.getAttribute("doc")))
            else:
                props.append(StkProperty(id=e.getAttribute("id"), name=e.getAttribute("name"), default=defaultval))
        
        elif e.localName == "EnumProp":
            
            args = dict()
            args["id"] = e.getAttribute("id")
            args["name"] = e.getAttribute("name")
            args["default"] = e.getAttribute("default")
            
            if e.hasAttribute("unique_prefix"):
                args["unique_prefix"] = e.getAttribute("unique_prefix")
            
            if e.hasAttribute("doc"):
                args["doc"] = e.getAttribute("doc")
            
            args["values"] = readEnumValues(e.childNodes, contextLevel)
            args["contextLevel"] = contextLevel
            
            props.append(StkEnumProperty(**args))
        
        elif e.localName == "CombinableEnumProp":
        
            args = dict()
            args["id"] = e.getAttribute("id")
            args["name"] = e.getAttribute("name")
            args["default"] = e.getAttribute("default")
            
            if e.hasAttribute("unique_prefix"):
                args["unique_prefix"] = e.getAttribute("unique_prefix")
            
            args["values"] = readEnumValues(e.childNodes, contextLevel)
            args["contextLevel"] = contextLevel
            
            props.append(StkCombinableEnumProperty(**args))
        
        elif e.localName == "IntProp":
            if e.hasAttribute("doc"):
                props.append(StkIntProperty(id=e.getAttribute("id"), name=e.getAttribute("name"), default=int(e.getAttribute("default")),
                                            doc=e.getAttribute("doc")))
            else:
                props.append(StkIntProperty(id=e.getAttribute("id"), name=e.getAttribute("name"), default=int(e.getAttribute("default"))))
        
        elif e.localName == "FloatProp":
            args = dict()
            args["id"] = e.getAttribute("id")
            args["name"] = e.getAttribute("name")
            args["default"] = float(e.getAttribute("default"))
            
            if e.hasAttribute("doc"):
                args["doc"] = e.getAttribute("doc")
            if e.hasAttribute("min"):
                args["min"] = float(e.getAttribute("min"))
            if e.hasAttribute("max"):
                args["max"] = float(e.getAttribute("max"))
            
            props.append(StkFloatProperty(**args))
        
        elif e.localName == "ColorProp":
            if e.hasAttribute("doc"):
                props.append(StkColorProperty(id=e.getAttribute("id"), name=e.getAttribute("name"), default=e.getAttribute("default"),
                                              doc=e.getAttribute("doc"), contextLevel=contextLevel))
            else:
                props.append(StkColorProperty(id=e.getAttribute("id"), name=e.getAttribute("name"), default=e.getAttribute("default"),
                                              contextLevel=contextLevel))
                
        elif e.localName == "BoolProp":
        
            args = dict()
            args["id"] = e.getAttribute("id")
            args["name"] = e.getAttribute("name")
            args["default"] = e.getAttribute("default")
            args["subproperties"] = parseProperties(e, contextLevel)
            args["contextLevel"] = contextLevel
            
            if e.hasAttribute("doc"):
                args["doc"] = e.getAttribute("doc")
            
            if e.hasAttribute("box"):
                args["box"] = bool(e.getAttribute("box"))
            
            props.append(StkBoolProperty(**args))

        elif e.localName == "ObjRefProp":
            args = dict()
            args["id"] = e.getAttribute("id")
            args["name"] = e.getAttribute("name")
            args["default"] = e.getAttribute("default")
            args["contextLevel"] = contextLevel
            
            global_env = {}
            local_env = {}
            exec("filterFn = " + e.getAttribute("filter"), global_env, local_env)
            args["filter"] = local_env["filterFn"]
            
            if e.hasAttribute("static_objects"):
                exec("static_objects_fn = " + e.getAttribute("static_objects"), global_env, local_env)
                args["static_objects"] = local_env["static_objects_fn"]
            
            if e.hasAttribute("doc"):
                args["doc"] = e.getAttribute("doc")
            
            if e.hasAttribute("unique_id_suffix"):
                args["unique_id_suffix"] = e.getAttribute("unique_id_suffix")
            
            if e.hasAttribute("obj_identifier"):
                exec("obj_identifier_fn = " + e.getAttribute("obj_identifier"), global_env, local_env)
                args["obj_identifier"] = local_env["obj_identifier_fn"]
            
            if e.hasAttribute("obj_text"):
                exec("obj_text_fn = " + e.getAttribute("obj_text"), global_env, local_env)
                args["obj_text"] = local_env["obj_text_fn"]
            
            props.append(StkObjectReferenceProperty(**args))
            
    return props
        
def getPropertiesFromXML(filename, contextLevel):
    node = xml.dom.minidom.parse(filename)
    for curr in node.childNodes:
        if curr.localName == "Properties":
            return parseProperties(curr, contextLevel)
    raise Exception("No <Properties> node in " + filename)

import os.path

datapath = None
for curr in bpy.utils.script_paths():
    if os.path.exists(os.path.join(curr, "addons", "stkdata")):
        datapath = os.path.join(curr, "addons", "stkdata")
        break

if datapath is None:
    print("Make sure the stkdata folder is installed, cannot locate it!!")

SCENE_PROPS = getPropertiesFromXML(os.path.join(datapath, "stk_panel_parameters.xml"), contextLevel=CONTEXT_SCENE)
STK_PER_OBJECT_TRACK_PROPERTIES = getPropertiesFromXML(os.path.join(datapath, "stk_object_parameters.xml"), contextLevel=CONTEXT_OBJECT)
STK_MATERIAL_PROPERTIES = getPropertiesFromXML(os.path.join(datapath, "stk_material_parameters.xml"), contextLevel=CONTEXT_MATERIAL)


# ==== PANEL BASE ====
class PanelBase:
    
    def recursivelyAddProperties(self, properties, layout, obj, contextLevel):
        
        for id in properties.keys():
            curr = properties[id]
            
            row = layout.row()
            
            if isinstance(curr, StkBoolProperty):
                
                 split = row.split(0.8)
                
                 split.label(text=curr.name)
                 
                 state = "false"
                 icon = 'CHECKBOX_DEHLT'
                 if id in obj:
                     state = obj[id]
                     if state == "true":
                         icon = 'CHECKBOX_HLT'
                 split.operator("screen.stk_toggle_bool_"+str(contextLevel)+"_"+id, text="                ", icon=icon, emboss=False)
                 
                 if state == "true":
                     if len(curr.subproperties) > 0:
                         if curr.box:
                             box = layout.box()
                             self.recursivelyAddProperties(curr.subproperties, box, obj, contextLevel)
                         else:
                             self.recursivelyAddProperties(curr.subproperties, layout, obj, contextLevel)
                 
            elif isinstance(curr, StkColorProperty):
                row.label(text=curr.name)
                if curr.id in obj:
                    row.prop(obj, '["' + curr.id + '"]', text="")
                    row.operator("screen.apply_color_"+curr.id, text="", icon='COLOR')
            
            elif isinstance(curr, StkCombinableEnumProperty):
                
                row.label(text=curr.name)
                
                if curr.id in obj:
                    curr_val = obj[curr.id]
                    
                    for value_id in curr.values:
                        icon = 'CHECKBOX_DEHLT'
                        if value_id in curr_val:
                            icon = 'CHECKBOX_HLT'
                        row.operator("screen.stk_set_"+id+"_"+value_id, text=curr.values[value_id].name, icon=icon)
                
            elif isinstance(curr, StkEnumProperty):
                
                row.label(text=curr.name)
                
                if id in obj:
                    curr_value = obj[id]
                else:
                    curr_value = ""
                
                label = curr_value
                if curr_value in curr.values:
                    label = curr.values[curr_value].name
                
                row.operator_menu_enum(curr.getOperatorName(), property="value", text=label)
                
                if curr_value in curr.values and len(curr.values[curr_value].subproperties) > 0:
                    box = layout.box()
                    self.recursivelyAddProperties(curr.values[curr_value].subproperties, box, obj, contextLevel)
            
            elif isinstance(curr, StkObjectReferenceProperty):
                
                row.label(text=curr.name)
              
                if curr.id in obj:
                    row.prop(obj, '["' + curr.id + '"]', text="")
                    row.menu("screen.stk_object_menu_" + curr.id + curr.unique_id_suffix, text="", icon='TRIA_DOWN')
              
            else:
                row.label(text=curr.name)
                
                # String or int or float property (Blender chooses the correct widget from the type of the ID-property)
                if curr.id in obj:
                    if "min" in dir(curr) and "max" in dir(curr) and curr.min is not None and curr.max is not None:
                        row.prop(obj, '["' + curr.id + '"]', text="", slider=True)
                    else:
                        row.prop(obj, '["' + curr.id + '"]', text="")

# ==== OBJECT PANEL ====
class SuperTuxKartObjectPanel(bpy.types.Panel, PanelBase):
    bl_label = "SuperTuxKart Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
    
        layout = self.layout
        
        is_track = ("is_stk_track" in context.scene and context.scene["is_stk_track"] == "true")
        is_kart = ("is_stk_kart" in context.scene and context.scene["is_stk_kart"] == "true")

        if not is_track and not is_kart:
            layout.label("(Not a SuperTuxKart scene)")
            return
        
        obj = context.object
        
        if obj is not None:
            if is_track:
                properties = OrderedDict([])
                for curr in STK_PER_OBJECT_TRACK_PROPERTIES:
                    properties[curr.id] = curr
                self.recursivelyAddProperties(properties, layout, obj, CONTEXT_OBJECT)
                
            if is_kart:
                properties = OrderedDict([])
                for curr in STK_PER_OBJECT_KART_PROPERTIES:
                    properties[curr.id] = curr
                self.recursivelyAddProperties(properties, layout, obj, CONTEXT_OBJECT)


# ==== SCENE PANEL ====
class SuperTuxKartScenePanel(bpy.types.Panel, PanelBase):
    bl_label = "SuperTuxKart Scene Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
                                        
    def draw(self, context):
        layout = self.layout
        
        obj = context.scene
        
        if obj is not None:
            
            properties = OrderedDict([])
            for curr in SCENE_PROPS:
                properties[curr.id] = curr
            
            self.recursivelyAddProperties(properties, layout, obj, CONTEXT_SCENE)


# ==== IMAGE PANEL ====
def createPreviewTexture():
    bpy.ops.texture.new()
    bpy.data.textures[-1].name = "STKPreviewTexture"
    bpy.data.textures["STKPreviewTexture"].type = 'IMAGE'
    bpy.data.textures["STKPreviewTexture"].use_preview_alpha = True

createPreviewTexture()

import os

class ImagePickerMenu(bpy.types.Menu):    
    bl_idname = "scene.stk_image_menu"
    bl_label  = "SuperTuxKart Image Menu"
    
    def draw(self, context):
        objects = context.scene.objects
        
        layout = self.layout
        row = layout.row()
        col = row.column()

        for i,curr in enumerate(bpy.data.images):
            
            if (i % 20 == 0):
                col = row.column()
            
            col.operator("scene.stk_select_image", text=curr.name).name=curr.name

bpy.utils.register_class(ImagePickerMenu)

class STK_SelectImage(bpy.types.Operator):
    bl_idname = ("scene.stk_select_image")
    bl_label = ("STK Object :: select image")
    
    name = bpy.props.StringProperty()
    
    def execute(self, context):
        global selected_image
        context.scene['selected_image'] = self.name
        
        if "STKPreviewTexture" not in bpy.data.textures:
            createPreviewTexture()

        if "STKPreviewTexture" in bpy.data.textures:
            if self.name in bpy.data.images:
                bpy.data.textures["STKPreviewTexture"].image = bpy.data.images[self.name]
            else:
                bpy.data.textures["STKPreviewTexture"].image = None
        else:
            print("STK Panel : can't create preview texture!")
        
        if self.name in bpy.data.images:
            
            properties = OrderedDict([])
            for curr in STK_MATERIAL_PROPERTIES:
                properties[curr.id] = curr
            
            createProperties(bpy.data.images[self.name], properties)
        
        return {'FINISHED'}

bpy.utils.register_class(STK_SelectImage)

class SuperTuxKartImagePanel(bpy.types.Panel, PanelBase):
    bl_label = "SuperTuxKart Image Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
    m_current_image = ''
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        
        if "STKPreviewTexture" in bpy.data.textures:
            layout.template_preview(bpy.data.textures["STKPreviewTexture"])
        else:
            layout.label("Sorry, no image preview available")
    
        label = "Select an image"
        if 'selected_image' in context.scene:
            label = context.scene['selected_image']
        
        self.m_op_name = "scene.stk_image_menu"
        #row.label(label)
        row.menu(self.m_op_name, text=label)
        
        obj = getObject(context, CONTEXT_MATERIAL)
        if obj is not None:
            
            properties = OrderedDict([])
            for curr in STK_MATERIAL_PROPERTIES:
                properties[curr.id] = curr
                
            self.recursivelyAddProperties(properties, layout, obj, CONTEXT_MATERIAL)


class STK_AddObject(bpy.types.Operator):
    bl_idname = ("scene.stk_add_object")
    bl_label = ("STK Object :: add object")
    
    name = bpy.props.StringProperty()
    
    value = bpy.props.EnumProperty(attr="values", name="values", default='banana',
                                           items=[('banana', 'Banana', 'Banana'),
                                                  ('item', 'Item (Gift Box)', 'Item (Gift Box)'),
                                                  ('nitro_big', 'Nitro (Big)', 'Nitro (big)'),
                                                  ('nitro_small', 'Nitro (Small)', 'Nitro (Small)'),
                                                  ('particle_emitter', 'Particle Emitter', 'Particle Emitter'),
                                                  ('sfx_emitter', 'Sound Emitter', 'Sound Emitter'),
                                                  ('start', 'Start position (for battle mode)', 'Start position (for battle mode)')
                                                  ])

    def execute(self, context):
        bpy.ops.object.add(type='EMPTY', location=bpy.data.scenes[0].cursor_location)
                
        for curr in bpy.data.objects:
            if curr.type == 'EMPTY' and curr.select:
                # FIXME: create associated subproperties if any
                curr['type'] = self.value
                
                if self.value == 'item':
                    curr.empty_draw_type = 'CUBE'
                elif self.value == 'nitro_big' or self.value == 'nitro_small' :
                    curr.empty_draw_type = 'CONE'
                elif self.value == 'sfx_emitter':
                    curr.empty_draw_type = 'SPHERE'
                    
                for prop in STK_PER_OBJECT_TRACK_PROPERTIES:
                    if prop.name == "Type":
                        createProperties(curr, prop.values[self.value].subproperties)
                        break
            
                break
        
        return {'FINISHED'}

bpy.utils.register_class(STK_AddObject)

def menu_func_add_banana(self, context):
    self.layout.operator_menu_enum("scene.stk_add_object", property="value", text="STK", icon='AUTO')
    
def register():
    bpy.types.INFO_MT_add.append(menu_func_add_banana)
    bpy.utils.register_module(__name__)

def unregister():
    pass


if __name__ == "__main__":
    register()

def unregister():
    pass
