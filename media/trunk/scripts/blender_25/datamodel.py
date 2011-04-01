# *** INSTRUCTIONS ***
#
# This tool is programmed in 4 layers:
# 1. Define which STK Types belong to what Blender Types
# 2. Define which properties belong to the STK Type
# 3. Define the properties themselves
# 4. Is a property is a Picklist, what are the values in the picklist?

# Define Property Types
type_STRING = 0
type_INTEGER = 1
type_FLOAT = 2
type_COLOUR = 3
type_BOOLEAN = 4
type_PICKLIST = 10
type_STATIC = 11
type_TYPELIST = 12 
type_URL = 14
type_IMAGEURL = 15
type_CHOICELIST = 17
type_DELETE = 20
type_RESET = 21

# Define which STK types correspond to which Blender types 
# *** Mental note: ***
# All Blender Object types: 'Armature', 'Camera', 'Curve', 'Lamp', 'Lattice', 'Mball',
#             'Mesh', 'Surf', 'Empty', 'Wave' (deprecated) or 'unknown'
# Additional Blender types: "Scene" and "Image" 
lBlender2STKTypes = {
    "Camera":["Ignore", "Ahead", "Fixed"], \
    "Empty":["Ignore", "Banana", "Item", "Nitro-Big", "Nitro-Small"], \
    "Image":["Texture"], \
    "Lamp":["Ignore", "Sun"], \
    "Mesh":["Ignore", "Billboard", "Check", "Driveline", "Lap", \
            "Maindriveline", "Particle-Emitter", "Object", "Water"], \
    "Scene":["Track"], \
    "Other":["Ignore"] # All Blender types that cannot be used in STK
}

# Define what properties are coupled with what STK types
# Also determines property order
# The notation "aaa|bbb=ccc" means: show aaa only when bbb equals ccc 
lSTKTypes2Properties = {
    "Ahead":["start"], \
    "Banana":[], \
    "Billboard":[], \
    "Check":["name", "activate", "toggle", "inner-radius", "color"], \
    "Driveline":["invisible", "ai-ignore"], \
    "Empty":[], \
    "Fixed":["start"], \
    "Ignore":[], \
    "Item":[], \
    "Lap":["activate", "toggle", "inner-radius", "color"], \
    "Maindriveline":["activate"], \
    "Nitro-Big":[], \
    "Nitro-Small":[], \
    "Object":["animated", \
                "anim-texture|animated=yes", \
                "anim-dx|animated=yes", \
                "anim-dy|animated=yes", \
               "name", \
               "interaction", \
                "shape|interaction=static",
                "shape|interaction=move",
                "mass|interaction=move"], \
    "Particle-Emitter":[], \
    "Sun":["ambient", "diffuse", "specular"], \
    "Texture":["anisotropic", "backface-culling", "clampU", "clampV", "compositing", "disable-z-write", \
               "friction", "ignore", "light", "max-speed", "reset", "slowdown-time", "sphere", \
               "graphical-effect", "surface", "below-surface", \
               "falling-effect", "sound-effect", \
                "sfx:filename|sound-effect=yes", \
                "sfx:name|sound-effect=yes", \
                "sfx:rolloff|sound-effect=yes", \
                "sfx:min-speed|sound-effect=yes", \
                "sfx:max-speed|sound-effect=yes", \
                "sfx:min-pitch|sound-effect=yes", \
                "sfx:max-pitch|sound-effect=yes", \
                "sfx:positional|sound-effect=yes", \
               "zipper", \
                "zipper:duration|zipper=yes", \
                "zipper:max-speed-increase|zipper=yes", \
                "zipper:fade-out-time|zipper=yes", \
                "zipper:speed-gain|zipper=yes", \
               "particle", \
                "particle:base|particle=yes", \
                "particle:condition|particle=yes"], \
    "Track":["name", "groups", "designer", "music", "screenshot", "arena", \
             "sky-type", \
              "sky-texture|sky-type=dome", \
              "sky-texture1|sky-type=box", \
              "sky-texture2|sky-type=box", \
              "sky-texture3|sky-type=box", \
              "sky-texture4|sky-type=box", \
              "sky-texture5|sky-type=box", \
              "sky-texture6|sky-type=box", \
              "sky-horizontal|sky-type=dome", \
              "sky-vertical|sky-type=dome", \
              "sky-texture-percent|sky-type=dome", \
              "sky-sphere-percent|sky-type=dome", \
              "sky-color|sky-type=simple", \
             "ambient-color", "camera-far", \
             "fog", \
              "fog-color|fog=yes", \
#             "fog-density|fog=yes",\
              "fog-start|fog=yes", \
              "fog-end|fog=yes", \
             "start-karts-per-row", "start-forwards-distance", "start-sidewards-distance", \
              "start-upwards-distance", \
             "weather"], \
    "Water":["name", \
             "height", \
             "length", \
             "speed", \
             "animated", \
              "anim-texture|animated=yes", \
              "anim-dx|animated=yes", \
              "anim-dy|animated=yes"], \
}

