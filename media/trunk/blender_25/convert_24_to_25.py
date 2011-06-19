import bpy

for obj in bpy.data.objects:
    print("Processing", obj.name)
    if obj.game and obj.game.properties:
        for k in obj.game.properties.keys():
            # TODO: remove old values?
            val = obj.game.properties[k].value

            if val == "nitro-small":         val = "nitro_small"
            elif val == "nitro-big" :        val = "nitro_big"
            elif val == "yes" :              val = "true"
            elif val == "no" :               val = "false"
            elif val == "particle-emitter" : val = "particle_emitter"
            elif val == "main-driveline" :   val = "maindriveline"

            obj[k.replace("-","_").lower()] = val
        
        if 'anim_texture' in obj and len(obj['anim_texture']) > 0:
            obj['enable_anim_texture'] = 'true'
        else:
            obj['enable_anim_texture'] = 'false'

s = bpy.data.scenes[0]
for prop in s.keys():
    # TODO: remove old values?
    val = s[prop]
    if val == "yes" : val = "true"
    s[prop.replace("-","_").lower()] = val

for m in bpy.data.images:
    for prop in m.keys():
        # TODO: remove old values?
        val = m[prop]
        if val == "yes" : val = "true"
        m[prop.replace("-","_").replace(":","_").lower()] = val
    
    if 'max_speed' in m and m['max_speed'] < 1.0:
        m['use_slowdown'] = 'true'
    else:
        m['use_slowdown'] = 'false'
    
    if 'sfx_filename' in m and len(m['sfx_filename']) > 0:
        m['use_sfx'] = 'true'
    else:
        m['use_sfx'] = 'false'
    
    if 'particle_base' in m and len(m['particle_base']) > 0:
        m['particle'] = 'true'
    else:
        m['particle'] = 'false'
        

# TODO: while we're at it, convert all old transparency/alpha properties over to the new compositing one?
# TODO: Convert kart color from floating point format to integer format

bpy.data.scenes[0]['is_stk_track'] = 'true'