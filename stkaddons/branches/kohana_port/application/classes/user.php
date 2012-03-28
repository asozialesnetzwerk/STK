<?php defined('SYSPATH') or die('No direct script access.');

/**
 * User data object
 */
class User {
    public $id;
    public $user;
    public $name;
    public $role;

    public function __construct($attributes)
    {
        $this->id = $attributes['id'];
        $this->user = $attributes['user'];
        $this->name = $attributes['name'];
        $this->role = $attributes['role'];
    }
}
