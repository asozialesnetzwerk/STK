# data/karts

pkgdatadir= $(datadir)/games/$(PACKAGE)/data/karts

nobase_dist_pkgdata_DATA = $(shell find $(srcdir) -name "materials.xml") \
                           $(shell find $(srcdir) -name "*.png")         \
                           $(shell find $(srcdir) -name "*.jpg")         \
                           $(shell find $(srcdir) -name "*.b3d")         \
                           $(shell find $(srcdir) -name "*.ogg")         \
                           $(shell find $(srcdir) -name "*.challenge")   \
                           $(shell find $(srcdir) -iname "License.txt")  \
                           stk_kart.py \
                           $(shell find $(srcdir) -name "kart.xml")
