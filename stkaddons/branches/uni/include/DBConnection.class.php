<?php

require_once('config.php');

class DBException extends Exception {}

class DBConnection
{
    private $conn;
    private static $instance;
    
    //Faking enumeration
    const ROW_COUNT = 1;
    const FETCH_ALL = 2;
    const NOTHING = 4;
    

    private function __construct() {
        $this->conn = new PDO('mysql:host='. DB_HOST . ';dbname=' . DB_NAME, DB_USER, DB_PASSWORD);
        $this->conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); 
        
    }

    public static function get() {
        if( !self::$instance ) {
	        self::$instance = new DBConnection();
        }
        return self::$instance;
    }

    public function query($query, $return_type = DBConnection::NOTHING, $params = NULL) {
        if(!$query)
	        throw new DBException("Empty Query");     
        try{
	        $sth = $this->conn->prepare($query);
	        $sth->execute($params);
	        if($return_type == self::NOTHING)
	            return;
            if($return_type == self::ROW_COUNT)
                return $sth->rowCount();
            if($return_type == self::FETCH_ALL)
                return $sth->fetchAll(PDO::FETCH_ASSOC);    
        } catch (PDOException $e){
            if (DEBUG_MODE){
                printf("SQLSTATE ERR: %s<br />\nmySQL ERR: %s<br />\nMessage: %s<br />\n",$e->errorInfo[0], $e->errorInfo[1], $e->errorInfo[2]);
            }
            throw new DBException();
        }
    }
    
    public function lastInsertId(){
        return $this->conn->lastInsertId();  
    }
}
?>
