<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
        <meta http-equiv="X-UA-Compatible" content="IE=9" />
        <base href="<?php echo URL::base(true); ?>" />
        <title><?php echo HTML::chars($title);?></title>
        <link href="css/skin_default.css" rel="stylesheet" media="all" type="text/css" />
        <script type="text/javascript" src="js/jquery.js"></script>
        <script type="text/javascript" src="js/jquery.newsticker.js"></script>
        <script type="text/javascript" src="js/script.js"></script>
        <meta name="description" content="<?php echo HTML::chars($description); ?>" />
    </head>

    <body>
    <div id="global">
        <div id="top-menu">
            <div id="top-menu-content">
                <div class="left">
                    <?php
                    if (!empty($top_menu_msg)) {
                        echo HTML::chars($top_menu_msg).'&nbsp;&nbsp;&nbsp;';
                    }
                    foreach($top_menu as $item) {
                        printf('<a href="%s">%s</a>', HTML::chars($item->url), HTML::chars($item->title));
                    }
                    ?>
                </div>
                <div class="right">
                    <div id="lang-menu">
                        <a class="menu_head"><?php echo HTML::chars(I18n::get("Languages"));?></a>
                        <ul class="menu_body">
                            <li class="flag"><a href="<?php echo URL::site('?lang=en_US'); ?>" style="background-position: 0px 0px;">EN</a></li>
                            <li class="flag"><a href="<?php echo URL::site('?lang=de_DE'); ?>" style="background-position: 0px -33px;">DE</a></li>
                            <li class="flag"><a href="<?php echo URL::site('?lang=fr_FR'); ?>" style="background-position: 0px -66px;">FR</a></li>
                            <li class="flag"><a href="<?php echo URL::site('?lang=ga_IE'); ?>" style="background-position: 0px -99px;">GA</a></li>
                            <li class="flag"><a href="<?php echo URL::site('?lang=gl_ES'); ?>" style="background-position: -48px 0px;">GL</a></li>
                            <li class="flag"><a href="<?php echo URL::site('?lang=id_ID'); ?>" style="background-position: -48px -33px;">ID</a></li>
                            <li class="flag"><a href="<?php echo URL::site('?lang=nl_NL'); ?>" style="background-position: -48px -66px;">NL</a></li>
                            <li class="flag"><a href="<?php echo URL::site('?lang=ru_RU'); ?>" style="background-position: -48px -99px;">RU</a></li>
                            <li class="flag"><a href="<?php echo URL::site('?lang=zh_TW'); ?>" style="background-position: -96px 0px;">ZH (T)</a></li>
                            <li class="label"><a href="https://translations.launchpad.net/stk/stkaddons">Translate<br />STK-Addons</a></li>
                        </ul>
                    </div>
                    <a href="http://supertuxkart.sourceforge.net"> <?php echo HTML::chars(I18n::get('STK Homepage'));?></a>
                </div>
            </div>
        </div>

    <?php echo $content; ?>

    </div>
    <p style="font-size: small; color: #000000; text-align: center;">Site hosted by <a href="http://www.tuxfamily.org/">tuxfamily.org</a></p>
    </body>
</html>
