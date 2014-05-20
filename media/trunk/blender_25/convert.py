import bpy

print('=======================================')

for img in bpy.data.images:
    print(img.name)
    if 'compositing' in img:
        #print('    compositing = ', img['compositing'])
        
        if img['compositing'] == 'blend':
            img['shader'] = 'alphablend'
        if img['compositing'] == 'test':
            img['shader'] = 'alphatest'
        if img['compositing'] == 'additive':
            img['shader'] = 'additive'
        if img['compositing'] == 'coverage':
            img['shader'] = 'alphatest'
        
    if 'graphical_effect' in img:
        #print('    graphical_effect = ', img['graphical_effect'])
        
        if img['graphical_effect'] == 'bubble':
            img['shader'] = 'bubble'
        if img['graphical_effect'] == 'grass':
            img['shader'] = 'grass'
        if img['graphical_effect'] == 'spheremap':
            img['shader'] = 'spheremap'
        if img['graphical_effect'] == 'splatting':
            img['shader'] = 'splatting'
        if img['graphical_effect'] == 'water_shader':
            img['shader'] = 'water_shader'
            
    if 'light' in img and img['light'] == 'false':
        img['shader'] = 'unlit'
        
        