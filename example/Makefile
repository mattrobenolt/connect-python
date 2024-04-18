fmt:
	python -m ruff format *.py

lint:
	python -m ruff check *.py

protoc-gen-connect-python:
	$(MAKE) -C .. bin/protoc-gen-connect-python

proto: protoc-gen-connect-python
	buf generate -v

.PHONY: fmt lint proto protoc-gen-connect-python
