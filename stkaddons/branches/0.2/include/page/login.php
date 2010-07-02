<?php
$title = "Login";
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
        $text =  "Logged in";
        $_SESSION['logged'] = true;
    }
    else
    {
        $text = "Not logged in.";
    }
}
else if(get("action") == "logout")
{
    session_destroy();
    session_start();
    $text = "Successfully loged out";
}
else
{
    $text = "<form action=\"".SITE_ACCESS."index.php?go=login&amp;action=submit\" method=\"POST\">
    <input type=\"text\" name=\"login\" />
    <input type=\"password\" name=\"pass\" />
    <input type=\"submit\" />
    </form>";
}

require ROOT."include/session.php";
require ROOT."include/header.php";
echo $text;
require ROOT."include/footer.php";
?>
