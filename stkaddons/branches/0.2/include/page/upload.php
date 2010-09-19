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
            <form action="index.php?go=upload&amp;type=<?=$type?>&amp;action=valid" method="POST"  enctype="multipart/form-data">
                <input type="text" name="name" value="<?=_("Name of the addons, it must be in english.")?>"/>
                <br />
                <textarea name="description"><?=_("Description of the addons, it must be in english.")?></textarea>
                <br />
                <label><?=_("File:")?> </label>
                <input type="file" name="file" id="file"/>
                <br/>
                <input type="submit"/>
            </form>
            <?php
        }
        else
        {
            if (isset($_FILES['file']) &&
                $_FILES['file']['type'] == "application/zip") {
                SQL\insert("addons", array('user', 'name', 'description',
                           'type'), array($USER->GetId(), post("name"), post("description"), $type));
                move_uploaded_file($_FILES['file']['tmp_name'],
                                   DOWNLOAD_PATH."/".post("name").".zip");
            }
            else
            {
                ?>
                <span class="error upload_error">
                <?=_("Please re-upload your file. It must be a .zip."."<br />")?>
                </span>
                <br />
                
                <form action="index.php?go=upload&amp;type=<?=$type?>&amp;action=valid" method="POST"  enctype="multipart/form-data">
                    <input type="text" name="name" value="<?=post("name")?>"/>
                    <br />
                    <textarea name="description"><?=post("description")?></textarea>
                    <br />
                    <label><span span="error"><?=_("File:")?> </span></label>
                    <input type="file" name="file" id="file"/>
                    <br/>
                    <input type="submit"/>
                </form>
                <?php
            }
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
