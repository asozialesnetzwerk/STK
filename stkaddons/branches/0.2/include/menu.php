<div id="menu">
    <a class="main_link" href="index.php"><?php echo _("Home"); ?></a>
    <a class="main_link" href="index.php?go=addons-view&amp;type=karts"><?php echo _("Karts"); ?></a>
    <a class="main_link" href="index.php?go=addons-view&amp;type=tracks"><?php echo _("Tracks"); ?></a>
    <?php if($logged)
    { ?>
        <a class="main_link" href="index.php?go=login&amp;action=logout"><?php echo _("Log out"); ?></a>
        <span class="main_link"><?php if($logged) echo $USER->GetLogin(); ?></span>
    <?php
    }
    else
    {
    ?>
    <a class="main_link" href="index.php?go=login&amp;action=login"><?php echo _("Login"); ?></a>
    <?php
    }
    ?>
    <div class="clearer"></div>
</div>
