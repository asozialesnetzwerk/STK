<?php
namespace SQL
{
    mysql_connect(DB_HOST, DB_USER, DB_PASSWORD);
    mysql_select_db(DB_NAME);
    function getAllFromTable($table)
    {
        return mysql_query("SELECT * FROM" .$table);
    }
    function getAllFromTableWhere($table, $property, $value)
    {
        return mysql_query("SELECT * FROM $table WHERE `$property` = '$value'");
    }
    function nextItem($sql_query)
    {
        return mysql_fetch_array($sql_query);
    }
}
?>
