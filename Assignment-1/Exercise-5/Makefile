# Compiler and flags
CC = gcc
CFLAGS =  #-Wall -O2 -pthread

# Target executable
TARGET1 = exercise_5_1
TARGET2 = exercise_5_2
TARGET3 = exercise_5_3


# Source files
SRC1 = exercise_5_1.c
SRC2 = exercise_5_2.c
SRC3 = exercise_5_3.c

# Default rule
all: $(TARGET1) $(TARGET2) $(TARGET3)

$(TARGET1): $(SRC1)
	$(CC) $(CFLAGS) -o $(TARGET1) $(SRC1) -lpthread
	$(CC) $(CFLAGS) -o $(TARGET2) $(SRC2) -lpthread
	$(CC) $(CFLAGS) -o $(TARGET3) $(SRC3) -lpthread

run: $(TARGET1)
	./$(TARGET1) 4 1000
	./$(TARGET2) 4 1000
	./$(TARGET3) 4 1000

# Clean up build files
clean:
	rm -f $(TARGET1) $(TARGET2) $(TARGET3) *.o