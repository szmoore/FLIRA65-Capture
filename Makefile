# Makefile for FLIRA65-Capture 

CC = gcc
FLAGS = --std=c99 -I./contrib/include/aravis-0.4 $(shell pkg-config --cflags gobject-2.0) $(shell pkg-config --cflags libpng12)
LIB = -L./contrib/lib -laravis-0.4 $(shell pkg-config --libs gobject-2.0) $(shell pkg-config --libs libpng12)
PREPROCESSOR_FLAGS = 
OBJ = FLIRA65-Capture.o savebuffer.o
BIN = FLIRA65-Capture

$(BIN) : $(OBJ)
	$(CC) -o $(BIN) $(OBJ) $(LIB)

%.o : %.c
	$(CC) $(FLAGS) $(PREPROCESSOR_FLAGS) -o $@ -c $<


clean :
	$(RM) $(OBJ)

