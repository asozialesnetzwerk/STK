//  $Id: OldGUI.cxx,v 1.4 2005/08/19 20:51:47 joh Exp $
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

#include "OldGUI.h"
#include "World.h"
#include "Kart.h"
#include "PlayerKart.h"
#include "Loader.h"
#include "Config.h"
#include "status.h"
#include "sound.h"

#include <plib/pu.h>
#include <plib/pw.h>

static jsJoystick *joystick ;

static int mouse_x ;
static int mouse_y ;
static int mouse_dx = 0 ;
static int mouse_dy = 0 ;
static int mouse_buttons = 0 ;

fntTexFont *font ;

void motionfn ( int x, int y )
{
  mouse_x = x ;
  mouse_y = y ;
  mouse_dx += mouse_x - 320 ;
  mouse_dy += mouse_y - 240 ;
  puMouse ( x, y ) ;
}


void mousefn ( int button, int updown, int x, int y )
{
  mouse_x = x ;
  mouse_y = y ;

  if ( updown == PW_DOWN )
    mouse_buttons |= (1<<button) ;
  else
    mouse_buttons &= ~(1<<button) ;

  mouse_dx += mouse_x - 320 ;
  mouse_dy += mouse_y - 240 ;

  puMouse ( button, updown, x, y ) ;

  if ( updown == PW_DOWN )
    hide_status () ;
}

static void credits_cb ( puObject * )
{
  hide_status () ;
  credits () ;
}

static void versions_cb ( puObject * )
{
  hide_status () ;
  versions () ;
}

static void about_cb ( puObject * )
{
  hide_status () ;
  about () ;
}

static void help_cb ( puObject * )
{
  hide_status () ;
  help () ;
}

static void music_off_cb     ( puObject * ) { sound->disable_music () ; } 
static void music_on_cb      ( puObject * ) { sound->enable_music  () ; } 
static void sfx_off_cb       ( puObject * ) { sound->disable_sfx   () ; } 
static void sfx_on_cb        ( puObject * ) { sound->enable_sfx    () ; } 

static void exit_cb ( puObject * )
{
  fprintf ( stderr, "Exiting TuxKart.\n" ) ;
  exit ( 1 ) ;
}

/* Menu bar entries: */

static char      *exit_submenu    [] = {  "Exit", NULL } ;
static puCallback exit_submenu_cb [] = { exit_cb, NULL } ;

static char      *sound_submenu    [] = { "Turn off Music", "Turn off Sounds", "Turn on Music", "Turn on Sounds", NULL } ;
static puCallback sound_submenu_cb [] = {  music_off_cb,        sfx_off_cb,     music_on_cb,        sfx_on_cb, NULL } ;

static char      *help_submenu    [] = { "Versions...", "Credits...", "About...",  "Help", NULL } ;
static puCallback help_submenu_cb [] = {   versions_cb,   credits_cb,   about_cb, help_cb, NULL } ;



GUI::GUI ()
{
  paused = FALSE ;
  hidden = TRUE  ;
  mouse_x = 320 ;
  mouse_y = 240 ;

/*
  Already done in start_tuxkart!

  ssgInit () ;
  puInit () ;
*/
  font = new fntTexFont ;
  font -> load ( loader->getPath("fonts/sorority.txf").c_str()) ;
  puFont ff ( font, 20 ) ;
  puSetDefaultFonts        ( ff, ff ) ;
  puSetDefaultStyle        ( PUSTYLE_SMALL_SHADED ) ;
  puSetDefaultColourScheme ( 0.1, 0.5, 0.1, 0.6 ) ;

  /* Make the menu bar */

  main_menu_bar = new puMenuBar () ;

  {
    main_menu_bar -> add_submenu ( "Exit", exit_submenu, exit_submenu_cb ) ;
    main_menu_bar -> add_submenu ( "Sound", sound_submenu, sound_submenu_cb ) ;
    main_menu_bar -> add_submenu ( "Help", help_submenu, help_submenu_cb ) ;
  }

  main_menu_bar -> close () ;
  main_menu_bar -> hide  () ;

  joystick = new jsJoystick ( 0 ) ;
  joystick -> setDeadBand ( 0, 0.1 ) ;
  joystick -> setDeadBand ( 1, 0.1 ) ;
}


void GUI::show ()
{
  hide_status () ;
  hidden = FALSE ;
  main_menu_bar -> reveal () ;
}

