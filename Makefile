build:
	cd test_runner && docker build -f Dockerfile.subinterpreters -t test_runner_subinterpreters . --build-arg PYTHON_VERSION=3.13.0
	cd test_runner && docker build -f Dockerfile.freethreading -t test_runner_freethreading . --build-arg PYTHON_VERSION=3.13.0

clean:
	rm -r output/*
