void onStart()
{
    Utils::logWarning("ScriptingCallback: onStart");
}

void onKartObjectCollision(int idKart)
{
    // Test
    Utils::logWarning("ScriptingCallback: onKartObjectCollision, idKart = " + idKart);
}

void onItemObjectCollision()
{
    // Test
    Utils::logWarning("ScriptingCallback: onItemObjectCollision");
}

void onKartKartCollision(int idKart1, int idKart2)
{
    // Test
    Utils::logWarning("ScriptingCallback: onKartKartCollision: " + idKart1 + " - " + idKart2);
}

void tutorial_drive(int idKart)
{
    GUI::displayMessage(
        GUI::translate("Accelerate with <%s> and steer with <%s> and <%s>",
            GUI::getKeyBinding(GUI::PlayerAction::ACCEL),
            GUI::getKeyBinding(GUI::PlayerAction::STEER_LEFT),
            GUI::getKeyBinding(GUI::PlayerAction::STEER_RIGHT)
        )
    );
}


void tutorial_bananas(int idKart)
{
    GUI::displayMessage(GUI::translate("Avoid bananas!"));
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

void tutorial_exit(int idKart)
{
    Track::exitRace();
}


// ============= DEBUG TESTS ==============
void debug_squash()
{
    int idKart = 0;
    Utils::logWarning("Testing squash");
    Kart::squash(idKart, 5.0);
}

void debug_set_velocity()
{
    int idKart = 0;
    Utils::logWarning("Testing setVelocity");
    Kart::setVelocity(idKart, Vec3(0, 10, 0));
}

// TODO: teleport doesn't work very well
void debug_teleport()
{
    int idKart = 0;
    Utils::logWarning("Testing getLocation + teleport");
    Vec3 loc = Kart::getLocation(idKart);
    Utils::logWarning(Utils::insertValues("Kart %s location : %s %s %s", idKart + "", loc.getX() + "", loc.getY() + "", loc.getZ() + ""));
    Kart::teleport(idKart, Vec3(loc.getX() - 3, loc.getY(), loc.getZ() - 3));
}