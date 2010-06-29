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

namespace SQL
{
    mysql_connect(DB_HOST, DB_USER, DB_PASSWORD);
    mysql_select_db(DB_NAME);
    function getAllFromTable($table)
    {
        return mysql_query("SELECT * FROM ".DB_PREFIX.$table);
    }
    function getAllFromTableWhere($table, $property, $value)
    {
        return mysql_query("SELECT * FROM ".DB_PREFIX.$table." WHERE `$property` = '$value'");
    }
    function nextItem($sql_query)
    {
        return mysql_fetch_array($sql_query);
    }
}
?>