# Finally define the properties of each property
#
# Formatting is:
# BOOLEAN  - default
# COLOUR   - default(r,g,b)
# FLOAT    - default, min, max, step
# IMAGEURL - default, max_length
# INTEGER  - default, min, max
# PICKLIST - default ==> Please don't forget to update lSTK_Picklist, below.
# STATIC   - value 
# STRING   - default, max_length
# URL      - default, max_length
lPropertyDef = {
# General use                
    "activate":[type_STRING, "", 50], \
    "color":[type_COLOUR, 0.0, 0.0, 0.0], \
    "inner-radius":[type_FLOAT, 1, 0, 10000, 0.1], \
    "name":[type_STRING, "", 50], \
    "start":[type_FLOAT, 25, 1, 2000, 1], \
    "toggle":[type_STRING, "", 50], \
# Driveline
    "invisible":[type_BOOLEAN, "no"],
    "ai-ignore":[type_BOOLEAN, "no"],
# Scene only
    "ambient-color":[type_COLOUR, 0.0, 0.0, 0.0], \
    "arena":[type_BOOLEAN, "no"], \
    "camera-far":[type_INTEGER, 200, 10, 100000], \
    "designer":[type_STRING, "", 200], \
    "fog":[type_BOOLEAN, "no"], \
    "fog-color":[type_COLOUR, 0.0, 0.0, 0.0], \
#    "fog-density":[type_FLOAT,16,0,1000,0.1],\
    "fog-start":[type_FLOAT, 1000, 0, 1000000, 0.1], \
    "fog-end":[type_FLOAT, 1000, 0, 1000000, 0.1], \
    "groups":[type_STRING, "", 200], \
    "music":[type_URL, "", 200], \
    "screenshot":[type_IMAGEURL, "", 200], \
    "sky-type":[type_PICKLIST, "dome"], \
    "sky-color":[type_COLOUR, 0.0, 0.0, 0.0], \
    "sky-texture":[type_IMAGEURL, "", 200], \
    "sky-texture1":[type_IMAGEURL, "", 200], \
    "sky-texture2":[type_IMAGEURL, "", 200], \
    "sky-texture3":[type_IMAGEURL, "", 200], \
    "sky-texture4":[type_IMAGEURL, "", 200], \
    "sky-texture5":[type_IMAGEURL, "", 200], \
    "sky-texture6":[type_IMAGEURL, "", 200], \
    "sky-texture-percent":[type_FLOAT, 0.5, 0, 1, 0.1], \
    "sky-sphere-percent":[type_FLOAT, 1.3, 0, 2, 0.1], \
    "sky-horizontal":[type_INTEGER, 16, 0, 1000], \
    "sky-vertical":[type_INTEGER, 16, 0, 1000], \
    "start-karts-per-row":[type_INTEGER, 2, 1, 10], \
    "start-forwards-distance":[type_FLOAT, 1.1, 0, 1000, 0.1], \
    "start-sidewards-distance":[type_FLOAT, 1.1, 0, 1000, 0.1], \
    "start-upwards-distance":[type_FLOAT, 1.1, 0, 1000, 0.1], \
    "weather":[type_PICKLIST, "none"], \
#For Textures  
    "clampU":[type_BOOLEAN, "no"], \
    "clampV":[type_BOOLEAN, "no"], \
    "compositing":[type_PICKLIST, "none"], \
    "light":[type_BOOLEAN, "yes"], \
    "sphere":[type_BOOLEAN, "no"], \
    "slowdown-time":[type_FLOAT, 1.0, 0, 100, 0.1], \
    "anisotropic":[type_BOOLEAN, "no"], \
    "max-speed":[type_FLOAT, 1.0, 0, 1.0, 0.1], \
    "friction":[type_FLOAT, 1.0, 0.0, 50000, 0.1], \
    "particle":[type_BOOLEAN, "no"], \
    "particle:base":[type_URL, "", 200], \
    "particle:condition":[type_CHOICELIST, "none"], \
    "backface-culling":[type_BOOLEAN, "yes"], \
    "ignore":[type_BOOLEAN, "no"], \
    "disable-z-write":[type_BOOLEAN, "no"], \
    "zipper":[type_BOOLEAN, "no"], \
    "zipper:duration":[type_FLOAT, 3.5, 0, 10, 0.1], \
    "zipper:max-speed-increase":[type_FLOAT, 15, 0, 100, 0.1], \
    "zipper:fade-out-time":[type_FLOAT, 3, 0, 100, 0.1], \
    "zipper:speed-gain":[type_FLOAT, 4.5, 0, 100, 0.1], \
    "reset":[type_BOOLEAN, "no"], \
    "surface":[type_BOOLEAN, "no"], \
    "falling-effect":[type_BOOLEAN, "no"], \
    "below-surface":[type_BOOLEAN, "no"], \
    "graphical-effect":[type_PICKLIST, "none"], \
    "sound-effect":[type_BOOLEAN, "no"], \
    "sfx:filename":[type_STRING, "", 200], \
    "sfx:name":[type_STRING, "", 50], \
    "sfx:rolloff":[type_FLOAT, 0.1, 0, 100, 0.1], \
    "sfx:min-speed":[type_FLOAT, 0.0, 0, 500, 0.1], \
    "sfx:max-speed":[type_FLOAT, 30.0, 0, 500, 0.1], \
    "sfx:min-pitch":[type_FLOAT, 1.0, 0.5, 2, 0.1], \
    "sfx:max-pitch":[type_FLOAT, 1.0, 0.5, 2, 0.1], \
    "sfx:positional":[type_BOOLEAN, "no"], \
#For Lights
    "ambient":[type_COLOUR, 0.0, 0.0, 0.0], \
    "diffuse":[type_COLOUR, 0.0, 0.0, 0.0], \
    "specular":[type_COLOUR, 0.0, 0.0, 0.0], \
#For Waters
    "height":[type_FLOAT, 2, 0, 100, 0.1], \
    "length":[type_FLOAT, 10, 0, 100, 0.1], \
    "speed":[type_FLOAT, 300, 0, 1000, 0.1], \
#For Objects
    "animated":[type_BOOLEAN, "no"], \
    "anim-texture":[type_IMAGEURL, "", 200], \
    "anim-dx":[type_FLOAT, 0, 0, 1000, 10], \
    "anim-dy":[type_FLOAT, 0, 0, 1000, 10], \
    "interaction":[type_PICKLIST, "none"], \
    "shape":[type_PICKLIST, "box"], \
    "mass":[type_FLOAT, 225, 0, 10000, 0.1], \
}
             
# For picklist, add <name>:<valuelist> to lSTK_Picklist. The valuelist items are |-separated...
lSTK_Picklist = {"sky-type": "dome|box|simple", \
                "graphical-effect": "none|water", \
                "compositing": "none|blend|test|additive", \
                "particle:condition": "skid|drive", \
                "interaction": "none|ghost|static|move", \
                "shape": "box|sphere|coneX|coneY|coneZ", \
                "weather": "none|rain|snow"
}
