# Makefile

install:
	poetry lock ;\
	poetry install


build:
	poetry build


package-install:
	uv tool install --reinstall --force dist/*.whl


lint:
	poetry run flake8 page_loader ;\
	poetry run flake8 tests

test-cov:
	poetry run pytest --cov=page_loader -vv --cov-report xml

test: # запуск pytest
	poetry run pytest -vv

.PHONY: install build publish package-install lint test test-cov