//  $Id: status.cxx 267 2005-08-31 17:27:00Z joh $
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
#include "gui/OldGUI.h"
#include "World.h"
#include "Kart.h"
#include "WorldScreen.h"
#include "Config.h"
#include "MaterialManager.h"
#include <stdarg.h>
#include "Collectable.h"

#define MAX_STRING          30
#define MAX_STRING_LENGTH  256

double time_left = 0.0 ;

float tt[6]={0,0,0,0,0,0};

static fntRenderer *text = NULL ;

char debug_strings [ MAX_STRING ][ MAX_STRING_LENGTH ] ;
int next_string   = 0 ;
int stats_enabled = FALSE ;

// temporary, this will be removed
#define NUM_KARTS 8
sgVec3 player_colour [ NUM_KARTS ] =
{
  { 1, 0, 0 }, /* Tux   */
  { 0, 1, 0 }, /* Geeko */
  { 0, 0, 1 }, /* BSOD  */
  { 1, 0, 1 }, /* Gown  */
  { 0, 1, 1 }, { 1, 1, 0 }, { 0, 0, 0 }, { 1, 1, 1 }
} ;


void stToggle ()
{
  if ( stats_enabled )
    stats_enabled = FALSE ;
  else
  {
    stats_enabled = TRUE ;

    for ( int i = 0 ; i < MAX_STRING ; i++ )
       debug_strings [ i ][ 0 ] = '\0' ;

    next_string = 0 ;
  }
}


void stPrintf ( char *fmt, ... )
{
  char *p = debug_strings [ next_string++ ] ;

  if ( next_string >= MAX_STRING )
    next_string = 0 ;

  va_list ap ;
  va_start ( ap, fmt ) ;
/*
  Ideally, we should use this:

     vsnprintf ( p, MAX_STRING_LENGTH, fmt, ap ) ;

  ...but it's only in Linux   :-(
*/

  vsprintf ( p, fmt, ap ) ;

  va_end ( ap ) ;
}

static int    about_timer = 99999 ;
static int versions_timer = 99999 ;
static int  credits_timer = 99999 ;
static int    intro_timer =    0  ;
static int     help_timer = 99999 ;

void hide_status () { versions_timer = credits_timer =
                         intro_timer = help_timer = about_timer = 99999 ; }
void about       () {    about_timer = 0 ; }
void credits     () {  credits_timer = 0 ; }
void versions    () { versions_timer = 0 ; }
void help        () {     help_timer = 0 ; }

void drawText ( char *str, int sz, int x, int y )
{
  text -> setFont      ( font ) ;
  text -> setPointSize ( sz ) ;

  text -> begin () ;
    text -> start2f ( x, y ) ;
    text -> puts ( str ) ;
  text -> end () ;
}


void drawInverseDropShadowText ( char *str, int sz, int x, int y )
{
  glColor4f ( 1.0f, 1.0f, 1.0f, 1.0f ) ;
  drawText ( str, sz, x, y ) ;
  glColor4f ( 0.0f, 0.0f, 0.0f, 1.0f ) ;
  drawText ( str, sz, x+1, y+1 ) ;
}


void drawDropShadowText ( char *str, int sz, int x, int y )
{
  glColor4f ( 0.0f, 0.0f, 0.0f, 1.0f ) ;

  drawText ( str, sz, x, y ) ;

  glColor4f ( 1.0f, 1.0f, 1.0f, 1.0f ) ;

  drawText ( str, sz, x+1, y+1 ) ;
}


