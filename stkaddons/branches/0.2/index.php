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
session_start();

define("ROOT", "./");
require ROOT."include/include.php";
if(!isset($_GET['go']) or $_GET['go'] == "index")
{
    require ROOT."include/page/index.php";
}
elseif($_GET['go'] == "addons-view")
{
    $css = "addons-view.css";
    require ROOT."include/page/addons-view.php";
}
elseif(get("go") == "login")
{
    $css = "login.css";
    require ROOT."include/page/login.php";
}
else
{
    ?>
    No page named <?php echo $_GET['go'];?>.
    <?php
}
?>
