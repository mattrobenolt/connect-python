fmt:
	python -m black src
	python -m isort src

lint:
	python -m ruff src

.PHONY: fmt lint
