.PHONY: clean install update-deps test build full-build pylint dev run scheduler
.DEFAULT_GOAL: build

clean:
	@rm -rf .pytest_cache dist __pycache__ */__pycache__

install: clean
	@uv sync --all-extras

update-deps:
	@uv sync --upgrade --all-extras

test: install
	@uv run pytest

build: test
	@uv build

full-build: clean
	@docker image build -t scheduler .

pylint:
	@uv run pylint scheduler

dev: install
	@CONFIG=tests/config.yml uv run python3 -m scheduler.flask

run: install
	@CONFIG=tests/config.yml uv run gunicorn -b 0.0.0.0:8000 --access-logfile '-' --error-logfile '-' scheduler.flask:app

scheduler: install
	@CONFIG=tests/config.yml uv run python3 -m scheduler.main
