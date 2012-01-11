
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
                 obj_text=lambda self, obj: (obj.name + (" (" + obj["name"] + ")") if "name" in obj else "")):
        super(StkObjectReferenceProperty, self).__init__(id, name, default)
        self.doc = doc
        self.unique_id_suffix = unique_id_suffix
        
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

# Properties when the "type" property is an end-camera
camera_properties = [StkFloatProperty(id='start', name="Start Sphere Radius", default=10.0)]

# Property when type="object"
object_properties = [
         StkProperty('name', "Name", "", doc="Name of this object (objects with the same name are exported as a single file)"),
         StkEnumProperty('interaction', "Interaction",
                             {'ghost'  : StkEnumChoice("Ghost", [], doc="This object will be non-physical (player can drive through it)"),
                              'static' : StkEnumChoice("Static (wont move)", subproperties=
                                             [StkEnumProperty(id='shape', name="Shape (if animated object)", contextLevel=CONTEXT_OBJECT, unique_prefix="static",
                                                    values={'coneX'     : StkEnumChoice("Cone (X)",     []),
                                                            'coneY'     : StkEnumChoice("Cone (Y)",     []),
                                                            'coneZ'     : StkEnumChoice("Cone (Z)",     []),
                                                            'cylinderX' : StkEnumChoice("Cylinder (X)", []),
                                                            'cylinderY' : StkEnumChoice("Cylinder (Y)", []),
                                                            'cylinderZ' : StkEnumChoice("Cylinder (Z)", []),
                                                            'box'       : StkEnumChoice("Box",          []),
                                                            'sphere'    : StkEnumChoice("Sphere",       []),
                                                            'exact'     : StkEnumChoice("Exact",        [])
                                                           }, default='box', doc="Shape to use in the physics engine to represent this object"),
                                                StkProperty('if',    "Visible if...", "", doc="Make this object conditionally visible"),
                                                StkProperty('ifnot', "Visible if not...", "", doc="Make this object conditionally visible")
                                              ],
                                              doc="This object will stay in place, if the user drives on this object they will 'hit a wall'"),
                              'move'   : StkEnumChoice("Movable by player",
                                  [StkFloatProperty(id='mass', name="Mass (kg)", default=100.0, min=0.0, doc="How heavy the object is"),
                                    StkEnumProperty(id='shape', name="Shape", contextLevel=CONTEXT_OBJECT, unique_prefix="move",
                                                    values={'coneX'     : StkEnumChoice("Cone (X)",     []),
                                                            'coneY'     : StkEnumChoice("Cone (Y)",     []),
                                                            'coneZ'     : StkEnumChoice("Cone (Z)",     []),
                                                            'cylinderX' : StkEnumChoice("Cylinder (X)", []),
                                                            'cylinderY' : StkEnumChoice("Cylinder (Y)", []),
                                                            'cylinderZ' : StkEnumChoice("Cylinder (Z)", []),
                                                            'box'       : StkEnumChoice("Box",          []),
                                                            'sphere'    : StkEnumChoice("Sphere",       [])
                                                           }, default='box', doc="Shape to use in the physics engine to represent this object")
                                  ], doc="The player will be able to move this object around by pushing it"),
                               'reset' : StkEnumChoice("Reset player", subproperties=
                                                       [StkEnumProperty(id='shape', name="Shape", contextLevel=CONTEXT_OBJECT, unique_prefix="itrc_reset",
                                                             values={'coneX'     : StkEnumChoice("Cone (X)",     []),
                                                                     'coneY'     : StkEnumChoice("Cone (Y)",     []),
                                                                     'coneZ'     : StkEnumChoice("Cone (Z)",     []),
                                                                     'cylinderX' : StkEnumChoice("Cylinder (X)", []),
                                                                     'cylinderY' : StkEnumChoice("Cylinder (Y)", []),
                                                                     'cylinderZ' : StkEnumChoice("Cylinder (Z)", []),
                                                                     'box'       : StkEnumChoice("Box",          []),
                                                                     'sphere'    : StkEnumChoice("Sphere",       []),
                                                                     'exact'     : StkEnumChoice("Exact",        [])
                                                                    }, default='box', doc="Shape to use in the physics engine to represent this object")
                                                       ], doc="The player will be resetted when touching this object")
                             },
                             contextLevel=CONTEXT_OBJECT, default='static',
                             doc="How this object should interact with other objects in the physics engine")
        ]

