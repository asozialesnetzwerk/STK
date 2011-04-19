import bpy
 

# ==== TYPE OPERATORS ====
class STK_TypeUnset(bpy.types.Operator):
    bl_idname = ("screen.stk_unset_type")
    bl_label = ("STK Object :: unset type")
    
    def execute(self, context):
        obj = context.object
        obj["type"] = ""
        return {'FINISHED'}


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
                    'water'            : ['name', 'height', 'length', 'speed']
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

                                   # Numeric | Default
PROP_SETTNGS = { 'inner_radius' :  (True,      -1),
                 'mass'         :  (True,      15),
                 'height'       :  (True,      1.0),
                 'length'       :  (True,      10),
                 'speed'        :  (True,      300)
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


# ==== PANEL ====
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
    bpy.utils.register_module(__name__)

register()
