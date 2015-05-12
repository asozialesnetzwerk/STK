void onStart()
{
    Utils::logWarning("ScriptingCallback: onStart");
    
    //Vec3 created = Vec3(0.0, 0.0, 0.0);
    //printVec3(created);
    //createTrigger("added_script", created , 30.0);                    	//name,x,y,z,trigger distance
}

void onKartObjectCollision(int idKart)
{
    Utils::logWarning("ScriptingCallback: onKartObjectCollision, idKart = " + idKart);
}

void onItemObjectCollision()
{
    Utils::logWarning("ScriptingCallback: onItemObjectCollision");
}

void onKartKartCollision(int idKart1, int idKart2)
{
    Utils::logWarning("ScriptingCallback: onKartKartCollision: " + idKart1 + " - " + idKart2);
}

void added_script(int idKart)
{
    /*GUI::displayMessage(GUI::getKeyBinding(GUI::PlayerAction::FIRE) + GUI::getKeyBinding(GUI::PlayerAction::ACCEL) + "This trigger was added by another script");
    jumpKartTo( 0, 67.90, 99.49 );
    Vec3 a;
    Vec3 b;
    b=a;
    Vec3 c = Vec3();
    Vec3 d = Vec3(2,3,0);
    printVec3(d); */
    
    //Kart::squash(0, 5.0); //id of kart,time to squash
    
    //Kart::teleport(idKart, Vec3(0,10,0));
    
    //Kart::setVelocity(idKart, Vec3(0, 10, 0));
    
    // Vec3 loc = Kart::getLocation(idKart);
    // Utils::logWarning(Utils::insertValues("Kart %s location : %s %s %s", idKart + "", loc.getX() + "", loc.getY() + "", loc.getZ() + ""));
}

void tutorial_drive(int idKart)
{
    //Utils::logWarning(Utils::insertValues("idKart : %i", idKart + ""));
    
    GUI::displayMessage(
        GUI::translate("Accelerate with <%s> and steer with <%s> and <%s>",
            GUI::getKeyBinding(GUI::PlayerAction::ACCEL),
            GUI::getKeyBinding(GUI::PlayerAction::STEER_LEFT),
            GUI::getKeyBinding(GUI::PlayerAction::STEER_RIGHT)
        )
    );
    
    // TEST DEBUG
    Utils::logWarning("Testing squash");
    Kart::squash(idKart, 5.0);
}


void tutorial_bananas(int idKart)
{
    GUI::displayMessage(GUI::translate("Avoid bananas!"));
    
    // TEST DEBUG
    Utils::logWarning("Testing setVelocity");
    Kart::setVelocity(idKart, Vec3(0, 10, 0));
}

void tutorial_giftboxes(int idKart)
{
    GUI::displayMessage(GUI::translate("Collect gift boxes, and fire the weapon with <%s> to blow away these boxes!", GUI::getKeyBinding(GUI::PlayerAction::FIRE)));
}

void tutorial_backgiftboxes(int idKart)
{
    GUI::displayMessage(
        GUI::translate("Press <%s> to look behind. Fire the weapon with <%s> while pressing <%s> to fire behind!",
            GUI::getKeyBinding(GUI::PlayerAction::LOOK_BACK),
            GUI::getKeyBinding(GUI::PlayerAction::FIRE),
            GUI::getKeyBinding(GUI::PlayerAction::LOOK_BACK)
        )
    );
}

void tutorial_nitro_use(int idKart)
{
    GUI::displayMessage(GUI::translate("Use the nitro you collected by pressing <%s>!", GUI::getKeyBinding(GUI::PlayerAction::NITRO)));
}

void tutorial_nitro_collect(int idKart)
{
    GUI::displayMessage(GUI::translate("Collect nitro bottles (we will use them after the curve)"));
    
    // DEBUG TEST
    Utils::logWarning("Testing getLocation + teleport");
    Vec3 loc = Kart::getLocation(idKart);
    Utils::logWarning(Utils::insertValues("Kart %s location : %s %s %s", idKart + "", loc.getX() + "", loc.getY() + "", loc.getZ() + ""));
    Kart::teleport(idKart, Vec3(loc.getX(), loc.getY(), loc.getZ() + 2));
}

void tutorial_rescue(int idKart)
{
    GUI::displayMessage(GUI::translate("Oops! When you're in trouble, press <%s> to be rescued", GUI::getKeyBinding(GUI::PlayerAction::RESCUE)));
}

void tutorial_skidding(int idKart)
{
    GUI::displayMessage(
        GUI::translate("Accelerate and press the <%s> key while turning to skid. Skidding for a short while can help you turn faster to take sharp turns.",
            GUI::getKeyBinding(GUI::PlayerAction::DRIFT)
        )
    );
}

void tutorial_skidding2(int idKart)
{
    GUI::displayMessage(GUI::translate("Note that if you manage to skid for several seconds, you will receive a bonus speedup as a reward!"));
}

void tutorial_endmessage(int idKart)
{
    GUI::displayMessage(GUI::translate("You are now ready to race. Good luck!"));
}

