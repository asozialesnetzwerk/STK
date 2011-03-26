#!BPY

"""
Name: 'B3D Exporter (.b3d)...'
Blender: 248a
Group: 'Export'
Tooltip: 'Export to Blitz3D file format (.b3d)'
"""
__author__ = ["Diego 'GaNDaLDF' Parisi"]
__url__ = ["www.gandaldf.com"]
__version__ = "3.0"
__bpydoc__ = """\
"""

# BLITZ3D EXPORTER 2.06:
# Copyright (C) 2009 by Diego "GaNDaLDF" Parisi  -  www.gandaldf.com
#
# Lightmap issue fixed by Capricorn 76 Pty. Ltd. - www.capricorn76.com
#
# With changes by Marianne Gagnon and Joerg Henrichs, supertuxkart.sf.net
#
# LICENSE:
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


#If you get an error here, it might be
#because you don't have Python installed.
import bpy
import sys,os,os.path,struct,math,string
import mathutils
import math

if not hasattr(sys,"argv"): sys.argv = ["???"]


#Global Stacks
b3d_parameters = {}
sets_stack     = []
texs_stack     = []
brus_stack     = []
mesh_stack     = []
bone_stack     = []
keys_stack     = []

per_face_vertices = {}

the_scene = None

#Transformation Matrix
TRANS_MATRIX = mathutils.Matrix([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]])

DEBUG = False
PROGRESS = True

#Support Functions
def write_int(value):
    return struct.pack("<i",value)

def write_float(value):
    return struct.pack("<f",round(value,4))

def write_string(value):
    binary_format = "<%ds"%(len(value)+1)
    return struct.pack(binary_format, str.encode(value))

def write_chunk(name,value):
    dummy = bytearray()
    return dummy + name + write_int(len(value)) + value

# ==== Write B3D File ====
# (main exporter function)
def write_b3d_file(filename, objects=[]):
    global sets_stack, texs_stack
    global brus_stack, mesh_stack, bone_stack, keys_stack

    #Global Stacks
    sets_stack = []
    texs_stack = []
    brus_stack = []
    mesh_stack = []
    bone_stack = []
    keys_stack = []
    file_buf = bytearray()
    temp_buf = bytearray()

    temp_buf += write_int(1) #Version
    temp_buf += write_texs(objects) #TEXS
    temp_buf += write_brus(objects) #BRUS
    temp_buf += write_node(objects) #NODE

    if len(temp_buf) > 0:
        file_buf += write_chunk(b"BB3D",temp_buf)
        temp_buf = ""

    file = open(filename,'wb')
    file.write(file_buf)
    file.close()

# ==== Write TEXS Chunk ====
def write_texs(objects=[]):
    global b3d_parameters
    texs_buf = bytearray()
    temp_buf = bytearray()
    layer_max = 0
    obj_count = 0
    set_wrote = 0

    if objects:
        exp_obj = objects
    else:
        if b3d_parameters.get("export-selected"):
            exp_obj = [ob for ob in bpy.data.objects if ob.select]
        else:
            exp_obj = bpy.data.objects

    if PROGRESS: progress = 0

    for obj in exp_obj:
        
        if PROGRESS:
            progress = progress + 1
            if (progress % 10 == 0): print("TEXS",progress,"/",len(exp_obj))
        
        if obj.type == "MESH":
            set_count = 0
            set_wrote = 0
            #data = obj.getData(mesh = True)
            data = obj.data
            
            # FIXME?
            #orig_uvlayer = data.activeUVLayer
            
            layer_set = [[],[],[],[],[],[],[],[]]
            sets_stack.append([[],[],[],[],[],[],[],[]])

            #if len(data.getUVLayerNames()) <= 8:
            if len(data.uv_textures) <= 8:
                if len(data.uv_textures) > layer_max:
                    layer_max = len(data.uv_textures)
            else:
                layer_max = 8

            for face in data.faces:
                for iuvlayer,uvlayer in enumerate(data.uv_textures):
                    if iuvlayer < 8:
                        
                        # FIXME?
                        #data.activeUVLayer = uvlayer
                        
                        #layer_set[iuvlayer].append(face.uv)
                        layer_set[iuvlayer].append( uvlayer.data[face.index].uv )

            for i in range(len(data.uv_textures)):
                if set_wrote:
                    set_count += 1
                    set_wrote = 0

                for iuvlayer in range(i,len(data.uv_textures)):
                    if layer_set[i] == layer_set[iuvlayer]:
                        if sets_stack[obj_count][iuvlayer] == []:
                            if set_count == 0:
                                tex_flag = 1
                            elif set_count == 1:
                                tex_flag = 65536
                            elif set_count > 1:
                                tex_flag = 1
                            if b3d_parameters.get("mipmap"):
                                enable_mipmaps=8
                            else:
                                enable_mipmaps=0
                            sets_stack[obj_count][iuvlayer] = tex_flag|enable_mipmaps
                            set_wrote = 1

            for face in data.faces:
                for iuvlayer,uvlayer in enumerate(data.uv_textures):
                    if iuvlayer < 8:
                        
                        # FIXME?
                        #data.activeUVLayer = uvlayer
                        
                        #if DEBUG: print("<uv face=", face.index, ">")
                        if data.uv_textures[0].data[face.index].image:
                            
                            img_name = os.path.basename(data.uv_textures[0].data[face.index].image.filepath)
                            #img_name = data.uv_textures[0].data[face.index].image.name
                            
                            if not [img_name, sets_stack[obj_count][iuvlayer]] in texs_stack:
                                if DEBUG: print("<image id=",len(texs_stack),"name=","'"+img_name+"'","/>")
                                texs_stack.append([img_name, sets_stack[obj_count][iuvlayer]])
                                temp_buf += write_string(img_name) #Texture File Name
                                temp_buf += write_int(sets_stack[obj_count][iuvlayer]) #Flags
                                temp_buf += write_int(2)   #Blend
                                temp_buf += write_float(0) #X_Pos
                                temp_buf += write_float(0) #Y_Pos
                                temp_buf += write_float(1) #X_Scale
                                temp_buf += write_float(1) #Y_Scale
                                temp_buf += write_float(0) #Rotation
                            #else:
                            #    if DEBUG: print("    <image id=(previous)","name=","'"+img_name+"'","/>")
                            
                        #if DEBUG: print("</uv>")

            obj_count += 1

            #FIXME?
            #if orig_uvlayer:
            #    data.activeUVLayer = orig_uvlayer

    texs_stack.append(layer_max)

    if len(temp_buf) > 0:
        texs_buf += write_chunk(b"TEXS",temp_buf)
        temp_buf = ""

    return texs_buf

