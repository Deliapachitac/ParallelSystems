CC = mpicc
CFLAGS = -g -Wall  -O3 -mavx2
BUILD_DIR = build
SRC_MYRAND = Shared/my_rand.c
SRC1 = Exercise-1/solution.c

all: Ex1 Ex2 Ex3

Ex1: $(SRC1)
	@mkdir -p $(BUILD_DIR)/Exercise-1
	$(CC) $(CFLAGS) -o $(BUILD_DIR)/Exercise-1/solution $(SRC1)

script1:
	python3 Exercise-1/script.py


clean:
	rm -rf $(BUILD_DIR)

.PHONY: all clean Ex1 Ex2 Ex3 script1 script2