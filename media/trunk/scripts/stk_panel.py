import bpy
#import datamodel

### Things 2 do:
# - Enable list objects (now handled by input fields
# - make operations for switchable objects
# - Determine where texture objects should go (World?)
# - lots more 

# First, define the relation between Blender types and STK types.
# this determines 
BLENDER_OBJECT_TYPES = {'camera'    : ['ignore','ahead', 'fixed'],
                        'empty'     : ['ignore', 'banana', 'item', 'nitro_big', 'nitro_small'],
#    "Image":["Texture"], \
                        'lamp'      : ['ignore', 'sun'],
                        'mesh'      : ['ignore', 'billboard', 'check', 'driveline', 'lap',
                                       'maindriveline', 'particle_emitter', 'object', 'water'],
#    "Scene":["Track"], \
                        'other'     : ['ignore'] # All Blender types that cannot be used in STK
}

STK_TYPE_NAMES = {''                : '(None)',
                  'ahead'           : 'Look Ahead Camera',
                  'banana'          : 'Banana',
                  'billboard'       : 'Billboard',
                  'check'           : 'Check',
                  'driveline'       : 'Driveline',
                  'fixed'           : 'Fixed Camera',
                  'ignore'          : 'Ignore',
                  'item'            : 'Item',
                  'lap'             : 'Lap',
                  'maindriveline'   : 'Main Driveline',
                  'nitro_big'       : 'Nitro (Big)',
                  'nitro_small'     : 'Nitro (Small)',
                  'object'          : 'Object',
                  'particle_emitter': 'Particle Emitter',
                  'sun'             : 'Sun',
                  'water'           : 'Water'}

# Second, define all STK object types
STK_OBJECT_TYPES = {'ahead'            : ['start'],
                    'banana'           : [],
                    'billboard'        : [],
                    'check'            : ['name','activate', 'toggle', 'inner_radius', 'color'],
                    'driveline'        : ['invisible', 'ai-ignore'],
                    'fixed'            : ['start'],
                    'ignore'           : [],
                    'item'             : [],
                    'lap'              : ['activate', 'toggle', 'inner_radius', 'color'],
                    'maindriveline'    : ['activate'],
                    'nitro_big'        : [],
                    'nitro_small'      : [],
                    'object'           : ['name', 'animated', 'interaction'],
                    'particle_emitter' : ['kind'],
                    'sun'              : ['ambient', 'diffuse', 'specular'],
                    'water'            : ['name', 'height', 'length', 'speed', 'animated'],
# Track 'object' (officially not a blender object, but still important)
                    'track'            : ['name', 'groups', 'designer', 'music', 'screenshot',
                                          'arena', 'sky_type', 'ambient-color', 'camera-far', 'fog',
                                          'start-karts-per-row', 'start-forwards-distance',
                                          'start-sidewards-distance', 'start-upwards-distance', 'weather'],
# Texture 'object' (not really an object, but still important) 
                    'texture'           : ['anisotropic', 'backface-culling', 'clampU', 'clampV', 'compositing',
                                           'disable-z-write', 'friction', 'ignore', 'light', 'max-speed', 
                                           'reset', 'slowdown-time', 'sphere', 'graphical_effect', 'surface', 
                                           'below-surface', 'falling-effect', 'sound-effect', 'zipper', 'particle'],                                         
# Conditional types
                    'animated=yes'      : ['anim-texture', 'anim-dx', 'anim-dy'],                                   
                    'fog=yes'           : ['fog-color', 'fog-start', 'fog-end'],
                    'interaction=move'  : ['shape','mass'],
                    'interaction=static': ['shape'],
                    'particle=yes'      : ['base', 'condition'],
                    'sky-type=box'      : ['texture1', 'texture2', 'texture3', 'texture4', 'texture5',
                                          'texture6'],
                    'sky-type=dome'     : ['texture', 'horizontal', 'vertical', 'texture-percent', 'sphere-percent'],
                    'sky-type=simple'   : ['sky-color'],
                    'sound-effect=yes'  : ['filename', 'name', 'rolloff', 'min-speed', 'max-speed', 
                                           'min-pitch', 'max-pitch', 'positional'],
                    'zipper=yes'        : ['duration', 'max-speed-increase', 'fade-out-time', 'speed-gain']
                  }

