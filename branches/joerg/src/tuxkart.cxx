//  $Id: tuxkart.cxx,v 1.16 2005/09/30 16:43:43 joh Exp $
//
//  SuperTuxKart - a fun racing game with go-kart
//  Copyright (C) 2004 Steve Baker <sjbaker1@airmail.net>
//
//  This program is free software; you can redistribute it and/or
//  modify it under the terms of the GNU General Public License
//  as published by the Free Software Foundation; either version 2
//  of the License, or (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

#include "tuxkart.h"
#include "Herring.h"
#include "sound.h"
#include "MaterialManager.h"
#include "World.h"
#include "Kart.h"
#include "gfx.h"
#include "gui/OldGUI.h"
#include "plibdrv.h"

#define MIN_CAM_DISTANCE      5.0f  
#define MAX_CAM_DISTANCE     10.0f  // Was 15

int player=0;

int finishing_position = -1 ;

static ulClock ck2 ;
extern float tt[6];
guUDPConnection *net = NULL ;
ssgLoaderOptions *loader_opts = NULL ;

int network_enabled = FALSE ;
int network_testing = FALSE ;

Herring *silver_h ;
Herring *gold_h   ;
Herring *red_h    ;
Herring *green_h  ;
 
int num_herring   ;
int num_laps_in_race ;

char *trackname = "tuxtrack" ;

HerringInstance herring [ MAX_HERRING ] ;

sgCoord steady_cam ;
 
char *traffic_files [] =
{
  "icecreamtruck.ac", "truck1.ac",
} ;


char *projectile_files [] =
{
  "spark.ac",         /* COLLECT_SPARK          */
  "missile.ac",       /* COLLECT_MISSILE        */
  "flamemissile.ac",  /* COLLECT_HOMING_MISSILE */
  NULL
} ;


GFX            *gfx = NULL ;
int       num_karts = 0 ;
Track        *track = NULL ;
int      cam_follow =  0 ;
float    cam_delay  = 10.0f ;

#define MAX_FIXED_CAMERA 9

sgCoord fixedpos [ MAX_FIXED_CAMERA ] =
{
  { {    0,    0, 500 }, {    0, -90, 0 } },

  { {    0,  180,  30 }, {  180, -15, 0 } },
  { {    0, -180,  40 }, {    0, -15, 0 } },

  { {  300,    0,  60 }, {   90, -15, 0 } },
  { { -300,    0,  60 }, {  -90, -15, 0 } },

  { {  200,  100,  30 }, {  120, -15, 0 } },
  { {  200, -100,  40 }, {   60, -15, 0 } },
  { { -200, -100,  30 }, {  -60, -15, 0 } },
  { { -200,  100,  40 }, { -120, -15, 0 } }
} ;



static void banner ()
{
  printf ( "\n\n" ) ;
  printf ( "   TUXEDO T. PENGUIN stars in TUXKART!\n" ) ;
  printf ( "               by Steve and Oliver Baker\n" ) ;
  printf ( "                 <sjbaker1@airmail.net>\n" ) ;
  printf ( "                  http://tuxkart.sourceforge.net\n" ) ;
  printf ( "\n\n" ) ;
}

static void cmdline_help ()
{
  banner () ;

  printf ( "Usage:\n\n" ) ;
  printf ( "    tuxkart [OPTIONS] [machine_name]\n\n" ) ;
  printf ( "Options:\n" ) ;
  printf ( "  -h     Display this help message.\n" ) ;
  printf ( "  -t     Run a network test.\n" ) ;
  printf ( "\n" ) ;
}


