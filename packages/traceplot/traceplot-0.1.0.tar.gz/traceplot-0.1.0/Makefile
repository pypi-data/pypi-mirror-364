run:
	uv run python3 main.py
test:
	uv run coverage run -m pytest
lint:
	uv run ruff check
format:
	uv run ruff format
mypy:
	uv run mypy --strict .
check-all:
	make format
	make lint
	make mypy
coverage:
	uv run coverage report
	uv run coverage html
	uv run open tests/coverage-report/index.html
publish-test:
	uv build && uv publish --publish-url https://test.pypi.org/legacy/
publish:
	uv build && uv publish
