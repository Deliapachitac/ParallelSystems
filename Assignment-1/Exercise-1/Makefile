# Compiler and flags
CC = gcc
CFLAGS = 

# Target executable
TARGET = exercise_1

# Source files
SRC = exercise_1.c

# Default rule
all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) -lpthread

run: $(TARGET)
	python3 script.py
	
# Clean up build files
clean:
	rm -f $(TARGET) *.o