# The 'type' property
type = StkEnumProperty('type', "Type",
       {''                 : StkEnumChoice('None',      [], doc="Nothing special about this object"),
        'none'             : StkEnumChoice('None',      [], doc="Nothing special about this object"),
        'banana'           : StkEnumChoice('Banana',    [], doc="A banana object that needs to be avoided (apply to an Empty)"),
        'billboard'        : StkEnumChoice('Billboard',
                                 [
                                             StkBoolProperty(id='fadeout', name="Fadeout when close", default="false",
                                                             contextLevel=CONTEXT_OBJECT, doc="Make this billboard fade out when approaching it",
                                                             subproperties=[StkFloatProperty(id='start', name="Start", default=1.0, min=0.0, max=200.0,
                                                                                             doc="Distance from the camera at which the billboard is no more visible"),
                                                                            StkFloatProperty(id='end', name="End", default=15.0, min=0.0, max=200.0,
                                                                                             doc="Distance from the camera at which the billboard is fully visible"),
                                                                           ])
                                 ], doc="A flat quad that will always face the camera"),
        'check'            : StkEnumChoice('Checkline',
                                 [               StkProperty(id='name', name="Name", default="", doc="Name of the checkline"),
                                  StkObjectReferenceProperty(id='activate', unique_id_suffix="_checkline", name="Activate", default="",
                                                             contextLevel=CONTEXT_OBJECT, static_objects=[("lap","Lap")],
                                                             filter=lambda self, o : 'type' in o and o['type'] == 'check',
                                                             doc="Which check structure to activate when crossing this checkline")
                                  #'toggle'  : Stkproperty("Toggle"),
                                  #'inner_radius' : StkFloatProperty("Color radius"),
                                  #'color'        : 
                                 ], doc="A checkline that the player must cross (used to forbid shortcuts)"),
        'driveline'        : StkEnumChoice('Driveline (additional)',
                                 [StkBoolProperty(id='invisible', name="Invisible",      default="false",
                                                  contextLevel=CONTEXT_OBJECT, doc="If checked, this path will not appear in the minimap"),
                                  StkBoolProperty(id='ai_ignore', name="Ignored by AIs", default="false",
                                                  contextLevel=CONTEXT_OBJECT, doc="If checked, AIs will not drive on this path")
                                 ], doc="Driveline used to mark an alternate path"),
        'maindriveline'    : StkEnumChoice('Driveline (main)',
                                 [StkObjectReferenceProperty(id='activate', unique_id_suffix="_maindriveline", name="Activate",
                                                             default="", contextLevel=CONTEXT_OBJECT,
                                                             filter=lambda self, o : 'type' in o and o['type'] == 'check',
                                                             doc="Which check structure to activate when crossing the lap line")
                                 ]),
        'fixed'            : StkEnumChoice('End Camera (Fixed)',      camera_properties, doc="An end camera that stays in place"),
        'ahead'            : StkEnumChoice('End Camera (Look Ahead)', camera_properties, doc="An end camera that follows the kart"),
        'ignore'           : StkEnumChoice('Ignore',          [], doc="An object that is not exported and will not appear in-game"),
        'item'             : StkEnumChoice('Item (Gift Box)', [], doc="A gift box containing a random collectible (apply to an Empty)"),
        'lap'              : StkEnumChoice('Lap line',
                                 [StkObjectReferenceProperty(id='activate', unique_id_suffix="_lap", name="Activate", default="",
                                                             contextLevel=CONTEXT_OBJECT,
                                                             filter=lambda self, o : 'type' in o and o['type'] == 'check',
                                                             doc="Which check structure to activate when crossing the lap line")
                                 ], doc="An extension to the factory lap line"),
        'lod_instance'     : StkEnumChoice('LOD Instance',
                                 [StkObjectReferenceProperty( id='lod_name', name="LOD Group Name", default="SomeModel",
                                                              doc="Name of the LOD group this object is an instance of",
                                                              contextLevel=CONTEXT_OBJECT,
                                                              filter=lambda self, o: "lod_name" in o,
                                                              obj_identifier=lambda self, o : o["lod_name"],
                                                              obj_text=lambda self, o : o["lod_name"]),
                                                StkProperty('if',    "Visible if...", "", doc="Make this object conditionally visible"),
                                                StkProperty('ifnot', "Visible if not...", "", doc="Make this object conditionally visible")
                                 ], doc="A LOD (level-of-detail) instance, will display either of the LOD Models in this LOD group at this location"),
        'lod_model'        : StkEnumChoice('LOD Model',
                                 [StkFloatProperty( id='lod_distance', name="Distance",       default=60.0, min=0.0, max=5000.0,
                                                    doc="Distance from the camera at which this level of detail starts being used"),
                                       StkProperty( id='lod_name',     name="LOD Group Name", default="SomeModel",
                                                    doc="Name of the LOD group this object is part of"),
                                       StkProperty( id='name',         name="Model Filename", default="",
                                                    doc="Name of the model to export")
                                 ], doc="A LOD (level-of-detail) model (this model will not be visible in game, only LOD instances will)"),
        'nitro_big'        : StkEnumChoice('Nitro (big)',   [], doc="A big nitro collectible (apply to an Empty)"),
        'nitro_small'      : StkEnumChoice('Nitro (small)', [], doc="A small nitro collectible (apply to an Empty)"),
        'object'           : StkEnumChoice('Object', object_properties, doc="An (animatable) object that is exported to a separate model file"),
        'particle_emitter' : StkEnumChoice('Particle Emitter',
                                 [   StkProperty(id='kind',          name="Particle File", default="smoke.xml"),
                                  StkIntProperty(id='clip_distance', name="Clip Distance", default=0,
                                                 doc="If non-zero, the camera distance at which particles are hidden (for performance reasons)")
                                 ], doc="To be applied to an empty; particles will be emitted from this point"),
        'start'            : StkEnumChoice('Start position', subproperties=[StkIntProperty('start_index', "Start Index", 1,
                                                                                           doc="Start position index for battle mode")],
                                           doc="A start position for karts in battle mode (only useful if this track is an arena)"),
        'sfx_emitter'      : StkEnumChoice('Sound Emitter',
                                           [     StkProperty( id='sfx_filename', name="Sound File",   default="some_file.ogg",
                                                              doc="Filename of the sound to play"),
                                            StkFloatProperty( id='sfx_volume',   name="Sound volume", default=1.0, min=0.0, max=1.0),
                                            StkFloatProperty( id='sfx_rolloff',  name="Rolloff rate", default=0.1, min=0.0, max=2.5,
                                                              doc="How fast this sound decays when going farther from the emission point"),
                                            StkBoolProperty(  id='play_when_near', name="Play on approach",      default="false",
                                                              contextLevel=CONTEXT_OBJECT, doc="Play when the kart approaches this object",
                                                              subproperties=[StkFloatProperty('play_distance', "Play when at distance", 1.0,
                                                                                              doc="Distance at which the sound starts playing when approaching")]),
                                           ],
                                           doc="A sound will be heard when close to this point"),
        'sun'              : StkEnumChoice('Sun',
                                 [StkColorProperty('ambient',  "Ambient Color",  contextLevel=CONTEXT_OBJECT,
                                                   doc="Click here to pick an ambient color", default="120 120 120"),
                                  StkColorProperty('diffuse',  "Diffuse Color",  contextLevel=CONTEXT_OBJECT,
                                                   doc="Click here to pick a diffuse color"),
                                  StkColorProperty('specular', "Specular Color", contextLevel=CONTEXT_OBJECT,
                                                   doc="Click here to pick a specular color")
                                 ], doc="Set on a sun; used to specify intensity, direction and color of the ambient light in the track"),
        'water'            : StkEnumChoice('Water',
                                 [     StkProperty(id='name',   name="Name",         default="",                        doc="Name of the model to export"),
                                  StkFloatProperty(id='height', name="Waves Height", default=1.0,   min=0.0,            doc="Height of the waves"),
                                  StkFloatProperty(id='speed',  name="Waves Speed",  default=200.0, min=0.0, max=500.0, doc="Speed of the waves"),
                                  StkFloatProperty(id='length', name="Waves Length", default=10.0,  min=0.0,            doc="Length of the waves")
                                 ], doc="Animate the mesh with waves")
       }, contextLevel=CONTEXT_OBJECT, default='none', unique_prefix="track_", doc="SuperTuxKart Object Type")