COMBOS = {'type' :  [('',               '(None)'),
                     ('banana',         'Banana'),
                     ('billboard',      'Billboard'),
                     ('check',          'Check'),
                     ('driveline',      'Driveline'),
                     ('ignore',         'Ignore'),
                     ('item',           'Item'),
                     ('lap',            'Lap'),
                     ('maindriveline',  'Main Driveline'),
                     ('nitro_big',      'Nitro (Big)'),
                     ('nitro_small',    'Nitro (Small)'),
                     ('object',         'Object'),
                     ('particle_emitter', 'Particle Emitter'),
                     ('water',          'Water')],
#          }
#COMBOS = {
          'compositing' : [('none',         'None'),
                           ('blend',        'Blended'),
                           ('test',         'Threshold'),
                           ('additive',     'Additive')],
          'interaction' : [('static',       'Static (won''t move)'),
                           ('none',         'None (ghost)'),
                           ('move',         'Movable by player')],
          'shape'       : [('box',          'Box'),
                           ('sphere',       'Sphere'),
                           ('coneX',        'ConeX'),
                           ('coneY',        'ConeY'),
                           ('coneZ',        'ConeZ'),
                           ('cylinderX',    'CylinderX'),
                           ('cylinderY',    'CylinderY'),
                           ('cylinderZ',    'CylinderZ')],
          'sky_type'    : [('dome',         'Dome'),
                           ('box',          'Box'),
                           ('simple',       'Simple')],
          'graphical_effect':[('none',      'No Effect'),
                              ('water',     'Water')], 
          'condition'   : [('skid',         'When Skidding'),
                           ('drive',        'When Driving')],
          'weather'     : [('none', 'Normal (Sunny)'),
                           ('rain', 'Rainy'),
                           ('snow', 'Snowy')]
         }

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
type_DELETE = 20
type_RESET = 21

                                # Type      | Default | Length/Min | Max  | Step
