import bpy
 

# ==== TYPE OPERATORS ====
class STK_TypeUnset(bpy.types.Operator):
    bl_idname = ("screen.stk_unset_type")
    bl_label = ("STK Object :: unset type")
    
    def execute(self, context):
        obj = context.object
        obj["type"] = ""
        return {'FINISHED'}

#! @see StkEnumProperty
class StkEnumChoice:
    
    #! @param name          User-visible name for this property
    #! @param subproperties A dictionary of type { 'name' : StkProperty(...) }. Contains the
    #                       properties that are to be shown when this enum item is selected
    def __init__(self, name, subproperties):
        self.name = name
        self.subproperties = subproperties

#! The base class for all properties
class StkProperty:
    def __init__(self, id, name, default):
        self.name = name
        self.id = id
        self.default = default


#! An enum property
class StkEnumProperty(StkProperty):
    
    #! @param name   User-visible name for this property
    #! @param values A dictionnary of type { 'value' : StkEnumChoice(...) }
    #! @note         The first value will be used by default
    def __init__(self, id, name, values, default):
        super(StkEnumProperty, self).__init__(id, name, default)
        self.values = values
        
        default_value = default
        
        values_for_blender_unsorted = []
        for curr_val in values.keys():
            curr_obj = values[curr_val]
            values_for_blender_unsorted.append( (curr_val, curr_obj.name, curr_obj.name) )
        
        values_for_blender = sorted(values_for_blender_unsorted, key=lambda k: k[1])
        
        # Create operator for this combo
        class STK_SetComboValue(bpy.types.Operator):
        
            value = bpy.props.EnumProperty(attr="values", name="values", default=default_value,
                                           items=values_for_blender)
            
            bl_idname = ("screen.stk_set_"+id)
            bl_label  = ("SuperTuxKart set "+id)
            
            m_property_id = id
            m_items_val = values_for_blender
            m_values = values
            
            def createProperties(self, object, props):
                for p in props.keys():
                    
                    if not p in object:
                        # create property by setting default  value
                        v = props[p].default
                        object[p] = v
                        
                        if isinstance(props[p], StkEnumProperty):
                            if v in props[p].values:
                                self.createProperties(object, props[p].values[v].subproperties)
                            
            def execute(self, context):
                
                # Set the property
                object = context.object
                object[self.m_property_id] = self.value
                
                # If sub-properties are needed, create them
                if self.value in self.m_values:
                    self.createProperties(object, self.m_values[self.value].subproperties)
                
                return {'FINISHED'}

#! A floating-point property
class StkFloatProperty(StkProperty):
    
    #! @param name   User-visible name for this property
    def __init__(self, id, name, default=0.0):
        super(StkFloatProperty, self).__init__(id, name, default)
        self.default

#! An integer property
class StkIntProperty(StkProperty):
    
    #! @param name   User-visible name for this property
    def __init__(self, id, name, default=0):
        super(StkIntProperty, self).__init__(id, name, default)

#! A boolean property
class StkBoolProperty(StkProperty):
    
    #! A floating-point property
    def __init__(self, id, name, default=False):
        super(StkBoolProperty, self).__init__(id, name, default)

#! A color property
class StkColorProperty(StkProperty):
    
    #! A floating-point property
    def __init__(self, id, name, default=[255,255,255]):
        super(StkColorProperty, self).__init__(id, name, default)


# Properties when the "type" property is an end-camera
camera_properties = {'start' : StkFloatProperty(id='start', name="Start Sphere Radius", default=10.0)
                    }

# Property when type="object"
object_properties = {'name'        : StkProperty('name', "Name", ""),
                     'interaction' : StkEnumProperty('interaction', "Interaction",
                                         {'ghost'  : StkEnumChoice("Ghost", {}),
                                          'static' : StkEnumChoice("Static (wont move)", {}),
                                          'move'   : StkEnumChoice("Movable by player",
                                              {'mass'  : StkFloatProperty(id='mass', name="Mass (kg)", default=100.0),
                                               'shape' : StkEnumProperty(id='shape', name="Shape",
                                                  values={'coneX'     : StkEnumChoice("Cone (X)", {}),
                                                          'coneY'     : StkEnumChoice("Cone (Y)", {}),
                                                          'coneZ'     : StkEnumChoice("Cone (Z)", {}),
                                                          'cylinderX' : StkEnumChoice("Cylinder (X)", {}),
                                                          'cylinderY' : StkEnumChoice("Cylinder (Y)", {}),
                                                          'cylinderZ' : StkEnumChoice("Cylinder (Z)", {}),
                                                          'box'       : StkEnumChoice("Box", {}),
                                                          'sphere'    : StkEnumChoice("Sphere", {})
                                                         }, default='box')
                                              })
                                         }, 'static')
                    }