STK_PER_OBJECT_TRACK_PROPERTIES = [
        type,
        StkBoolProperty(id='enable_anim_texture', name='Use animated Texture',  default="false", contextLevel=CONTEXT_OBJECT,
                        subproperties=[     StkProperty(id='anim_texture', name='Texture to animate', default="",
                                                       doc="Filename of the texture to animate"),
                                       StkFloatProperty(id='anim_dx', name='Animation X Speed',  default=0.0, min=0.0),
                                       StkFloatProperty(id='anim_dy', name='Animation Y Speed',  default=0.0, min=0.0)
                                       ], doc="Make a texture on this object move")
       ]

STK_PER_OBJECT_KART_PROPERTIES = [
        StkEnumProperty('type', "Type", values=OrderedDict([  (''      , StkEnumChoice('None',   [])),
                                                              ('none'  , StkEnumChoice('None',   [])),
                                                              ('wheel' , StkEnumChoice('Wheel',  [])),
                                                              ('ignore', StkEnumChoice('Ignore', []))
                                                            ]),
                        contextLevel=CONTEXT_OBJECT, default='none', unique_prefix="kart_", doc="Supertuxkart Object Type")
       ]

SKY_TYPES = {
        'none'   : StkEnumChoice('None', [], doc="No sky (useful for indoor scenes)"),
        'box'    : StkEnumChoice('Box',
                         [StkProperty(id='sky_texture2', name='Sky Texture Top',    default=""),
                          StkProperty(id='sky_texture3', name='Sky Texture Bottom', default=""),
                          StkProperty(id='sky_texture4', name='Sky Texture East',   default=""),
                          StkProperty(id='sky_texture5', name='Sky Texture West',   default=""),
                          StkProperty(id='sky_texture1', name='Sky Texture North',  default=""),
                          StkProperty(id='sky_texture6', name='Sky Texture South',  default="")
                         ]),
        'dome'   : StkEnumChoice('Dome',
                         [     StkProperty(id='sky_texture',         name='Sky Texture',           default=""),
                            StkIntProperty(id='sky_horizontal',      name='Horizontal Definition', default=20),
                            StkIntProperty(id='sky_vertical',        name='Vertical Definition',   default=20),
                          StkFloatProperty(id='sky_texture_percent', name='Sky Texture Percent',   default=1.0, min=0.0, max=1.0,
                                           doc="How much of the height of the texture is used"),
                          StkFloatProperty(id='sky_sphere_percent',  name='Sky Sphere Percent',    default=1.3, min=0.0, max=2.0,
                                           doc="1.0 : half-sphere; 2.0 : full sphere"),
                          StkFloatProperty(id='sky_speed_x',         name='Sky Speed X',           default=0.0, min=0.0, max=10.0,
                                           doc="Speed at which the sky moves horizontally"),
                          StkFloatProperty(id='sky_speed_y',         name='Sky Speed Y',           default=0.0, min=0.0, max=10.0,
                                           doc="Speed at which the sky moves vertically")
                         ]),
        'simple' : StkEnumChoice('Plain color',
                     [StkColorProperty(id="sky_color", name="Sky Color", default="77 104 255", contextLevel=CONTEXT_SCENE,
                                       doc="Click here to select the color of the sky")],
                     doc="A plain-color sky")
        }


