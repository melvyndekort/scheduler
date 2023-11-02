.PHONY = clean install test build full-build dev
.DEFAULT_GOAL := build

clean:
	@rm -rf .pytest_cache dist __pycache__ */__pycache__

install:
	@poetry install

test: install
	@poetry run pytest

build: test
	@poetry build

full-build:
	@docker image build -t job-scheduler .

dev:
	@poetry run flask --app job_scheduler.main run --debug

run:
	@poetry run gunicorn -w 2 --threads 2 -b 0.0.0.0 'job_scheduler.main:app' --access-logfile -
