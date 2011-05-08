import bpy
from collections import OrderedDict
import getpass

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
    def __init__(self, id, name, values, objectLevel, default):
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
            m_object_level = objectLevel
            
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
                
                if self.m_object_level:
                    object = context.object
                else:
                    object = context.scene
                
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
    
    # (self, id, name, values, default):
    
    #! A floating-point property
    def __init__(self, id, name, objectLevel, default="false", subproperties={}):
        super(StkBoolProperty, self).__init__(id, name, default)
        
        self.subproperties = subproperties
        
        super_self = self
        
        # Create operator for this bool
        class STK_ToggleBoolValue(bpy.types.Operator):
        
            
            bl_idname = ("screen.stk_toggle_bool_"+id)
            bl_label  = ("SuperTuxKart toggle "+id)
            
            m_object_level = objectLevel
            m_property_id = id
            m_super_self = super_self
            
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
                
                if self.m_object_level:
                    object = context.object
                else:
                    object = context.scene
                
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
                    self.createProperties(object, self.m_super_self.subproperties)
                
                return {'FINISHED'}

#! A color property
class StkColorProperty(StkProperty):
    
    #! A floating-point property
    def __init__(self, id, name, objectLevel, default="255 255 255"):
        super(StkColorProperty, self).__init__(id, name, default)

        #! Color picker operator (TODO: this operator is mostly for backwards compatibility with our
        #                               blend files that come from 2.4; blender 2.5 has a color property
        #                               type we could use)
        class Apply_Color_Operator(bpy.types.Operator):
            bl_idname = ("screen.apply_color_"+id)
            bl_label = ("Apply Color")
           
            property_id = id
            
            m_object_level = objectLevel
           
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
                    if self.m_object_level:
                        object = context.object
                    else:
                        object = context.scene
                    
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
                
                if self.m_object_level:
                    object = context.object
                else:
                    object = context.scene
                
                object[self.property_id] = "%i %i %i" % (self.temp_color[0]*255, self.temp_color[1]*255, self.temp_color[2]*255)
                return {'FINISHED'}


# Properties when the "type" property is an end-camera
camera_properties = {'start' : StkFloatProperty(id='start', name="Start Sphere Radius", default=10.0)
                    }