int tuxkart_main ( char *level_name )
{
  net   = new guUDPConnection ;

  if ( loader_opts == NULL )
  {
    loader_opts = new ssgLoaderOptions () ;
    loader_opts -> setCreateStateCallback ( getAppState ) ;
    loader_opts -> setCreateBranchCallback ( process_userdata ) ;
    ssgSetCurrentOptions ( loader_opts ) ;
  }

  //JH  num_laps_in_race = race_manager->getNumLaps() ;
  num_laps_in_race = 3;

  trackname = level_name ;

  network_testing = FALSE ;
  network_enabled = FALSE ;
/*
  network_enabled = TRUE ;
  net->connect ( argv[i] ) ;
*/

  if ( network_enabled && network_testing )
  {
    fprintf ( stderr, "You'll need to run this program\n" ) ;
    fprintf ( stderr, "on the other machine too\n" ) ;
    fprintf ( stderr, "Type ^C to exit.\n" ) ;

    while ( 1 )
    {
      char buffer [ 20 ] ;

#ifdef _MSC_VER
      Sleep ( 1000 ) ;
#else
	  sleep ( 1 ) ;
#endif

      if ( net->recvMessage( buffer, 20 ) > 0 )
	fprintf ( stderr, "%s\n", buffer ) ;
      else
	fprintf ( stderr, "*" ) ;

      net->sendMessage ( "Testing...", 11 ) ;
    }
  }

  banner () ;

  char fname [ 100 ] ;
  sprintf ( fname, "data/%s.drv", trackname ) ;

  gfx   = new GFX ;

  sound = new SoundSystem ;
  // sound -> change_track ( "mods/Boom_boom_boom.mod" ) ;
  //JH old gui: gui   = new GUI ;

  pwSetCallbacks ( keystroke, mousefn, motionfn, reshape, NULL ) ;

  //JH  if ( network_enabled )
    //JH    kart[1] = new NetworkKartDriver ( 1, new ssgTransform ) ;
  //JH  else
    //JH    kart[1] = new AutoKartDriver ( 1, new ssgTransform ) ;

  /*
    Load the models - optimise them a bit
    and then add them into the scene.
  */

  sprintf ( fname, "data/%s.loc", trackname ) ;

  fprintf ( stderr, "READY TO RACE!!\n" ) ;

  //  tuxKartMainLoop () ;
  return TRUE ;
}

