CC = g++
CFLAGS = -std=c++17 -w -O2
LIBS =

# List of source files
SRCS = main.cpp MCMC.cpp helpers.cpp

# List of object files (one for each source file)
OBJS = $(SRCS:.cpp=.o)

# Main target
main: $(OBJS)
	$(CC) $(CFLAGS) -o main $(OBJS) $(LIBS)

# Rule to compile source files into object files
main.o: main.cpp MCMC.h helpers.h
	$(CC) $(CFLAGS) -c main.cpp -o main.o

MCMC.o: MCMC.cpp MCMC.h
	$(CC) $(CFLAGS) -c MCMC.cpp -o MCMC.o

helpers.o: helpers.cpp helpers.h
	$(CC) $(CFLAGS) -c helpers.cpp -o helpers.o

clean:
	rm -f main $(OBJS)