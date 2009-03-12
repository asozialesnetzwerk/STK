# Very simple makefile, feel free to adjust!

CC	= gcc
CFLAGS	= 
LDFLAGS = -lglut

OBJ = showtxf.o texfont.o

default: showtxf DomesticManners.txf

showtxf: showtxf.o texfont.o
	$(CC) $^ -o showtxf $(LDFLAGS)

clean:
	rm $(OBJ) showtxf *.txf *.ppm

%.o:	%.c
	$(CC) -c $^

.PRECIOUS: DomesticManners.afm

%.afm:	%.ttf
	(export GS_FONTPATH=`pwd`; ttf2afm $^ >$*.afm)

%.txf:	%.afm
	./font.pl $^