# ==== Write BRUS Chunk ====
def write_brus(objects=[]):
    global b3d_parameters
    brus_buf = bytearray()
    temp_buf = bytearray()
    mat_count = 0
    obj_count = 0

    if DEBUG: print("<!-- BRUS chunk -->")

    if objects:
        exp_obj = objects
    else:
        if  b3d_parameters.get("export-selected"):
            exp_obj = [ob for ob in bpy.data.objects if ob.select]
        else:
            exp_obj = bpy.data.objects

    if PROGRESS: progress = 0

    for obj in exp_obj:
        
        if PROGRESS:
            progress += 1
            if (progress % 10 == 0): print("BRUS",progress,"/",len(exp_obj))
            
        if obj.type == "MESH":
            #data = obj.getData(mesh = True)
            data = obj.data
            
            # FIXME?
            #orig_uvlayer = data.activeUVLayer

            if DEBUG: print("<obj name=",obj.name,">")

            for face in data.faces:
                img_found = 0
                face_stack = []
                
                if DEBUG: print("    <!-- Building FACE 'stack' -->")
                
                #for iuvlayer,uvlayer in enumerate(data.getUVLayerNames()):
                for iuvlayer,uvlayer in enumerate(data.uv_textures):
                    if iuvlayer < 8:
                        
                        #FIXME?
                        #data.activeUVLayer = uvlayer
                        
                        img_id = -1
                        
                        #if data.faceUV and face.image:
                        if data.uv_textures[0].data[face.index].image:
                            img_found = 1
                            
                            #print("len(texs_stack) =", len(texs_stack))
                            for i in range(len(texs_stack)-1):
                                
                                img_name = os.path.basename(data.uv_textures[0].data[face.index].image.filepath)
                                #img_name = data.uv_textures[0].data[face.index].image.name
                                
                                if texs_stack[i][0] == img_name:
                                    if texs_stack[i][1] == sets_stack[obj_count][iuvlayer]:
                                        img_id = i
                        
                        face_stack.insert(iuvlayer,img_id)
                        if DEBUG: print("    <uv face=",face.index,"layer=", iuvlayer, " imgid=", img_id, "/>")

                for i in range(len(face_stack),texs_stack[-1]):
                    face_stack.append(-1)


                if DEBUG: print("    <!-- Writing chunk -->")
                
                if not img_found:
                    if data.materials:
                        if data.materials[face.material_index]:
                            mat_data = data.materials[face.material_index]
                            mat_colr = mat_data.diffuse_color[0]
                            mat_colg = mat_data.diffuse_color[1]
                            mat_colb = mat_data.diffuse_color[2]
                            mat_alpha = mat_data.alpha
                            mat_name = mat_data.name

                            if not mat_name in brus_stack:
                                brus_stack.append(mat_name)
                                temp_buf += write_string(mat_name) #Brush Name
                                temp_buf += write_float(mat_colr)  #Red
                                temp_buf += write_float(mat_colg)  #Green
                                temp_buf += write_float(mat_colb)  #Blue
                                temp_buf += write_float(mat_alpha) #Alpha
                                temp_buf += write_float(0)         #Shininess
                                temp_buf += write_int(1)           #Blend
                                if b3d_parameters.get("vertex-colors") and len(data.vertex_colors):
                                    temp_buf += write_int(2) #Fx
                                else:
                                    temp_buf += write_int(0) #Fx

                                for i in face_stack:
                                    temp_buf += write_int(i) #Texture ID
                    else:
                        if b3d_parameters.get("vertex-colors") and data.getColorLayerNames():
                            if not face_stack in brus_stack:
                                brus_stack.append(face_stack)
                                mat_count += 1
                                temp_buf += write_string("Brush.%.3i"%mat_count) #Brush Name
                                temp_buf += write_float(1) #Red
                                temp_buf += write_float(1) #Green
                                temp_buf += write_float(1) #Blue
                                temp_buf += write_float(1) #Alpha
                                temp_buf += write_float(0) #Shininess
                                temp_buf += write_int(1)   #Blend
                                temp_buf += write_int(2)   #Fx

                                for i in face_stack:
                                    temp_buf += write_int(i) #Texture ID
                else: # img_found
                    if not face_stack in brus_stack:
                        brus_stack.append(face_stack)
                        mat_count += 1
                        temp_buf += write_string("Brush.%.3i"%mat_count) #Brush Name
                        temp_buf += write_float(1) #Red
                        temp_buf += write_float(1) #Green
                        temp_buf += write_float(1) #Blue
                        temp_buf += write_float(1) #Alpha
                        temp_buf += write_float(0) #Shininess
                        temp_buf += write_int(1)   #Blend
                        
                        if DEBUG: print("    <brush id=",len(brus_stack),">")
                        
                        if b3d_parameters.get("vertex-colors") and len(data.vertex_colors) > 0:
                            temp_buf += write_int(2) #Fx
                        else:
                            temp_buf += write_int(0) #Fx

                        for i in face_stack:
                            temp_buf += write_int(i) #Texture ID
                            if DEBUG: print("        <texture id=",i,">")
                        
                        if DEBUG: print("    </brush>")
                
                if DEBUG: print("")

            if DEBUG: print("</obj>")
            obj_count += 1

            #FIXME?
            #if orig_uvlayer:
            #    data.activeUVLayer = orig_uvlayer

    if len(temp_buf) > 0:
        brus_buf += write_chunk(b"BRUS",write_int(texs_stack[-1]) + temp_buf) #N Texs
        temp_buf = ""

    return brus_buf

