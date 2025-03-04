build:
	cd test_runner && docker build -f Dockerfile.subinterpreters -t test_runner_subinterpreters . --build-arg PYTHON_VERSION=3.13.2
	cd test_runner && docker build -f Dockerfile.freethreading -t test_runner_freethreading . --build-arg PYTHON_VERSION=3.13.2

clean:
	rm -r output/*

server:
	uv run prefect server start

run:
	uv run workflow.py
