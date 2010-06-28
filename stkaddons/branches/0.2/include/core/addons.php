<?php
class Addons
{
    function Addons()
    {
        $this->all = array();
        $this->sql_query = \SQL\getAllFromTableWhere("addons", "type", "karts");
    }
    function Next()
    {
        return $this->addon = \SQL\nextItem($this->sql_query);
    }
    function GetName()
    {
        return $this->addon['name'];
    }
    function GetId()
    {
        return $this->addon['id'];
    }
    function GetType()
    {
        return $this->addon['type'];
    }
}
?>
