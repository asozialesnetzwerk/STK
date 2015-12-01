import bpy
import bmesh
 
navmeshfile=open('./navmesh.xml', 'w+')
 
obj = bpy.context.edit_object
me = obj.data
bm = bmesh.from_edit_mesh(me)
 
obj_m = bpy.context.scene.objects.active
om = obj_m.matrix_world
 
navmeshfile.write('<navmesh>\n')
navmeshfile.write('<MaxVertsPerPoly nvp="5" />\n') #write a suitable number yourself
navmeshfile.write('<vertices>\n')
 
for vert in bm.verts:
    navmeshfile.write('<vertex x="%f" y="%f" z="%f" />\n' % ((om*vert.co).x, (om*vert.co).z, (om*vert.co).y))
 
navmeshfile.write('</vertices>\n')
navmeshfile.write('<faces>\n')
 
for face in bm.faces:
    navmeshfile.write('<face indices="')
    for vert in face.verts:
        navmeshfile.write('%d ' % vert.index)
 
    list_face = []
    unique_face = []
    for edge in face.edges:
        for l_face in edge.link_faces:
            list_face.append(l_face.index)
 
    [unique_face.append(item) for item in list_face if item not in unique_face]
    unique_face.remove(face.index) #remove current face index
 
    navmeshfile.write('" adjacents="')
    for num in unique_face:
        navmeshfile.write('%d ' % num)
    navmeshfile.write('" />\n')
 
navmeshfile.write('</faces>\n')
navmeshfile.write('</navmesh>\n')