FOG_PROPERTIES = [StkColorProperty(id='fog_color', name='Fog Color', default="0 0 0", contextLevel=CONTEXT_SCENE,
                                   doc="Click here to pick the color of the fog"),
                  StkFloatProperty(id='fog_start', name='Fog Start', default=50.0, min=0.0, max=1000.0,
                                   doc="Distance from camera at which fog starts dimming objects"),
                  StkFloatProperty(id='fog_end',   name='Fog End',   default=300.0, min=0.0, max=1000.0,
                                   doc="Distance from camera at which fog is so dense you can't see a thing")
                 ]

WEATHER = {'none' : StkEnumChoice("None",[]),
           'rain' : StkEnumChoice("Rain",[]),
           'snow' : StkEnumChoice("Snow",[])
          }

# these names are just waaaay too long to fit in the table below
k  = ['start_karts_per_row', 'start_forwards_distance', 'start_sidewards_distance', 'start_upwards_distance']
kk = ['Karts per row on start', 'Start Forwards Distance', 'Start Sidewards Distance', 'Start upwards distance']

STK_TRACK_WIDE_PROPERTIES = [
              StkProperty( id='name',          name='Name',            default='My New Track',
                           doc="Name of the track"),
              StkProperty( id='groups',        name='Groups',          default='standard',
                           doc="Tabs in track selection screen this track appears under"),
              StkProperty( id='designer',      name='Designer',        default=getpass.getuser(),
                           doc="Name of the person that made this track"),
              StkProperty( id='music',         name='Music',           default='kart_grand_prix.music',
                           doc="Music played in this track"),
              StkProperty( id='screenshot',    name='Screenshot',      default='screenshot.jpg',
                           doc="Name of the file that contains a screenshot of this track"),
          StkEnumProperty( id='sky_type',      name='Sky Type',        default='dome',
                           contextLevel=CONTEXT_SCENE,  values=SKY_TYPES, doc="The type of sky"),
          StkBoolProperty( id='arena',         name='Battle Arena',    default="false",
                           contextLevel=CONTEXT_SCENE,  doc="Whether this scene is a battle arena"),
          StkBoolProperty( id='fog',           name='Fog',             default='false',
                           contextLevel=CONTEXT_SCENE,  subproperties=FOG_PROPERTIES, doc="Whether to enable fog in the track"),
         StkFloatProperty( id='camera_far',    name='Camera Far Clip', default=1000.0,
                           doc="Distance from camera at which objects are clipped (no more visible)"),
           StkIntProperty( id=k[0],            name=kk[0],             default=2),
         StkFloatProperty( id=k[1],            name=kk[1],             default=1.1),
         StkFloatProperty( id=k[2],            name=kk[2],             default=1.1),
         StkFloatProperty( id=k[3],            name=kk[3],             default=1.1),
          StkEnumProperty( id='weather',       name='Weather',         default='none',
                           contextLevel=CONTEXT_SCENE, values=WEATHER, doc="The weather effect to use in this track")
        ]

