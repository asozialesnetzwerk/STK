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

$addons = new Addons();
$user = new User();
switch(get("go"))
{
    case "addons-view":
        $addons->SelectById(get("value"));
        echo $addons->GetInformations();
        break;
    case "user":
        $user->SelectById(get("id"));
        switch(get("action"))
        {
            case "range":
                $user->SetRange(get("value"));
                break;
        }
        break;
}
?>
