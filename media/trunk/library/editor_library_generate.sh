os_name=$(/bin/uname -o)
if [ "$os_name" = "Cygwin" ]; then
    blender_path="/cygdrive/c/Program Files/Blender Foundation/Blender/blender.exe"

    curr_dir=$(/bin/pwd)
    curr_dir_win=$(/bin/cygpath -w "$curr_dir")

    for blend in $(/bin/find . -name "*.blend"); do  
        echo "$blend"
        blend2=$(/bin/cygpath -w "$blend")
        echo "$blend2"
        "$blender_path" -P "$curr_dir_win\\editor_library_generate.py" "$curr_dir_win\\$blend2"
    done
else
    blender_path="/bin/blender"

    curr_dir=$(/bin/pwd)

    for blend in $(/bin/find . -name "*.blend"); do  
        echo "$blend"
        "$blender_path" -P "$curr_dir/editor_library_generate.py" "$curr_dir/$blend"
    done
fi