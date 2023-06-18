import sys
from pathlib import Path

proto_folder = Path(".") / "gen"

sys.path.append(str(proto_folder.absolute()))

from elizav1 import eliza_connect, eliza_pb2
from mattv1 import matt_connect, matt_pb2

import connect

# eliza_client = eliza_connect.ElizaServiceClient(
#     # "https://demo.connect.build",
#     "http://127.0.0.1:4000",
#     compressor=connect.GzipCompressor,
# )
# print(eliza_client.Say(eliza_pb2.SayRequest(sentence="hello")))

# for resp in eliza_client.Introduce(eliza_pb2.IntroduceRequest(name="Matt")):
#     print(resp)

matt_client = matt_connect.MattServiceClient("http://127.0.0.1:4000")
print(matt_client.Hey(matt_pb2.HeyRequest(name="Matt")))
# matt_connect.OtherServiceClient("")