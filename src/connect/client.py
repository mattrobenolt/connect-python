import gzip
import json
import struct
import sys
import base64
import logging
from enum import Flag, IntEnum

import httpcore
from google.protobuf import json_format, descriptor_pool, message_factory

logger = logging.getLogger(__name__)


class EnvelopeFlags(Flag):
    compressed = 0b00000001
    end_stream = 0b00000010


class Code(IntEnum):
    canceled = 1
    unknown = 2
    invalid_argument = 3
    deadline_exceeded = 4
    not_found = 5
    already_exists = 6
    permission_denied = 7
    resource_exhausted = 8
    failed_precondition = 9
    aborted = 10
    out_of_range = 11
    unimplemented = 12
    internal = 13
    unavailable = 14
    data_loss = 15
    unauthenticated = 16


def http_to_code(code: int) -> Code:
    return {
        400: Code.internal,
        401: Code.unauthenticated,
        403: Code.permission_denied,
        404: Code.unimplemented,
        429: Code.unavailable,
        502: Code.unavailable,
        503: Code.unavailable,
        504: Code.unavailable,
    }.get(code, Code.unknown)


def connect_code_to_http(code: Code) -> int:
    return {
        Code.canceled: 499,
        Code.unknown: 500,
        Code.invalid_argument: 400,
        Code.deadline_exceeded: 504,
        Code.not_found: 404,
        Code.already_exists: 409,
        Code.permission_denied: 403,
        Code.resource_exhausted: 429,
        Code.failed_precondition: 400,
        Code.aborted: 409,
        Code.out_of_range: 400,
        Code.unimplemented: 501,
        Code.internal: 500,
        Code.unavailable: 503,
        Code.unauthenticated: 401,
    }.get(code, 500)


def decode_detail(detail):
    type_name = detail["type"]
    # XXX Python requires padding for base64 decoding, but it can be too much padding
    # so always appending `==` makes sure there's always enough padding.
    value = base64.b64decode(detail["value"] + "==")
    desc = descriptor_pool.Default().FindMessageTypeByName(type_name)
    msg = message_factory.GetMessageClass(desc)()
    msg.ParseFromString(value)
    logger.debug(f"decode_detail {type_name=} {desc=} {msg=}")
    return msg


class Error(Exception):
    def __init__(
        self,
        code: Code,
        *,
        message: str | None = None,
        details=None,
        headers=None,
        http_status_code: int | None = None,
    ):
        logger.debug(f"Error.init {code=} {message=} {details=}")
        self.code = code
        self.message = message
        if details is not None:
            self.details = list(map(decode_detail, details))
        else:
            self.details = []
        self.headers, self.trailers = split_headers_trailers(headers)
        self.http_status_code = http_status_code


envelope_header_length = 5
envelope_header_pack = ">BI"

_default_connection_pool = None


def default_connection_pool():
    global _default_connection_pool
    if _default_connection_pool is None:
        try:
            import h2  # noqa: F401

            http2 = True
            del h2
        except ModuleNotFoundError:
            http2 = False
        _default_connection_pool = httpcore.ConnectionPool(http2=http2)

    return _default_connection_pool


def encode_envelope(*, flags: EnvelopeFlags, data):
    return encode_envelope_header(flags=flags.value, data=data) + data


def encode_envelope_header(*, flags, data):
    return struct.pack(envelope_header_pack, flags, len(data))


def decode_envelope_header(header):
    flags, data_len = struct.unpack(envelope_header_pack, header)
    return EnvelopeFlags(flags), data_len


def error_for_response(http_resp):
    try:
        error = json.loads(http_resp.content) or {}
    except (json.decoder.JSONDecodeError, KeyError):
        return Error(
            http_to_code(http_resp.status),
            message=http_resp.extensions.get("reason_phrase"),
            headers=http_resp.headers,
            http_status_code=http_resp.status,
        )
    try:
        code = Code[error["code"]]
    except KeyError:
        code = http_to_code(http_resp.status)
    return Error(
        code,
        message=error.get("message", ""),
        details=error.get("details", None),
        headers=http_resp.headers,
        http_status_code=http_resp.status,
    )


def make_error(error):
    try:
        code = Code[error["code"]]
    except (KeyError, TypeError):
        code = Code.unknown
    return Error(
        code,
        message=error.get("message", ""),
        details=error.get("details", None),
    )


class GzipCompressor:
    name = "gzip"
    decompress = gzip.decompress
    compress = gzip.compress


class JSONCodec:
    content_type = "json"

    @staticmethod
    def encode(msg):
        return json_format.MessageToJson(msg).encode("utf8")

    @staticmethod
    def decode(data, *, msg_type):
        msg = msg_type()
        json_format.Parse(data.decode("utf8"), msg)
        return msg