PROP_SETTINGS = {
# General use                
                 'type':        [type_PICKLIST, 'ignore'], \
                 "activate":    [type_STRING,   "",     50], \
                 "color":       [type_COLOUR,   0.0,    0.0,        0.0], \
                 'inner_radius':[type_FLOAT,    -1,     0,          10000,  0.1], \
                 "name":        [type_STRING,   "",     50], \
                 "start":       [type_FLOAT,    25,     1,          2000,   1], \
                "toggle":       [type_STRING,   "",     50], \
# Driveline
    "invisible":[type_BOOLEAN, "no"],
    "ai-ignore":[type_BOOLEAN, "no"],
# Scene only
    "ambient-color":[type_COLOUR, 0.0, 0.0, 0.0], \
    "arena":[type_BOOLEAN, "no"], \
    "camera-far":[type_INTEGER, 200, 10, 100000], \
    "designer":[type_STRING, "", 200], \
    "fog":[type_BOOLEAN, "no"], \
    "fog-color":[type_COLOUR, 0.0, 0.0, 0.0], \
#    "fog-density":[type_FLOAT,16,0,1000,0.1],\
    "fog-start":[type_FLOAT, 1000, 0, 1000000, 0.1], \
    "fog-end":[type_FLOAT, 1000, 0, 1000000, 0.1], \
    "groups":[type_STRING, "", 200], \
    "music":[type_URL, "", 200], \
    "screenshot":[type_IMAGEURL, "", 200], \
    "sky_type":[type_PICKLIST, "dome"], \
    "sky-color":[type_COLOUR, 0.0, 0.0, 0.0], \
    "sky-texture":[type_IMAGEURL, "", 200], \
    "sky-texture1":[type_IMAGEURL, "", 200], \
    "sky-texture2":[type_IMAGEURL, "", 200], \
    "sky-texture3":[type_IMAGEURL, "", 200], \
    "sky-texture4":[type_IMAGEURL, "", 200], \
    "sky-texture5":[type_IMAGEURL, "", 200], \
    "sky-texture6":[type_IMAGEURL, "", 200], \
    "sky-texture-percent":[type_FLOAT, 0.5, 0, 1, 0.1], \
    "sky-sphere-percent":[type_FLOAT, 1.3, 0, 2, 0.1], \
    "sky-horizontal":[type_INTEGER, 16, 0, 1000], \
    "sky-vertical":[type_INTEGER, 16, 0, 1000], \
    "start-karts-per-row":[type_INTEGER, 2, 1, 10], \
    "start-forwards-distance":[type_FLOAT, 1.1, 0, 1000, 0.1], \
    "start-sidewards-distance":[type_FLOAT, 1.1, 0, 1000, 0.1], \
    "start-upwards-distance":[type_FLOAT, 1.1, 0, 1000, 0.1], \
    "weather":[type_PICKLIST, "none"], \
#For Textures  
    "clampU":[type_BOOLEAN, "no"], \
    "clampV":[type_BOOLEAN, "no"], \
    "compositing":[type_PICKLIST, "none"], \
                 'condition'    : [type_PICKLIST, 'skid'], \
    "light":[type_BOOLEAN, "yes"], \
    "sphere":[type_BOOLEAN, "no"], \
    "slowdown-time":[type_FLOAT, 1.0, 0, 100, 0.1], \
    "anisotropic":[type_BOOLEAN, "no"], \
    "max-speed":[type_FLOAT, 1.0, 0, 1.0, 0.1], \
    "friction":[type_FLOAT, 1.0, 0.0, 50000, 0.1], \
    "particle":[type_BOOLEAN, "no"], \
    "particle:base":[type_URL, "", 200], \
    "particle:condition":[type_CHOICELIST, "none"], \
    "backface-culling":[type_BOOLEAN, "yes"], \
    "ignore":[type_BOOLEAN, "no"], \
    "disable-z-write":[type_BOOLEAN, "no"], \
    "zipper":[type_BOOLEAN, "no"], \
    "zipper:duration":[type_FLOAT, 3.5, 0, 10, 0.1], \
    "zipper:max-speed-increase":[type_FLOAT, 15, 0, 100, 0.1], \
    "zipper:fade-out-time":[type_FLOAT, 3, 0, 100, 0.1], \
    "zipper:speed-gain":[type_FLOAT, 4.5, 0, 100, 0.1], \
    "reset":[type_BOOLEAN, "no"], \
    "surface":[type_BOOLEAN, "no"], \
    "falling-effect":[type_BOOLEAN, "no"], \
    "below-surface":[type_BOOLEAN, "no"], \
    "graphical_effect":[type_PICKLIST, "none"], \
    "sound-effect":[type_BOOLEAN, "no"], \
    "sfx:filename":[type_STRING, "", 200], \
    "sfx:name":[type_STRING, "", 50], \
    "sfx:rolloff":[type_FLOAT, 0.1, 0, 100, 0.1], \
    "sfx:min-speed":[type_FLOAT, 0.0, 0, 500, 0.1], \
    "sfx:max-speed":[type_FLOAT, 30.0, 0, 500, 0.1], \
    "sfx:min-pitch":[type_FLOAT, 1.0, 0.5, 2, 0.1], \
    "sfx:max-pitch":[type_FLOAT, 1.0, 0.5, 2, 0.1], \
    "sfx:positional":[type_BOOLEAN, "no"], \
#For Lights
    "ambient":[type_COLOUR, 0.0, 0.0, 0.0], \
    "diffuse":[type_COLOUR, 0.0, 0.0, 0.0], \
    "specular":[type_COLOUR, 0.0, 0.0, 0.0], \
#For Waters
    "height":[type_FLOAT, 1.0, 0, 100, 0.1], \
    "length":[type_FLOAT, 10, 0, 100, 0.1], \
    "speed":[type_FLOAT, 300, 0, 1000, 0.1], \
#For Objects
    "animated":[type_BOOLEAN, "no"], \
    "anim-texture":[type_IMAGEURL, "", 200], \
    "anim-dx":[type_FLOAT, 0, 0, 1000, 10], \
    "anim-dy":[type_FLOAT, 0, 0, 1000, 10], \
    "interaction":[type_PICKLIST, "none"], \
    "shape":[type_PICKLIST, "box"], \
    "mass":[type_FLOAT, 15, 0, 10000, 0.1], \

    }

# ==== OPERATORS ====

# == TYPE CHOOSERS ==

#for param in BLENDER_OBJECT_TYPES.keys():
#    default_val = STK_TYPE_NAMES[''][1]
#    items_val = [(STK_TYPE_NAMES[''][0],STK_TYPE_NAMES[''][1],STK_TYPE_NAMES[''][1])]
#    for i in BLENDER_OBJECT_TYPES[param]:
#        items_val.append((STK_TYPE_NAMES[i][0],STK_TYPE_NAMES[i][1],STK_TYPE_NAMES[i][1]))
        
