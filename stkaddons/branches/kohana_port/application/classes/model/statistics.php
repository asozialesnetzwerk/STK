<?php defined('SYSPATH') or die('No direct script access.');

/**
 * Get statistical data out of our database
 */
class Model_Statistics extends Model_Database {

    private static $_addon_types = array('karts', 'tracks', 'arenas');

    public function newest_addon($addon_type)
    {
        if (!in_array($addon_type, Model_Statistics::$_addon_types)) {
            $addon_type = Model_Statistics::$_addon_types[0];
        }

        $query = DB::select('addons.id')->from('addons')
            ->join(array($addon_type.'_revs', 'revs'), 'LEFT')
            ->on('addons.id', '=', 'revs.addon_id')
            ->where('revs.status', '&', AssetFlags::$approved)
            ->order_by('addons.creation_date', 'DESC')
            ->limit(1);

        return $query->execute($this->_db)->get('id');
    }

    public function most_downloaded($addon_type, $file_type = 'addon')
    {
        if (!in_array($addon_type, Model_Statistics::$_addon_types)) {
            $addon_type = Model_Statistics::$_addon_types[0];
        }

        $query = DB::select('addon_id', array('SUM("downloads")', 'downloads'))
            ->from('files')->where('addon_type', '=', $addon_type)
            ->and_where('file_type', '=', $file_type)
            ->group_by('addon_id')
            ->order_by('downloads', 'DESC')
            ->limit(1);

        return $query->execute($this->_db)->get('addon_id');
    }

    public function most_downloaded_addon($addon_type)
    {
        return $this->most_downloaded($addon_type, 'addon');
    }
}