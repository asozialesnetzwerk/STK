<?php
require ROOT."config.php";
require ROOT."include/sql.php";
require ROOT."include/core/addons.php";
setlocale(LC_ALL, $_COOKIE['lang'].'.UTF-8');

bindtextdomain('translations', 'locale');
textdomain('translations');
bind_textdomain_codeset('translations', 'UTF-8');
?>
