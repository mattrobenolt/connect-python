# Code generated by protoc-gen-connect-python 0.1.0.dev2, DO NOT EDIT.
import connect

from elizav1 import eliza_pb2 as elizav1_dot_eliza__pb2
from mattv1 import matt_pb2 as mattv1_dot_matt__pb2

MattServiceName = "matt.v1.MattService"
OtherServiceName = "matt.v1.OtherService"


class MattServiceClient:
    def __init__(self, base_url, *, pool=None, compressor=None, json=False, **opts):
        self._hey = connect.Client(
            pool=pool,
            url=f"{base_url}/{MattServiceName}/Hey",
            response_type=mattv1_dot_matt__pb2.HeyResponse,
            compressor=compressor,
            json=json,
            **opts
        )
        self._say = connect.Client(
            pool=pool,
            url=f"{base_url}/{MattServiceName}/Say",
            response_type=elizav1_dot_eliza__pb2.SayResponse,
            compressor=compressor,
            json=json,
            **opts
        )

    def hey(self, req, **opts):
        return self._hey.call_unary(req, **opts)

    def say(self, req, **opts):
        return self._say.call_unary(req, **opts)


class OtherServiceClient:
    def __init__(self, base_url, *, pool=None, compressor=None, json=False, **opts):
        pass
