.PHONY = clean install test build full-build
.DEFAULT_GOAL := build

clean:
	@rm -rf .pytest_cache dist */__pycache__ */*/__pycache__

install:
	@poetry install

test: install
	@poetry run pytest

build: test
	@poetry build

full-build:
	@docker image build -t job-scheduler .
