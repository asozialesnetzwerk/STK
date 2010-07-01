<?php
/*echo "<h1>Session debug:</h1>";
print_r( $_SESSION);
$_SESSION['var'] = 0;*/
if(isset($_SESSION["logged"]) and $_SESSION["logged"])
{
    $logged = true;
    $user = new User();
    $user->SelectById($_SESSION["id"]);
}
else
{
    if(isset($_SESSION['logged']))
        echo "var logged";
    $logged = false;
}
?>
