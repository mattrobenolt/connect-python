fmt:
	python -m black run.py
	python -m isort run.py

lint:
	python -m ruff run.py

protoc-gen-connect-python:
	$(MAKE) -C .. bin/protoc-gen-connect-python

proto: protoc-gen-connect-python
	buf generate -v

.PHONY: fmt lint proto protoc-gen-connect-python
