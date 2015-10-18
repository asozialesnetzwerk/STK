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

void testMove()
{
    Track::TrackObject@ obj = Track::getTrackObject("", "LibInst3");
    Vec3 coord(0,0,0);
    obj.moveTo(coord, true);
}

void testParticlesRate()
{
    Track::TrackObject@ obj = Track::getTrackObject("", "TestEmitter");
    Track::ParticleEmitter@ emitter = obj.getParticleEmitter();
    emitter.setEmissionRate(1.0);
    emitter.stopIn(3.0);
}
