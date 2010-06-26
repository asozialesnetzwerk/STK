<?php
define("ROOT", "./");
require ROOT."include/include.php";
if(!isset($_GET['go']) or $_GET['go'] == "index")
{
    require ROOT."include/page/index.php";
}
elseif($_GET['go'] == "addons-view")
{
    require ROOT."include/page/addons-view.php";
}
else
{
    ?>
    No page named <?php echo $_GET['go'];?>.
    <?php
}
?>
