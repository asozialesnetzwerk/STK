<?php
    $title = "Upload an addons";
    if(get("type") == "karts")
    {
        $type = "karts";
        $addons = new Addons($type);
    }
    elseif(get("type") == "tracks")
    {
        $type = "tracks";
        $addons = new Addons($type);
    }
    else
    {
        $type = "";
    }

    require ROOT."include/header.php";
    if(get("type") == "karts" || get("type") == "tracks")
    {
        if(get("action") != "valid")
        {
            ?>
            <form action="index.php?go=upload&amp;type=<?=$type?>&amp;action=valid" method="POST">
                <input type="text" name="name" value="<?=_("Name of the addons, it must be in english.")?>"/>
                <br />
                <textarea name="description"><?=_("Description of the addons, it must be in english.")?></textarea>
                <br />
                <label>File: </label>
                <input type="file" name="file"/>
                <br/>
                <input type="submit"/>
            </form>
            <?php
        }
    }
    else
    {
        ?>
        <a href="index.php?go=upload&amp;type=tracks">Upload a track.</a><br />
        <a href="index.php?go=upload&amp;type=kart">Upload a kart.</a>
        <?php
    }
    require ROOT."include/footer.php";
?>
