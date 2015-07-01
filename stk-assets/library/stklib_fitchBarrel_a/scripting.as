void onFitchBarrelCollision(int idKart, const string libraryInstance, const string objID)
{
    //Utils::logInfo("Wall Collision! Kart " + idKart + " with obj " + objID + " from " + libraryInstance);
    blowUpFitchBarrel(libraryInstance);
}

void blowUpFitchBarrel(string instID)
{
    Track::TrackObject@ wall = Track::getTrackObject(instID, "stklib_fitchBarrel_a_main");
    wall.setEnabled(false);
    
    Track::TrackObject@ part = Track::getTrackObject(instID, "stklib_fitchBarrel_a_cover");
    part.setEnabled(true);
    
    Track::TrackObject@ part2 = Track::getTrackObject(instID, "stklib_fitchBarrel_a_bodyPartA");
    part2.setEnabled(true);
}
