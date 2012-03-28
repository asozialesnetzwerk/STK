<?php defined('SYSPATH') or die('No direct script access.');

return array(
    'cookie' => array(
        'encrypted' => false,
    ),
    'native' => array(
        'lifetime' => 60 * 60 * 2,
        'name' => 'session'
    )
);
