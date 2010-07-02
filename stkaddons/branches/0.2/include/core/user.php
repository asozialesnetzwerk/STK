<?php
/*
copyright 2010 Lucas Baudin <xapantu@gmail.com>                   
                                                                          
This file is part of stkusers

stkusers is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stkusers is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of       
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with stkusers.  If not, see <http://www.gnu.org/licenses/>.
*/
class User
{
    function User()
    {
        $this->sql_query = \SQL\getAllFromTable("users");
    }
    function Next()
    {
        return $this->user = \SQL\nextItem($this->sql_query);
    }
    function SelectById($id)
    {
        $this->sql_query = \SQL\getAllFromTableWhere("users", "id", $id);
        return $this->user = \SQL\nextItem($this->sql_query);
    }
    function SelectByName($id)
    {
        $this->sql_query = \SQL\getAllFromTableWhere("users", "login", $id);
        return $this->user = \SQL\nextItem($this->sql_query);
    }
    function GetName()
    {
        return $this->user['login'];
    }
    function GetPass()
    {
        return $this->user['pass'];
    }
    function GetRange()
    {
        return $this->user['range'];
    }
    function GetDescription()
    {
        return $this->user['description'];
    }
    function GetLogin()
    {
        return $this->user['login'];
    }
    function GetId()
    {
        return $this->user['id'];
    }
    function GetType()
    {
        return $this->user['type'];
    }
    function GetInformations()
    {
        $test_users = "";
        $test_users .= "<span class=\"usersview_info\">"._("Name:")."</span> ".$this->GetName();
        $test_users .= "<a href=\"javascript:editOption('input', '', 'Name')\" >x</a>";
        $test_users .= "<span class=\"usersview_info\">"._("Range:")."</span> ".$this->GetRange();
        return $test_users;
    }
}
?>
