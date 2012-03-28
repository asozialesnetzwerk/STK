<?php defined('SYSPATH') or die('No direct script access.');

/**
 * Base controller for frontend pages
 */
abstract class Controller_Frontend extends Controller {
    /**
     * @var string Name of layout view, loaded in before()
     */
    private $view = 'layout';

    /**
     * @var array List of menu items, use add_menu() to item
     */
    private $top_menu = array();

    /**
     * @var string Page title
     */
    protected $title = 'SuperTuxKart Add-ons';

    /**
     * @var string Page description (used in meta section)
     */
    protected $description = 'This is the official SuperTuxKart add-on repository. It contains extra karts and tracks for the SuperTuxKart game.';

    /**
     * @var mixed Page content (string or something convertible to string)
     */
    protected $content = '';

    /**
     * @var UserSession current user session
     */
    protected $session;

    /**
     * @see Kohana_Controller::before()
     */
    public function before()
    {
        $this->load_session();
        $this->load_language();

        // This will always be the first menu item
        $this->add_menu(URL::site(''), I18n::get('Home'));

        $this->title = I18n::get($this->title);
        $this->description = I18n::get($this->description);

        $this->view = View::factory($this->view);
        $this->view->bind('title', $this->title);
        $this->view->bind('description', $this->description);
        $this->view->bind('content', $this->content);
        $this->view->bind('top_menu', $this->top_menu);
        $this->view->bind('user_session', $this->session);
    }

    /**
     * @see Kohana_Controller::after()
     */
    public function after()
    {
        // Remaining menu items (last in list)
        $this->add_user_menu();
        $this->add_menu(URL::site('about'), I18n::get('About'));

        if ($this->session->logged_in()) {
            $this->view->top_menu_msg = sprintf(I18n::get('Welcome, %s'), $this->session->name);
        }

        $this->response->body($this->view->render());
        $this->session->regenerate();
    }

    /**
     * Load user session
     */
    private function load_session()
    {
        $this->session = new UserSession();
    }

    /**
     * Handle language settings
     */
    private function load_language()
    {
        $lang = $this->request->query('lang');
        if (is_null($lang)) {
            $lang = Cookie::get('lang', 'en_US');
        }
        else {
            Cookie::set('lang', $lang);
        }
        I18n::lang($lang);
    }

    /**
     * Add user related menu items
     */
    private function add_user_menu()
    {
        if ($this->session->logged_in()) {
            $this->add_menu(URL::site('auth/logout'), I18n::get('Log out'));
            $this->add_menu(URL::site('users'), I18n::get('Users'));
            $this->add_menu(URL::site('upload'), I18n::get('Upload'));
            // TODO: only with 'managesettings' role
            $this->add_menu(URL::site('manage'), I18n::get('Manage'));
        } else {
            $this->add_menu(URL::site('auth/login'), I18n::get('Login'));
        }
    }

    /**
     * Add menu item
     * @param string $url Destination URL
     * @param string $title Title
     */
    protected function add_menu($url, $title)
    {
        $item = new stdClass();
        $item->url = $url;
        $item->title = $title;
        $this->top_menu[] = $item;
    }
}
