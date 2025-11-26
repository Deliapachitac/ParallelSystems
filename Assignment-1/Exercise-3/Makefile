# Makefile for solution.c and improved_solution.c

CC = gcc
CFLAGS = -Wall -O2
LDFLAGS = -lpthread

TARGETS = solution improved_solution
SRC_solution = solution.c
SRC_improved = improved_solution.c
SRC_MYRAND = ../Shared/my_rand.c

all: $(TARGETS)

solution: $(SRC_solution) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o solution $(SRC_solution) $(SRC_MYRAND) $(LDFLAGS)

improved_solution: $(SRC_improved) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o improved_solution $(SRC_improved) $(SRC_MYRAND) $(LDFLAGS)

clean:
	rm -f $(TARGETS)
