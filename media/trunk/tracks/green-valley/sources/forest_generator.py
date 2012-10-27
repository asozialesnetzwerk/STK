# Forest Generator 0.1
# Copyright (c) 2012 by Wolfs
# Dual-licensed under the GNU General Public License 3 and the Creative Commons Attribution Share-Alike License v3.0

# README: Please read this carefully
# ----------------------------------
# This script will create a forest out of a tree model and a mesh which indicates the area where the forest will be.
# Change the values below to edit the settings and then press "Run Script".
# The script will interprete the origin of the tree model as the bottom of the tree. You will either have to 
# adapt the origin or move the resulting forest around a bit. However, the script requires the origin to be at the (x,y)
# center of the tree, otherwise neighbouring trees could intersect.
# All properties of the tree models will be copied. The name of the resulting trees will be the name of the model plus
# ".[number]".
#
# NOTE: The forest area model has to have rotation, scale and location applied!
#       The tree model should NOT have rotation, scale and location applied!
#
# WARNING: Since this is a untested, low quality script, it is a good idea to back up your work before using this script :)

import bpy
import math
import mathutils
import mathutils.geometry
import operator
import random

# REQUIRED: Edit these values

# Blender object name of the tree model
tree_model_name = "tree_model"

# Blender object name of the forest area polygon.
# NOTE: The polygon may only consist of triangles
forest_area_name = "forest_area"

# Number of trees in the forest
trees_count = 100

# The following settings will change the trees a bit to avoid a forest full of clones.

# The minimum and the maximum allowed scale of the trees. The script will then choose a
# random scale within these borders.
min_tree_size = 0.6
max_tree_size = 1.3

# The percentage of their radius the trees may intersect
# The lower the value is (0 < value < 1), the more dense the forest will be
tree_radius_max_intersect = 0.5

# Whether the trees should be rotated on the Z axis by a random angle
rotate_trees = True

# YOU ARE FINISHED!
# If you haven't backed up your work yet, this is a good time to do so now.
# Now start the script via the "Run Script" button.
# If you experience errors, check the terminal.
# -------------------------------------------------------------------------------------------------------------------
# Don't change anything below unless you know what you're doing


# Function which calculates the angle between three points
# Arguments must be arrays with two floats
def angle_of(origin, p1, p2):	
	s1 = [p1[0] - origin[0], p1[1] - origin[1]]
	s2 = [p2[0] - origin[0], p2[1] - origin[1]]	
	
	angle = math.atan2(s1[0],s1[1]) - math.atan2(s2[0],s2[1])
	
	return math.degrees(angle)
	
# Returns the cross product of two vectors
def cross_product(x, y):
    result = [x[1]*y[2] - x[2]*y[1], x[2]*y[0] - x[0]*y[2], x[0]*y[1] - x[1]*y[0]]
    
    return result

# Returns the dot product of two vectors
def dot_product(v1, v2):
	return sum(map(operator.mul,v1,v2))

# Whether a point is located on the same side of a line than another one
# All arguments must be float arrays with three coors
def is_on_same_side(p1, p2, x, y):
	cr_pr1 = cross_product([y[0] - x[0], y[1] - x[1], y[2] - x[2]], [p1[0] - x[0], p1[1] - x[1], p1[2] - x[2]])
	cr_pr2 = cross_product([y[0] - x[0], y[1] - x[1], y[2] - x[2]], [p2[0] - x[0], p2[1] - x[1], p2[2] - x[2]])
	
	if dot_product(cr_pr1, cr_pr2) >= 0:
		return True
	else:
		return False
		
# Functions which indicates whether a point is lying inside a given triangle or not	
# All arguments must be float arrays with three coors
def is_point_in_triangle(p, x, y, z):
	if is_on_same_side(p, x, y, z) and is_on_same_side(p, y, x, z) and is_on_same_side(p, z, x, y):
		return True
	else:
		return False
		
def get_intersection_point(p, v1, v2, v3):
	normal = cross_product([v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]], [v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]])
	
	point = mathutils.geometry.intersect_line_plane(
		mathutils.Vector((p[0], p[1], 0)),
		mathutils.Vector((p[0], p[1], 10)),
		mathutils.Vector((v1[0], v1[1], v1[2])),
		mathutils.Vector((normal[0], normal[1], normal[2])),
		False)
	return [point.x, point.y, point.z]
	
