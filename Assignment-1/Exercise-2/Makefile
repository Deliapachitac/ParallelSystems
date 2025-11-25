# Compiler and flags
CC = gcc
CFLAGS =  #-Wall -O2 -pthread

# Target executable
TARGET1 = mutex
TARGET2 = rwlock
TARGET3 = atomic

# Source files
SRC1 = mutex.c
SRC2 = rwlock.c
SRC3 = atomic.c

# Default rule1
all: $(TARGET1)

$(TARGET1): $(SRC1)
	$(CC) $(CFLAGS) -o $(TARGET1) $(SRC1)
	$(CC) $(CFLAGS) -o $(TARGET2) $(SRC2)
	$(CC) $(CFLAGS) -o $(TARGET3) $(SRC3)

# Run example (4 threads, 1000 iterations)
run: 
	./$(TARGET1) 4 1000
	./$(TARGET2) 4 1000
	./$(TARGET3) 4 1000

# Clean up build files
clean:
	rm -f $(TARGET1) $(TARGET2) $(TARGET3) *.o