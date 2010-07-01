<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title><?php
        if(isset($title))
        {
            echo $title;
        }
        echo " | ";
        echo SITE_NAME;
        ?></title>
        <script src="js/jquery.js"></script>
        <script src="js/addons-view.js"></script>
    	<link rel="stylesheet" href="css/base.css" type="text/css" />
    	<link rel="stylesheet" href="css/<?php echo $css; ?>" type="text/css" />
    </head>
    <body>
    <div id="global">
    <?php
    require ROOT."include/menu.php";
    ?>
        <div id="content">
