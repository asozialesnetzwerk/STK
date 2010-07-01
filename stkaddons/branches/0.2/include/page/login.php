<?php
$title = "Login";
require ROOT."include/header.php";
//light anti bruteforcing
sleep(1);
if(get("action") == "submit")
{
    $login = true;
    $user = new User();
    if($user->SelectByName(post("login")))
    {
        if($user->GetPass() == md5(post("pass")))
        {
            $_SESSION["id"] = $user->GetId();
            $login = true;
        }
        else
            $login = false;
    }
    else
    {
        $login = false;
    }
    if($login)
    {
        echo "Logged in";
        $_SESSION['logged'] = true;
    }
    else
    {
        echo "Not logged in.";
    }
}
else if(get("action") == "logout")
{
    session_destroy();
    echo "Successfully loged out";
}
else
{
    ?>
    <form action="<?php echo SITE_ACCESS."index.php?go=login&amp;action=submit"; ?>" method="POST">
    <input type="text" name="login" />
    <input type="password" name="pass" />
    <input type="submit" />
    </form>
    <?php
}
require ROOT."include/footer.php";
?>
