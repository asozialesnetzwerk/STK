void onFitchBarrelCollision(int idKart, const string libraryInstance, const string objID)
{
    //Utils::logInfo("Wall Collision! Kart " + idKart + " with obj " + objID + " from " + libraryInstance);
    Vec3 velocity = Kart::getVelocity(idKart);
    //Utils::logInfo("Kart velocity : " + velocity.getLength());
    if (velocity.getLength() > 2.5)
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
    
    Track::TrackObject@ part3 = Track::getTrackObject(instID, "stklib_fitchBarrel_a_bodyPartB");
    part3.setEnabled(true);
    
    Track::TrackObject@ part4 = Track::getTrackObject(instID, "stklib_fitchBarrel_a_bodyPartC");
    part4.setEnabled(true);
    
    Track::TrackObject@ part5 = Track::getTrackObject(instID, "stklib_fitchBarrel_a_bodyPartD");
    part5.setEnabled(true);
    
    Track::TrackObject@ part6 = Track::getTrackObject(instID, "stklib_fitchBarrel_a_bodyPartE");
    part6.setEnabled(true);
    
    Track::TrackObject@ part7 = Track::getTrackObject(instID, "stklib_fitchBarrel_a_bottom");
    part7.setEnabled(true);
    
    Track::TrackObject@ obj = Track::getTrackObject(instID, "stklib_fitchBarrel_a_sandExplosion");
    Track::ParticleEmitter@ emitter = obj.getParticleEmitter();
    emitter.setEmissionRate(1.0);
    emitter.stopIn(0.1);
}



