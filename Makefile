install:
	poetry install

test:
	@poetry run pytest

test-cov:
	poetry run pytest --cov

test-coverage:
	poetry run pytest --cov=page_loader --cov-report xml

lint:
	@poetry run flake8 page_loader
	@poetry run flake8 tests

selfcheck:
	poetry check

check:
	make lint
	make test

build:
	poetry build

run:
	poetry run page_loader/scripts/main.py -o tmp $(ARGS)

install-dist:
	python3 -m pip install --force-reinstall --user $$(ls -t dist/*.whl | head -n 1)

.PHONY: install test test-cov test-coverage lint selfcheck check build run install-dist