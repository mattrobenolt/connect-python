fmt:
	python -m black run.py
	python -m isort run.py

lint:
	python -m ruff run.py

proto:
	buf generate -v

.PHONY: fmt lint proto
