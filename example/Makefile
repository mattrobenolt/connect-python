files = $(wildcard *.py)

fmt:
	python -m black $(files)
	python -m isort $(files)

lint:
	python -m ruff $(files)

protoc-gen-connect-python:
	$(MAKE) -C .. bin/protoc-gen-connect-python

proto: protoc-gen-connect-python
	buf generate -v

.PHONY: fmt lint proto protoc-gen-connect-python