# The 'type' property
type = StkEnumProperty('type', "Type",
                       {''                 : StkEnumChoice('None', {}),
                        'banana'           : StkEnumChoice('Banana', {}),
                        'billboard'        : StkEnumChoice('Billboard', {}),
                        'check'            : StkEnumChoice('Checkline',
                                                 {'name'     : StkProperty(id='name', name="Name", default=""),
                                                  'activate' : StkProperty(id='activate', name="Activate", default="")
                                                  #'toggle'  : Stkproperty("Toggle"),
                                                  #'inner_radius' : StkFloatProperty("Color radius"),
                                                  #'color'        : 
                                                 }),
                        'driveline'        : StkEnumChoice('Driveline (additional)',
                                                 {'invisible' : StkBoolProperty(id='invisible', name="Invisible", default=False),
                                                  'ai_ignore' : StkBoolProperty(id='ai_ignore', name="Ignored by AIs", default=False)
                                                 }),
                        'maindriveline'    : StkEnumChoice('Driveline (main)',
                                                 {'activate' : StkProperty(id='activate', name="Activate", default="")
                                                 }),
                        'fixed'            : StkEnumChoice('End Camera (Fixed)', camera_properties),
                        'ahead'            : StkEnumChoice('End Camera (Look Ahead)', camera_properties),
                        'ignore'           : StkEnumChoice('Ignore', {}),
                        'item'             : StkEnumChoice('Item (Gift Box)', {}),
                        'lap'              : StkEnumChoice('Lap line',
                                                 {'activate' : StkProperty(id='activate', name="Activate", default="")
                                                  #'toggle'  : Stkproperty("Toggle"),
                                                  #'inner_radius' : StkFloatProperty("Color radius"),
                                                  #'color'        : 
                                                 }),
                        'nitro_big'        : StkEnumChoice('Nitro (big)', {}),
                        'nitro_small'      : StkEnumChoice('Nitro (small)', {}),
                        'object'           : StkEnumChoice('Object', object_properties),
                        'particle_emitter' : StkEnumChoice('Particle Emitter',
                                                 {'kind' : StkProperty(id='kind', name="Particle File", default="smoke.xml")
                                                 }),
                        'sun'              : StkEnumChoice('Sun',
                                                 {'ambient'  : StkColorProperty('ambient', "Ambient Color"),
                                                  'diffuse'  : StkColorProperty('diffuse', "Diffuse Color"),
                                                  'specular' : StkColorProperty('specular', "Specular Color")
                                                 }),
                        'water'            : StkEnumChoice('Water',
                                                 {'name'     : StkProperty(id='name', name="Name", default=""),
                                                  'height'   : StkFloatProperty('height', "Waves Height", 1.0),
                                                  'speed'    : StkFloatProperty('speed', "Waves Speed", 200.0),
                                                  'length'   : StkFloatProperty('length', "Waves Length", 10.0)
                                                 })
                       }, '')

STK_PER_OBJECT_PROPERTIES = {'type' : type}

# ==== OTHER OPERATORS ====

class STK_TypeSetAnimTex(bpy.types.Operator):
    bl_idname = ("screen.stk_set_animtex")
    bl_label = ("STK Object :: set animtex")
    
    def execute(self, context):
        obj = context.object
        
        if "anim_texture" not in obj:
            obj["anim_texture"] = ""
        
        if "anim_dx" not in obj:
            obj["anim_dx"] = 0.0
        
        if "anim_dy" not in obj:
            obj["anim_dy"] = 0.0
        
        return {'FINISHED'}


# ==== PANEL ====
class OBJECT_PT_hello(bpy.types.Panel):
    bl_label = "SuperTuxKart Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def recursivelyAddProperties(self, properties, layout, obj):
        
        for id in properties.keys():
            curr = properties[id]
            
            row = layout.row()
            row.label(text=curr.name)
            
            if isinstance(curr, StkEnumProperty):
                if id in obj:
                    curr_value = obj[id]
                else:
                    curr_value = ""
                
                label = curr_value
                if curr_value in curr.values:
                    label = curr.values[curr_value].name
                
                row.operator_menu_enum("screen.stk_set_"+id, property="value", text=label)
                
                if curr_value in curr.values and len(curr.values[curr_value].subproperties) > 0:
                    box = layout.box()
                    self.recursivelyAddProperties(curr.values[curr_value].subproperties, box, obj)
                    
            else:
                # String or int or float property (Blender chooses the correct widget from the type of the ID-property)
                if curr.id in obj:
                    row.prop(obj, '["' + curr.id + '"]', text="")
                
    def draw(self, context):
        layout = self.layout
 
        obj = context.object


        self.recursivelyAddProperties(STK_PER_OBJECT_PROPERTIES, layout, obj)
            
        
        # ==== Anim Texture group ====
        box = layout.box()
        
        row = box.row()
        row.label("Animated Texture")
        
        row = box.row()
        row.operator("screen.stk_set_animtex", text="Enable Animated Texture")
 
        if "anim_texture" in obj:
            try:
                row = box.row()
                row.prop(obj, '["anim_texture"]', text="Animated Texture")
            except:
                pass
        if "anim_dx" in obj:
            try:
                row = box.row()
                row.prop(obj, '["anim_dx"]', text="X Speed")
            except:
                pass
        if "anim_dy" in obj:
            try:
                row = box.row()
                row.prop(obj, '["anim_dy"]', text="Y Speed")
            except:
                pass


def register():
    bpy.utils.register_module(__name__)

register()