def process_forest_creation(tree_model_name, forest_area_name, trees_count, min_tree_size, max_tree_size, tree_radius_max_intersect, rotate_trees):
	print("+------------------------------+")
	print("| This is Forest Generator 0.1 |")
	print("+------------------------------+")
	print("")
	
	# Checking the values
	print("Checking values ...")
	
	if trees_count < 0:
		print("ERROR: The amount of trees cannot be negative!")
		print("Exiting.")
		return
	if trees_count == 0:
		print("ERROR: Why are you trying to create a forest without any trees? :)")
		print("Exiting.")
		return
	
	if min_tree_size > max_tree_size:
		print("WARNING: The minimum tree size cannot be higher than the maximum tree size.")
		print("         I am assuming you accidentally swapped these values.")
		helper = max_tree_size
		max_tree_size = min_tree_size
		min_tree_size = max_tree_size
	if min_tree_size == 0:
		print("WARNING: The minimum tree size is 0. Some trees will be too small to see")
	if max_tree_size == 0:
		print("WARNING: The minimum tree size is 0. Some trees will be too small to see")
	if min_tree_size < 0:
		print("WARNING: The minimum tree size is negative. Some trees will be turned upside down.")
	if max_tree_size < 0:
		print("WARNING: The maximum tree size is negative. All trees will be turned upside down.")
	
	if rotate_trees != False and rotate_trees != True:
		print("ERROR: The tree rotation value has to be \"True\" or \"False\".")
		print("Exiting.")
		return
	
	tree_model = None
	for obj in bpy.data.objects:
	    if obj.name == tree_model_name:
	        tree_model = obj
	        break
	if tree_model == None:
		print("ERROR: The given tree model could not be found.")
		print("       Make sure you entered the name correctly and that you provided the object name")
		print("Exiting.                                                                  ------")
		return
		
	forest_area_model = None
	for obj in bpy.data.objects:
	    if obj.name == forest_area_name:
	        forest_area_model = obj
	        break
	if forest_area_model == None:
		print("ERROR: The given forest area could not be found.")
		print("       Make sure you entered the name correctly and that you provided the object name")
		print("Exiting.                                                                  ------")
		return
		
	# Checking if forest area contains only triangles
	forest_area_mesh = forest_area_model.data
	fam_faces = forest_area_mesh.faces
	
	for face in fam_faces:
		count = len(face.vertices)
		if count != 3:
			print("ERROR: The forest area model contains a face with an illegal vertex count: "+str(count))
			print("       Make sure the area model contains only triangles.")
			print("Exiting.")
			return
	
	# Finished, all values OK
	print("Finished checking. Everything is OK.")
	
	# Generate a rectangle parallel to the x- and the y-axis, in which all x- and y-coordinates of the forest
	# area fit
	
	fa_highest_x = -1
	fa_highest_y = -1
	fa_lowest_x = -1
	fa_lowest_y = -1
	
	first_time = True
	
	for vertex in forest_area_mesh.vertices:
		co = vertex.co
		
		if first_time:
			fa_highest_x = co.x
			fa_lowest_x = co.x
			fa_highest_y = co.y
			fa_lowest_y = co.y
			
			first_time = False
			continue		
		
		if co.x > fa_highest_x:
			fa_highest_x = co.x
		if co.x < fa_lowest_x:
			fa_lowest_x = co.x
		if co.y > fa_highest_y:
			fa_highest_y = co.y
		if co.y < fa_lowest_y:
			fa_lowest_y = co.y
	
	# OK, now we have this rectangle
	#  y
	#  ^
	#  |
	#  3----------------2
	#  |                |
	#  |                |
	#  0----------------1-------> x
	#	
	# Generate rectangle with this indices
	
	forest_area_rect = [[fa_lowest_x,  fa_lowest_y ],
						[fa_highest_x, fa_lowest_y ],
						[fa_highest_x, fa_highest_y],
						[fa_lowest_x, fa_highest_y]
					   ]				
	
	print("Found following rectangle:")
	print("\t\t  ^ y")
	print("\t\t  |")
	print("\t\t  |")
	print("\t\t  |")
	print(str(fa_highest_y)+" 3----------------------2")
	print(               "\t\t  |                      |")
	print(               "\t\t  |                      |")
	print(               "\t\t  |                      |")
	print(str(fa_lowest_y)+ " 0----------------------1------------> x")
	print("   "+str(fa_lowest_x)+"               "+str(fa_highest_x))
	
	print("")
	print("Point 0: ("+str(forest_area_rect[0][0])+"|"+str(forest_area_rect[0][1])+")")
	print("Point 1: ("+str(forest_area_rect[1][0])+"|"+str(forest_area_rect[1][1])+")")
	print("Point 2: ("+str(forest_area_rect[2][0])+"|"+str(forest_area_rect[2][1])+")")
	print("Point 3: ("+str(forest_area_rect[3][0])+"|"+str(forest_area_rect[3][1])+")")
	
	# Calculate radius of tree (assuming it is round)
	tree_radius = ((tree_model.dimensions[0] + tree_model.dimensions[1]) / 2) / 2.0
	print("Der Radius des Baums beträgt "+str(tree_radius))
	
	# Add all trees
	
	print("Forest area model has "+str(len(fam_faces))+" faces")
	
	# Contains data of all added trees: x-coor, y-coor, scale
	tree_data = []
	new_trees = 0
	i = 0
	
	# All trees will be grouped
	# Create a new group
	tree_group = []
	
	while i < trees_count:
		i = i+1
		#print("Trying to place next tree ...")
		# Adding a new tree
		# First choose random x and y coordinates (based on the rectangle in which the forest area polygon fits) and check 
		# whether they are inside the polygon. If not, choose new coordinates. Now check if the coordinates are too near to
		# an existing tree (by using the radius and the scale of the tree). If so, choose new coordinates.
		# If after a thousand tries or so no valid coordinates have been found, the forest is too dense too place another tree.
		
		fertig = False
		
		rounds = 0
		
		x = 0
		y = 0
		scale = 1.0
			
		while not fertig:
			rounds = rounds + 1
			
			if rounds > 1000:
				print("NOTE: Could not find places for more trees. Your number of trees could not be reached.")
				break
			
			x = random.random()*(fa_highest_x - fa_lowest_x) + fa_lowest_x
			y = random.random()*(fa_highest_y - fa_lowest_y) + fa_lowest_y
			scale = random.random()*(max_tree_size - min_tree_size) + min_tree_size
			z = 0
			
			# Inside the polygon?		
			inside_polygon = False
			for face in fam_faces:
				v0 = forest_area_mesh.vertices[face.vertices[0]]
				v1 = forest_area_mesh.vertices[face.vertices[1]]
				v2 = forest_area_mesh.vertices[face.vertices[2]]
				
				assert v0 != None
				assert v1 != None
				assert v2 != None
				
				if is_point_in_triangle([x,y,0], [v0.co.x, v0.co.y,0], [v1.co.x, v1.co.y,0], [v2.co.x, v2.co.y,0]):
					inside_polygon = True
					
					# Find Z value
					pz = get_intersection_point([x,y], [v0.co.x, v0.co.y, v0.co.z], [v1.co.x, v1.co.y, v1.co.z], [v2.co.x, v2.co.y, v2.co.z])
					
					z = pz[2]
					
					break
			
			if not inside_polygon:
				#print("Point not inside polygon")
				continue
			
			fertig = True
			# Check for other trees
			for data in tree_data:
				# Distance of center points
				distance = math.sqrt(math.pow(data[0] - x,2)+math.pow(data[1] - y,2))
				
				if distance < (data[2]*tree_radius + scale*tree_radius)*tree_radius_max_intersect:
					fertig = False
					break
			
			
		if rounds > 1000:
			break
			
		# Copy the tree
		copymodel = tree_model.copy()
		bpy.data.scenes[0].objects.link(copymodel)
		
		# Apply custom properties (position etc.)
		copymodel.scale = [scale, scale, scale]
		copymodel.location = [x,y,z]
		
		if rotate_trees:
			copymodel.rotation_euler = [copymodel.rotation_euler[0], copymodel.rotation_euler[1], random.random() * 360.0]
		
		# Rename the tree and select it
		copymodel.name = tree_model.name+"."+str(new_trees)
		copymodel.select = True
		
		# Add the tree to the list
		tree_data.append([x,y,scale])
		
		# Add the tree to the object group
		tree_group.append(copymodel)
		
		new_trees = new_trees + 1
	
	# Add a new tree group to the scene if this makes sense (more than one tree)
	real_tree_group = None
	if new_trees > 1:
		real_tree_group = bpy.data.groups.new("forest")
		
		for tree in tree_group:
			real_tree_group.objects.link(tree)
	
	print("Successfully finished. "+str(new_trees)+" trees have been added.")
	if real_tree_group != None:
		print("The trees are connected via the group \""+real_tree_group.name+"\"")
# End of process_forest_creation()

# Start forest creation
process_forest_creation(tree_model_name, forest_area_name, trees_count, min_tree_size, max_tree_size, tree_radius_max_intersect, rotate_trees)