# ==== Write NODE Chunk ====
def write_node(objects=[]):
    global bone_stack
    global keys_stack
    global b3d_parameters
    global the_scene
    
    root_buf = bytearray()
    node_buf = bytearray()
    main_buf = bytearray()
    temp_buf = bytearray()
    obj_count = 0
    amb_light = 0

    num_mesh = 0
    num_ligs = 0
    num_cams = 0
    num_lorc = 0
    #exp_scn = Blender.Scene.GetCurrent()
    #exp_scn = the_scene
    #exp_con = exp_scn.getRenderingContext()

    #first_frame = Blender.Draw.Create(exp_con.startFrame())
    #last_frame = Blender.Draw.Create(exp_con.endFrame())
    #num_frames = last_frame.val - first_frame.val
    first_frame = the_scene.frame_start
    last_frame = the_scene.frame_end
    num_frames = last_frame - first_frame


    if DEBUG: print("<node first_frame=", first_frame, " last_frame=", last_frame, ">")

    if objects:
        exp_obj = objects
    else:
        if b3d_parameters.get("export-selected"):
            exp_obj = [ob for ob in bpy.data.objects if ob.select]
        else:
            exp_obj = bpy.data.objects

    for obj in exp_obj:
        if obj.type == "MESH":
            num_mesh += 1
        if obj.type == "CAMERA":
            num_cams += 1
        if obj.type == "LAMP":
            num_ligs += 1

    if b3d_parameters.get("cameras"):
        num_lorc += num_cams

    if b3d_parameters.get("lights"):
        num_lorc += 1
        num_lorc += num_ligs

    if num_mesh + num_lorc > 1:
        exp_root = 1
    else:
        exp_root = 0

    if exp_root:
        root_buf += write_string("ROOT") #Node Name

        root_buf += write_float(0) #Position X
        root_buf += write_float(0) #Position Y
        root_buf += write_float(0) #Position Z

        root_buf += write_float(1) #Scale X
        root_buf += write_float(1) #Scale Y
        root_buf += write_float(1) #Scale Z

        root_buf += write_float(1) #Rotation W
        root_buf += write_float(0) #Rotation X
        root_buf += write_float(0) #Rotation Y
        root_buf += write_float(0) #Rotation Z

    if PROGRESS: progress = 0

    for obj in exp_obj:
        
        if PROGRESS:
            progress += 1
            print("NODE:",progress,"/",len(exp_obj))
        
        if obj.type == "MESH":
            
            if DEBUG: print("    <mesh name=",obj.name,">")
            
            bone_stack = []
            keys_stack = []
            #data = obj.getData(mesh = True)

            arm_action = None
            if obj.parent:
                if obj.parent.type == "ARMATURE":
                    arm = obj.parent
                    if arm.getAction():
                        arm_action = arm.getAction()

            if arm_action:
                matrix = Matrix()

                temp_buf += write_string(obj.name) #Node Name
                
                position = matrix.translationPart()
                temp_buf += write_float(-position[0]) #Position X
                temp_buf += write_float(position[1])  #Position Y
                temp_buf += write_float(position[2])  #Position Z

                scale = matrix.scalePart()
                temp_buf += write_float(scale[0]) #Scale X
                temp_buf += write_float(scale[2]) #Scale Y
                temp_buf += write_float(scale[1]) #Scale Z

                if DEBUG: print("        <arm name=", obj.name, " loc=", -position[0], position[1], position[2], " scale=", scale[0], scale[1], scale[2], "/>")
                
                quat = matrix.toQuat()
                quat.normalize()

                temp_buf += write_float(quat.w) #Rotation W
                temp_buf += write_float(quat.x) #Rotation X
                temp_buf += write_float(quat.z) #Rotation Y
                temp_buf += write_float(quat.y) #Rotation Z
            else:
                if b3d_parameters.get("local-space"):
                    matrix = TRANS_MATRIX
                else:
                    matrix = obj.matrix_world
                    matrix *= TRANS_MATRIX

                temp_buf += write_string(obj.name) #Node Name

                #print("Matrix : ", matrix)
                position = matrix.to_translation()

                temp_buf += write_float(position[0]) #Position X
                temp_buf += write_float(position[2])  #Position Y
                temp_buf += write_float(position[1])  #Position Z

                scale = matrix.to_scale()
                temp_buf += write_float(scale[0]) #Scale X
                temp_buf += write_float(scale[2]) #Scale Y
                temp_buf += write_float(scale[1]) #Scale Z

                matrix *= mathutils.Matrix.Rotation(math.pi, 4, 'Z')
                matrix *= mathutils.Matrix.Rotation(math.pi/2, 4, 'X')
                quat = matrix.to_quaternion()
                quat.normalize()

                temp_buf += write_float(quat.w) #Rotation W
                temp_buf += write_float(quat.x) #Rotation X
                temp_buf += write_float(quat.y) #Rotation Y
                temp_buf += write_float(quat.z) #Rotation Z

                if DEBUG: print("        <position>",position[0],position[2],position[1],"</position>")
                if DEBUG: print("        <scale>",scale[0],scale[1],scale[2],"</scale>")
                if DEBUG: print("        <rotation>", quat.w, quat.x, quat.y, quat.z, "</rotation>")
                
                
            if arm_action:
                Blender.Set("curframe",0)
                Blender.Window.Redraw()

                data = arm.getData()
                arm_matrix = arm.getMatrix("worldspace")
                arm_matrix *= TRANS_MATRIX.invert()

                def read_armature(arm_matrix,bone,parent = None):
                    if (parent and not bone.parent.name == parent.name):
                        return

                    matrix = Blender.Mathutils.Matrix(bone.matrix["ARMATURESPACE"])

                    if parent:
                        par_matrix = matrix * Blender.Mathutils.Matrix(parent.matrix["ARMATURESPACE"]).invert()
                    else:
                        par_matrix = matrix * arm_matrix

                    bone_stack.append([par_matrix,parent,bone])

                    if bone.children:
                        for child in bone.children: read_armature(arm_matrix,child,bone)

                for bone in data.bones.values():
                    if not bone.parent:
                        read_armature(arm_matrix,bone)

                arm_action.setActive(arm)
                frame_count = first_frame.val

                while frame_count <= last_frame.val:
                    Blender.Set("curframe",int(frame_count))
                    if DEBUG: print("        <frame>", int(frame_count), "</frame>")
                    #Blender.Window.Redraw()
                    arm_pose = arm.getPose()
                    arm_matrix = arm.getMatrix("worldspace")
                    arm_matrix *= TRANS_MATRIX

                    for bone_name in data.bones.keys():
                        bone_matrix = mathutils.Matrix(arm_pose.bones[bone_name].poseMatrix)

                        for ibone in range(len(bone_stack)):
                            if bone_stack[ibone][2].name == bone_name:
                                if bone_stack[ibone][1]:
                                    par_matrix = mathutils.Matrix(arm_pose.bones[bone_stack[ibone][1].name].poseMatrix)
                                    bone_matrix *= par_matrix.invert()
                                else:
                                    if b3d_parameters.get("local-space"):
                                        bone_matrix *= TRANS_MATRIX
                                    else:
                                        bone_matrix *= arm_matrix

                                bone_loc = bone_matrix.translation_part()
                                bone_rot = bone_matrix.rotation_part().toQuat()
                                bone_rot.normalize()
                                bone_sca = bone_matrix.scale_part()
                                keys_stack.append([frame_count - first_frame.val+1,bone_name,bone_loc,bone_sca,bone_rot])

                    frame_count += 1

                Blender.Set("curframe",0)
                Blender.Window.Redraw()

            temp_buf += write_node_mesh(obj,obj_count,arm_action,exp_root) #NODE MESH

            if arm_action:
                temp_buf += write_node_anim(num_frames) #NODE ANIM

                for ibone in range(len(bone_stack)):
                    if not bone_stack[ibone][1]:
                        temp_buf += write_node_node(ibone) #NODE NODE

            obj_count += 1

            if len(temp_buf) > 0:
                node_buf += write_chunk(b"NODE",temp_buf)
                temp_buf = bytearray()
            
            if DEBUG: print("    </mesh>")

        if b3d_parameters.get("cameras"):
            if obj.type == "CAMERA":
                data = obj.data
                matrix = obj.getMatrix("worldspace")
                matrix *= TRANS_MATRIX

                if data.type == "ORTHO":
                    cam_type = 2
                    cam_zoom = round(data.scale,4)
                else:
                    cam_type = 1
                    cam_zoom = round(data.lens,4)

                cam_near = round(data.clipStart,4)
                cam_far = round(data.clipEnd,4)

                node_name = ("CAMS"+"\n%s"%obj.name+"\n%s"%cam_type+\
                             "\n%s"%cam_zoom+"\n%s"%cam_near+"\n%s"%cam_far)
                temp_buf += write_string(node_name) #Node Name

                position = matrix.translation_part()
                temp_buf += write_float(-position[0]) #Position X
                temp_buf += write_float(position[1])  #Position Y
                temp_buf += write_float(position[2])  #Position Z

                scale = matrix.scale_part()
                temp_buf += write_float(scale[0]) #Scale X
                temp_buf += write_float(scale[1]) #Scale Y
                temp_buf += write_float(scale[2]) #Scale Z

                matrix *= mathutils.Matrix.Rotation(180,4,'Y')
                quat = matrix.to_quat()
                quat.normalize()

                temp_buf += write_float(quat.w)  #Rotation W
                temp_buf += write_float(quat.x)  #Rotation X
                temp_buf += write_float(quat.y)  #Rotation Y
                temp_buf += write_float(-quat.z) #Rotation Z

                if len(temp_buf) > 0:
                    node_buf += write_chunk(b"NODE",temp_buf)
                    temp_buf = ""

        if b3d_parameters.get("lights"):
            if amb_light == 0:
                data = Blender.World.GetCurrent()

                amb_light = 1
                amb_color = (int(data.amb[2]*255) |(int(data.amb[1]*255) << 8) | (int(data.amb[0]*255) << 16))

                node_name = (b"AMBI"+"\n%s"%amb_color)
                temp_buf += write_string(node_name) #Node Name

                temp_buf += write_float(0) #Position X
                temp_buf += write_float(0) #Position Y
                temp_buf += write_float(0) #Position Z

                temp_buf += write_float(1) #Scale X
                temp_buf += write_float(1) #Scale Y
                temp_buf += write_float(1) #Scale Z

                temp_buf += write_float(1) #Rotation W
                temp_buf += write_float(0) #Rotation X
                temp_buf += write_float(0) #Rotation Y
                temp_buf += write_float(0) #Rotation Z

                if len(temp_buf) > 0:
                    node_buf += write_chunk(b"NODE",temp_buf)
                    temp_buf = ""

            if obj.type == "LAMP":
                data = obj.getData()
                matrix = obj.getMatrix("worldspace")
                matrix *= TRANS_MATRIX

                if data.type == 0:
                    lig_type = 2
                elif data.type == 2:
                    lig_type = 3
                else:
                    lig_type = 1

                lig_angle = round(data.spotSize,4)
                lig_color = (int(data.b*255) |(int(data.g*255) << 8) | (int(data.r*255) << 16))
                lig_range = round(data.dist,4)

                node_name = ("LIGS"+"\n%s"%obj.name+"\n%s"%lig_type+\
                             "\n%s"%lig_angle+"\n%s"%lig_color+"\n%s"%lig_range)
                temp_buf += write_string(node_name) #Node Name

                position = matrix.translation_part()
                temp_buf += write_float(-position[0]) #Position X
                temp_buf += write_float(position[1])  #Position Y
                temp_buf += write_float(position[2])  #Position Z
                if DEBUG: print("        <position>",-position[0],position[1],position[2],"</position>")

                scale = matrix.scale_part()
                temp_buf += write_float(scale[0]) #Scale X
                temp_buf += write_float(scale[1]) #Scale Y
                temp_buf += write_float(scale[2]) #Scale Z
                
                if DEBUG: print("        <scale>",scale[0],scale[1],scale[2],"</scale>")

                matrix *= mathutils.Matrix.Rotation(180,4,'Y')
                quat = matrix.toQuat()
                quat.normalize()

                temp_buf += write_float(quat.w)  #Rotation W
                temp_buf += write_float(quat.x)  #Rotation X
                temp_buf += write_float(quat.y)  #Rotation Y
                temp_buf += write_float(-quat.z) #Rotation Z

                if DEBUG: print("        <rotation>", quat.w, quat.x, quat.y, quat.z, "</rotation>")

                if len(temp_buf) > 0:
                    node_buf += write_chunk(b"NODE",temp_buf)
                    temp_buf = ""

    if len(node_buf) > 0:
        if exp_root:
            main_buf += write_chunk(b"NODE",root_buf + node_buf)
        else:
            main_buf += node_buf

        node_buf = ""
        root_buf = ""

    if DEBUG: print("</node>")

    return main_buf

