namespace stklib_kiki_a
{
    // Frame 0 to 109 is waving hand animation, used in stklib_carousel_a
    // Frame 110 to 287 is painting animation, used in stklib_kikiPainter_a
    void onStart(const string instID) 
    {
        Track::TrackObject@ tobj = Track::getTrackObject(instID,
            "stklib_kiki_a_main");
        Track::Mesh@ kiki_mesh = tobj.getMesh();
        if (tobj !is null and kiki_mesh !is null)
        {
            // Try to see if this kiki is used by a meta library
            // tobj is the kiki .spm in kiki library, so 2 getParentLibrary()
            // will do the job
            Track::TrackObject@ meta =
                tobj.getParentLibrary().getParentLibrary();
            if (meta !is null)
            {
                if (meta.getName() == "stklib_carousel_a")
                {
                    kiki_mesh.removeAllAnimationSet();
                    kiki_mesh.addAnimationSet(0, 109);
                    kiki_mesh.useAnimationSet(0);
                }
                else if (meta.getName() == "stklib_kikiPainter_a")
                {
                    kiki_mesh.removeAllAnimationSet();
                    kiki_mesh.addAnimationSet(110, 287);
                    kiki_mesh.useAnimationSet(0);
                }
            }
        }
        else if (kiki_mesh !is null)
        {
            // For now use painting animation if kiki is used alone
            kiki_mesh.removeAllAnimationSet();
            kiki_mesh.addAnimationSet(110, 287);
            kiki_mesh.useAnimationSet(0);
        }
    }
}
