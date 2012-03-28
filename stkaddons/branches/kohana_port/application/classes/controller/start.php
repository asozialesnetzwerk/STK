<?php defined('SYSPATH') or die('No direct script access.');

class Controller_Start extends Controller_Frontend {

    public function action_index()
    {
        $this->content = View::factory('start');
        $this->content->news = $this->load_news();
    }

    private function load_news()
    {
        $news = array();

        $stats_model = Model::factory('Statistics');
        $addon_model = Model::factory('Addon');
        $pop_kart = $addon_model->get_name($stats_model->most_downloaded_addon('karts'));
        $pop_track = $addon_model->get_name($stats_model->most_downloaded_addon('tracks'));

        $news[] = sprintf(I18n::get('The most downloaded kart is %s.'), $pop_kart);
        $news[] = sprintf(I18n::get('The most downloaded track is %s.'), $pop_track);

        $news_model = Model::factory('News');
        foreach($news_model->get_current_web_news() as $news_item) {
            $news[] = $news_item->content;
        }

        return $news;
    }
}
