<?php
function addEdit($type, $name, $option="")
{
    return "<a href=\"javascript:editOption('$type', '$name', '$option')\" ><img class=\"edit_option\" src=\"image/edit.png\" /></a>";
}
?>
