The scripts in this directory are UNSTABLE WORK IN PROGRESS and should not be used for production.
Please use the scripts from data/tracks and data/karts in the main game repository for actual work.

Needed changes to port :
* Move properties from Logic to ID-properties for objects
* Replace '-' with '_' in property names
* Enable 'is stk track' property
* Take 'enable animated texture' boolean into account
* Take 'enable slowdown on texture' boolean into account
* Take 'enable sfx on texture' boolean into account
* Old browser used yes/no for booleans... new one uses true/false. Fix this.
* clampU --> clampu, clampV --> clampv