COMPOSITING_VALUES = {'none'     : StkEnumChoice("None",              []),
                      'blend'    : StkEnumChoice("Alpha Blend",       [],
                                                 doc="Use transparency on this texture, using the alpha channel or a specified external mask"),
                      'test'     : StkEnumChoice("Alpha Test",        [],
                                                 doc="Use fully-opaque-or-fully-transparent transparency on this texture, using the alpha channel or a specified external mask"),
                      'coverage' : StkEnumChoice("Alpha to Coverage",        [],
                                                 doc="Like alpha testing but with softer edges"),
                      'additive' : StkEnumChoice("Additive Blending", [],
                                                 doc="Brighten up anything under by adding the current color on top (useful for fire or light)")
                     }

GFX_VALUES = {'none'     : StkEnumChoice("None",                  []),
              'bubble'   : StkEnumChoice("Bubble (wavy texture)", []),
              'water'    : StkEnumChoice("Water Splash",          [])
             }

SLOWDOWN_PROPERTIES = [
         StkFloatProperty( id='slowdown_time', name="Slowdown Time (seconds)",  default=1.0, min=0.0, max=10.0,
                           doc="Time it takes for speed to drop to its low point when driving here" ),
         StkFloatProperty( id='max_speed',     name="Maximum Speed (fraction)", default=1.0, min=0.0, max=1.0, 
                           doc="Fraction of the maximum speed can be reached when driving here" )
       ]

