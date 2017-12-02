namespace stklib_wilbertSecurity_a
{
    // Frame 0 to 20 is "calm down" animation
    // Frame 21 to 48 is handstand animation
    // Frame 49 to 190 is painting animation, used in stklib_wilberPainter_a
    void onStart(const string instID) 
    {
        Track::TrackObject@ tobj = Track::getTrackObject(instID,
            "stklib_wilbertSecurity_a_main");
        Track::Mesh@ wilber_mesh = tobj.getMesh();
        if (tobj !is null and wilber_mesh !is null)
        {
            // Try to see if this wilber is used by a meta library
            // tobj is the wilber .spm in wilber library, so 2 getParentLibrary()
            // will do the job
            Track::TrackObject@ meta =
                tobj.getParentLibrary().getParentLibrary();
            if (meta !is null)
            {
                if (meta.getName() == "stklib_wilberPainter_a")
                {
                    wilber_mesh.removeAllAnimationSet();
                    wilber_mesh.addAnimationSet(49, 190);
                    wilber_mesh.useAnimationSet(0);
                }
            }
            else
            {
                // If wilber is used alone, use random animation set
                wilber_mesh.removeAllAnimationSet();
                wilber_mesh.addAnimationSet(0, 20);
                wilber_mesh.addAnimationSet(21, 48);
                wilber_mesh.useAnimationSet(Utils::randomInt(0, 2));
            }
        }
    }
}