# Property when type="object"
object_properties = OrderedDict([
         ('name'       , StkProperty('name', "Name", "")),
         ('interaction', StkEnumProperty('interaction', "Interaction",
                             {'ghost'  : StkEnumChoice("Ghost", {}),
                              'static' : StkEnumChoice("Static (wont move)", {}),
                              'move'   : StkEnumChoice("Movable by player",
                                  {'mass'  : StkFloatProperty(id='mass', name="Mass (kg)", default=100.0),
                                   'shape' : StkEnumProperty(id='shape', name="Shape", objectLevel=True,
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
                             }, objectLevel=True, default='static'))
        ])

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
                                 {'invisible' : StkBoolProperty(id='invisible', name="Invisible",      default="false",
                                                                objectLevel=True),
                                  'ai_ignore' : StkBoolProperty(id='ai_ignore', name="Ignored by AIs", default="false",
                                                                objectLevel=True)
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
                                 {'ambient'  : StkColorProperty('ambient',  "Ambient Color",  objectLevel=False),
                                  'diffuse'  : StkColorProperty('diffuse',  "Diffuse Color",  objectLevel=False),
                                  'specular' : StkColorProperty('specular', "Specular Color", objectLevel=False)
                                 }),
        'water'            : StkEnumChoice('Water', OrderedDict([
                                 ('name'  , StkProperty(id='name', name="Name", default="")),
                                 ('height', StkFloatProperty('height', "Waves Height", 1.0)),
                                 ('speed' , StkFloatProperty('speed', "Waves Speed", 200.0)),
                                 ('length', StkFloatProperty('length', "Waves Length", 10.0))
                                 ]))
       }, objectLevel=True, default='')


STK_PER_OBJECT_PROPERTIES = OrderedDict([
       ('type'               , type),
       ('enable_anim_texture', StkBoolProperty(id='enable_anim_texture', name='Use animated Texture', default="false", objectLevel=True,
             subproperties={'anim_texture' : StkProperty(id='anim_texture', name='Texture to animate', default=""),
                            'anim_dx'      : StkFloatProperty(id='anim_dx', name='Animation X Speed', default=0.0),
                            'anim_dy'      : StkFloatProperty(id='anim_dy', name='Animation Y Speed', default=0.0)
                            }))
        ])

SKY_TYPES = {
        'box'    : StkEnumChoice('Box', OrderedDict([
                     ('sky_texture1'       ,      StkProperty(id='sky_texture1',        name='Sky Texture 1',         default="")),
                     ('sky_texture2'       ,      StkProperty(id='sky_texture2',        name='Sky Texture 2',         default="")),
                     ('sky_texture3'       ,      StkProperty(id='sky_texture3',        name='Sky Texture 3',         default="")),
                     ('sky_texture4'       ,      StkProperty(id='sky_texture4',        name='Sky Texture 4',         default="")),
                     ('sky_texture5'       ,      StkProperty(id='sky_texture5',        name='Sky Texture 5',         default="")),
                     ('sky_texture6'       ,      StkProperty(id='sky_texture6',        name='Sky Texture 6',         default=""))])),
        'dome'   : StkEnumChoice('Dome', OrderedDict([
                     ('sky_texture'        ,      StkProperty(id='sky_texture',         name='Sky Texture',           default="")),
                     ('sky_horizontal'     ,   StkIntProperty(id='sky_horizontal',      name='Horizontal Definition', default=20)),
                     ('sky_vertical'       ,   StkIntProperty(id='sky_vertical',        name='Vertical Definition',   default=20)),
                     ('sky_texture_percent', StkFloatProperty(id='sky_texture_percent', name='Sky Texture Percent',   default=1.0))])),
        'simple' : StkEnumChoice('Plain color',
                     {'sky_color' : StkColorProperty(id="sky_color", name="Sky Color", default="77 104 255", objectLevel=False)})
        }


FOG_PROPERTIES = {'fog_color' : StkColorProperty(id='fog_color', name='Fog Color', default="0 0 0", objectLevel=False),
                  'fog_start' : StkFloatProperty(id='fog_start', name='Fog Start', default=50.0),
                  'fog_end'   : StkFloatProperty(id='fog_end',   name='Fog End',   default=300.0)
                 }

WEATHER = {'none' : StkEnumChoice("None",{}),
           'rain' : StkEnumChoice("Rain",{}),
           'snow' : StkEnumChoice("Snow",{})
          }

# these names are just waaaay too long to fit in the table below
k  = ['start-karts-per-row', 'start-forwards-distance', 'start-sidewards-distance', 'start-upwards-distance']
kk = ['Karts per row on start', 'Start Forwards Distance', 'Start Sidewards Distance', 'Start upwards distance']

STK_TRACK_WIDE_PROPERTIES = OrderedDict([
        ('name',               StkProperty( id='name',          name='Name',            default='My New Track')),
        ('groups',             StkProperty( id='groups',        name='Groups',          default='standard')),
        ('designer',           StkProperty( id='designer',      name='Designer',        default=getpass.getuser())),
        ('music',              StkProperty( id='music',         name='Music',           default='kart_grand_prix.music')),
        ('screenshot',         StkProperty( id='screenshot',    name='Screenshot',      default='screenshot.jpg')),
        ('sky_type',       StkEnumProperty( id='sky_type',      name='Sky Type',        default='dome',        objectLevel=False,  values=SKY_TYPES)),
        ('arena',          StkBoolProperty( id='arena',         name='Battle Arena',    default="false",       objectLevel=False)),
        ('fog',            StkBoolProperty( id='fog',           name='Fog',             default='false',       objectLevel=False,  subproperties=FOG_PROPERTIES)),
        ('ambient_color', StkColorProperty( id='ambient_color', name="Ambient Color",   default="255 255 255", objectLevel=False)),
        ('camera_far',    StkFloatProperty( id='camera_far',    name='Camera Far Clip', default=1000.0)),
        (k[0],              StkIntProperty( id=k[0],            name=kk[0],             default=2)),
        (k[1],            StkFloatProperty( id=k[1],            name=kk[1],             default=1.1)),
        (k[2],            StkFloatProperty( id=k[2],            name=kk[2],             default=1.1)),
        (k[3],            StkFloatProperty( id=k[3],            name=kk[3],             default=1.1)),
        ('weather',        StkEnumProperty( id='weather',       name='Weather',         default='none',        objectLevel=False, values=WEATHER))
        ])

TRACK = {'is_stk_track' : StkBoolProperty(id='is_stk_track', name='Is a SuperTuxKart track', default='false', objectLevel=False,
                                         subproperties=STK_TRACK_WIDE_PROPERTIES)}

# TODO
# weather : rain, snow


# ==== PANEL BASE ====
class PanelBase:
    
    def recursivelyAddProperties(self, properties, layout, obj):
        
        for id in properties.keys():
            curr = properties[id]
            
            row = layout.row()
            row.label(text=curr.name)
            
            if isinstance(curr, StkBoolProperty):
                 state = "false"
                 icon = 'CHECKBOX_DEHLT'
                 if id in obj:
                     state = obj[id]
                     if state == "true":
                         icon = 'CHECKBOX_HLT'
                 row.operator("screen.stk_toggle_bool_"+id, text="                ", icon=icon, emboss=False)
                 
                 if state == "true":
                     if len(curr.subproperties) > 0:
                         box = layout.box()
                         self.recursivelyAddProperties(curr.subproperties, box, obj)
                 
            elif isinstance(curr, StkColorProperty):
                if curr.id in obj:
                    row.prop(obj, '["' + curr.id + '"]', text="")
                    row.operator("screen.apply_color_"+curr.id, text="", icon='COLOR')
            
            elif isinstance(curr, StkEnumProperty):
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

# ==== OBJECT PANEL ====
class SuperTuxKartObjectPanel(bpy.types.Panel, PanelBase):
    bl_label = "SuperTuxKart Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout
        
        obj = context.object
        
        if obj is not None:
            self.recursivelyAddProperties(STK_PER_OBJECT_PROPERTIES, layout, obj)


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
            self.recursivelyAddProperties(TRACK, layout, obj)   


def register():
    bpy.utils.register_module(__name__)

register()
