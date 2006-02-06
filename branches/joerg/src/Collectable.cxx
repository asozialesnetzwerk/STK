//  $Id: Collectable.cxx,v 1.6 2005/08/23 20:00:57 joh Exp $
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

#include "Collectable.h"
#include "MaterialManager.h"
#include "ProjectileManager.h"

typedef struct {collectableType collectable; char *iconFile;} 
  initCollectableType;

initCollectableType ict[]={
  {COLLECT_ZIPPER,         "zipper.rgb"        },
  {COLLECT_MAGNET,         "magnet.rgb"        },
  {COLLECT_SPARK,          "spark.rgb"         },
  {COLLECT_MISSILE,        "missile.rgb"       },
  {COLLECT_HOMING_MISSILE, "homingmissile.rgb" },
  {COLLECT_MAX,            0                   },
};

CollectableManager::CollectableManager() {
  for(int i=0; ict[i].collectable!=COLLECT_MAX; i++) {
    icons[ict[i].collectable]=material_manager->getMaterial(ict[i].iconFile);
  }
}

CollectableManager *Collectable::collectable_manager=0;

Collectable::Collectable(Kart* kart_) {
  if(!collectable_manager) {
    collectable_manager=new CollectableManager();
  }
  kart   = kart_;
  type   = COLLECT_NOTHING;
  number = 0;
}   // Collectable

// -----------------------------------------------------------------------------
void Collectable::set(collectableType _type, int n) {
  if (type==_type) {
    number+=n;
    return;
  }
  type=_type;
  number=n;
}  // set

// -----------------------------------------------------------------------------
Material *Collectable::getIcon() {
  // Cheock if it's one of the types which have a separate
  // data file which includes the icon:
  return collectable_manager->getIcon(type);
}

// -----------------------------------------------------------------------------
void Collectable::use() {
  number--;
  switch (type) {
    case COLLECT_MAGNET:   kart->attach(ATTACH_MAGNET, 10.0f);
                           break ;
    case COLLECT_ZIPPER:   kart->handleZipper();
			   break ;
    case COLLECT_HOMING_MISSILE: 
    case COLLECT_SPARK:
    case COLLECT_MISSILE:  projectile_manager->newProjectile(kart, type);
                           break ;
	 
    case COLLECT_NOTHING:
    default :             break ;
  }
   
  if ( number <= 0 ) {
    clear();
  }                                                                           
}   // use

// -----------------------------------------------------------------------------
void Collectable::hitRedHerring(int n) {
  collectableType newC=(collectableType)(rand()%5+1);
  if(type==COLLECT_NOTHING) {
    type=newC;
    number=n;
  } else if(newC==type) {
    number+=n;
  }  
  // Ignore new collectable if it is different from the current one
}   // hitRedHerring
