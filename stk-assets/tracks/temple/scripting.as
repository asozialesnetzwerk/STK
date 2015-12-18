void onStart()
{
    // Disable water flooding when there's AI karts because they can't handle it
    int karts = Track::getNumberOfKarts();
    int players = Track::getNumLocalPlayers();
    
    if (karts > players)
    {
        Track::TrackObject@ water = Track::getTrackObject("", "water");
        Track::Animator@ animator = water.getIPOAnimator();
        animator.setPaused(true);
        
        Track::TrackObject@ waterwarp = Track::getTrackObject("", "waterwarp");
        Track::Animator@ animator2 = waterwarp.getIPOAnimator();
        animator2.setPaused(true);
        
        Track::TrackObject@ waterdeath = Track::getTrackObject("", "waterdeath");
        Track::Animator@ animator3 = waterdeath.getIPOAnimator();
        animator3.setPaused(true);
    }
}
