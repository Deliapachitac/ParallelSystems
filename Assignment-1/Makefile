# ============================================================
# COMPILER SETTINGS
# ============================================================
CC = gcc
CFLAGS = -g -Wall
LDFLAGS = -lpthread

# ============================================================
# TARGET LIST
# ============================================================
TARGETS = Ex1 Ex2 Ex3solution Ex3improved_solution Ex4solution Ex4solution_rw Ex5_1 Ex5_2 Ex5_3

# ============================================================
# SOURCE FILE DEFINITIONS
# ============================================================
# Exercise 1
SRC1 = Exercise-1/exercise_1.c

# Exercise 2
SRC2 = Exercise-2/exercise_2.c

# Exercise 3
SRC_solution_3 = Exercise-3/solution.c
SRC_improved_3 = Exercise-3/improved_solution.c

# Exercise 4
SRC_solution_4 = Exercise-4/solution.c
SRC_solution_rw_4 = Exercise-4/solution_rw.c

# Exercise 5
SRC5_1 = Exercise-5/exercise_5_1.c
SRC5_2 = Exercise-5/exercise_5_2.c
SRC5_3 = Exercise-5/exercise_5_3.c

# Shared code
SRC_MYRAND = Shared/my_rand.c


# ============================================================
# DEFAULT RULE
# ============================================================
all: $(TARGETS)


# ============================================================
# EXERCISE 1
# ============================================================
Ex1: $(SRC1)
	$(CC) $(CFLAGS) -o Exercise-1/exercise_1 $(SRC1) $(LDFLAGS)

run1: Ex1
	python3 Exercise-1/script.py


# ============================================================
# EXERCISE 2
# ============================================================
Ex2: $(SRC2)
	$(CC) $(CFLAGS) -o Exercise-2/exercise_2 $(SRC2) $(LDFLAGS)

run2: Ex2
	python3 Exercise-2/script.py


# ============================================================
# EXERCISE 3
# ============================================================
Ex3solution: $(SRC_solution_3) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o Exercise-3/solution $(SRC_solution_3) $(SRC_MYRAND) $(LDFLAGS)

Ex3improved_solution: $(SRC_improved_3) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o Exercise-3/improved_solution $(SRC_improved_3) $(SRC_MYRAND) $(LDFLAGS)

run3: Ex3solution Ex3improved_solution
	python3 Exercise-3/script.py


# ============================================================
# EXERCISE 4
# ============================================================
Ex4solution: $(SRC_solution_4) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o Exercise-4/solution $(SRC_solution_4) $(SRC_MYRAND) $(LDFLAGS)

Ex4solution_rw: $(SRC_solution_rw_4) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o Exercise-4/solution_rw $(SRC_solution_rw_4) $(SRC_MYRAND) $(LDFLAGS)

run4: Ex4solution Ex4solution_rw
	python3 Exercise-4/script.py


# ============================================================
# EXERCISE 5
# ============================================================
Ex5_1: $(SRC5_1) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o Exercise-5/exercise_5_1 $(SRC5_1) $(SRC_MYRAND) $(LDFLAGS)

Ex5_2: $(SRC5_2) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o Exercise-5/exercise_5_2 $(SRC5_2) $(SRC_MYRAND) $(LDFLAGS)

Ex5_3: $(SRC5_3) $(SRC_MYRAND)
	$(CC) $(CFLAGS) -o Exercise-5/exercise_5_3 $(SRC5_3) $(SRC_MYRAND) $(LDFLAGS)

run5: Ex5_1 Ex5_2 Ex5_3
	python3 Exercise-5/script.py


# ============================================================
# RUN ALL SCRIPTS
# ============================================================
run: run1 run2 run3 run4 run5
	@echo "✔ All exercises executed."


# ============================================================
# CLEAN
# ============================================================
clean:
	rm -f Exercise-1/exercise_1 \
	      Exercise-2/exercise_2 \
	      Exercise-3/solution \
	      Exercise-3/improved_solution \
	      Exercise-4/solution \
	      Exercise-4/solution_rw \
	      Exercise-5/exercise_5_1 \
	      Exercise-5/exercise_5_2 \
	      Exercise-5/exercise_5_3
	rm -f $(TARGETS)
	rm -f *.png *.txt
