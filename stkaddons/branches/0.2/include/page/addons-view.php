<?php
/*
copyright 2010 Lucas Baudin <xapantu@gmail.com>                   
                                                                          
This file is part of stkaddons

stkaddons is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stkaddons is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of       
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with stkaddons.  If not, see <http://www.gnu.org/licenses/>.
*/
    $title = "Addons";
    if(get("type") == "karts")
    {
        $type = "karts";
    }
    else
    {
        $type = "tracks";
    }

    $addons = new Addons($type);

    require ROOT."include/header.php";


    echo "\t<div id=\"listAddons\">\n";
    echo "\t\t<ul>\n";
    while($addons->Next())
    {
        echo "\t\t\t<li>\n";
        echo "\t\t\t\t<a href=\"javascript:loadAddonsInformations(".$addons->GetId().")\">".$addons->GetName()."</a>\n";
        echo "\t\t\t</li>\n";
    }
    echo "\t\t</ul>\n";
    echo "\t</div>\n";

    echo "\t<div id=\"viewAddons\">\n";
    echo "\t\t<p>"._("To start, click on an addon.")."</p>\n";
    echo "\t</div>\n";

    require ROOT."include/footer.php";
?>