# ==== Write NODE MESH Chunk ====
def write_node_mesh(obj,obj_count,arm_action,exp_root):
    global mesh_stack
    mesh_stack = []
    mesh_buf = bytearray()
    temp_buf = bytearray()

    temp_buf += write_int(-1) #Brush ID
    temp_buf += write_node_mesh_vrts(obj,obj_count,arm_action,exp_root) #NODE MESH VRTS
    temp_buf += write_node_mesh_tris(obj,obj_count,arm_action,exp_root) #NODE MESH TRIS

    if len(temp_buf) > 0:
        mesh_buf += write_chunk(b"MESH",temp_buf)
        temp_buf = ""

    return mesh_buf

#ids_count = 0

# ==== Write NODE MESH VRTS Chunk ====
def write_node_mesh_vrts(obj,obj_count,arm_action,exp_root):
    #global ids_count
    vrts_buf = bytearray()
    temp_buf = bytearray()
    obj_flags = 0
    ids_count = 0

    #data = obj.getData(mesh = True)
    data = obj.data
    
    # FIXME: port to 2.5 API?
    #orig_uvlayer = data.activeUVLayer

    if b3d_parameters.get("vertex-normals"):
        obj_flags += 1

    #if b3d_parameters.get("vertex-colors") and data.getColorLayerNames():
    if b3d_parameters.get("vertex-colors") and len(data.vertex_colors) > 0:
        obj_flags += 2

    temp_buf += write_int(obj_flags) #Flags
    #temp_buf += write_int(len(data.getUVLayerNames())) #UV Set
    temp_buf += write_int(len(data.uv_textures)) #UV Set
    temp_buf += write_int(2) #UV Set Size

    # ---- Prepare the mesh "stack"

    #for i in data.vertices:
    #    mesh_stack.append([-1,-1,-1,[],[[],[],[],[],[],[],[],[]],[]])

    for f in data.faces:
        for v in f.vertices:
            mesh_stack.append([-1,-1,-1,[],[[],[],[],[],[],[],[],[]],[]])

    # ---- Fill the mesh "stack"
    if DEBUG: print("")
    if DEBUG: print("        <!-- Building mesh_stack -->")

    ivert = -1


    if PROGRESS:
        progress = 0
        print("    mesh_stack, face:",0,"/",len(data.faces))
    
    for face in data.faces:
        
        if DEBUG: print("        <!-- Face",face.index,"-->")
        
        if PROGRESS:
            progress += 1
            if (progress % 50 == 0): print("    mesh_stack, face:",progress,"/",len(data.faces))
        
                
        per_face_vertices[face.index] = []
        
        for vertex_id,vert in enumerate(face.vertices):
            
            ivert += 1
            
            #ivert = data.vertices[vert].index
            
            if DEBUG: print("            <!-- B3D Vertex",ivert,"is blender vertex",data.vertices[vert].index,"for face",face.index,"-->")
           
            per_face_vertices[face.index].append(ivert)
            
            if mesh_stack[ivert][0] != -1:
                if DEBUG: print("            <!-- Vertex",ivert,"already handled -->")
            
            if mesh_stack[ivert][0] == -1:
                link_matrix = obj.matrix_world
                mesh_matrix = mathutils.Matrix([link_matrix[0],link_matrix[1],link_matrix[2],link_matrix[3]])
                vert_matrix = mathutils.Matrix.Translation(data.vertices[vert].co)

                if arm_action:
                    vert_matrix *= mesh_matrix

                vert_matrix *= TRANS_MATRIX
                vert_matrix = vert_matrix.to_translation()


                mesh_stack[ivert][0] = ivert
                mesh_stack[ivert][1] = vert_matrix
                
                #if DEBUG: print "        <vertex id=",vert.index,"/>"

                if b3d_parameters.get("vertex-normals"):
                    link_matrix = obj.matrix_world
                    mesh_matrix = mathutils.Matrix([link_matrix[0],link_matrix[1],link_matrix[2],link_matrix[3]])
                    norm_matrix = mathutils.Matrix.Translation(data.vertices[vert].normal)

                    if arm_action:
                        norm_matrix *= mesh_matrix

                    norm_matrix *= TRANS_MATRIX
                    norm_matrix = norm_matrix.to_translation()

                    mesh_stack[ivert][2] = norm_matrix

                if b3d_parameters.get("vertex-colors") and len(data.vertex_colors) > 0:
                    if vertex_id == 0:
                        mesh_stack[ivert][3] = data.vertex_colors[0].data[face.index].color1
                    elif vertex_id == 1:
                        mesh_stack[ivert][3] = data.vertex_colors[0].data[face.index].color2
                    elif vertex_id == 2:
                        mesh_stack[ivert][3] = data.vertex_colors[0].data[face.index].color3
                    elif vertex_id == 3:
                        mesh_stack[ivert][3] = data.vertex_colors[0].data[face.index].color4

                if (len(data.uv_textures) > 0):
                    if vertex_id == 0:
                        mesh_stack[ivert][4][0].append([face.index,data.uv_textures[0].data[face.index].uv1])
                        if DEBUG: print("            <uv face=",face.index,"vertex=",vertex_id,">",
                                                      data.uv_textures[0].data[face.index].uv1,"</uv>")
                    elif vertex_id == 1:
                        mesh_stack[ivert][4][0].append([face.index,data.uv_textures[0].data[face.index].uv2])
                        if DEBUG: print("            <uv face=",face.index,"vertex=",vertex_id,">",
                                                      data.uv_textures[0].data[face.index].uv2,"</uv>")
                    elif vertex_id == 2:
                        mesh_stack[ivert][4][0].append([face.index,data.uv_textures[0].data[face.index].uv3])
                        if DEBUG: print("            <uv face=",face.index,"vertex=",vertex_id,">",
                                                      data.uv_textures[0].data[face.index].uv3,"</uv>")
                    elif vertex_id == 3:
                        mesh_stack[ivert][4][0].append([face.index,data.uv_textures[0].data[face.index].uv4])
                        if DEBUG: print("            <uv face=",face.index,"vertex=",vertex_id,">",
                                                      data.uv_textures[0].data[face.index].uv4,"</uv>")
                    else:
                        self.report({'ERROR'}, "Only triangles and quads are supported")
                else:
                    mesh_stack[ivert][4][0].append([face.index,[0.0,0.0]])
	            
                #mesh_stack[vert.index][5].append(vert_influ)
                mesh_stack[ivert][5].append(data.vertices[vert].bevel_weight)
                
                #if data.vertexUV and not data.faceUV:
                #    mesh_stack[vert.index][4][0].append([face.index,vert.uvco[0]])
                #if not data.vertexUV and not data.faceUV:
                #    mesh_stack[vert.index][4][0].append([face.index,[0.0,0.0]])
    
    if DEBUG: print("")

    #if data.faceUV:
    #    if not 65536 in sets_stack[obj_count]:
    #        vert_opti = 1
    #    else:
    #        vert_opti = 0
