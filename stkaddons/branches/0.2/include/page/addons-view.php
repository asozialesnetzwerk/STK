<?php
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
