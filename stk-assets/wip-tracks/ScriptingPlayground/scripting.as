/*
void onLibraryNodeCollision(int idKart, const string libraryInstance, const string objID)
{
    Utils::logInfo("Collision! Kart " + idKart + " with obj " + objID + " from " + libraryInstance);
}
*/

void enableYellowInGreen(bool enable)
{
    Track::TrackObject@ to = Track::getTrackObject("", "MovableYellowInGreen");
    to.setEnabled(enable);
}

void enableListInst3(bool enable)
{
    Track::TrackObject@ to = Track::getTrackObject("LibInst3", "Cube.001");
    to.setEnabled(enable);
}


void testBlowUpWall()
{
    blowUpWall("Wall_proxy");
}

