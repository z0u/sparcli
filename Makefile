.PHONY:
	test
	lint
	format

all:
	@make test
	@make lint

test:
	poetry run pytest -v

lint:
	poetry run black --check --diff sparcli tests
	poetry run flake8 sparcli tests

format:
	poetry run black sparcli tests
