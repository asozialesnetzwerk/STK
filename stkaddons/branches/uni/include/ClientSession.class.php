<?php
/**
 * copyright 2013
 *
 * This file is part of SuperTuxKart
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

require_once('exceptions.php');
require_once('DBConnection.class.php');
require_once('Validate.class.php');

class ClientSessionException extends Exception {}
class ClientSessionConnectException extends ClientSessionException {}
class ClientSessionExpiredException extends ClientSessionException {}

/**
 * Abstract base class for handling client sessions
 */
abstract class ClientSession
{
    protected $session_id;
    protected $user_id;
    protected $user_name;
    protected $role;

    protected function __construct($session_id, $user_id, $user_name, $user_role)
    {
        $this->session_id = $session_id;
        $this->user_id = $user_id;
        $this->user_name = $user_name;
        $this->user_role = $user_role;
    }

    /**
     * Get current session id
     * @return string session id
     */
    public function getSessionId()
    {
        return $this->session_id;
    }

    /**
     * Get user name for this session
     * @return string user name
     */
    public function getUserName()
    {
        return $this->user_name;
    }

    /**
     * Get user id for this session
     * @return int user id
     */
    public function getUserId()
    {
        return $this->user_id;  
    }
    

    /**
     * Create new session
     * @param string $username user name (registered user or temporary nickname)
     * @param string $password password of registered user (optional)
     * @return ClientSession object
     * @throws InvalidArgumentException when username is not provided
     */
    public static function create($username, $password = '')
    {
        if (empty($username)) {
            throw new InvalidArgumentException('Username required');
        }
        else if (empty($password)) {
            throw new InvalidArgumentException('Password required');
            //return ClientSessionAnonymous::create($username);
        }
        else {
            return RegisteredClientSession::create($username, $password);
        }
    }

    /**
     * Get session object for already created session
     * @param string $session_id session id
     * @param numeric $user_id user id
     * @return ClientSessionAnonymous|ClientSessionUser
     * @throws ClientSessionExpiredException when session does not exist
     */
    public static function get($session_id, $user_id)
    {
        try{
            $session_info = DBConnection::get()->query
            (
                "SELECT * FROM `" . DB_PREFIX . "client_sessions` 
                WHERE cid = :sessionid AND uid = :userid",
                DBConnection::FETCH_ALL,
                array
                (
                    ':sessionid'   => $session_id,
                    ':userid'   => $user_id
                )
            );
            $size = count($session_info);
            if ($size == 0) {
                throw new ClientSessionExpiredException(_('No session found'));
            }elseif ($size > 1) {
                throw new ClientSessionExpiredException('Error!'); //FIXME
            }else {
                //Valid session found, get more user info
                $user_info = DBConnection::get()->query
                (
                    "SELECT `user`,`role`
                    FROM `" . DB_PREFIX . "users`
                    WHERE `id` = :userid",
                    DBConnection::FETCH_ALL,
                    array
                    (
                        ':userid'   => $user_id
                    )
                );
                // FIXME check the size of $user_info
                // here an if statement will come for Guest and registered
                return new RegisteredClientSession( $session_info[0]["cid"], 
                                                    $session_info[0]["uid"], 
                                                    $user_info[0]["user"],
                                                    $user_info[0]["role"]);
            }
        }catch (PDOException $e){
            throw new UserException(htmlspecialchars(
                _('An error occurred while verifying session.') .' '.
                _('Please contact a website administrator.')
            ));
        }
    }

    /**
     * Destroy session, you could also call it logout
     * @param string $session_id session id
     * @param int $user_id user id
     * @throws ClientSessionExpiredException when session does not exist
     */
    public static function destroy($session_id, $user_id)
    {
        try{
            $result = DBConnection::get()->query(
                "DELETE FROM `".DB_PREFIX."client_sessions`
    	        WHERE `cid` = :session_id AND uid = :user_id",
                DBConnection::ROW_COUNT,
                array(
                    ':session_id'   => (string) $session_id,
                    ':user_id'    => $user_id
                )
            );
        }catch(DBException $e){
            throw new ClientSessionExpiredException(htmlspecialchars(
                _('An error occurred while logging out.') .' '.
                _('Please contact a website administrator.')
            ));
        }

        if ($result == 0)
            throw new ClientSessionExpiredException(_('Could not log out. Perhaps you were already signed out.'));
    }

    /**
     * Generate a alphanumerical session id
     * @return string session id
     */
    protected static function calcSessionId()
    {
        // TODO: Not sure if this is strong enough, looks quite good for a first trial though
        return substr(md5(uniqid('', true)), 0, 24);
    }
}

/**
 * ClientSession implementation for registered users
 */
class RegisteredClientSession extends ClientSession
{

    /**
     * New instance
     * @param string $session_id
     * @param int $user_id
     * @param string $user_name
     */
    protected function __construct($session_id, $user_id, $user_name, $user_role)
    {
        parent::__construct($session_id, $user_id, $user_name, $user_role);
        
        
        
    }

    /**
     * Create session for registered user
     * @param string $username username
     * @param type $password password (plain)
     * @return ClientSessionUser
     * @throws ClientSessionConnectException when credentials are wrong
     */
    public static function create($username, $password = '')
    {      
        $result = Validate::credentials($username,$password);
        User::updateLoginTime($result[0]['id']);
        $size = count($result);
        if ($size == 0) {
            throw new ClientSessionConnectException(_('Username and/or password is wrong.'));
        }elseif ($size > 1) {
            throw new ClientSessionConnectException(_('Error!2'));
        }else{
            $session_id = ClientSession::calcSessionId();
            $user_id = $result[0]["id"];
            $role = $result[0]["role"];
            $username = $result[0]["user"];
            $result = DBConnection::get()->query
            (
                "INSERT INTO `" . DB_PREFIX ."client_sessions` (cid, uid)
                VALUES (:session_id, :user_id) 
                ON DUPLICATE KEY UPDATE cid = :session_id",
                DBConnection::ROW_COUNT,
                array
                (
                    ':session_id'   => (string) $session_id,
                    ':user_id'   => (int) $user_id
                )
            );
            if ($result == 0) {
                throw new ClientSessionConnectException('Could not create new session');
            }elseif ($result > 2) {
                throw new ClientSessionConnectException('Error!!!');
            }elseif ($result == 2) {
                //FIXME : research this. Apparantly the session was still alive, and got updated.
            }
            return new RegisteredClientSession($session_id, $user_id, $username, $role);
        }
    }
    

}
?>
