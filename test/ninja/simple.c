#include <stdio.h>

int test() {
	return 1;
}

int test2(int a) {
	return a + 1;
}

int main() {
    printf("test\n");
	return test() + test2(2) ;
}
