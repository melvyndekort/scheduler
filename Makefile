.PHONY: clean install test build full-build dev run scheduler
.DEFAULT_GOAL: build

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
	@CONFIG=tests/config.yml poetry run python3 -m scheduler.flask
#@CONFIG=tests/config.yml poetry run flask --app scheduler.flask run --debug

run:
	@CONFIG=tests/config.yml poetry run gunicorn -b 0.0.0.0:8000 --access-logfile '-' --error-logfile '-' scheduler.flask:app

scheduler:
	@CONFIG=tests/config.yml poetry run python3 -m scheduler.main
