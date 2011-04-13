import bpy
 
STK_OBJECT_TYPES = {'banana'           : [],
                    'billboard'        : [],
                    'check'            : ['activate', 'toggle', 'inner_radius'],
                    'driveline'        : [],
                    'ignore'           : [],
                    'item'             : [],
                    'lap'              : ['activate'],
                    'maindriveline'    : ['activate'],
                    'nitro_big'        : [],
                    'nitro_small'      : [],
                    'object'           : ['name', 'shape', 'interaction', 'mass'],
                    'particle_emitter' : ['kind'],
                    'water'            : ['name', 'height', 'length', 'speed'],
# MY OBJECTS 
                    'track'            : ['name', 'groups', 'designer', 'music', 'screenshot',
                                          'arena', 'sky-type', 'ambient-color', 'camera-far', 'fog',
                                          'start-karts-per-row', 'start-forwards-distance',
                                          'start-sidewards-distance', 'start-upwards-distance', 'weather'],
# Conditional types                                          
                   'sky-type=dome'     : ['texture', 'horizontal', 'vertical', 'texture-percent', 'sphere-percent'],
                   'sky-type=box'      : ['texture1', 'texture2', 'texture3', 'texture4', 'texture5',
                                          'texture6'],
                   'sky-type=simple'   : ['sky-color'],
                   'fog=yes'           : ['fog-color', 'fog-start', 'fog-end']
                  }


