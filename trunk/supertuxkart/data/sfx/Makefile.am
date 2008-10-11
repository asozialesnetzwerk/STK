# sfx/

pkgdatadir = $(datadir)/games/@PACKAGE@/data/sfx

nobase_pkgdata_DATA =  $(shell find $(srcdir) -name "*.wav") \
                       $(shell find $(srcdir) -name "README")\
                       $(shell find $(srcdir) -name "sfx.config")

EXTRA_DIST = $(nobase_pkgdata_DATA) 
