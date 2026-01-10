CC = mpicc
CFLAGS = -g -Wall
BUILD_DIR = build
SRC_MYRAND = Shared/my_rand.c
SRC1 = Exercise-1/solution.c
SRC2 = Exercise-2/solution.c
SRC3 = Exercise-3/solution.c

all: Ex1 Ex2 Ex3

Ex1: $(SRC1)
	@mkdir -p $(BUILD_DIR)/Exercise-1
	$(CC) $(CFLAGS) -o $(BUILD_DIR)/Exercise-1/solution $(SRC1)


Ex2: $(SRC2) $(SRC_MYRAND)
	@mkdir -p $(BUILD_DIR)/Exercise-2
	$(CC) $(CFLAGS) -o $(BUILD_DIR)/Exercise-2/solution $(SRC2) $(SRC_MYRAND)

Ex3: $(SRC3) $(SRC_MYRAND)
	@mkdir -p $(BUILD_DIR)/Exercise-3
	$(CC) $(CFLAGS) -fopenmp -o $(BUILD_DIR)/Exercise-3/solution $(SRC3) $(SRC_MYRAND) 

clean:
	rm -rf $(BUILD_DIR)

.PHONY: all clean Ex1 Ex2 Ex3