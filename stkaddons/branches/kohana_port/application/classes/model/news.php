<?php defined('SYSPATH') or die('No direct script access.');

/**
 * Access news entries in database
 */
class Model_News extends Model_Database {

    /**
     * Get all currently active news messages intended for web display
     * @return mixed Iterable list of news objects with date and content property
     */
    public function get_current_web_news()
    {
        $query = DB::select('content', 'date')->from('news')
            ->where('active', '=', 1)
            ->and_where('web_display', '=', 1)
            ->order_by('date', 'DESC');

        return $query->execute($this->_db, true);
    }
}
