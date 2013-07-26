<?php
/**
 * copyright 2011 Stephen Just <stephenjust@users.sf.net>
 *           2013 Glenn De Jonghe
 *
 * This file is part of stkaddons
 *
 * stkaddons is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * stkaddons is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with stkaddons.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once('Validate.class.php');
require_once('Verification.class.php');
require_once('DBConnection.class.php');
require_once('exceptions.php');

class User
{
    public static $logged_in = false;
    public static $user_id = 0;
    
    static function init() {
        if(defined('API')) return;
        // Validate user's session on every page
        if (session_id() == "") {
            session_start();
        }

        // Check if any session variables are not set
        if (!isset($_SESSION['userid']) ||
                !isset($_SESSION['user']) ||
                !isset($_SESSION['real_name']) ||
                !isset($_SESSION['last_login']) ||
                !isset($_SESSION['role']))
        {
            // One or more of the session variables was not set - this may
            // be an issue, so force logout
            User::logout();
            return;
        }
        // Validate session if complete set of variables is available
   
        try{
            $result = DBConnection::get()->query(
                "SELECT `id`,`user`,`pass`,`name`,`role`
    	        FROM `" . DB_PREFIX . "users`
                WHERE `user` = :username
                AND `last_login` = :lastlogin
                AND `name` = :realname
                AND `active` = 1",
                DBConnection::ROW_COUNT,
                array(
                    ':username'     => (string) $_SESSION['user'],
                    ':lastlogin'    => $_SESSION['last_login'],
                    ':realname'     => (string) $_SESSION['real_name']
                )
            );
        }catch(DBException $e){
            throw new UserException(htmlspecialchars(
                _('An error occurred trying to validate your session.') .' '.
                _('Please contact a website administrator.')
            ));
        }
        
        
        if ($result != 1) {
            User::logout();
            return false;
        }
        User::$user_id = $_SESSION['userid'];
        User::$logged_in = true;
    }
    
    static function updateLoginTime($userid)
    {       
        try{
            $result = DBConnection::get()->query(
                "UPDATE `".DB_PREFIX."users`
                SET `last_login` = NOW()
                WHERE `id` = :userid",
                DBConnection::NOTHING,
                array
                (
                    ':userid'   => $userid
                )
            );
            $result = DBConnection::get()->query(
                "SELECT `last_login`
                FROM `".DB_PREFIX."users`
                WHERE `id` = :userid",
                DBConnection::FETCH_ALL,
                array
                (
                    ':userid'   => $userid
                )
            );
            if (count($result) !== 1) {
                throw new PDOException();
            }
            return $result[0]['last_login'];
        }
        catch (PDOException $e){
            User::logout();
            throw new UserException(htmlspecialchars(
                _('An error occurred while recording last login time.') .' '.
                _('Please contact a website administrator.')
            ));
        }
        return $time;
    }

    static function login($username,$password)
    {
        $result = Validate::credentials($username, $password);
        // Check if the user exists
        if(count($result) != 1) {
            User::logout();
            throw new UserException(htmlspecialchars(_('Your username or password is incorrect.')));
        }

        $_SESSION['userid'] = $result[0]["id"];      
        $_SESSION['user'] = $result[0]["user"];
        $_SESSION['real_name'] = $result[0]["name"];
        User::$user_id = $result[0]['id'];  
        $_SESSION['last_login'] = User::updateLoginTime(User::$user_id);
        User::$logged_in = true;
        include(ROOT.'include/allow.php');
        
        // Convert unsalted password to a salted one
        if (strlen($password) === 64) {
            $password = Validate::password($password);
            User::change_password($password);
            Log::newEvent("Converted the password of '$username' to use a password salting algorithm");
        }
        
        return true;
    }

    static function logout()
    {
        unset($_SESSION['userid']);
        unset($_SESSION['user']);
        unset($_SESSION['role']);
        unset($_SESSION['real_name']);
        unset($_SESSION['last_login']);
        session_destroy();
        session_start();
        User::$user_id = 0;
        User::$logged_in = false;
    }
    
    /**
     * Change the password of the supplied user; if none supplied, currently logged in user is used.
     * @param string $new_password
     * @param int $userid defaults to currently logged in user.
     * @throws UserException
     */
    static function change_password($new_password, $userid = 0) {
        if ($userid === 0)
            if (!User::$logged_in)
                throw new UserException(htmlspecialchars(_('You must be logged in to change a password.')));
            else
                $userid = User::$user_id;
   
        try{
            $count = DBConnection::get()->query(
                "UPDATE `".DB_PREFIX."users`
                SET `pass`   = :pass
    	        WHERE `id` = :userid",
                DBConnection::ROW_COUNT,
                array(
                        ':userid'   => (int) $userid,
                        ':pass'     => (string) $new_password
                )
            );
            if ($count === 0)
                throw new DBException();
        }catch(DBException $e){
            throw new UserException(htmlspecialchars(
                _('An error occured while trying to change your password.') .' '.
                _('Please contact a website administrator.')
            ));
        }
    }
    /*
    static function exists($username) {
	   try { 
	       Validate::username($username); 
	   }
	   catch (UserException $e) {
	       return false;
	   }
	
    	$query = 'SELECT `id`
                    FROM `'.DB_PREFIX."users`
                    WHERE `user` = '$username'";
    	$handle = sql_query($query);
    	if (!$handle)
    	    return false;
    	if (mysql_num_rows($handle) === 0)
    	    return false;
    	return true;
    }*/
    
    /**
     * Activate a new user
     * @param int $userid
     * @param string $ver_code 
     * @throws UserException when activation failed
     */
    static function activate($userid, $ver_code) {
        Verification::verify($userid, $ver_code);
        try{
            $count = DBConnection::get()->query(
                "UPDATE `".DB_PREFIX."users` 
                SET `active` = '1' 
    	        WHERE `id` = :userid",
                DBConnection::ROW_COUNT,
                array(
                        ':userid'   => $userid
                )
            );
            if ($count === 0)
                throw new DBException();
            Verification::delete($userid);
        }catch(DBException $e){
            throw new UserException(htmlspecialchars(
                    _('An error occurred trying to activate your useraccount.') .' '.
                    _('Please contact a website administrator.')
            ));
        }        
        Log::newEvent("User with ID '{$userid}' activated.");
    }


    /**
     * Register a new user account
     * @param string $username Must be unique
     * @param string $password
     * @param string $password_conf
     * @param string $email Must be unique
     * @param string $name
     * @param string $terms
     * @throws UserException 
     */
    public static function register($username, $password, $password_conf, $email, $name, $terms)
    {
	    // Sanitize inputs
	    $username = Validate::username($username);
	    $password = Validate::password($password, $password_conf);
	    $email = Validate::email($email);
	    $name = Validate::realname($name);
	    $terms = Validate::checkbox($terms,htmlspecialchars(_('You must agree to the terms to register.')));
	    // Make sure requested username is not taken
        try{
            $result = DBConnection::get()->query(
                "SELECT `user` 
    	        FROM `".DB_PREFIX."users` 
    	        WHERE `user` LIKE :username",
                DBConnection::FETCH_ALL,
                array(
                    ':username'   => $username
    	        )	        
            );
        }catch(DBException $e){
            throw new UserException(htmlspecialchars(
                _('An error occurred trying to validate your username.') .' '.
                _('Please contact a website administrator.')
            ));
        }
        if(count($result) !== 0){
	        throw new UserException(htmlspecialchars(
	            _('This username is already taken.')
            ));
        }
	    // Make sure the email address is unique
        try{
            $result = DBConnection::get()->query(
                "SELECT `email` 
    	        FROM `".DB_PREFIX."users` 
    	        WHERE `email` LIKE :email",
                DBConnection::FETCH_ALL,
                array(
                    ':email'   => $email
    	        )	        
            );
        }catch(DBException $e){
            throw new UserException(htmlspecialchars(
                _('An error occurred trying to validate your email address.') .' '.
                _('Please contact a website administrator.')
            ));
        }
        if(count($result) !== 0){
	        throw new UserException(htmlspecialchars(
	            _('This email address is already taken.')
            ));
        }

	    // No exception occurred - continue with registration
        try{
            $result = DBConnection::get()->query
            (
                "INSERT INTO `".DB_PREFIX."users` 
                (`user`,`pass`,`name`, `email`, `active`, `reg_date`)
                VALUES(:username, :password, :name, :email, 0, CURRENT_DATE())",
                DBConnection::ROW_COUNT,
                array
                (
                    ':username'     => $username,
                    ':password'     => $password,
                    ':name'         => $name,
                    ':email'        => $email                            
                )
            );
            if($result !== 1){
                throw new DBException();
            }
            $userid = DBConnection::get()->lastInsertId();
            $verification_code = Verification::generate($userid);
        }catch(DBException $e){
            throw new UserException(htmlspecialchars(
		        _('An error occurred while creating your account.') .' '. 
		        _('Please contact a website administrator.')
            ));
        }
        
	    // Send verification email	    
	    try {
	        $mail = new SMail;
	        $mail->newAccountNotification($email, $userid, $username, $verification_code, SITE_ROOT.'register.php');
	    }
	    catch (Exception $e) {
	        Log::newEvent("Registration email for user '$username' with id '$userid' failed.");
	        throw new UserException($e->getMessage().' '._('Please contact a website administrator.'));
	    }
	    Log::newEvent("Registration submitted for user '$username' with id '$userid'.");
    }
    
    /**
     * Get the role of the current user
     * @return string Role identifier
     */
    public static function getRole() {
	    if (!User::$logged_in) {
	        return 'unregistered';
	    } else {
	        $query = 'SELECT `role`
		    FROM `'.DB_PREFIX.'users`
		    WHERE `user` = \''.mysql_real_escape_string($_SESSION['user']).'\'';
	        $handle = sql_query($query);
	        if (!$handle) return 'unregistered';
	        
	        $result = mysql_fetch_array($handle);
	        return $result[0];
        }
    } // FIXME
}

