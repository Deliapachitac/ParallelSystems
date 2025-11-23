# Makefile for solution.c and improved_solution.c

CC = gcc
CFLAGS = -Wall -O2
LDFLAGS = -lpthread

TARGETS = solution improved_solution
SRC_solution = solution.c
SRC_improved = improved_solution.c

all: $(TARGETS)

solution: $(SRC_solution)
	$(CC) $(CFLAGS) -o solution $(SRC_solution) $(LDFLAGS)

improved_solution: $(SRC_improved)
	$(CC) $(CFLAGS) -o improved_solution $(SRC_improved) $(LDFLAGS)

clean:
	rm -f $(TARGETS)
