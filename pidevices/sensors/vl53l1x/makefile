.PHONY: clean lib

CC = gcc
SRC = api
LIB = test.so
LDFLAGS :=
CFLAGS := -Iapi/core -Iapi/platform -std=c99

SC_FILES := $(wildcard $(SRC)/*/*.c)
SRC_FILES := $(wildcard $(SRC)/*/*.c)
OBJ_FILES := $(patsubst $(SRC)/*/*.c,$(SRC)/*/%.o,$(SRC_FILES))

$(LIB): $(OBJ_FILES)
	$(CC) $(LDFLAGS) $(CFLAGS) -fPIC -shared -o $@ $^

$(SRC)/%.o: $(SRC)/%.c
	$(CC) $(LDFLAGS) $(CFLAGS) -c -o $@ $<
