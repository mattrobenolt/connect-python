import connect

from . import eliza_pb2

ElizaServiceName = "buf.connect.demo.eliza.v1.ElizaService"


class ElizaServiceClient:
    def __init__(self, base_url, *, pool=None, compressor=None):
        self._say = connect.Client(
            pool=pool,
            url=f"{base_url}/{ElizaServiceName}/Say",
            response_type=eliza_pb2.SayResponse,
            compressor=compressor,
        )
        self._introduce = connect.Client(
            pool=pool,
            url=f"{base_url}/{ElizaServiceName}/Introduce",
            response_type=eliza_pb2.IntroduceResponse,
            compressor=compressor,
        )

    def Say(self, req):
        return self._say.call_unary(req)

    def Introduce(self, req):
        return self._introduce.call_server_stream(req)