void drawHelpText ()
{
  drawDropShadowText ( "Press SPACE to toggle the menu.",  18, 70, 400 ) ;
  drawDropShadowText ( "Press ESCAPE to exit the game.",   18, 70, 370 ) ;

  drawDropShadowText ( "Joystick: A - Accellerate.  B - Brake.",
                                                           18, 70, 330 ) ;
  drawDropShadowText ( "          C - Use an item.  D - Ask to be rescued.",
                                                           18, 70, 300 ) ;
  drawDropShadowText ( "          L - Pop a wheelie R - Jump.",
                                                           18, 70, 270 ) ;
 
  drawDropShadowText ( "Keyboard: ARROWS - Steer, accellerate and brake",
                                                           18, 70, 230 ) ;
 
  drawDropShadowText ( "          A - Pop a Wheelie S - Jump",
                                                           18, 70, 200 ) ;
  drawDropShadowText ( "          F - Use an item.  D - Ask to be rescued",
                                                           18, 70, 170 ) ;
  drawDropShadowText ( "          R - Restart race. P - Pause.",
                                                           18, 70, 150 ) ;
}


void drawTitleText ()
{
  drawDropShadowText ( "TuxKart", 20, 80, 400 ) ;
  drawDropShadowText ( "By Steve & Oliver Baker", 12, 180, 385 ) ;
}


void drawIntroText ()
{
  drawTitleText () ;

  if ( intro_timer & 8 )
    drawDropShadowText ( "Press SPACE bar for menu.", 15, 10, 430 ) ;
}


char *aboutText [] =
{
  "Written    by Steve Baker",
  "Playtested by Oliver Baker",
  "Music      by Matt Thomas",
  "Track design and other 3D models by Both Bakers.",
  NULL
} ;


void drawVersionsText ()
{
  char str [ 256 ] ;

#ifdef VERSION
  sprintf ( str, "TuxKart: Version: %s", VERSION ) ;
#else
  sprintf ( str, "TuxKart: Unknown Version." ) ;
#endif
  drawDropShadowText ( str, 15, 20, 250 ) ;

  sprintf ( str, "PLIB Version: %s", ssgGetVersion() ) ;
  drawDropShadowText ( str, 15, 20, 225 ) ;

  sprintf ( str, "OpenGL Version: %s", glGetString ( GL_VERSION ) ) ;
  drawDropShadowText ( str, 15, 20, 200 ) ;

  sprintf ( str, "OpenGL Vendor: %s", glGetString ( GL_VENDOR ) ) ;
  drawDropShadowText ( str, 15, 20, 175 ) ;

  sprintf ( str, "OpenGL Renderer: %s", glGetString ( GL_RENDERER ) ) ;

  if ( strlen ( str ) > 50 )
  {
    int l = strlen ( str ) ;
    int ll = 0 ;

    for ( int i = 0 ; i < l ; i++, ll++ )
    {
      if ( ll > 40 && str[i] == ' ' )
      {
        str[i] = '\n' ;
        ll = 0 ;
      }
    }
  }

  drawDropShadowText ( str, 15, 20, 150 ) ;

  if ( versions_timer & 8 )
    drawDropShadowText ( "Press SPACE to continue",
                       15, 10, 430 ) ;
}


void drawAboutText ()
{
  drawTitleText () ;

  drawDropShadowText ( "The Rules of TuxKart:",
                       20, 10, 300 ) ;

  for ( int i = 0 ; aboutText [ i ] != NULL ; i++ )
    drawDropShadowText ( aboutText [ i ],
                       16, 10, 280 - 18 * i ) ;

  if ( about_timer & 8 )
    drawDropShadowText ( "Press SPACE to continue",
                       15, 10, 430 ) ;
}


char *creditsText [] =
{
  "  Steve  Baker    - Coding, design, bug insertion.",
  "  Oliver Baker    - Modelling, Play Testing, Ideas.",
  "  Matt  Thomas    - Music.",
  " ",
  "Special thanks to:",
  " ",
  "  Daryll Strauss, Brian Paul, Linus Torvalds",
  NULL
} ;



void drawCreditsText ()
{
  drawTitleText () ;

  drawDropShadowText ( "Credits:",
                       20, 70, 250 ) ;

  for ( int i = 0 ; creditsText [ i ] != NULL ; i++ )
    drawDropShadowText ( creditsText [ i ],
                       12, 100, 230 - 12 * i ) ;

  if ( credits_timer & 8 )
    drawDropShadowText ( "Press SPACE to continue",
                       15, 10, 430 ) ;
}


