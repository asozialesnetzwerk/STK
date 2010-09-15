<?php
/* range, manage user, manage moderator, manage addons, manage site*/
/*we could do that programmatically but it is clearer like this*/
$status_index = array();
$status_index["User"] = 0;
$status_index["Moderator"] = 1;
$status_index["Administrator"] = 2;
$status = array(array("User", false, false, false, false, false), array("Moderator", true, true, false, false, false), array("Administrator", true, true, false, true, true)); 
?>
