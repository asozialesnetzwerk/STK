"""
Name: 'STK Material Exporter...'
Blender: 259
Group: 'Export'
Tooltip: 'Export a SuperTuxKart track scene'
"""
__author__ = ["Joerg Henrichs (hiker), Marianne Gagnon (Auria)"]
__url__ = ["supertuxkart.sourceforge.net"]
__version__ = "$Revision$"
__bpydoc__ = """\
"""

bl_info = {
    "name": "SuperTuxKart Material Exporter",
    "description": "Exports image properties to the SuperTuxKart track format",
    "author": "Joerg Henrichs, Marianne Gagnon",
    "version": (1,0),
    "blender": (2, 5, 9),
    "api": 31236,
    "location": "File > Export",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://supertuxkart.sourceforge.net/Get_involved",
    "tracker_url": "https://sourceforge.net/apps/trac/supertuxkart/",
    "category": "Import-Export"}


def getScriptVersion():
    try:
        m = re.search('(\d+)', __version__)
        return str(m.group(0))
    except:
        return "Unknown"

import bpy
import os

# ------------------------------------------------------------------------------
# Gets an id property of an object, returning the default if the id property
# is not set. If set_value_if_undefined is set and the property is not
# defined, this function will also set the property to this default value.
def getIdProperty(obj, name, default="", set_value_if_undefined=1):
    import traceback
    try:
        prop = obj[name]
        if isinstance(prop, str):
            return obj[name].replace('&', '&amp;') # this is XML
        else:
            return prop
    except:
        if default!=None and set_value_if_undefined:
            obj[name] = default
    return default

# --------------------------------------------------------------------------
# Write several ways of writing true/false as Y/N
def convertTextToYN(sText):
    sTemp = sText.strip().upper()
    if sTemp=="0" or sTemp[0]=="N" or sTemp=="FALSE":
        return "N"
    else:
        return "Y"


