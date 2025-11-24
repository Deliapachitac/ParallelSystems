# Compiler and flags
CC = gcc
CFLAGS =  #-Wall -O2 -pthread

# Target executable
TARGET = exercise_1

# Source files
SRC = exercise_1.c

# Default rule
all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

# Run example (degree 1000, 4 threads)
run: $(TARGET)
	./$(TARGET) 1000 4
# Clean up build files
clean:
	rm -f $(TARGET) *.o