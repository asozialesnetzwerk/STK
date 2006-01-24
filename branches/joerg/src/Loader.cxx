//  $Id: Loader.cxx,v 1.3 2005/08/19 20:51:56 joh Exp $
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

#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#include <stdexcept>
#include <sstream>
#undef USE_SDL
#ifdef USE_SDL
#  include <SDL.h>
#  include <SDL_image.h>
#endif
#include "Loader.h"

Loader* loader = 0;

Loader::Loader() {
  char *datadir;

  if ( getenv ( "TUXKART_DATADIR" ) != NULL )
    datadir = getenv ( "TUXKART_DATADIR" ) ;
  else
#ifdef _MSC_VER
    if ( _access ( "data/levels.dat", 04 ) == 0 )
#else
    if ( access ( "data/levels.dat", F_OK ) == 0 )
#endif
      datadir = "." ;
    else
#ifdef _MSC_VER
      if ( _access ( "../data/levels.dat", 04 ) == 0 )
#else
      if ( access ( "../data/levels.dat", F_OK ) == 0 )
#endif
	datadir = ".." ;
      else
#ifdef TUXKART_DATADIR
	datadir = TUXKART_DATADIR ;
#else
      datadir = "/usr/local/share/games/tuxkart" ;
#endif
  fprintf ( stderr, "Data files will be fetched from: '%s'\n", datadir ) ;
  addSearchPath(datadir);
}

Loader::~Loader() {
}

void Loader::make_path(char* path, const char* dir, const char* fname) const {
  struct stat mystat;
    
  for(std::vector<std::string>::const_iterator i = searchPath.begin();
      i != searchPath.end(); ++i) {
    sprintf(path, "%s/%s/%s", i->c_str(), dir, fname);
    // convert backslashes to slashes
    size_t len = strlen(path);
    for(size_t i = 0; i < len; ++i)
      if(path[i] == '\\')
        path[i] = '/';
    
    if(stat(path, &mystat) < 0)
      continue;

    return;
  }

  // error case...
  // hmm ideally we'd throw an exception here, but plib is not prepared for that
  sprintf(path, "NotFound: %s", fname);
}

void Loader::makeModelPath(char* path, const char* fname) const {
  make_path(path, getModelDir(), fname);
}

void Loader::makeTexturePath(char* path, const char* fname) const {
  make_path(path, getTextureDir(), fname);
}

void Loader::addSearchPath(const std::string& path) {
  searchPath.push_back(path);
}

void Loader::addSearchPath(const char* path)
{
  searchPath.push_back(std::string(path));
}

void Loader::initConfigDir() {
#ifdef WIN32
  /*nothing*/
#else
  /*if HOME environment variable exists
    create directory $HOME/.tuxkart*/
  if(getenv("HOME")!=NULL) 
  {
    std::string pathname;
    pathname = getenv("HOME");
    pathname += "/.supertuxkart";
    mkdir(pathname.c_str(), 0755);
  }
#endif
}

std::string Loader::getPath(const std::string& fname) const {
  struct stat mystat;
  std::string result;
   
  for(std::vector<std::string>::const_iterator i = searchPath.begin();
      i != searchPath.end(); ++i) {
    result = *i;
    result += '/';
    result += fname;
    
    if(stat(result.c_str(), &mystat) < 0)
      continue;
    
    return result;
  }

  std::stringstream msg;
  msg << "Couldn't find file '" << fname << "'.";
  throw std::runtime_error(msg.str());
}

void Loader::listFiles(std::set<std::string>& result, const std::string& dir) 
     const {
  struct stat mystat;

#ifdef DEBUG
  // don't list directories with a slash on the end, it'll fail on win32
  assert(dir[dir.size()-1] != '/');
#endif

  result.clear();

  for(std::vector<std::string>::const_iterator i = searchPath.begin();
      i != searchPath.end(); ++i) {
    std::string path = *i;
    path += '/';
    path += dir;
    
    if(stat(path.c_str(), &mystat) < 0)
      continue;
    if(! S_ISDIR(mystat.st_mode))
      continue;
    
    DIR* mydir = opendir(path.c_str());
    if(!mydir)
      continue;

    struct dirent* mydirent;
    while( (mydirent = readdir(mydir)) != 0) {
      result.insert(mydirent->d_name);
    }
    closedir(mydir);
  }
}
#ifdef USE_SDL
// PNG and JPEG loader (with help of SDL_Image)

bool ssgLoadIMG(const char* fname, ssgTextureInfo* info)
{
  SDL_Surface* surface = IMG_Load(fname);
  if(!surface) {
    ulSetError(UL_WARNING, "ssgLoadPNG: Failed to load '%s': %s",
        fname, SDL_GetError());
    return false;
  }
  if(surface->pitch != surface->w * surface->format->BytesPerPixel) {
    ulSetError(UL_WARNING, "ssgLoadPNG: incompatible surface while "
        "loading '%s' (pitch mismatch)", fname);
    return false;
  }
  
  if(info != 0) {
    info->width = surface->w;
    info->height = surface->h;
    info->depth = surface->format->BytesPerPixel;
    info->alpha = surface->format->BytesPerPixel > 3;
  }

  // create mipmaps
  int bpp = surface->format->BytesPerPixel;

  // grrr, ssgMakeMipMaps calls delete[] on the data, it also seems to need
  // the texture upsidedown...
  size_t datasize = surface->w * surface->h * bpp;
  GLubyte* data = new GLubyte[datasize];
  GLubyte* dest = data + surface->pitch * (surface->h - 1);
  GLubyte* src = (GLubyte*) surface->pixels;
  for(int i = 0; i < surface->h; ++i) {
    memcpy(dest, src, surface->pitch);
    dest -= surface->pitch;
    src += surface->pitch;
  }
  
  bool result = ssgMakeMipMaps(data, surface->w, surface->h, bpp);
  SDL_FreeSurface(surface);

  return result;
}
#endif
void registerImageLoaders() {
#ifdef USE_SDL
  ssgAddTextureFormat(".png", ssgLoadIMG);
  ssgAddTextureFormat(".jpg", ssgLoadIMG);
  ssgAddTextureFormat(".jpeg", ssgLoadIMG);    
#endif
}