COMBOS = {'type' :
             [('', '(None)', '(None)'),
              ('banana', 'Banana', 'Banana'),
              ('billboard', 'Billboard', 'Billboard'),
              ('check', 'Check', 'Check'),
              ('driveline', 'Driveline', 'Driveline'),
              ('ignore', 'Ignore', 'Ignore'),
              ('item', 'Item', 'Item'),
              ('lap', 'Lap', 'Lap'),
              ('maindriveline', 'Main Driveline', 'Main Driveline'),
              ('nitro_big', 'Nitro (Big)', 'Nitro (Big)'),
              ('nitro_small', 'Nitro (Small)', 'Nitro (Small)'),
              ('object', 'Object', 'Object'),
              ('particle_emitter', 'Particle Emitter', 'Particle Emitter'),
              ('water', 'Water', 'Water')],
          'shape' :
             [('box',       'Box',       'Box'),
              ('sphere',    'Sphere',    'Sphere'),
              ('coneX',     'ConeX',     'ConeX'),
              ('coneY',     'ConeY',     'ConeY'),
              ('coneZ',     'ConeZ',     'ConeZ'),
              ('cylinderX', 'CylinderX', 'CylinderX'),
              ('cylinderY', 'CylinderY', 'CylinderY'),
              ('cylinderZ', 'CylinderZ', 'CylinderZ')],
          'interaction' :
             [('static', 'Static (won''t move)', 'Static (won''t move)'),
              ('none', 'None (ghost)', 'None (ghost)'),
              ('move', 'Movable by player', 'Movable by player')]
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

                                   # Numeric | Default
PROP_SETTINGS = { 'inner_radius' :  (True,      -1),
                 'mass'         :  (True,      15),
                 'height'       :  (True,      1.0),
                 'length'       :  (True,      10),
                 'speed'        :  (True,      300),

                                   # Type | Default | length
                                   # Type | Default | min | max
                 'name'          : [type_STRING,  "", 50], \
                 'ambient-color' : [type_COLOUR,  (0.0, 0.0, 0.0)], \
                 'arena'         : [type_BOOLEAN, "no"], \
                 'camera-far'    : [type_INTEGER, 200, 10, 100000], \
                 'designer':[type_STRING, "", 200], \
    'fog':[type_BOOLEAN, "no"], \
    'fog-color':[type_COLOUR, 0.0, 0.0, 0.0], \
    'fog-start':[type_FLOAT, 1000, 0, 1000000, 0.1], \
    'fog-end':[type_FLOAT, 1000, 0, 1000000, 0.1], \
                 'groups':[type_STRING, "", 200], \
    'music':[type_URL, "", 200], \
    'screenshot':[type_IMAGEURL, "", 200], \
    'sky-type':[type_PICKLIST, "dome"], \
    'sky-color':[type_COLOUR, 0.0, 0.0, 0.0], \
    'sky-texture':[type_IMAGEURL, "", 200], \
    'sky-texture1':[type_IMAGEURL, "", 200], \
    'sky-texture2':[type_IMAGEURL, "", 200], \
    'sky-texture3':[type_IMAGEURL, "", 200], \
    'sky-texture4':[type_IMAGEURL, "", 200], \
    'sky-texture5':[type_IMAGEURL, "", 200], \
    'sky-texture6':[type_IMAGEURL, "", 200], \
    'sky-texture-percent':[type_FLOAT, 0.5, 0, 1, 0.1], \
    'sky-sphere-percent':[type_FLOAT, 1.3, 0, 2, 0.1], \
    'sky-horizontal':[type_INTEGER, 16, 0, 1000], \
    'sky-vertical':[type_INTEGER, 16, 0, 1000], \
    'start-karts-per-row':[type_INTEGER, 2, 1, 10], \
    'start-forwards-distance':[type_FLOAT, 1.1, 0, 1000, 0.1], \
    'start-sidewards-distance':[type_FLOAT, 1.1, 0, 1000, 0.1], \
    'start-upwards-distance':[type_FLOAT, 1.1, 0, 1000, 0.1], \
    'weather':[type_PICKLIST, "none"] \
    }



for param in COMBOS.keys():
    default_val = COMBOS[param][0][0]
    items_val = COMBOS[param]
    
    class STK_SetType(bpy.types.Operator):
        
        value = bpy.props.EnumProperty(attr="values", name="values", default=default_val,
                                       items=items_val)
        
        bl_idname = ("screen.stk_set_"+param)
        bl_label  = ("STK Object :: set "+param)
        
        m_param = param
        m_items_val = items_val
        
        def execute(self, context):
            
            # Set the property
            object = context.object
            object[self.m_param] = self.value

            # If sub-properties are needed, create them
            if self.value in STK_OBJECT_TYPES:
                for p in STK_OBJECT_TYPES[self.value]:
                    
                    if not p in object:
                    
                        numeric = False
                        if p in PROP_SETTNGS:
                            numeric = PROP_SETTNGS[p][0]
                        
                        # create proeprty by setting default  value
                        if p in COMBOS:
                            object[p] = COMBOS[p][0][0]
                        elif numeric:
                            object[p] = PROP_SETTNGS[p][1]
                        else:
                            object[p] = ""
                    
            
            return {'FINISHED'}


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


# ==== PANELS ====

#for curr in datamodel.lSTK_Picklist:
#    class STK_SetItem(bpy.types.Operator):
#           
#            bl_idname = ("screen.stk_set_" + curr)
#            bl_label = ("STK Object :: set " + curr)
#           
#  #          value = bpy.props.EnumProperty("values", "values", datamodel.lSTK_Picklist[curr][0],
#  #                                         datamodel.lSTK_Picklist[curr])
#            
#            def execute(self, context):
#                scene = context.scene
#                scene[curr] = value
#               
#                return {'FINISHED'}

# ==== OPERATORS ====

# == type operatorsS ====
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

class OBJECT_PT_hello(bpy.types.Panel):
    bl_label = "SuperTuxKart Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout
 
        obj = context.object

        # ==== Types group ====
        row = layout.row()
        row.label(text="Type")
        
        if "type" in obj:
            objtype = obj["type"]
        else:
            objtype = ""
        
        if objtype == '':
            row.operator_menu_enum("screen.stk_set_type", property="value", text="(None)")
        else:
            row.operator_menu_enum("screen.stk_set_type", property="value", text=objtype)
        
        if objtype in STK_OBJECT_TYPES:
            props = STK_OBJECT_TYPES[objtype]
        else:
            props = []
        
        if len(props) > 0:
            box = layout.box()
            

            for currprop in props:
                if currprop in obj:
                
                    if currprop == 'mass':
                        if 'interaction' not in obj or obj['interaction'] != 'move':
                            continue
                
                    row = box.row()
                    
                    if currprop in COMBOS.keys():
                        # Create a combo if this property is a combo type property
                        caption = obj[currprop][0].capitalize() + obj[currprop][1:]
                        for x in COMBOS[currprop]:
                            if x[0] == obj[currprop]:
                                caption = x[1]
                                break
                        
                        row.label(currprop[0].capitalize() + currprop[1:])
                        
                        op = "screen.stk_set_"+currprop
                        
                        # FIXME: for some reason, without that print the dropdown doesn't work??????
                        print(op)
                        row.operator_menu_enum(op, property="value", text=caption)
                        
                    else:
                        # Otherwise just create a plain text field or numeric field (guessed from type)
                        row.prop(obj, '["' + currprop + '"]', text=currprop[0].capitalize() + currprop[1:])
        
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
    bpy.utils.register_module(OBJECT_PT_hello)
    bpy.utils.register_module(STK_PANEL_Render)

if __name__ == "__main__":
    register()
