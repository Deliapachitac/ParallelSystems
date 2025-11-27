# Makefile for solution.c and improved_solution.c

CC = gcc
CFLAGS = -g -Wall 
LDFLAGS = -lpthread

TARGETS = solution solution_rw
SRC_solution = solution.c
SRC_solution_rw = solution_rw.c
SRC_MYRAND = ../Shared/my_rand.c

all: $(TARGETS)

solution: $(SRC_solution) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o solution $(SRC_solution) $(SRC_MYRAND) $(LDFLAGS)

solution_rw: $(SRC_solution_rw) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o solution_rw $(SRC_solution_rw) $(SRC_MYRAND) $(LDFLAGS)

clean:
	rm -f $(TARGETS)