PARTICLE_PROPERTIES = [
                       StkProperty( id='particle_base',      name="Particles file",        default="smoke.xml",
                                    doc="Name of the XML file containing the description of particles to use on this terrain"),
         StkCombinableEnumProperty( id='particle_condition', name="Use particles when...", default="skid", contextLevel=CONTEXT_MATERIAL,
                                    values={'skid'  : StkEnumChoice('Skid',  [], doc="Use particle when skidding"),
                                            'drive' : StkEnumChoice('Drive', [], doc="Use particles during regular driving")})
       ]

long_names = ['zipper_max_speed_increase', "Zipper max speed increase", 'zipper_fade_out_time', "Zipper fade out time"]

ZIPPER_PROPERTIES = [
         StkFloatProperty( id='zipper_duration',   name="Zipper duration",   default=3.5,  min=0.0, max=10.0),
         StkFloatProperty( id=long_names[0],       name=long_names[1],       default=15.0, min=0.0, max=25.0),
         StkFloatProperty( id=long_names[2],       name=long_names[3],       default=3.0,  min=0.0, max=10.0),
         StkFloatProperty( id='zipper_speed_gain', name="Zipper speed gain", default=4.5,  min=0.0, max=10.0)
      ]

# TODO: only enable rolloff if positional is checked

SFX_PROPERTIES = [
             StkProperty( id='sfx_filename',   name="Sound File",               default="some_file.ogg"),
        StkFloatProperty( id='sfx_min_speed',  name="Minimum kart speed",       default=0.0),
        StkFloatProperty( id='sfx_max_speed',  name="Maximum kart speed",       default=0.0),
        StkFloatProperty( id='sfx_min_pitch',  name="Sound pitch at min speed", default=0.8, min=0.1, max=3.0,
                          doc="Pitch of the sound when the kart is going slowly (1.0 is no change, < 1.0 is lower pitch, > 1.0 is higher pitch)"),
        StkFloatProperty( id='sfx_max_pitch',  name="Sound pitch at max speed", default=1.2, min=0.1, max=3.0,
                          doc="Pitch of the sound when the kart is going fastly (1.0 is no change, < 1.0 is lower pitch, > 1.0 is higher pitch)"),
         StkBoolProperty( id='sfx_positional', name="Positional sound effect",  default="true", contextLevel=CONTEXT_MATERIAL,
                          doc="If true, the sound will get dimmer when far from camera, and with panning; if false, it's heard at centered pan and at full volume"),
        StkFloatProperty( id='sfx_rolloff',    name="Rolloff rate",             default=0.1, min=0.0, max=2.5,
                          doc="Speed at which the sound fades out as you stand further from the sound emitter")
      ]

