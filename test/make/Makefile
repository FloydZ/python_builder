.PHONY : all

simple:
	${CC} -o simple simple.c -g

simple2:
	${CC} simple.c -g -o simple

load:
	${CC} load.c -g -o load -O3

loadpg:
	clang load.c -g -o load -O3 -pg -lprofiler
