namespace stklib_kiki_a
{
    // Animation set 1 frame 0 to 109 is used in stklib_carousel_a
    // Animation set 2 frame 110 to 287 is used in stklib_kikiPainter_a
    void onStart(const string instID) 
    {
        Track::TrackObject@ tobj = Track::getTrackObject(instID,
            "stklib_kiki_a_main");
        if (tobj !is null)
        {
            // Try to see if this kiki is used by a meta library
            // tobj is the kiki .spm in kiki library, so 2 getParentLibrary()
            // will do the job
            Track::TrackObject@ meta =
                tobj.getParentLibrary().getParentLibrary();
            if (meta !is null)
            {
                string nn = meta.getName();
                if (meta.getName() == "stklib_carousel_a")
                {
                    Track::Mesh@ mesh = tobj.getMesh();
                    // For disabled animated scenery
                    if (mesh !is null)
                    {
                        mesh.removeAllAnimationSet();
                        mesh.addAnimationSet(0, 109);
                        mesh.useAnimationSet(0);
                    }
                }
                else
                {
                    // For now use painting animation if kiki is used alone
                    Track::Mesh@ mesh = tobj.getMesh();
                    if (mesh !is null)
                    {
                        mesh.removeAllAnimationSet();
                        mesh.addAnimationSet(110, 287);
                        mesh.useAnimationSet(0);
                    }
                }
            }
        }
    }
}
