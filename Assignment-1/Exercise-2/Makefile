# Compiler and flags
CC = gcc
CFLAGS =  #-Wall -O2 -pthread

# Target executable
TARGET = exercise_2

# Source files
SRC= exercise_2.c

# Default rule1
all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) -lpthread 
	
# Run example (4 threads, 1000 iterations)
run: 
	python3 script.py

# Clean up build files
clean:
	rm -f $(TARGET)*.o