import sys
from pathlib import Path

proto_folder = Path(".") / "gen"

sys.path.append(str(proto_folder.absolute()))

from elizav1 import eliza_pb2
from mattv1 import matt_connect, matt_pb2


class server:
    def Hey(self, req):
        return matt_pb2.HeyResponse(message=f"Hey {req.name}")

    def Say(self, req):
        return eliza_pb2.SayResponse(sentence="I'm not Eliza")


from werkzeug.serving import run_simple

run_simple(
    "127.0.0.1",
    4000,
    matt_connect.NewMattServiceHandler(server()),
    use_debugger=True,
    use_reloader=True,
)