COLLISION_DETECTION_PROPERTIES = [StkEnumProperty( id='collision_reaction', name="Action", default='none',  contextLevel=CONTEXT_MATERIAL,
                                                   values={'none' : StkEnumChoice("None", []),
                                                           'reset' : StkEnumChoice("Rescue kart", []),
                                                           'push' : StkEnumChoice("Push back kart", [])},
                                                   doc="How to react when kart touches this material"),
                                  StkProperty( id='collision_particles', name="Particles on hit", default="")]

STK_MATERIAL_PROPERTIES = [
        StkBoolProperty( id='fog',              name="Affected by fog (if any)",   default="true",  contextLevel=CONTEXT_MATERIAL,
                         doc="Whether this material is affected by fog (if there is fog in this track)"),
        StkBoolProperty( id='light',            name="Affected by lights",         default="true",  contextLevel=CONTEXT_MATERIAL,
                         doc="Whether this material is affected by lights and shadows"),
        StkBoolProperty( id='backface_culling', name="Backface Culling",           default="true",  contextLevel=CONTEXT_MATERIAL,
                         doc="If checked, this material will only be visible on the side of the normal"),
        StkBoolProperty( id='below_surface',    name="Below Surface",              default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="Used for the terrain under shallow water where you can drive"),
        StkBoolProperty( id='clampu',           name="Clamp texture horizontally", default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="if checked, this texture will not be repeated horizontally (if the UV texturing goes beyond the texture bounds)"),
        StkBoolProperty( id='clampv',           name="Clamp texture vertically",   default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="if checked, this texture will not be repeated vertically (if the UV texturing goes beyond the texture bounds)"),
        StkBoolProperty( id='collision_detect', name="Collision action",      default="false", contextLevel=CONTEXT_MATERIAL,
                         subproperties=COLLISION_DETECTION_PROPERTIES, doc="What happens when the kart touches/hits this material in any way"),
        StkEnumProperty( id='compositing',      name="Compositing Type",           default='none',  contextLevel=CONTEXT_MATERIAL,
                         values=COMPOSITING_VALUES, doc="How to composite this texture with what is behind it"),
        StkBoolProperty( id='disable_z_write',  name="Disable writing to Z-buffer",default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="disable writing to the Z buffer (useful for materials with transparency, if irrlicht fails to do proper alpha sorting, in order not to hide what is behind)"),
        StkBoolProperty( id='use_slowdown',     name="Enable Slowdown",            default="false", contextLevel=CONTEXT_MATERIAL,
                         subproperties=SLOWDOWN_PROPERTIES, doc="Whether to slow down the kart when driving on this material"),
        StkBoolProperty( id='falling_effect',   name="Falling Effect",             default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="Whether this material is the bottom of a pit (then camera will look down at kart falling when over it)"),
        StkEnumProperty( id='graphical_effect', name="Graphical Effect",           default='none',  contextLevel=CONTEXT_MATERIAL,
                         values=GFX_VALUES, doc="Select a special graphical effect"),
        StkBoolProperty( id='high_adhesion',    name="High tires adhesion",        default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="If checked, karts will have good grip on this surface and not slip, even at angles"),
        StkBoolProperty( id='ignore',           name="Ignore (ghost material)",    default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="Drive through this texture like it didn't exist (good for smoke, etc.)"),
        StkBoolProperty( id='additive_lightmap',name="Lightmap is additive",    default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="Make lightmap additive (only makes sense if this material has a lightmap)"),
            StkProperty( id='mask',             name="Mask image",                 default="",
                         doc="Greyscale image containing the alpha channel (transparency) for this image"),
        StkBoolProperty( id='use_normal_map',name="Normal Map",    default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="Use a normal map for this image",
                         subproperties=
                         [
                            StkProperty( id='normal_map',       name="Normal Map Image", default="",
                                         doc="Image containing the normal map for this texture (optional)"),
                            StkBoolProperty( id='normal_map_uv2',name="Use second UV layer",  default="false",
                                             contextLevel=CONTEXT_MATERIAL,
                                             doc="If checked, UV layer 2 will be used to map the normal map on the object")
                         ]),
        StkBoolProperty( id='particle',         name="Particle effect",            default="false", contextLevel=CONTEXT_MATERIAL,
                         subproperties=PARTICLE_PROPERTIES, doc="Whether to emit particles (e.g. smoke) when driving on this surface"),
        StkBoolProperty( id='use_sfx',          name="Play sound effect",          default="false", contextLevel=CONTEXT_MATERIAL,
                         subproperties=SFX_PROPERTIES, doc="Whether to play a sound when driving on this surface"),
        StkBoolProperty( id='reset',            name="Reset kart (on drive)",      default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="whether to rescue kart if it ends up [driving] on this surface"),
        StkBoolProperty( id='sphere',           name="Sphere mapping",             default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="use sphere mapping on this object (mainly used to simulate a reflection effect)"),
        StkBoolProperty( id='splatting',        name="Splatting",                  default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="Use splatting (multiple textures with smooth transitions)", subproperties=
                         [
                          StkProperty(id='splatting_texture_1', name="Red Texture",   default=""),
                          StkProperty(id='splatting_texture_2', name="Green Texture", default=""),
                          StkProperty(id='splatting_texture_3', name="Blue Texture",  default=""),
                          StkProperty(id='splatting_texture_4', name="Black Texture", default="")
                         ]),
        StkBoolProperty( id='surface',          name="Surface",                    default="false", contextLevel=CONTEXT_MATERIAL,
                         doc="whether this material is the surface of a water area"),
        StkBoolProperty( id='zipper',           name="Zipper (speed boost)",       default="false", contextLevel=CONTEXT_MATERIAL,
                         subproperties=ZIPPER_PROPERTIES, doc="Whether to get a speed boost when driving on this surface")
       ]

