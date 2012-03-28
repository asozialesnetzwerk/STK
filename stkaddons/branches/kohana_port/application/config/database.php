<?php defined('SYSPATH') or die('No direct access allowed.');

return array(
    'default' => array(
        'type'       => 'mysql',
        'connection' => array(
            'hostname'   => 'localhost',
            'database'   => 'stkaddons_dev',
            'username'   => 'stkaddons',
            'password'   => 'stkaddons',
            'persistent' => false,
        ),
        'table_prefix' => 'v2_',
        'charset'      => 'utf8',
        'caching'      => false,
        'profiling'    => true,
    )
);