#    default_val = PROP_SETTINGS['shape'][1]
#    items_val = []
#    for i in COMBOS['shape']:
#        items_val.append((i[0],i[1],i[1]))
            
#    class STK_SetType(bpy.types.Operator):
#        bl_idname = ("type.stk_set_"+param)
#        bl_label  = ("STK Object :: set "+param)
        
#        value = bpy.props.EnumProperty(attr="values", name="values", default=default_val,
#                                       items=items_val)
        
#        m_param = param
#        m_items_val = items_val
        
#        def execute(self, context):
#            
            # Set the property
#            object = context.object
#            object[self.m_param] = self.value

            # If sub-properties are needed, create them
#            for iter_type in STK_OBJECT_TYPES:
#                current_type = iter_type.split('=')[0] 
#                if current_type == self.value:
#                    for curr_prop in STK_OBJECT_TYPES[iter_type]:  
#                        if not curr_prop in object:
#                            object[curr_prop] = PROP_SETTINGS[curr_prop][1]
            
#            return {'FINISHED'}

# == COMBOS ==

#for param in COMBOS.keys():
#    default_val = PROP_SETTINGS[param][1]
#    items_val = []
 #   for i in COMBOS[param]:
#        items_val.append((i[0],i[1],i[1]))
    
#    class STK_SetType(bpy.types.Operator):
#        bl_idname = ("combo.stk_set_"+param)
#        bl_label  = ("STK Object :: set "+param)
        
#        value = bpy.props.EnumProperty(attr="values", name="values", default=default_val,
#                                       items=items_val)
        
#        m_param = param
#        m_items_val = items_val
        
#        def execute(self, context):
            
            # Set the property
#            object = context.object
#            object[self.m_param] = self.value

            # If sub-properties are needed, create them
#            for iter_type in STK_OBJECT_TYPES:
#                current_type = iter_type.split('=')[0] 
#                if current_type == self.value:
#                    for curr_prop in STK_OBJECT_TYPES[iter_type]:  
#                        if not curr_prop in object:
#                            object[curr_prop] = PROP_SETTINGS[curr_prop][1]
            
#            return {'FINISHED'}


    
        


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

# == type operators ====
class STK_TypeUnset(bpy.types.Operator):
    bl_idname = ("screen.stk_unset_type")
    bl_label = ("STK Object :: unset type")
    
    def execute(self, context):
        obj = context.object
        obj["type"] = ""
        return {'FINISHED'}

class STK_CreateProperties(bpy.types.Operator):
        bl_idname = ("screen.stk_create_props")
        bl_label = ("STK Track : create properties")
       
        def execute(self, context):
            scene = context.scene

            for current_property in STK_OBJECT_TYPES['track']:
                if not current_property in scene:
                    scene[current_property] = PROP_SETTINGS[current_property][1]
                    # Now add the restrictions
                    if PROP_SETTINGS[current_property][0] in [type_INTEGER,type_FLOAT]:
                        scene["_RNA_UI"] = {current_property: {'min':PROP_SETTINGS[current_property][2],
                                                               'max':PROP_SETTINGS[current_property][3]}} 
                    elif PROP_SETTINGS[current_property][0] == type_COLOUR:
                        scene["_RNA_UI"] = {current_property: {'subtype':'COLOR'}}
                        
            #scene["_RNA_UI"] = {'ambient-color': {'subtype':'COLOR'}} 
           
            return {'FINISHED'}
        
# == operator track export ==

class STK_OPER_StartExport(bpy.types.Operator):
    bl_idname = ("render.stk_make_track")
    bl_label = ("STK Track: create track")
    
    def execute(self, context):
        try:
            stk_track.main()
        except:
            context.invoke_popup("Error%t|Could not start exporter!")
        return {'FINISHED'}

# ==== PANELS ====

# == Render panel ==

class STK_PANEL_Render(bpy.types.Panel):
    bl_label = "SuperTuxKart Track Export"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    
    def draw(self, context):
        layout = self.layout
        
        # ==== Create Exporter Button ====
        row = layout.row()
        row.operator("render.stk_make_track", "Start the track exporter")
        
# == Scene Panel ==
        
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
        
        # ==== Track attributes ====
        for current_property in STK_OBJECT_TYPES['track']:
            try:
                if current_property in scene:
                    row = layout.row()
                    row.prop(scene, '["%s"]' % current_property, current_property)
            except:
                pass

# == Object Panel

