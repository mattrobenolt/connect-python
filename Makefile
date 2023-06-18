fmt:
	python -m black run.py connect
	python -m isort run.py connect

lint:
	python -m ruff connect

.PHONY: fmt lint
