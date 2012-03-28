<div style="text-align: center; width: 100%;">
    <img id="logo_center" src="image/logo_large.png" alt="SuperTuxKart Logo"
        title="SuperTuxKart Logo" width="424" height="325" />
</div>

<div id="index-menu">
    <div>
        <a href="<?php echo URL::site('addons/karts'); ?>" style="background-position: -106px 0px;">
            <span><?php echo HTML::chars(I18n::get('Karts')); ?></span>
        </a>
    </div>
    <div>
        <a href="<?php echo URL::site('addons/tracks'); ?>" style="background-position: 0px 0px;">
            <span><?php echo HTML::chars(I18n::get('Tracks')); ?></span>
        </a>
    </div>
    <div>
        <a href="<?php echo URL::site('addons/arenas'); ?>" style="background-position: -212px 0px;">
            <span><?php echo HTML::chars(I18n::get('Arenas')); ?></span>
        </a>
    </div>
    <div>
        <a href="http://supertuxkart.sourceforge.net/Category:Stkaddons" style="background-position: -318px 0px;">
            <span><?php echo HTML::chars(I18n::get('Help')); ?></span>
        </a>
    </div>
</div>

<div id="news-panel">
    <ul id="news-messages">
        <?php
        foreach ($news as $msg) {
            echo '<li>'.HTML::chars($msg).'</li>';
        }
        ?>
    </ul>
</div>
