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
        $this->sql_query = getAllFromTable("users");
    }
    function Next()
    {
        return $this->user = nextItem($this->sql_query);
    }
    function SelectById($id)
    {
        $this->sql_query = getAllFromTableWhere("users", "id", $id);
        $succes = true;
        if(!$this->user = nextItem($this->sql_query))
            $succes = false;
        if($succes)
            $this->UpdateStatus();
        return $succes;
    }
    function SelectByName($id)
    {
        $this->sql_query = getAllFromTableWhere("users", "login", $id);
        $succes = $this->user = nextItem($this->sql_query);
        if($succes)
            $this->UpdateStatus();
        return $succes;
    }
    function UpdateStatus()
    {
        global $status, $status_index;
        $this->status = $status[$status_index[$this->GetRange()]];
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
    function SetRange($range)
    {
        global $status, $status_index, $USER;
        if($USER->status[$status_index[$this->GetRange()] + 1] && $USER->status[$status_index[$range] + 1])
        {
            update("users", "id", $this->GetId(), "range", $range);
            return true;
        }
        else
        {
            echo "Security fail...";
            return false;
        }
    }
    function SetName($name)
    {
        global $status, $status_index, $USER;
        if($USER->status[$status_index[$this->GetRange()] + 1])
        {
            update("users", "id", $this->GetId(), "login", $name);
            return true;
        }
        else
        {
            echo "Security fail...";
            return false;
        }
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
        global $status;
        $test_users = "";
        $test_users .= "<span class=\"usersview_info\">"._("Name:")."</span> ".$this->GetName();
        $test_users .= addEdit("input", "&amp;action=username&amp;id=".$this->GetId());
        $test_users .= "<span class=\"usersview_info\">"._("Status:")."</span> ".$this->GetRange();
        $option_status = "";
        foreach($status as $statu)
        {
            $option_status .= "<option value=\'".$statu[0]."\'>".$statu[0]."</option>";
        }
        $test_users .= addEdit("select", "&amp;action=status&amp;id=".$this->GetId(), $option_status);
        return $test_users;
    }
}
?>
