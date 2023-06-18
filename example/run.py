import sys

sys.path.insert(0, ".")

import connect
from elizav1 import eliza_connect, eliza_pb2

eliza_client = eliza_connect.ElizaServiceClient(
    "https://demo.connect.build",
    compressor=connect.GzipCompressor,
)
print(eliza_client.Say(eliza_pb2.SayRequest(sentence="hello")))

for resp in eliza_client.Introduce(eliza_pb2.IntroduceRequest(name="Matt")):
    print(resp)
