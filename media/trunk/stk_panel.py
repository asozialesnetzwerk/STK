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
                    'lap'              : ['activate', 'toggle'],
                    'maindriveline'    : ['activate', 'toggle'],
                    'nitro_big'        : [],
                    'nitro_small'      : [],
                    'object'           : ['name', 'interaction', 'shape', 'mass'],
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
             [('box', 'box', 'box'),
              ('sphere', 'sphere', 'sphere'),
              ('coneX', 'coneX', 'coneX'),
              ('coneY', 'coneY', 'coneY'),
              ('coneZ', 'coneZ', 'coneZ'),
              ('cylinderX', 'cylinderX', 'cylinderX'),
              ('cylinderY', 'cylinderY', 'cylinderY'),
              ('cylinderZ', 'cylinderZ', 'cylinderZ')]
          }

                                   # Numeric | Default
PROP_SETTNGS = { 'inner_radius' :  (True,      -1),
                 'mass'         :  (True,      15),
                 'height'       :  (True,      1.0),
                 'length'       :  (True,      10),
                 'speed'        :  (True,      300)
               }

for param in COMBOS:
    default_val = COMBOS[param][0][0]
    items_val = COMBOS[param]
    
    class STK_SetType(bpy.types.Operator):
        
        value = bpy.props.EnumProperty(attr="values", name="values", default=default_val,
                                       items=items_val)
        
        bl_idname = ("screen.stk_set_"+param)
        bl_label  = ("STK Object :: set "+param)
        
        m_param = param
        
        def execute(self, context):
            object = context.object
            object[self.m_param] = self.value
            
            for p,q,s in COMBOS[self.m_param]:
                    
                    numeric = False
                    if p in PROP_SETTNGS:
                        numeric = PROP_SETTNGS[p][0]
                    
                    if numeric:
                        object[p] = PROP_SETTNGS[p][1]
                    else:
                        object[p] = "" # create properties
                
            
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
                row = box.row()
                
                if currprop in COMBOS:
                    row.label(currprop[0].capitalize() + currprop[1:])
                    row.operator_menu_enum("screen.stk_set_"+currprop, property="value", text=obj[currprop])
                else:
                    row.prop(obj, '["' + currprop + '"]', text=currprop[0].capitalize() + currprop[1:])
        

def register():
    bpy.utils.register_module(__name__)

register()
