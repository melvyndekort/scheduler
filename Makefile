.PHONY: clean install update-deps test build full-build pylint dev run scheduler
.DEFAULT_GOAL: build

clean:
	@rm -rf .pytest_cache dist __pycache__ */__pycache__

install: clean
	@poetry install

update-deps:
	@poetry update

test: install
	@poetry run pytest

build: test
	@poetry build

full-build: clean
	@docker image build -t scheduler .

pylint:
	@poetry run pylint scheduler

dev: install
	@CONFIG=tests/config.yml poetry run python3 -m scheduler.flask

run: install
	@CONFIG=tests/config.yml poetry run gunicorn -b 0.0.0.0:8000 --access-logfile '-' --error-logfile '-' scheduler.flask:app

scheduler: install
	@CONFIG=tests/config.yml poetry run python3 -m scheduler.main
