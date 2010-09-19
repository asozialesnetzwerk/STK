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
$title = "Redirecting...";
require ROOT."include/header.php";
if(get("action") == "status")
{
    $user = new User();
    $user->SelectById(get("id"));
    $user->SetRange(post("option_input"));
}
elseif(get("action") == "username")
{
    $user = new User();
    $user->SelectById(get("id"));
    $user->SetName(post("option_input"));
}
echo _("Redirecting...");
require ROOT."include/footer.php";
?>