class STK_PANEL_Object(bpy.types.Panel):
    bl_label = "SuperTuxKart Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def __init__(self):
        
        # It's really weird to do this outside a class, but hey... it works
        for param in BLENDER_OBJECT_TYPES.keys():
            default_val = STK_TYPE_NAMES['']
#            items_val = [('',STK_TYPE_NAMES[''],STK_TYPE_NAMES[''])]
            items_val = []
            for i in BLENDER_OBJECT_TYPES[param]:
                items_val.append((i,STK_TYPE_NAMES[i],STK_TYPE_NAMES[i]))
    
            #Is there a better way to do this?
            if param == 'camera': 
                bpy.types.Scene.cameraEnum = bpy.props.EnumProperty(name="Type",items=items_val)
            elif param == 'empty': 
                bpy.types.Scene.emptyEnum = bpy.props.EnumProperty(name="Type",items=items_val) 
            elif param == 'lamp': 
                bpy.types.Scene.lampEnum = bpy.props.EnumProperty(name="Type",items=items_val)
            elif param == 'mesh': 
                bpy.types.Scene.meshEnum = bpy.props.EnumProperty(name="Type",items=items_val)
            else: 
                bpy.types.Scene.otherEnum = bpy.props.EnumProperty(name="Type",items=items_val)                
            
    def draw(self, context):
        layout = self.layout
 
        obj = context.object
        #Determining object type
        try:
            objtype = obj.type.lower()
            if not objtype in BLENDER_OBJECT_TYPES:
                raise # raise another error
        except:
            objtype = 'other'

        row = layout.row()
        #row.label(text="Type")

        #currentEnum = self.typeEnum[objtype]
        row.prop(context.scene, objtype+"Enum")
#        row.operator_menu_enum("combo.stk_set_shape", property="value", text="(None)")
#        row.operator_menu_enum("combo.stk_set_type", property="value", text="(None)")

        # ==== Types group ====
        row = layout.row()
        row.label(text="Type")
        
#        if "type" in obj:
#            objtype = obj["type"]
#            row.operator_menu_enum("combo.stk_set_type", property="value", text=objtype)
            
#        else:
#            objtype = ""
            #row.operator_menu_enum("combo.stk_set_type", property="values", text="(None)")  

        
       # row.enum("combo.stk_set_type", property="value")  
            
        if objtype in STK_OBJECT_TYPES:
#            box = layout.box()

            for current_property in STK_OBJECT_TYPES[objtype]:
                try:
                    if current_property in obj:
                        row = layout.row()
                        row.prop(obj, '["%s"]' % current_property, current_property)
                except:
                    pass
                
#                    if currprop == 'mass':
#                        if 'interaction' not in obj or obj['interaction'] != 'move':
#                            continue
                
#                    row = box.row()
                    
#                    if currprop in COMBOS.keys():
                        # Create a combo if this property is a combo type property
 #                       caption = obj[currprop][0].capitalize() + obj[currprop][1:]
 #                       for x in COMBOS[currprop]:
 #                           if x[0] == obj[currprop]:
 #                               caption = x[1]
 #                               break
                        
 #                       row.label(currprop[0].capitalize() + currprop[1:])
                        
 #                       op = "screen.stk_set_"+currprop
                        
                        # FIXME: for some reason, without that print the dropdown doesn't work??????
    #                    print(op)
    #                    row.operator_menu_enum(op, property="value", text=caption)
                        
   #                 else:
                        # Otherwise just create a plain text field or numeric field (guessed from type)
  #                      row.prop(obj, '["' + currprop + '"]', text=currprop[0].capitalize() + currprop[1:])
        
        # ==== Anim Texture group ====
#        box = layout.box()
        
#        row = box.row()
#        row.label("Animated Texture")
        
#        row = box.row()
#        row.operator("screen.stk_set_animtex", text="Enable Animated Texture")
 
#        if "anim_texture" in obj:
#            try:
#                row = box.row()
#                row.prop(obj, '["anim_texture"]', text="Animated Texture")
#            except:
#                pass
#        if "anim_dx" in obj:
 #           try:
 #               row = box.row()
 #               row.prop(obj, '["anim_dx"]', text="X Speed")
 #           except:
 #               pass
 #       if "anim_dy" in obj:
  #          try:
   #             row = box.row()
    #            row.prop(obj, '["anim_dy"]', text="Y Speed")
    #        except:
       #         pass




def register():
    bpy.utils.register_module(__name__)
 
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
    
    
    
