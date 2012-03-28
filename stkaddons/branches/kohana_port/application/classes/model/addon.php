<?php defined('SYSPATH') or die('No direct script access.');

/**
 * Access addons in database
 */
class Model_Addon extends Model_Database {

    /**
     * Get name of an addon
     * @param string $addon_id addon id
     * @return string|null Name of addon or NULL if not found
     */
    public function get_name($addon_id)
    {
        $query = DB::select('name')->from('addons')->where('id', '=', $addon_id);
        return $query->execute($this->_db)->get('name');
    }

    /**
     * Sanitize addon id, i.e. remove everything except a-z, 0-9, - and _
     * @param string $addon_id Possibly 'dirty' addon id
     * @return string clean addon id (lowercase)
     */
    public static function trim_id($addon_id)
    {
        return preg_replace('[^a-z0-9_\-]', '', strtolower($addon_id));
    }
}
