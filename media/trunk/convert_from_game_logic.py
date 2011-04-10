import bpy

for obj in bpy.data.objects:
	print("Processing", obj.name)
	if obj.game and obj.game.properties:
		for k in obj.game.properties.keys():
			#print("    ",k,"=",obj.game.properties[k].value)
			obj[k] = obj.game.properties[k].value