void drawStatsText ()
{
  char str [ 256 ] ;

  sprintf ( str, "%3d,%3d,%3d,%3d,%3d,%3d", (int)tt[0],(int)tt[1],(int)tt[2],(int)tt[3],(int)tt[4],(int)tt[5]) ;
  drawDropShadowText ( str, 18, 5, 300 ) ;
}

void drawTimer ()
{
  char str [ 256 ] ;

  time_left = world->clock;

  int min     = (int) floor ( time_left / 60.0 ) ;
  int sec     = (int) floor ( time_left - (double) ( 60 * min ) ) ;
  int tenths  = (int) floor ( 10.0f * (time_left - (double)(sec + 60*min)));

  sprintf ( str, "%3d:%02d.%d", min,  sec,  tenths ) ;
  drawDropShadowText ( str, 18, 450, 430 ) ;
}

static char *pos_string [] =
{
  "?!?",
  "1st",
  "2nd",
  "3rd",
  "4th",
  "5th",
  "6th",
  "7th",
  "8th",
  "9th"
} ;

void drawScore () {
  char str [ 20 ] ;

  Kart* kart = world->getKart(0);
  if ( kart->getVelocity()->xyz[1] < 0 )
    sprintf ( str, "Reverse" ) ;
  else
    sprintf(str,"%3dmph",(int)(kart->getVelocity()->xyz[1]/MILES_PER_HOUR));

  drawDropShadowText ( str, 18, 450, 410 ) ;

  if ( kart->getLap() < 0 )
    sprintf ( str, "Not Started Yet!" ) ;
  else
  if ( kart->getLap() < num_laps_in_race - 1 )
    sprintf ( str, "%s - Lap %d",
      pos_string [ kart->getPosition() ],
                   kart->getLap() + 1 ) ;
  else
  {
    static int flasher = 0 ;

    if ( ++flasher & 32 )
      sprintf ( str, "%s - Last Lap!",
        pos_string [ kart->getPosition() ] ) ;
    else
      sprintf ( str, "%s",
        pos_string [ kart->getPosition() ] ) ;
  }

  drawDropShadowText ( str, 18, 450, 390 ) ;
}


void drawGameIntroText ()
{
  static int timer = 0 ;

  if ( timer++ & 8 )
    drawDropShadowText ( "Press S to start", 15, 10, 430 ) ;

  if ( help_timer++ < 400 )
    drawHelpText () ;
  else
  if ( intro_timer++ < 400 )
    drawIntroText () ;
  else
  if ( credits_timer++ < 1600 )
    drawCreditsText () ;
  else
  if ( about_timer++ < 1600 )
    drawAboutText () ;
  else
  if ( versions_timer++ < 1600 )
    drawVersionsText () ;
}


void drawGameRunningText ()
{
  drawScore () ;
  drawTimer () ;

  glColor4f ( 0.6, 0.0, 0.6, 1.0 ) ;

  if ( stats_enabled )
    drawStatsText () ;

  if ( help_timer++ < 400 )
    drawHelpText () ;
  else
  if ( credits_timer++ < 1600 )
    drawCreditsText () ;
  else
  if ( about_timer++ < 1600 )
    drawAboutText () ;
  else
  if ( versions_timer++ < 1600 )
    drawVersionsText () ;
}


void drawEmergencyText () {
  static float wrong_timer = 0.0f ;
  static float last_dist = -1000000.0f ;
  static int last_lap = -1 ;

  Kart* kart = world->getKart(0);
  float d = kart -> getDistanceDownTrack () ;
  int   l = kart -> getLap () ;

  if ( ( l < last_lap || ( l == last_lap && d < last_dist ) ) &&
       kart -> getVelocity () -> xyz [ 1 ] > 0.0f )
  {
    wrong_timer += 0.05;   // FIXME: was fclock -> getDeltaTime () ;

    if ( wrong_timer > 2.0f )
    {
      static int i = FALSE ;

      if ( i )
        glColor4f ( 1.0f, 0.0f, 1.0f, 1.0f ) ;
      else
        glColor4f ( 0.0f, 1.0f, 0.0f, 1.0f ) ;

      drawText ( "WRONG WAY!", 50, 100, 240 ) ;

      if ( ! i )
        glColor4f ( 1.0f, 0.0f, 1.0f, 1.0f ) ;
      else
        glColor4f ( 0.0f, 1.0f, 0.0f, 1.0f ) ;

      drawText ( "WRONG WAY!", 50, 100+2, 240+2 ) ;

      i = ! i ;
    }
  }
  else
    wrong_timer = 0.0f ;

  last_dist = d ;
  last_lap  = l ;
}


