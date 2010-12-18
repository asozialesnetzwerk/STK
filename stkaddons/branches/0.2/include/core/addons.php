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
class Addons
{
    function Addons($type="")
    {
        $this->all = array();
       if($type != "")
            $this->sql_query = getAllFromTableWhere("addons", "type", $type);
        else
            $this->sql_query = getAllFromTable("addons");
    }
    function Next()
    {
        return $this->addon = nextItem($this->sql_query);
    }
    function SelectById($id)
    {
        $this->sql_query = getAllFromTableWhere("addons", "id", $id);
        return $this->addon = nextItem($this->sql_query);
    }
    function GetName()
    {
        return $this->addon['name'];
    }
    function GetDescription()
    {
        return $this->addon['description'];
    }
    function GetAuthor()
    {
        return $this->addon['author'];
    }
    function GetId()
    {
        return $this->addon['id'];
    }
    function GetType()
    {
        return $this->addon['type'];
    }
    function GetInformations()
    {
        $test_addons = "";
        $test_addons .= "<img class=\"addonsview_image\" src=\"".DOWNLOAD."/image/".$this->addon['image']."\" />";
        $test_addons .= "<span class=\"addonsview_info\">"._("Name:")."</span> ".$this->GetName();
        $test_addons .= "<span class=\"addonsview_info\">"._("Description:")."</span> ".$this->GetDescription();
        $test_addons .= "<span class=\"addonsview_info\">"._("Author:")."</span> ".$this->GetAuthor();
        return $test_addons;
    }
}
?>
