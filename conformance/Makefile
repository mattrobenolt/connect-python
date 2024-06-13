clean:
	rm -rf gen

protoc-gen-connect-python:
	$(MAKE) -C .. bin/protoc-gen-connect-python

proto: protoc-gen-connect-python
	buf generate -v buf.build/connectrpc/conformance:v1.0.2

.PHONY: clean proto protoc-gen-connect-python
