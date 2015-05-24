void onStart()
{
    Utils::logInfo("ScriptingCallback: onStart");
}

void big_door(int idKart)
{
    int unlocked_challenges = Challenges::getCompletedChallengesCount();
    int challenges = Challenges::getChallengeCount();
    
    // allow ONE unsolved challenge : the last one
    if (unlocked_challenges < challenges - 1)
    {
        GUI::displayMessage(GUI::translate("Complete all challenges to unlock the big door!"));
    }
}

void garage(int idKart)
{
    Track::pauseRace();
}
