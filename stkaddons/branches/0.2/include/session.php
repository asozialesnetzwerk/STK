<?php
/*echo "<h1>Session debug:</h1>";
print_r( $_SESSION);
$_SESSION['var'] = 0;*/
$USER = new User();
if(isset($_SESSION["logged"]) and $_SESSION["logged"])
{
    $logged = true;
    $USER->SelectById($_SESSION["id"]);
}
else
{
    $logged = false;
}
?>
