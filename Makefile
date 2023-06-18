PY = python -m

dev:
	$(PY) pip install -r requirements-dev.txt

fmt:
	$(PY) black src
	$(PY) isort src

lint:
	$(PY) ruff src

clean:
	rm -f bin/protoc-gen-connect-python
	rm -rf dist

upload: clean
	$(PY) build
	$(PY) twine upload --repository=connect-python dist/*

bin/protoc-gen-connect-python: $(wildcard cmd/protoc-gen-connect-python/*.go)
	env GOBIN=$(PWD)/bin go install go.withmatt.com/connect-python/cmd/protoc-gen-connect-python

.PHONY: dev fmt lint upload clean
