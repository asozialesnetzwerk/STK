<?php defined('SYSPATH') or die('No direct script access.');

/**
 * Process user login and logout
 */
class Controller_Auth extends Controller_Frontend {

    public function action_login()
    {
        // Redirect to start page if already logged in
        if ($this->session->logged_in()) {
            $this->request->redirect(URL::site());
        }

        $this->content = View::factory('auth/login');
        $this->content->set('form_user', $this->request->post('user'));

        $post = Validation::factory($this->request->post())
            ->rule('user', 'not_empty')
            ->rule('user', 'Model_User::valid_username')
            ->rule('pass', 'not_empty')
            ->rule('pass', 'Model_User::valid_password');

        try {
            if ($post->check()) {
                $this->session->login($post['user'], $post['pass']);
                // Login successful, redirect to start page
                $this->request->redirect(URL::site());
            }
            else if (count($post->data()) > 0) {
                $this->content->error_msg = $post->errors('auth');
            }
        }
        catch (UserException $ex) {
            $this->content->error_msg = $ex->getMessage();
        }
        catch (Exception $ex) {
            $this->content->error_msg = I18n::get('Failed to log in.');
            Kohana::$log->add(Log::ERROR, "Unhandled exception during login:\n".$ex);
        }
    }

    public function action_logout()
    {
        $this->session->logout();
        $this->request->redirect(URL::site());
    }
}
