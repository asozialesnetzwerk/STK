<?php

include_once('config.php');

class DBException extends Exception {}

class DBConnection
{
    private $conn;
    private static $instance;

    private function __construct() {
        $this->conn = new PDO('mysql:host='. DB_HOST . ';dbname=' . DB_NAME, DB_USER, DB_PASSWORD);
        //$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); 
        
    }

    public static function get() {
        if( !self::$instance ) {
	        self::$instance = new DBConnection();
        }
        return self::$instance;
    }

    public function query($query, $params=NULL) {
        if(!$query) {
	        return false;
        } else {
	        $sth = $this->conn->prepare($query);
	        if($sth->execute($params) !== false ) {
	            if(preg_match("/^(" . implode("|", array("select", "describe", "pragma")) . ") /i", $query))
	                return $sth->fetchAll(PDO::FETCH_ASSOC);
                return $sth->rowCount();
	        } else {
	            //Error code for database connection debugging
	            /*
		        $err_arr = $sth->errorInfo();
		        $err_msg = sprintf("SQLSTATE ERR: %s<br />\nmySQL ERR: %s<br />\nMessage: %s<br />\n", $err_arr[0], $err_arr[1], $err_arr[2]);
		        */
	            throw new DBException();
	        }
        }
    }
}
?>
