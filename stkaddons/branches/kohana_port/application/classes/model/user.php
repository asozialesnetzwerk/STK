<?php defined('SYSPATH') or die('No direct script access.');

/**
 * Access user data stored in database
 */
class Model_User extends Model_Database {

    /**
     * Try to authenticate a user
     * @param string $username username
     * @param string $password plain-text password
     * @throws UserException if authentication failed
     * @return User data object
     */
    public function authenticate($username, $password)
    {
        $salted_password = $this->salt_password($password, $username);
        $query = DB::select('id', 'user', 'pass', 'role', 'name')->from('users')->
            where('user', '=', $username)->and_where('pass', '=', $salted_password)->
            and_where('active', '=', 1);
        $result = $query->execute($this->_db);

        if ($result->count() != 1) {
            throw new UserException(I18n::get('Your username or password is incorrect.'));
        }
        else {
            $this->update_login_time($result[0]['id']);

            // add salt to currently unsalted password
            if (strlen($result[0]['pass']) == 64) {
                $new_password = $this->salt_password($password);
                $this->set_password($result[0]['id'], $new_password);
                Kohana::$log->add(Log::INFO, "Converted :username's password to salting algorithm",
                        array(':username', $username));
            }
        }

        return new User($result[0]);
    }

    /**
     * Check if username is well-formed
     * @param string $username
     */
    public static function valid_username($username)
    {
        return (Valid::min_length($username, 4) && Valid::alpha_numeric($username));
    }

    /**
     * Check if password is well-formed
     * @param unknown_type $password
     */
    public static function valid_password($password)
    {
        return Valid::min_length($password, 6);
    }

    /**
     * Salt password
     * @param string $password Password
     * @param string|null $username Optional username
     * @return string Salted password
     */
    public function salt_password($password, $username = NULL)
    {
        $salt = NULL;

        if (empty($username)) {
            $salt = $this->default_salt();
        }
        else {
            $password_db = $this->get_password($username);
            if (is_null($password_db)) {
                $salt = default_salt();
            }
            else if (strlen($password_db) == 96) {
                $salt = substr($password_db, 0, 32);
            }
            else {
                // unsalted password
                return hash('sha256', $password);
            }
        }

        return $salt.hash('sha256', $salt.$password);
    }

    /**
     * Get password stored in database
     * @param string $username Username
     * @return string|null Password or NULL if user does not exist
     */
    private function get_password($username)
    {
        $query = DB::select('pass')->from('users')->where('user', '=', $username);
        return $query->execute($this->_db)->get('pass');
    }

    /**
     * Set password for user
     * @param string $user_id User's ID
     * @param string $password New password
     * @throws UserException when updating password failed
     */
    public function set_password($user_id, $password)
    {
        $query = DB::update('users')->set(array('pass' => $password))->where('id', '=', $user_id);
        if ($query->execute() != 1) {
            throw new UserException(I18n::get('Failed to change your password.'));
        }
    }

    /**
     * Update time stamp of last login
     * @param string $user_id User's ID
     */
    public function update_login_time($user_id)
    {
        $procedure = $this->_db->table_prefix().'set_logintime';
        $time = date('Y-m-d H:i:s');

        $query = DB::query(Database::UPDATE, "CALL `$procedure`(:user, :time)");
        $query->param(':user', $user_id);
        $query->param(':time', $time);
        $query->execute($this->_db);
    }

    /**
     * Generate default salt
     * @return string 32 characters long salt
     */
    public static function default_salt()
    {
        return md5(uniqid(NULL, true));
    }
}
