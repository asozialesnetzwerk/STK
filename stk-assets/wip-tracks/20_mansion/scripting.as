void onStart()
{   

    //array<string> light_list = {"gfx_lightning_a_main_proxy", "gfx_lightning_a_main_proxy.001"};

    LightningTimeout @ timeout = LightningTimeout("gfx_lightning_a_main_proxy");
    Utils::TimeoutCallback@ timerDelegate = Utils::TimeoutCallback(timeout.onTimerComplete);
    Utils::setTimeoutDelegate(timerDelegate, 0.1);

    LightningTimeout @ timeout1 = LightningTimeout("gfx_lightning_a_main_proxy.001");
    Utils::TimeoutCallback@ timerDelegate1 = Utils::TimeoutCallback(timeout1.onTimerComplete);
    Utils::setTimeoutDelegate(timerDelegate1, 0.1);

    LightningTimeout @ timeout2 = LightningTimeout("gfx_lightning_a_main_proxy.002");
    Utils::TimeoutCallback@ timerDelegate2 = Utils::TimeoutCallback(timeout2.onTimerComplete);
    Utils::setTimeoutDelegate(timerDelegate2, 0.1);

    LightningTimeout @ timeout3 = LightningTimeout("gfx_lightning_a_main_proxy.003");
    Utils::TimeoutCallback@ timerDelegate3 = Utils::TimeoutCallback(timeout3.onTimerComplete);
    Utils::setTimeoutDelegate(timerDelegate3, 0.1);
/*
    LightningTimeout @ timeout1 = LightningTimeout("gfx_lightning_a_main_proxy.001");
    Utils::TimeoutCallback@ timerDelegate1 = Utils::TimeoutCallback(timeout1.onTimerComplete);
    Utils::setTimeoutDelegate(timerDelegate1, 0.1);
*/
}


void LightningDisplay(string instID, bool tog) {
    Track::getTrackObject(instID, "gfx_lightning_a_main").setEnabled(tog);}

class LightningBlink
{
    string instID;

    LightningBlink(string instID)
    {
        this.instID = instID;
    
    }

    void onTimerComplete()
    {
        LightningDisplay(this.instID, false);
    }
}

class LightningSecondBlink
{
    string instID;

    LightningSecondBlink(string instID)
    {
        this.instID = instID;
    
    }

    void onTimerComplete()
    {
        LightningDisplay(this.instID, true);
    }
}

class LightningTimeout
{

    string instID;

    LightningTimeout(string instID)
    {
        this.instID = instID;
    
    }
    
    void onTimerComplete()
    {
        LightningDisplay(this.instID, true);

        LightningTimeout @ timeout = LightningTimeout(this.instID);
        Utils::TimeoutCallback@ timerDelegate = Utils::TimeoutCallback(timeout.onTimerComplete);
        Utils::setTimeoutDelegate(timerDelegate, Utils::randomFloat(4, 10));

        // After 0.1 we turn of the light ray
        LightningBlink @ timeout2 = LightningBlink(this.instID);
        Utils::TimeoutCallback@ timerDelegate2 = Utils::TimeoutCallback(timeout2.onTimerComplete);
        Utils::setTimeoutDelegate(timerDelegate2, 0.05);

        // After 0.1 we do a second blink
        LightningSecondBlink @ timeout3 = LightningSecondBlink(this.instID);
        Utils::TimeoutCallback@ timerDelegate3 = Utils::TimeoutCallback(timeout3.onTimerComplete);
        Utils::setTimeoutDelegate(timerDelegate3, 0.15);
        
        LightningBlink @ timeout4 = LightningBlink(this.instID);
        Utils::TimeoutCallback@ timerDelegate4 = Utils::TimeoutCallback(timeout4.onTimerComplete);
        Utils::setTimeoutDelegate(timerDelegate4, 0.2);
    }
}