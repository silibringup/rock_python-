SRCDIR := src
OUTDIR := build
ARGS := -I$(SRCDIR) 
SRC =

all: clean build


build: buildso
	mkdir $(OUTDIR)
	g++ $(SRCDIR)/$(SRC) -L. -Wl,-rpath,. -lutilft4222h -lft4222 -lwiringPi -Wl,-rpath,/usr/local/lib -o $(OUTDIR)/run

buildso:
	g++ src/local_util.c -Isrc -lft4222 -lwiringPi -Wl,-rpath,/usr/local/lib -shared -fPIC -o libutilft4222h.so

clean:
	rm -rf $(OUTDIR)