ENGINE_SOUNDS = {'large'    : StkEnumChoice("Large", []),
                 'small'    : StkEnumChoice("Small", [])
                }
                     

STK_KART_PROPERTIES = [
              StkProperty( id='name',          name='Name',                 default='My New Kart'),
              StkProperty( id='group',         name='Group',                default='standard'),
              StkProperty( id='icon',          name='Icon',                 default='icon.png',
                           doc="Filename of the icon to display in the kart selection screen"),
              StkProperty( id='minimap_icon',  name='Minimap Icon',         default='icon.png',
                           doc="Filename of the icon to display on the minimap"),
              StkProperty( id='shadow',        name='Shadow',               default='generic_shadow.png',
                           doc="Filename of the file containing the shadow of this kart"),
         StkColorProperty( id='color',         name="Color",                default="255 255 255", contextLevel=CONTEXT_SCENE,
                           doc="Color used to highlight the kart's icon in the interface"),
         StkFloatProperty( id='center_shift',  name="Gravity Center Shift", default=0.0,
                           doc="Can be used to lower the gravity center of the kart if it topples over too easily"),
          StkEnumProperty( id='engine_sfx',    name='Engine sound',         default='large', contextLevel=CONTEXT_SCENE,
                           values=ENGINE_SOUNDS)
        ]


SCENE_PROPS = [ StkBoolProperty(id='is_stk_track', name='Is a SuperTuxKart track', default='false', contextLevel=CONTEXT_SCENE,
                                subproperties=STK_TRACK_WIDE_PROPERTIES, box=False,
                                doc="Check this if this blender file is a SuperTuxKart track"),
                StkBoolProperty(id='is_stk_kart', name='Is a SuperTuxKart kart', default='false', contextLevel=CONTEXT_SCENE,
                                subproperties=STK_KART_PROPERTIES, box=False,
                                doc="Check this if this blender file is a SuperTuxKart kart")
              ]

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
