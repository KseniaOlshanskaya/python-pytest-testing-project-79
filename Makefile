install:
	uv sync

build:
	./build.sh

package-install:
	uv tool install dist/hexlet-code.whl

lint:
	uv run flake8 page_analyzer