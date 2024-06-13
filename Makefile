VIRTUALENV=.venv
PY=$(VIRTUALENV)/bin/python3 -m

plugin = protoc-gen-connect-python

all: bin/$(plugin)

dev: venv
venv: $(VIRTUALENV)/pyvenv.cfg

$(VIRTUALENV)/pyvenv.cfg: requirements-dev.txt pyproject.toml
	/usr/bin/env python3 -m venv .venv
	$(PY) pip install -r requirements-dev.txt

fmt: venv
	$(PY) ruff format src conformance/run.py
	$(PY) ruff check --fix --select I src conformance/run.py

lint: venv
	$(PY) ruff check src

clean:
	rm -f bin/protoc-gen-connect-python
	rm -rf dist

upload: venv clean
	$(PY) build
	$(PY) twine upload --repository=connect-python dist/*

runconformance: bin/connectconformance venv
	bin/connectconformance --vv --trace --mode client --conf conformance/config.yaml -- $(PY) conformance.runner

bin/connectconformance: Makefile
	env GOBIN=$(abspath bin) go install connectrpc.com/conformance/cmd/connectconformance@v1.0.2

bin/$(plugin): $(wildcard cmd/$(plugin)/*.go) pyproject.toml Makefile go.mod go.sum
	go build -o $@ \
	  -ldflags "-w -s" \
	  ./cmd/$(plugin)

.PHONY: dev fmt lint upload clean