# Writes the materials files, which includes all texture definitions 
# (remember: Blenders "image" objects are STK's "material" objects)
# Please use the STKProperty browser!!!
def writeMaterialsFile(sPath):
    # Read & Write the materials to the file
    limage = bpy.data.images
    
    materfound = False
    for i in limage:
        for sAttrib in i.keys():
            materfound = True
            break
    if not materfound:
        print("No Materials defined.")
        return


    # the values are of format (default value, parent property if any)
    lTextureDefaults = {
           'light'                 : ("Y", None),
           'additive_lightmap'     : ("N", None),
           'fog'                   : ("Y", None),
           'backface_culling'      : ("Y", None),
           'below_surface'         : ("N", None),
           'compositing'           : ('none', None),
           'collision_detect'      : ("N", None),
           'collision_particles'   : ("", 'collision_detect'),
           'collision_reaction'    : ("none", 'collision_detect'),
           'clampu'                : ("N", None),
           'clampv'                : ("N", None),
           'disable_z_write'       : ("N", None),
           'falling_effect'        : ("N", None),
           'graphical_effect'      : ('none', None),
           'ignore'                : ("N", None),
           'mask'                  : ("", None),
           'normal_map'            : ("", 'use_normal_map'),
           'use_normal_map'        : ("N", None),
           'reset'                 : ("N", None),
           'sphere'                : ("N", None),
           'surface'               : ("N", None),
           'high_adhesion'         : ('false', None),
           'slowdown_time'         : (1.0, 'use_slowdown'),
           'max_speed'             : (1.0, 'use_slowdown'),
           'splatting'             : ("N", None),
           'splatting_texture_1'   : ("", 'splatting'),
           'splatting_texture_2'   : ("", 'splatting'),
           'splatting_texture_3'   : ("", 'splatting'),
           'splatting_texture_4'   : ("", 'splatting'),
           'water_shader'          : ("N", None)
    }

    lBooleanAttributes = ["clampu","clampv","light","sphere","surface","below_surface",
                          "falling_effect", "collision_detect", "fog", "additive_lightmap",
                          "anisotropic","backface_culling","ignore","disable_z_write","reset",
                          "sfx_positional", "splatting", "use_normal_map", "water_shader"]
    
    #start_time = bsys.time()
    print("Writing material file --> \t")

    f = open(sPath+"/materials.xml", mode="w", encoding="utf-8")
    f.write("<?xml version=\"1.0\"?>\n")
    f.write("<!-- Generated with script from SVN rev %s -->\n"%getScriptVersion())
    f.write("<materials>\n")

    for i in limage:
        #iterate through material definitions and collect data
        sImage = ""
        sSFX = ""
        sParticle = ""
        sZipper = ""
        hasSoundeffect = (convertTextToYN(getIdProperty(i, "use_sfx", "no")) == "Y")
        hasParticle = (convertTextToYN(getIdProperty(i, "particle", "no")) == "Y")
        hasZipper = (convertTextToYN(getIdProperty(i, "zipper", "no")) == "Y")

        # Create a copy of the list of defaults so that it can be modified. Then add
        # all properties of the current image
        l = []
        for sAttrib in i.keys():
            if sAttrib not in l:
                l.append( (sAttrib, i[sAttrib]) )
        
        for AProperty,ADefault in l:
            # Don't add the (default) values to the property list
            currentValue = getIdProperty(i, AProperty, ADefault,
                                         set_value_if_undefined=0)
            #Correct for all the ways booleans can be represented (true/false;yes/no;zero/not_zero) 
            if AProperty in lBooleanAttributes:
                currentValue = convertTextToYN(currentValue)
            
            #These items pertain to the soundeffects (starting with sfx:)
            if AProperty.strip().startswith("sfx_"):
                strippedName = AProperty.strip()[len("sfx_"):]
                
                if strippedName in ['filename', 'rolloff', 'min_speed', 'max_speed', 'min_pitch', 'max_pitch', 'positional', 'volume']:
                    if isinstance(currentValue, float):
                        sSFX = "%s %s=\"%.2f\""%(sSFX,strippedName,currentValue)
                    else:
                        sSFX = "%s %s=\"%s\""%(sSFX,strippedName,currentValue)
            elif AProperty.strip().upper().startswith("PARTICLE_"):
                #These items pertain to the particles (starting with sfx:)
                strippedName = AProperty.strip()[len("PARTICLE_"):]
                sParticle = "%s %s=\"%s\""%(sParticle,strippedName,currentValue)   
            elif AProperty.strip().upper().startswith("ZIPPER_"):
                #These items pertain to the particles (starting with sfx:)
                strippedName = AProperty.strip()[len("ZIPPER_"):]
                
                sZipper = "%s %s=\"%s\""%(sZipper,strippedName,currentValue)   
            else:
                #These items are standard items
                prop = AProperty.strip()#.lower()
                
                if prop in lTextureDefaults.keys():
                    
                    # if this property is conditional on another
                    cond = lTextureDefaults[prop][1]
                    
                    if currentValue != lTextureDefaults[prop][0] and (cond is None or (cond in i and i[cond] == "true")):
                        if isinstance(currentValue, float):
                            # In blender, proeprties use '_', but STK still expects '-'
                            sImage = "%s %s=\"%.2f\""%(sImage,AProperty.replace("_","-"),currentValue)
                        else:
                            # In blender, proeprties use '_', but STK still expects '-'
                            sImage = "%s %s=\"%s\""%(sImage,AProperty.replace("_","-"),currentValue)

        # Now write the main content of the materials.xml file
        if sImage or hasSoundeffect or hasParticle or hasZipper:
            #Get the filename of the image.
            s = i.filepath
            sImage="  <material name=\"%s\"%s" % (os.path.basename(s),sImage)                
            if hasSoundeffect:
                sImage="%s>\n    <sfx%s/" % (sImage,sSFX)
            if hasParticle:
                sImage="%s>\n    <particles%s/" % (sImage,sParticle)
            if hasZipper:
                sImage="%s>\n    <zipper%s/" % (sImage,sZipper)
            if not hasSoundeffect and not hasParticle and not hasZipper:
                sImage="%s/>\n" % (sImage)
            else:
                sImage="%s>\n  </material>\n" % (sImage)
      
            f.write(sImage)
        
    f.write("</materials>\n")

    f.close()
    #print bsys.time()-start_time,"seconds"
    # ----------------------------------------------------------------------

class STK_Material_Export_Operator(bpy.types.Operator):
    bl_idname = ("screen.stk_material_exporter")
    bl_label = ("Export Materials")
    filepath = bpy.props.StringProperty()

    def execute(self, context):
        writeMaterialsFile(self.filepath)
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    