#
#        for iuvlayer,uvlayer in enumerate(data.getUVLayerNames()):
#            if iuvlayer < 8:
#                data.activeUVLayer = uvlayer
#                for face in data.faces:
#                    for ivert,vert in enumerate(face.verts):
#                        if vert_opti:
#                            if not face.uv[ivert] in mesh_stack[vert.index][4][iuvlayer]:
#                                mesh_stack[vert.index][4][iuvlayer].append([face.index,face.uv[ivert]])
#                        else:
#                            mesh_stack[vert.index][4][iuvlayer].append([face.index,face.uv[ivert]])

    # FIXME: port to 2.5 API?
    #if orig_uvlayer:
    #    data.activeUVLayer = orig_uvlayer

    if PROGRESS: progress = 0

    for ivert in range(len(mesh_stack)):
        
        if PROGRESS:
            progress += 1
            if (progress % 50 == 0): print("    VRTS:",progress,"/",len(mesh_stack))

        
        mesh_stack[ivert][0] = ids_count
        
        if DEBUG: print("        <ivert id=",ivert,">")
        
        for iuv in range(len(mesh_stack[ivert][4][0])):
            ids_count += 1

            temp_buf += write_float(mesh_stack[ivert][1].x)  #X
            temp_buf += write_float(mesh_stack[ivert][1].z)  #Y
            temp_buf += write_float(mesh_stack[ivert][1].y)  #Z
            
            if DEBUG: print("            <vertex id=",ids_count," loc=",-mesh_stack[ivert][1].x,
                                                                         mesh_stack[ivert][1].y,
                                                                         mesh_stack[ivert][1].z,">")

            if b3d_parameters.get("vertex-normals"):
                temp_buf += write_float(mesh_stack[ivert][2].x)  #NX
                temp_buf += write_float(mesh_stack[ivert][2].z)  #NY
                temp_buf += write_float(mesh_stack[ivert][2].y)  #NZ
                if DEBUG: print("                <normal>",-mesh_stack[ivert][2].x,
                                                            mesh_stack[ivert][2].y,
                                                            mesh_stack[ivert][2].z,"</normal>")

            if b3d_parameters.get("vertex-colors") and len(data.vertex_colors) > 0:
                temp_buf += write_float(mesh_stack[ivert][3].r) #R
                temp_buf += write_float(mesh_stack[ivert][3].g) #G
                temp_buf += write_float(mesh_stack[ivert][3].b) #B
                temp_buf += write_float(1.0) #A (FIXME?)
                #temp_buf += write_float(mesh_stack[ivert][3].a/255.0) #A
                if DEBUG: print("                <color>",mesh_stack[ivert][3].r,
                                                          mesh_stack[ivert][3].g,
                                                          mesh_stack[ivert][3].b,"</color>")

            #for iuvlayer in xrange(len(data.getUVLayerNames())):
            for iuvlayer in range(len(data.uv_textures)):
                temp_buf += write_float(-mesh_stack[ivert][4][iuvlayer][iuv][1][0])  #U
                temp_buf += write_float(1-mesh_stack[ivert][4][iuvlayer][iuv][1][1]) #V
                if DEBUG: print("                <uv layer=",iuvlayer,">",mesh_stack[ivert][4][iuvlayer][iuv][1][0],
                                                  1-mesh_stack[ivert][4][iuvlayer][iuv][1][1],"</uv>")

            if DEBUG: print("            </vertex>")

        if DEBUG: print("        </ivert>")

    if len(temp_buf) > 0:
        vrts_buf += write_chunk(b"VRTS",temp_buf)
        temp_buf = ""

    return vrts_buf

