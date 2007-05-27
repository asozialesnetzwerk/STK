OUTPUTFILES = index.html screenshots.html download.html contact.html

XALAN_VERSION_X=`xalan 2>&1 | head -n 1 | sed "s/\./ /g" | awk '{print $$3}'`
XALAN_VERSION_Y=`xalan 2>&1 | head -n 1 | sed "s/\./ /g" | awk '{print $$4}'`
XALAN_VERSION_Z=`xalan 2>&1 | head -n 1 | sed "s/\./ /g" | awk '{print $$5}'`

all : $(OUTPUTFILES)

clean :
	rm -vf $(OUTPUTFILES)

%.html :: %.xml default.xsl Makefile menu.xml
	FILENAME=$<; \
	LASTCHANGE=`date -I`; \
	echo $${FILENAME%%.xml}; \
        if [ $(XALAN_VERSION_X) -eq 1 -a $(XALAN_VERSION_Y) -ge 7 ]; then \
            XALAN_PARAM="-p"; \
            XALAN_IN=""; \
            XALAN_OUT="-o"; \
            XALAN_XSL=""; \
        else \
            XALAN_PARAM="-PARAM"; \
            XALAN_IN="-IN"; \
            XALAN_OUT="-OUT"; \
            XALAN_XSL="-XSL"; \
        fi; \
        xalan \
          $$XALAN_PARAM filename   "'$${FILENAME%%.xml}'" \
          $$XALAN_PARAM lastchange "'$${LASTCHANGE}'" \
          $$XALAN_OUT $@ \
          $$XALAN_IN $< \
          $$XALAN_XSL default.xsl

upload: berlios

commit: berlios

berlios: all
	rsync -Ctrv . sik0fewl@shell.berlios.de:/home/groups/supertuxkart/htdocs/

.PHONY: all clean upload

# EOF #
