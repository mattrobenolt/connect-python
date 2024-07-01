import connect
from elizav1 import eliza_connect, eliza_pb2
from mattv1 import matt_connect, matt_pb2

eliza_client = eliza_connect.ElizaServiceClient(
    "https://demo.connectrpc.com",
    compressor=connect.GzipCompressor,
    json=True,
)

resp = eliza_client.say(
    eliza_pb2.SayRequest(sentence="hello"),
    headers={"foo": "bar", "user-agent": "hello"},
)
print(resp, resp.headers, resp.trailers)

for resp in eliza_client.introduce(eliza_pb2.IntroduceRequest(name="Matt")):
    print(resp)

matt_connect.MattServiceClient("")
matt_connect.OtherServiceClient("")
