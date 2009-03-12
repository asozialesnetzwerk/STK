# data/music

pkgdatadir = $(datadir)/games/@PACKAGE@/data/music

pkgdata_DATA = $(shell find $(srcdir) -name "*.ogg")  \
               $(shell find $(srcdir) -name "*.music") \
               License.txt

EXTRA_DIST = $(pkgdata_DATA)
