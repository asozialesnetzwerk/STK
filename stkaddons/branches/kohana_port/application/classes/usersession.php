<?php defined('SYSPATH') or die('No direct script access.');

/**
 * Manages user session
 */
class UserSession {

    /**
     * @var Session Raw session object
     */
    private $_session;

    /**
     * @var string Name of session variable with user data
     */
    private $_key = 'session_user';

    public function __construct()
    {
        $this->_session = Session::instance('native');
    }

    /**
     * Try to login with credentials
     * @param unknown_type $username Username
     * @param unknown_type $password Password (plain-text)
     * @throws UserException when login failed
     */
    public function login($username, $password)
    {
        $user_model = Model::factory('User');
        $user = $user_model->authenticate($username, $password);
        $this->_session->set($this->_key, $user);
    }

    /**
     * Logout user and destroy associated user data
     */
    public function logout()
    {
        $this->_session->delete($this->_key);
        $this->_session->regenerate();
    }

    /**
     * Regenerate session id
     * @return string New session id
     */
    public function regenerate()
    {
        return $this->_session->regenerate();
    }

    /**
     * Check if user is logged in
     * @return boolean true if logged in
     */
    public function logged_in()
    {
        return !is_null($this->_session->get($this->_key, null));
    }

    /**
     * Access user properties
     * @param string $property Name of property
     */
    public function __get($property)
    {
        return $this->_session->get($this->_key)->$property;
    }
}
