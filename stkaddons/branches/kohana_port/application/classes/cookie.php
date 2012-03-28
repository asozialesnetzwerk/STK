<?php

class Cookie extends Kohana_Cookie {}

Kohana_Cookie::$salt = Kohana::$config->load('cookie.salt');
?>
