.PHONY:
	test
	lint
	scan
	build
	publish
	format

all:
	@make test
	@make lint
	@make scan
	@make build

init:
	poetry run pip install --upgrade pip setuptools
	poetry install

test:
	poetry run pytest -v

lint:
	poetry run black --check --diff sparcli tests
	poetry run flake8 sparcli tests
	find . -iname '*.yml' -o -iname '*.yaml' | xargs poetry run yamllint

scan:
	poetry run safety check
	poetry run bandit -s B101 -r sparcli

build:
	poetry build

publish: build
	poetry publish

format:
	poetry run black sparcli tests