# ==== Write NODE MESH TRIS Chunk ====
def write_node_mesh_tris(obj,obj_count,arm_action,exp_root):
    #data = obj.getData(mesh = True)
    data = obj.data

    #FIXME?
    #orig_uvlayer = data.activeUVLayer

    # An dictoriary that maps all brush-ids to a list of faces
    # using this brush. This helps to sort the triangles by
    # brush, creating less mesh buffer in irrlicht.
    dBrushId2Face = {}
    
    for face in data.faces:
        img_found = 0
        face_stack = []
        
        #for iuvlayer,uvlayer in enumerate(data.getUVLayerNames()):
        for iuvlayer,uvlayer in enumerate(data.uv_textures):
            if iuvlayer < 8:
	
	            #FIXME?
                #data.activeUVLayer = uvlayer

	            # Blender 2.5 :
	            # data.uv_textures[0].data[0].image

                img_id = -1

                #FIXME?
                #if data.faceUV and face.image:
                if data.uv_textures[0].data[face.index].image:
                    img_found = 1
                    for i in range(len(texs_stack)-1):
                        if texs_stack[i][0] == os.path.basename(data.uv_textures[0].data[face.index].image.filepath):
                            if texs_stack[i][1] == sets_stack[obj_count][iuvlayer]:
                                img_id = i

                face_stack.insert(iuvlayer,img_id)

        for i in range(len(face_stack),texs_stack[-1]):
            face_stack.append(-1)

        if img_found == 0:
            brus_id = -1
            if data.materials:
                if data.materials[face.material_index]:
                    mat_name = data.materials[face.material_index].name
                    for i in range(len(brus_stack)):
                        if brus_stack[i] == mat_name:
                            brus_id = i
            else:
                for i in range(len(brus_stack)):
                    if brus_stack[i] == face_stack:
                        brus_id = i
        else:
            brus_id = -1
            for i in range(len(brus_stack)):
                if brus_stack[i] == face_stack:
                    brus_id = i

        if brus_id in dBrushId2Face:
            dBrushId2Face[brus_id].append(face)
        else:
            dBrushId2Face[brus_id] = [face]
        
        if DEBUG: print("            <!-- Face",face.index,"in brush",brus_id,"-->")
            
    tris_buf = bytearray()
    
    if DEBUG: print("")
    if DEBUG: print("        <!-- TRIS chunk -->")
    
    if PROGRESS: progress = 0
                
    for brus_id in dBrushId2Face.keys():
        
        if PROGRESS:
            progress += 1
            print("BRUS:",progress,"/",len(dBrushId2Face.keys()))
        
        temp_buf = write_int(brus_id) #Brush ID
        
        if DEBUG: print("        <brush id=", brus_id, "/>")
        
        if PROGRESS: progress2 = 0
                
        for face in dBrushId2Face[brus_id]:
            
            if PROGRESS:
                progress2 += 1
                if (progress2 % 50 == 0): print("    TRIS:",progress2,"/",len(dBrushId2Face[brus_id]))
            
            #face_id = [0,0,0,0]
            #if data.faceUV:
            #if len(data.uv_textures) > 0:
            #    for i in range(len(face.vertices)):
            #        vi = data.vertices[face.vertices[i]].index
            #        for iuv in range(len(mesh_stack[vi][4][0])):
            #            if mesh_stack[vi][4][0][iuv][0] == face.index:
            #                face_id[i] = mesh_stack[vi][0] + iuv
            #else:
            #    for i in range(len(face.verts)):
            #        face_id[i] = mesh_stack[face.v[i].index][0]

            vertices = per_face_vertices[face.index]

            temp_buf += write_int(vertices[2]) #A
            temp_buf += write_int(vertices[1]) #B
            temp_buf += write_int(vertices[0]) #C

            if DEBUG: print("            <face id=", vertices[2], vertices[1], vertices[0],"/> <!-- face",face.index,"-->")

            if len(face.vertices) == 4:
                temp_buf += write_int(vertices[3]) #A
                temp_buf += write_int(vertices[2]) #B
                temp_buf += write_int(vertices[0]) #C
                if DEBUG: print("            <face id=", vertices[3], vertices[2], vertices[0],"/> <!-- face",face.index,"-->")

        if DEBUG: print("        </brush>")
        tris_buf += write_chunk(b"TRIS",temp_buf)
     
    #FIXME?   
    #if orig_uvlayer:
    #    data.activeUVLayer = orig_uvlayer

    return tris_buf

