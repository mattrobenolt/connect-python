fmt:
	python -m black run.py src
	python -m isort run.py src

lint:
	python -m ruff src

proto:
	buf generate -v

.PHONY: fmt lint proto
