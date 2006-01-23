//  $Id: widget_image.h 14 2005-05-25 21:54:15Z joh $
//
//  SuperTuxKart - a fun racing game with go-kart
//  This code originally from Neverball copyright (C) 2003 Robert Kooima
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

#ifndef IMAGE_H
#define IMAGE_H


//JH #include "widget_glext.h"
#ifdef __APPLE__
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif

//previously in config.h:
#define SDL_BIG_ENDIAN 1

#if SDL_BYTEORDER == SDL_BIG_ENDIAN
#define RMASK 0xFF000000
#define GMASK 0x00FF0000
#define BMASK 0x0000FF00
#define AMASK 0x000000FF
#else
#define RMASK 0x000000FF
#define GMASK 0x0000FF00
#define BMASK 0x00FF0000
#define AMASK 0xFF000000
#endif

/*---------------------------------------------------------------------------*/

void   image_snap(char *);
void   image_size(int *, int *, int, int);

//JH void         image_swab (SDL_Surface *);
//JH void         image_white(SDL_Surface *);
//JH SDL_Surface *image_scale(SDL_Surface *, int);
void         image_swab (void *);
void         image_white(void *);
//JH SDL_Surface *image_scale(void *, int);

//JH GLuint make_image_from_surf(int *, int *, SDL_Surface *);
GLuint make_image_from_file(int *, int *,
                            int *, int *, const char *);
//JH GLuint make_image_from_font(int *, int *,
//JH                            int *, int *, const char *, TTF_Font *);

/*---------------------------------------------------------------------------*/

#endif