User::init();

function loadUsers()
{
    global $js;
    $userLoader = new coreUser();
    $userLoader->loadAll();
    echo <<< EOF
<ul>
<li>
<a class="menu-item" href="javascript:loadFrame({$_SESSION['userid']},'users-panel.php')">
<img class="icon" src="image/user.png" />
EOF;
    echo htmlspecialchars(_('Me')).'</a></li>';
    ?>
    <?php
    while($userLoader->next())
    {
        // Make sure that the user is active, or the viewer has permission to
        // manage this type of user
        if ($_SESSION['role']['manage'.$userLoader->userCurrent['role'].'s']
                || $userLoader->userCurrent['active'] == 1)
        {
            echo '<li><a class="menu-item';
            if($userLoader->userCurrent['active'] == 0) echo ' unavailable';
            echo '" href="javascript:loadFrame('.$userLoader->userCurrent['id'].',\'users-panel.php\')">';
            echo '<img class="icon"  src="image/user.png" />';
            echo $userLoader->userCurrent['user']."</a></li>";
            // When running for the list of users, check if we want to load this
            // user's profile. Doing this here is more efficient than searching
            // for the user name with another query. Also, leaving this here
            // cause the lookup to fail if permissions were invalid.
            if($userLoader->userCurrent['user'] == $_GET['user']) $js.= 'loadFrame('.$userLoader->userCurrent['id'].',\'users-panel.php\')';
        }
    }
    echo "</ul>";

}
?>
