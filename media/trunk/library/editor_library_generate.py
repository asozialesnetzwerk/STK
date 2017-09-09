import bpy
import os
import threading, time
from bpy.app.handlers import persistent

@persistent
def on_load(arg):
    if os.name == 'nt':
        img_path = "C:\\Temp\\images\\"
        xml_path = "C:\\Temp\\xml\\"
    else: 
        img_path = "/tmp/images/"
        xml_path = "/tmp/xml/"

    bpy.ops.object.select_all(action='SELECT')
    bpy.data.scenes[0].render.engine = 'BLENDER_RENDER'

    #bpy.ops.object.hide_view_clear()

    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].viewport_shade = 'TEXTURED'
                
                override = {'window': window, 'screen': screen, 'area': area}
                #bpy.ops.view3d.localview(override)
                #bpy.ops.view3d.viewnumpad(type='FRONT')
            
            
    bpy.ops.object.select_all(action='DESELECT')

    bpy.data.scenes[0].render.image_settings.file_format = 'PNG'
    bpy.data.scenes[0].render.resolution_x = 512
    bpy.data.scenes[0].render.resolution_y = 512
    #bpy.ops.view3d.localview()
    
    name = bpy.path.basename(bpy.context.blend_data.filepath)
    if name.endswith('.blend'):
        image_file_name = name[:-6] + ".png"
    else:
        image_file_name = name + ".png"
    bpy.data.scenes[0].render.filepath = img_path + image_file_name
    
    bpy.ops.render.opengl(write_still=True)
    
    path_parts = bpy.path.abspath("//").split(os.sep)
    if (path_parts[-1] == ''):
        path_parts = path_parts[:-1]

    if not os.path.exists(xml_path):
        os.makedirs(xml_path)
        
    f = open(xml_path + name + ".xml", mode="w", encoding="utf-8")
    f.write("<?xml version=\"1.0\"?>\n")
    
    objname = path_parts[-1]
    if objname.startswith('stklib_'):
        objname = objname[7:]

    category = path_parts[-2]
    if category == 'library':
        category = 'None'
        
    f.write("<library name=\"" + objname + "\" category=\"" + category + "\">\n")
    f.write("<img path=\"" + image_file_name + "\">\n")
    f.write("<model path=\"" + path_parts[-1] + "/" + path_parts[-1] + "_main.spm\">\n")
    # TODO: tags
    f.write("</library>")
    f.close()
    
    bpy.ops.wm.quit_blender()
    
#@persistent
#def on_scene_updated(arg):
#    print("on_scene_updated", arg)    
#bpy.app.handlers.scene_update_post.append(on_scene_updated)
    
bpy.app.handlers.load_post.append(on_load)

#bpy.ops.render.opengl(write_still=True)
