#!/usr/bin/env python3

import collections
import json
import logging
import re
import ssl
import struct
import sys
import time
from typing import Any, List, Tuple

import connect
import httpcore
from connectrpc.conformance.v1 import (
    client_compat_pb2,
    config_pb2,
    service_connect,
    service_pb2,
)
from google.protobuf import any_pb2, descriptor_pb2, json_format

logger = logging.getLogger("conformance.runner")


def read_request() -> client_compat_pb2.ClientCompatRequest | None:
    data = sys.stdin.buffer.read(4)
    if not data:
        return
    if len(data) < 4:
        raise Exception("short read (header)")
    ll = struct.unpack(">I", data)[0]
    msg = client_compat_pb2.ClientCompatRequest()
    data = sys.stdin.buffer.read(ll)
    if len(data) < ll:
        raise Exception("short read (request)")
    msg.ParseFromString(data)
    return msg


def write_response(msg: client_compat_pb2.ClientCompatResponse) -> None:
    data = msg.SerializeToString()
    ll = struct.pack(">I", len(data))
    sys.stdout.buffer.write(ll)
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()


def camelcase_to_snakecase(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def log_message(request: Any, response: Any):
    with open("messages.log", "a") as fp:
        json.dump(
            {
                "case": request.test_name,
                "request": json.loads(json_format.MessageToJson(request)),
                "response": json.loads(json_format.MessageToJson(response)),
            },
            fp=fp,
        )


def to_pb_headers(headers: List[Tuple[bytes, bytes]]) -> list[service_pb2.Header]:
    h_dict: dict[str, list[str]] = collections.defaultdict(list)
    for key, value in headers:
        h_dict[key.decode("utf8")].append(value.decode("utf8"))

    return [
        service_pb2.Header(
            name=key,
            value=values,
        )
        for key, values in h_dict.items()
    ]


def handle_message(
    msg: client_compat_pb2.ClientCompatRequest,
) -> client_compat_pb2.ClientCompatResponse:
    if msg.stream_type != config_pb2.STREAM_TYPE_UNARY:
        return client_compat_pb2.ClientCompatResponse(
            test_name=msg.test_name,
            error=client_compat_pb2.ClientErrorResult(
                message="TODO STREAM TYPE NOT IMPLEMENTED"
            ),
        )

    if msg.use_get_http_method:
        return client_compat_pb2.ClientCompatResponse(
            test_name=msg.test_name,
            error=client_compat_pb2.ClientErrorResult(
                message="TODO HTTP GET NOT IMPLEMENTED"
            ),
        )

    if len(msg.request_messages) > 1:
        return client_compat_pb2.ClientCompatResponse(
            test_name=msg.test_name,
            error=client_compat_pb2.ClientErrorResult(
                message="TODO MULTIPLE MESSAGES NOT IMPLEMENTED"
            ),
        )

    logger.debug(f"** {msg.test_name} **")
    # logger.debug(log_message(msg))
    any = msg.request_messages[0]
    logger.debug(f"{any.TypeName()=}")

    req_types = {
        "connectrpc.conformance.v1.UnaryRequest": service_pb2.UnaryRequest,
        "connectrpc.conformance.v1.UnimplementedRequest": service_pb2.UnimplementedRequest,
    }

    try:
        req_type = req_types[any.TypeName()]
    except KeyError:
        return client_compat_pb2.ClientCompatResponse(
            test_name=msg.test_name,
            error=client_compat_pb2.ClientErrorResult(
                message=f"TODO unknown message type: {any.TypeName()}"
            ),
        )

    req = req_type()
    any.Unpack(req)

    http1 = msg.http_version in [
        config_pb2.HTTP_VERSION_1,
        config_pb2.HTTP_VERSION_UNSPECIFIED,
    ]
    http2 = msg.http_version in [
        config_pb2.HTTP_VERSION_2,
        config_pb2.HTTP_VERSION_UNSPECIFIED,
    ]
    ssl_context = None
    if msg.server_tls_cert:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(cadata=msg.server_tls_cert.decode("utf8"))
        proto = "https"
    else:
        proto = "http"

    url = f"{proto}://{msg.host}:{msg.port}"

    if msg.request_delay_ms > 0:
        time.sleep(msg.request_delay_ms / 1000.0)

    with httpcore.ConnectionPool(
        http1=http1, http2=http2, ssl_context=ssl_context
    ) as pool:
        try:
            client = service_connect.ConformanceServiceClient(
                url,
                pool=pool,
            )
            resp = getattr(client, camelcase_to_snakecase(msg.method))(
                req,
                timeout=msg.timeout_ms / 1000,
                headers={h.name: ",".join(h.value) for h in msg.request_headers},
            )
            return client_compat_pb2.ClientCompatResponse(
                test_name=msg.test_name,
                response=client_compat_pb2.ClientResponseResult(
                    payloads=[resp.msg.payload],
                    http_status_code=200,
                    response_headers=to_pb_headers(resp.headers),
                    response_trailers=to_pb_headers(resp.trailers),
                ),
            )
        except connect.Error as e:
            return client_compat_pb2.ClientCompatResponse(
                test_name=msg.test_name,
                response=client_compat_pb2.ClientResponseResult(
                    error=service_pb2.Error(
                        code=getattr(config_pb2, f"CODE_{e.code.name.upper()}"),
                        message=e.message,
                        details=e.details,
                    ),
                    http_status_code=e.http_status_code,
                    response_headers=to_pb_headers(e.headers),
                    response_trailers=to_pb_headers(e.trailers),
                ),
            )
        except Exception as e:
            return client_compat_pb2.ClientCompatResponse(
                test_name=msg.test_name,
                error=client_compat_pb2.ClientErrorResult(message=str(e)),
            )


if __name__ == "__main__":
    if "--debug" in sys.argv:
        logging.basicConfig(level=logging.DEBUG)

    while req := read_request():
        resp = handle_message(req)
        log_message(req, resp)
        write_response(resp)