class ProtobufCodec:
    content_type = "proto"

    @staticmethod
    def encode(msg):
        return msg.SerializeToString()

    @staticmethod
    def decode(data, *, msg_type):
        msg = msg_type()
        msg.ParseFromString(data)
        return msg


type Headers = dict[bytes | str, bytes | str]


def split_headers_trailers(headers):
    h = []
    t = []

    for key, value in headers or []:
        if key.lower().startswith(b"trailer-"):
            t.append((key[len("trailer-") :], value))
        else:
            h.append((key, value))
    return h, t


class Response:
    def __init__(self, msg, *, headers):
        self.msg = msg
        self.headers, self.trailers = split_headers_trailers(headers)
        logger.debug(f"Response {self.trailers=} {self.headers=}")


class Client:
    def __init__(
        self,
        url,
        *,
        pool,
        response_type,
        compressor=None,
        json=False,
        headers: Headers | None = None,
    ):
        if pool is None:
            pool = default_connection_pool()

        self.pool = pool
        self.url = url
        self._codec = JSONCodec if json else ProtobufCodec
        self._response_type = response_type
        self._compressor = compressor
        self._headers: dict[bytes | str, bytes | str] = {"user-agent": "connect-python"}
        if headers:
            self._headers |= headers

    def call_unary(
        self,
        req,
        *,
        timeout: float | None = None,
        headers: Headers | None = None,
        **opts,
    ) -> Response:
        data = self._codec.encode(req)
        logger.debug(f"call_unary.started {self.url=} {data=} {opts=}")

        if self._compressor is not None:
            data = self._compressor.compress(data)

        extensions = {}
        http_headers: Headers = self._headers.copy()

        if headers:
            http_headers |= headers

        http_headers |= {
            "connect-protocol-version": "1",
            "content-encoding": "identity"
            if self._compressor is None
            else self._compressor.name,
            "content-type": f"application/{self._codec.content_type}",
        }

        if timeout:
            extensions["timeout"] = {"read": timeout}
            http_headers["connect-timeout-ms"] = str(int(timeout * 1000))

        try:
            http_resp = self.pool.request(
                "POST",
                self.url,
                content=data,
                headers=http_headers,
                extensions=extensions,
            )
        except httpcore.TimeoutException:
            raise Error(Code.deadline_exceeded)

        logger.debug(
            f"call_unary.ended {http_resp.status=} {http_resp.content=} {http_resp.headers=}"
        )

        if http_resp.status != 200:
            raise error_for_response(http_resp)

        return Response(
            self._codec.decode(
                http_resp.content,
                msg_type=self._response_type,
            ),
            headers=http_resp.headers,
        )

    def call_server_stream(self, req, **opts):
        data = self._codec.encode(req)
        flags = EnvelopeFlags(0)

        if self._compressor is not None:
            data = self._compressor.compress(data)
            flags |= EnvelopeFlags.compressed

        with self.pool.stream(
            "POST",
            self.url,
            content=encode_envelope(
                flags=flags,
                data=data,
            ),
            headers=self._headers
            | opts.get("headers", {})
            | {
                "connect-protocol-version": "1",
                "connect-content-encoding": "identity"
                if self._compressor is None
                else self._compressor.name,
                "content-type": f"application/connect+{self._codec.content_type}",
            },
        ) as http_resp:
            if http_resp.status != 200:
                raise error_for_response(http_resp)

            buffer = b""
            end_stream = False
            needs_header = True
            flags, data_len = 0, 0

            for chunk in http_resp.iter_stream():
                buffer += chunk

                if needs_header:
                    header = buffer[:envelope_header_length]
                    buffer = buffer[envelope_header_length:]
                    flags, data_len = decode_envelope_header(header)
                    needs_header = False
                    end_stream = EnvelopeFlags.end_stream in flags

                if len(buffer) >= data_len:
                    buffer = buffer[:data_len]

                    if end_stream:
                        data = json.loads(buffer)
                        if "error" in data:
                            raise make_error(data["error"])

                        # TODO: Figure out what else might be possible
                        return

                    # TODO: handle server message compression
                    # if EnvelopeFlags.compression in flags:
                    # TODO: should the client potentially use a different codec
                    # based on response header? Or can we assume they're always
                    # the same and an error otherwise.
                    yield self._codec.decode(buffer, msg_type=self._response_type)

                    buffer = buffer[data_len:]
                    needs_header = True

    def call_client_stream(self, req, **opts):
        raise NotImplementedError("client stream not supported")

    def call_bidi_stream(self, req, **opts):
        raise NotImplementedError("bidi stream not supported")
