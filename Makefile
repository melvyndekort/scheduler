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
	@docker image build -t scheduler .

dev:
	@CONFIG=config.yml poetry run flask --app scheduler.main run --debug

run:
	@CONFIG=config.yml poetry run gunicorn --threads 4 --bind 0.0.0.0 --access-logfile - 'scheduler.main:app'