// now defined in WorldLoader
void updateWorld ()
{
  if ( network_enabled )
  {
    char buffer [ 1024 ] ;
    int len = 0 ;
    int got_one = FALSE ;

    while ( (len = net->recvMessage ( buffer, 1024 )) > 0 )
      got_one = TRUE ;
  
    if ( got_one )
    {
      //JH  char *p = buffer ;

      //JH      kart[1]->setCoord    ( (sgCoord *) p ) ; p += sizeof(sgCoord) ;
      //JH      kart[1]->setVelocity ( (sgCoord *) p ) ; p += sizeof(sgCoord) ;
    }
  }

  if ( network_enabled )
  {
    char buffer [ 1024 ] ;
    char *p = buffer ;

    //JH    memcpy ( p, kart[0]->getCoord   (), sizeof(sgCoord) ) ;
        p += sizeof(sgCoord) ;
    //JH    memcpy ( p, kart[0]->getVelocity(), sizeof(sgCoord) ) ;
    p += sizeof(sgCoord) ;

    net->sendMessage ( buffer, p - buffer ) ;
  }

  if ( cam_follow < 0 )
    cam_follow = 18 + MAX_FIXED_CAMERA - 1 ;
  else
  if ( cam_follow >= 18 + MAX_FIXED_CAMERA )
    cam_follow = 0 ;

  sgCoord final_camera ;

  if ( cam_follow < num_karts )
  {
    sgCoord cam, target, diff ;

    //JH    sgCopyCoord ( &target, kart[cam_follow]->getCoord   () ) ;
    //JH    sgCopyCoord ( &cam   , kart[cam_follow]->getHistory ( (int)cam_delay ) ) ;

    float dist = 5.0f + sgDistanceVec3 ( target.xyz, cam.xyz ) ;

    if ( dist < MIN_CAM_DISTANCE && cam_delay < 50 )
      cam_delay++ ;

    if ( dist > MAX_CAM_DISTANCE && cam_delay > 1 )
      cam_delay-- ;

    sgVec3 offset ;
    sgMat4 cam_mat ;

    sgSetVec3 ( offset, -0.5f, -5.0f, 1.5f ) ;
    sgMakeCoordMat4 ( cam_mat, &cam ) ;

    sgXformPnt3 ( offset, cam_mat ) ;

    sgCopyVec3 ( cam.xyz, offset ) ;

    cam.hpr[1] = -5.0f ;
    cam.hpr[2] = 0.0f;

    sgSubVec3 ( diff.xyz, cam.xyz, steady_cam.xyz ) ;
    sgSubVec3 ( diff.hpr, cam.hpr, steady_cam.hpr ) ;

    while ( diff.hpr[0] >  180.0f ) diff.hpr[0] -= 360.0f ;
    while ( diff.hpr[0] < -180.0f ) diff.hpr[0] += 360.0f ;
    while ( diff.hpr[1] >  180.0f ) diff.hpr[1] -= 360.0f ;
    while ( diff.hpr[1] < -180.0f ) diff.hpr[1] += 360.0f ;
    while ( diff.hpr[2] >  180.0f ) diff.hpr[2] -= 360.0f ;
    while ( diff.hpr[2] < -180.0f ) diff.hpr[2] += 360.0f ;

    steady_cam.xyz[0] += 0.2f * diff.xyz[0] ;
    steady_cam.xyz[1] += 0.2f * diff.xyz[1] ;
    steady_cam.xyz[2] += 0.2f * diff.xyz[2] ;
    steady_cam.hpr[0] += 0.1f * diff.hpr[0] ;
    steady_cam.hpr[1] += 0.1f * diff.hpr[1] ;
    steady_cam.hpr[2] += 0.1f * diff.hpr[2] ;

    final_camera = steady_cam ;
  }
  else
  if ( cam_follow < num_karts + MAX_FIXED_CAMERA )
  {
    final_camera = fixedpos[cam_follow-num_karts] ;
  }
  else
    final_camera = steady_cam ;

  sgVec3 interfovealOffset ;
  sgMat4 mat ;

  sgSetVec3 ( interfovealOffset, 0.2 * (float)stereoShift(), 0, 0 ) ;
  sgMakeCoordMat4 ( mat, &final_camera ) ;
  sgXformPnt3 ( final_camera.xyz, interfovealOffset, mat ) ;

  ssgSetCamera ( &final_camera ) ;
}
#ifdef JH

void tuxKartMainLoop ()
{
  while ( 1 )
  {
    //JH    if ( ! gui -> isPaused () )
    if ( 1 )
    {
      ck2.update() ; tt[0] = ck2.getDeltaTime()*1000.0f ;
      updateWorld () ;

      for ( int i = 0 ; i < MAX_HERRING ; i++ )
        if ( herring [ i ] . her != NULL )
          herring [ i ] . update () ;

      silver_h -> update () ;
      gold_h   -> update () ;
      red_h    -> update () ;
      green_h  -> update () ;

      updateWorld () ;
    }
    else
    {
      ck2.update() ; tt[0] = ck2.getDeltaTime()*1000.0f ;
      ck2.update() ; tt[1] = ck2.getDeltaTime()*1000.0f ;
      ck2.update() ; tt[2] = ck2.getDeltaTime()*1000.0f ;
      ck2.update() ; tt[3] = ck2.getDeltaTime()*1000.0f ;
    }

/*track  -> update () ; */

    ck2.update() ; tt[4] = ck2.getDeltaTime()*1000.0f ;
    gfx    -> update () ;
    //JH    gui    -> update () ;
    sound  -> update () ;
    gfx    -> done   () ;  /* Swap buffers! */
    ck2.update() ; tt[5] = ck2.getDeltaTime()*1000.0f ;
  }
}


#endif