# ==== Write NODE ANIM Chunk ====
def write_node_anim(num_frames):
    anim_buf = bytearray()
    temp_buf = bytearray()

    temp_buf += write_int(0) #Flags
    temp_buf += write_int(num_frames) #Frames
    temp_buf += write_float(60) #FPS

    if len(temp_buf) > 0:
        anim_buf += write_chunk(b"ANIM",temp_buf)
        temp_buf = ""

    return anim_buf

# ==== Write NODE NODE Chunk ====
def write_node_node(ibone):
    node_buf = ""
    temp_buf = ""

    matrix = bone_stack[ibone][0]
    temp_buf += write_string(bone_stack[ibone][2].name) #Node Name

    position = matrix.translationPart()
    temp_buf += write_float(-position[0]) #Position X
    temp_buf += write_float(position[1])  #Position Y
    temp_buf += write_float(position[2])  #Position Z

    scale = matrix.scalePart()
    temp_buf += write_float(scale[0]) #Scale X
    temp_buf += write_float(scale[1]) #Scale Y
    temp_buf += write_float(scale[2]) #Scale Z

    quat = matrix.toQuat()
    quat.normalize()

    temp_buf += write_float(quat.w)  #Rotation W
    temp_buf += write_float(-quat.x) #Rotation X
    temp_buf += write_float(quat.y)  #Rotation Y
    temp_buf += write_float(quat.z)  #Rotation Z

    temp_buf += write_node_bone(ibone)
    temp_buf += write_node_keys(ibone)

    for iibone in xrange(len(bone_stack)):
        if bone_stack[iibone][1] == bone_stack[ibone][2]:
            temp_buf += write_node_node(iibone)

    if len(temp_buf) > 0:
        node_buf += write_chunk(b"NODE",temp_buf)
        temp_buf = ""

    return node_buf