void GUI::hide ()
{
  hidden = TRUE ;
  hide_status () ;
  main_menu_bar -> hide () ;
}

void GUI::update ()
{
#ifdef JH
  keyboardInput  () ;
  joystickInput  () ;
  drawStatusText () ;

  glBlendFunc ( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA ) ;
  glAlphaFunc ( GL_GREATER, 0.1f ) ;
  glEnable    ( GL_BLEND ) ;

  puDisplay () ;
#endif
}

#ifdef JH   // can be deleted ... I think
void GUI::keyboardInput ()
{
  static int isWireframe = FALSE ;
  int c = getKeystroke () ;

  if ( c <= 0 )
    return ;

  int i;
  switch ( c )
  {
    case PW_KEY_F1              :
    case 0x1B                   :
    case 0x03 /* Control-C */   : exit ( 0 ) ;

    case PW_KEY_PAGE_UP   : cam_follow-- ; break ;
    case PW_KEY_PAGE_DOWN : cam_follow++ ; break ;

    case PW_KEY_F5: finishing_position = -1 ;
                    for ( i = 0 ; i < world->getNumKarts() ; i++ ) {
		      Kart* pd=world->getKart(i);
		      pd->reset() ;
		      world->getKart(i)->reset() ;
		    }
		    return ;
 
    case PW_KEY_F2:  if ( isWireframe )
		       glPolygonMode ( GL_FRONT_AND_BACK, GL_FILL ) ;
		     else
		       glPolygonMode ( GL_FRONT_AND_BACK, GL_LINE ) ;
                     isWireframe = ! isWireframe ;
                     return ;
    case PW_KEY_F3:  stToggle () ; return ;
    case PW_KEY_F4:  hide_status () ; help  () ; return ;
    case PW_KEY_F12: paused = ! paused ; return ;

    case ' ' : if ( isHidden () )
		 show () ;
	       else
		 hide () ;
	       return ;

  default : ((PlayerKart*)world->getPlayerKart(0))->incomingKeystroke ( c ) ; break ;
  }
}
#endif

#ifdef JH
void GUI::joystickInput ()
{
  // Ignore all user input during profiling
  if(config->profile) return;

  KartControl *ctrl = &world->getPlayerKart(0)->controls;

  if ( joystick -> notWorking () )
  {
    memset(ctrl, 0, sizeof(*ctrl));
  }
  else
  {
    joystick -> read ( & ctrl.buttons, ctrl.data ) ;
    ctrl.data[0] *= 1.3 ;
  }


  if ( isKeyDown ( PW_KEY_UP    ) ) ctrl.buttons |= 0x01 ;
  if ( isKeyDown ( PW_KEY_DOWN  ) ) ctrl.buttons |= 0x02 ;
  if ( isKeyDown ( PW_KEY_LEFT  ) ) ctrl.data [0] = -1.0f ;
  if ( isKeyDown ( PW_KEY_RIGHT ) ) ctrl.data [0] =  1.0f ;
  if ( isKeyDown ( 'h' ) ) ctrl.data [0] = -1.0f ;
  if ( isKeyDown ( 'j' ) ) ctrl.data [0] = -.5f ;
  if ( isKeyDown ( 'k' ) ) ctrl.data [0] =  .5f ;
  if ( isKeyDown ( 'l' ) ) ctrl.data [0] =  1.0f ;

  if ( isKeyDown ( 'f' ) || isKeyDown ( 'F' ) ||
       isKeyDown ( '\r' )|| isKeyDown ( '\n' )) ctrl.buttons |= 0x04 ;
  if ( isKeyDown ( 'a' ) || isKeyDown ( 'A' ) ) ctrl.buttons |= 0x20 ;
  if ( isKeyDown ( 's' ) || isKeyDown ( 'S' ) ) ctrl.buttons |= 0x10 ;
  if ( isKeyDown ( 'd' ) || isKeyDown ( 'D' ) ) ctrl.buttons |= 0x08 ;

  ctrl.hits        = (ctrl.buttons ^ ctrl.old_buttons) &  ctrl.buttons ;
  ctrl.releases    = (ctrl.buttons ^ ctrl.old_buttons) & ~ctrl.buttons ;
  ctrl.old_buttons =  ctrl.buttons ;
  ((PlayerKart *)world->getPlayerKart(0)) -> incomingJoystick ( &ctrl ) ;
}



#endif
