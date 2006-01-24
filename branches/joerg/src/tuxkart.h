//  $Id: tuxkart.h,v 1.10 2005/08/23 19:58:54 joh Exp $
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

#ifndef HEADER_TUXKART_H
#define HEADER_TUXKART_H
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#ifdef WIN32
#  ifdef __CYGWIN__
#    include <unistd.h>
#  endif
#  include <windows.h>
#  include <io.h>
#  include <direct.h>
#else
#  include <unistd.h>
#endif
#include <math.h>

#include <plib/pw.h>
#include <plib/ssg.h>
#include <plib/sl.h>
#include <plib/js.h>
#include <plib/fnt.h>

#include "guNet.h"
#include "constants.h"
#include "utils.h"

class GUI ;
class SoundSystem ;
class Track ;

extern Track       *track ;

extern int      game_state ;

extern ssgRoot *scene           ;
extern char    *tuxkart_datadir ;

void tuxKartMainLoop () ;
void initMaterials   () ;
ssgBranch *process_userdata ( char *data ) ;

//JH extern int cam_follow ;
//JH extern int num_karts ;
extern int num_laps_in_race ;

#endif
