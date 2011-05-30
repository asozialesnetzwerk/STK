import bpy

for obj in bpy.data.objects:
    print("Processing", obj.name)
    if obj.game and obj.game.properties:
        for k in obj.game.properties.keys():
            # TODO: remove old values?
            obj[k.replace("-","_").lower()] = obj.game.properties[k].value
        
        if 'anim_texture' in obj and len(obj['anim_texture']) > 0:
            obj['enable_anim_texture'] = 'true'
        else:
            obj['enable_anim_texture'] = 'false'

s = bpy.data.scenes[0]
for prop in s.keys():
    # TODO: remove old values?
    s[prop.replace("-","_").lower()] = s[prop]

for m in bpy.data.images:
    for prop in m.keys():
        # TODO: remove old values?
        m[prop.replace("-","_").lower()] = m[prop]

# TODO: create 'use_slowdown' boolean from material id-properties as needed
# TODO: create 'use_sfx' boolean from material id-properties as needed
# TODO: booleans now use "true" and "false"; I think it used to be "yes" and "no" :(
# TODO: Convert kart color from floating point format to integer format

bpy.data.scenes[0]['is_stk_track'] = 'true'