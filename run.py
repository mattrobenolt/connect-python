import sys

sys.path.insert(0, ".")

import httpcore

import connect
from connectgen import eliza_pb2

ElizaServiceName = "buf.connect.demo.eliza.v1.ElizaService"


class ElizaServiceClient:
    def __init__(self, pool, base_url, *, compressor=None):
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


pool = httpcore.ConnectionPool(http2=True)

eliza_client = ElizaServiceClient(
    pool,
    "https://demo.connect.build",
    compressor=connect.GzipCompressor,
)
print(eliza_client.Say(eliza_pb2.SayRequest(sentence="hello")))

for resp in eliza_client.Introduce(eliza_pb2.IntroduceRequest(name="Matt")):
    print(resp)
