OUTPUTFILES = index.html screenshots.html download.html contact.html

all : $(OUTPUTFILES)

clean :
	rm -vf $(OUTPUTFILES)

%.html :: %.xml default.xsl Makefile menu.xml
	FILENAME=$<; \
	LASTCHANGE=`date -I`; \
	echo $${FILENAME%%.xml}; \
	xalan \
          -PARAM filename   "'$${FILENAME%%.xml}'" \
          -PARAM lastchange "'$${LASTCHANGE}'" \
          -IN $< \
          -OUT $@ \
          -XSL default.xsl

upload: berlios

commit: berlios

berlios: all
	rsync -Ctrv . grumbel@shell.berlios.de:/home/groups/supertuxkart/htdocs/

.PHONY: all clean upload

# EOF #