void drawCollectableIcons ()
{
  int zz = FALSE ;

  Kart* kart = world->getKart(0);
  int x1 =  20 ;
  int y1 = 400 ;
  int n  = kart->getNumCollectables() ;

  if ( n > 5 ) n = 5 ;
  if ( n < 1 ) n = 1 ;

  glBegin ( GL_QUADS ) ;
    glColor4f    ( 1, 1, 1, 1 ) ;

    for ( int i = 0 ; i < n ; i++ )
    {
      if ( zz )
      {
	glTexCoord2f ( 0, 2 ) ; glVertex2i ( i*40 + x1   , y1    ) ;
	glTexCoord2f ( 0, 0 ) ; glVertex2i ( i*40 + x1+32, y1    ) ;
	glTexCoord2f ( 2, 0 ) ; glVertex2i ( i*40 + x1+64, y1+32 ) ;
	glTexCoord2f ( 2, 2 ) ; glVertex2i ( i*40 + x1+32, y1+32 ) ;

	glTexCoord2f ( 0, 2 ) ; glVertex2i ( i*40 + x1+32, y1+32 ) ;
	glTexCoord2f ( 0, 0 ) ; glVertex2i ( i*40 + x1+64, y1+32 ) ;
	glTexCoord2f ( 2, 0 ) ; glVertex2i ( i*40 + x1+32, y1+64 ) ;
	glTexCoord2f ( 2, 2 ) ; glVertex2i ( i*40 + x1   , y1+64 ) ;
      }
      else
      {
	glTexCoord2f ( 0, 0 ) ; glVertex2i ( i*30 + x1   , y1    ) ;
	glTexCoord2f ( 1, 0 ) ; glVertex2i ( i*30 + x1+64, y1    ) ;
	glTexCoord2f ( 1, 1 ) ; glVertex2i ( i*30 + x1+64, y1+64 ) ;
	glTexCoord2f ( 0, 1 ) ; glVertex2i ( i*30 + x1   , y1+64 ) ;
      }
    }
  glEnd () ;
}


void drawPartlyDigestedHerring ( float state )
{
  herringbones_gst -> apply () ;
 
  glBegin ( GL_QUADS ) ;
  glColor3f    ( 1, 1, 1 ) ;
  glTexCoord2f ( 0, 0 ) ; glVertex2i ( 200, 400 ) ;
  glTexCoord2f ( 1, 0 ) ; glVertex2i ( 300, 400 ) ;
  glTexCoord2f ( 1, 1 ) ; glVertex2i ( 300, 440 ) ;
  glTexCoord2f ( 0, 1 ) ; glVertex2i ( 200, 440 ) ;
  glEnd () ;
 
  herring_gst -> apply () ;
 
  glBegin ( GL_QUADS ) ;
  glColor3f    ( 0.7, 1, 1 ) ;
  glTexCoord2f ( 0, 0 ) ; glVertex2i ( 200,  400 ) ;
  glTexCoord2f ( state, 0 ) ; glVertex2i ( 200 + (int)(state * 100.0f), 400 ) ;
  glTexCoord2f ( state, 1 ) ; glVertex2i ( 200 + (int)(state * 100.0f), 440 ) ;
  glTexCoord2f ( 0, 1 ) ; glVertex2i ( 200, 440 ) ;
  glEnd () ;                                                                    
}

