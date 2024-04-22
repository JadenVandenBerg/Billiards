CFLAGS = -g -Wall -std=c99 -pedantic
CC = clang

PY_INC = /usr/include/python3.10
PY_INC_LIB = /usr/lib/python3.10

all: _phylib.so

clean:
	rm -f *.o *.so *.svg

main.o:  main.c phylib.h
	$(CC) $(CFLAGS) -c main.c -o main.o

phylib.o: phylib.c phylib.h
	$(CC) $(CFLAGS) -c phylib.c -fPIC -o phylib.o

phylib_wrap.c:
	swig -python phylib.i

phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -c phylib_wrap.c -I$(PY_INC) -fPIC -o phylib_wrap.o

_phylib.so: libphylib.so phylib_wrap.o
	$(CC) $(CFLAGS) -shared phylib_wrap.o -L. -L$(PY_INC_LIB) -lpython3.10 -lphylib -o _phylib.so -lm

libphylib.so: phylib.o phylib.h
	$(CC) phylib.o -shared -o libphylib.so

# export LD_LIBRARY_PATH=`pwd`
