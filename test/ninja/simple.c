int test() {
	return 1;
}

int test2(int a) {
	return a + 1;
}

int main() {
	return test() + test2(2);
}