# ==== Write NODE BONE Chunk ====
def write_node_bone(ibone):
    bone_buf = ""
    temp_buf = ""

    for ivert in xrange(len(mesh_stack)):
        for iuv in xrange(len(mesh_stack[ivert][4][0])):
            for vert_influ in mesh_stack[ivert][5]:
                if bone_stack[ibone][2].name == vert_influ[0]:
                    if DEBUG: print("        <bone name=",bone_stack[ibone][2].name,"face_vertex_id=", mesh_stack[ivert][0] + iuv,
                                    " weigth=", vert_influ[1] , "/>")
                    temp_buf += write_int(mesh_stack[ivert][0] + iuv) # Face Vertex ID
                    temp_buf += write_float(vert_influ[1]) #Weight

    bone_buf += write_chunk("bBONE",temp_buf)
    temp_buf = ""

    return bone_buf

# ==== Write NODE KEYS Chunk ====
def write_node_keys(ibone):
    keys_buf = ""
    temp_buf = ""

    temp_buf += write_int(7) #Flags

    for ikeys in xrange(len(keys_stack)):
        if keys_stack[ikeys][1] == bone_stack[ibone][2].name:
            temp_buf += write_int(keys_stack[ikeys][0]) #Frame

            position = keys_stack[ikeys][2]
            temp_buf += write_float(-position[0]) #Position X
            temp_buf += write_float(position[1])  #Position Y
            temp_buf += write_float(position[2])  #Position Z

            scale = keys_stack[ikeys][3]
            temp_buf += write_float(scale[0]) #Scale X
            temp_buf += write_float(scale[1]) #Scale Y
            temp_buf += write_float(scale[2]) #Scale Z

            quat = keys_stack[ikeys][4]
            quat.normalize()

            temp_buf += write_float(quat.w)  #Rotation W
            temp_buf += write_float(-quat.x) #Rotation X
            temp_buf += write_float(quat.y)  #Rotation Y
            temp_buf += write_float(quat.z)  #Rotation Z

    keys_buf += write_chunk(b"KEYS",temp_buf)
    temp_buf = ""

    return keys_buf


# ==== CONFIRM OPERATOR ====
class B3D_Confirm_Operator(bpy.types.Operator):
    bl_idname = ("screen.b3d_confirm")
    bl_label = ("File Exists, Overwrite?")
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        write_b3d_file(B3D_Confirm_Operator.filepath)
        return {'FINISHED'}
    
# ==== EXPORT OPERATOR ====
class B3D_Export_Operator(bpy.types.Operator):
    bl_idname = ("screen.b3d_export")
    bl_label = ("B3D Export")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    selected = bpy.props.BoolProperty(name="Export Selected Only", default=False)
    vnormals = bpy.props.BoolProperty(name="Export Vertex Normals", default=True)
    vcolors  = bpy.props.BoolProperty(name="Export Vertex Colors", default=True)
    cameras  = bpy.props.BoolProperty(name="Export Cameras", default=False)
    lights   = bpy.props.BoolProperty(name="Export Lights", default=False)
    mipmap   = bpy.props.BoolProperty(name="Mipmap", default=False)
    localsp  = bpy.props.BoolProperty(name="Use Local Space Coords", default=False)
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        
        global b3d_parameters
        b3d_parameters["export-selected"] = self.selected
        b3d_parameters["vertex-normals" ] = self.vnormals
        b3d_parameters["vertex-colors"  ] = self.vcolors
        b3d_parameters["cameras"        ] = self.cameras
        b3d_parameters["lights"         ] = self.lights
        b3d_parameters["mipmap"         ] = self.mipmap
        b3d_parameters["local-space"    ] = self.localsp
        
        if self.filepath == "":
            return {'FINISHED'}

        if not self.filepath.endswith(".b3d"):
            self.filepath += ".b3d"
    
        if os.path.exists(self.filepath):
            #self.report({'ERROR'}, "File Exists")
            B3D_Confirm_Operator.filepath = self.filepath
            bpy.ops.screen.b3d_confirm('INVOKE_DEFAULT')
            return {'FINISHED'}

        write_b3d_file(self.filepath)
        return {'FINISHED'}

# ==== PANEL ====
class OBJECT_PT_hello(bpy.types.Panel):
    bl_label = "B3D Exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
    def draw(self, context):
        global the_scene
        the_scene = context.scene
        
        layout = self.layout
        
        # ==== Types group ====
        row = layout.row()
        
        row.operator("screen.b3d_export", "Export", icon='BLENDER')


# Add to a menu
def menu_func_export(self, context):
    global the_scene
    the_scene = context.scene
    self.layout.operator(B3D_Export_Operator.bl_idname, text="B3D (.b3d)")

def register():
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
    