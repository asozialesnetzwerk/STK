<?php
    class DBConnection {
        private $conn;
        private static $instance;

        public function __construct() {
            $this->conn = new PDO('mysql:host='. DB_HOST . ';dbname=' . DB_NAME, DB_USER, DB_PASSWORD);
            //$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); 
        }

        public static function getInstance() {
	        if( !self::$instance ) {
		        self::$instance = new DBConnection();
	        }
	        return self::$instance;
        }

        public function query($query, $params=NULL) {
            echo 'check';
	        if(!$query) {
		        return NULL;
	        } else {
                var_dump($this->conn);
		        $sth = $this->conn->prepare($query);
		        if($sth->execute($params)) {
			        return $sth->fetchAll(PDO::FETCH_ASSOC);
		        } else {
			        $err_arr = $sth->errorInfo();
			        $err_msg = sprintf("SQLSTATE ERR: %s<br />\nmySQL ERR: %s<br />\nMessage: %s<br />\n", $err_arr[0], $err_arr[1], $err_arr[2]);
			        Throw new Exception($err_msg);
		        }
	        }
        }
    }
?>
