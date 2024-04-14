.PHONY : all

simple:
	${CC} -o simple ${CFLAGS} simple.c -g

simple2:
	${CC} simple.c -g -o simple

load:
	${CC} load.c -g -o load -O3

loadpg:
	${CC} load.c -g -o load -O3 -pg -lprofiler

clean:
	rm -f load loadpq simple simpe2