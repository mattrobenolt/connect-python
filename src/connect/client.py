import gzip
import json
import struct
from enum import Flag, IntEnum


class EnvelopeFlags(Flag):
    compressed = 0b00000001
    end_stream = 0b00000010


class Code(IntEnum):
    canceled = 408
    unknown = 500
    invalid_argument = 400
    deadline_exceeded = 408
    not_found = 404
    already_exists = 409
    permission_denied = 403
    resource_exhausted = 429
    failed_precondition = 412
    aborted = 409
    out_of_range = 400
    unimplemented = 404
    internal = 500
    unavailable = 503
    data_loss = 500
    unauthenticated = 401


class Error(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


envelope_header_length = 5
envelope_header_pack = ">BI"

_default_connection_pool = None


def default_connection_pool():
    global _default_connection_pool
    if _default_connection_pool is None:
        import httpcore

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
        error = json.loads(http_resp.content)
    except (json.decoder.JSONDecodeError, KeyError):
        print(http_resp.content)
        return Error(Code(http_resp.status), http_resp.reason)
    else:
        return make_error(error)


def make_error(error):
    try:
        code = Code[error["code"]]
    except KeyError:
        code = Code.unknown
    return Error(code, error.get("message", ""))


class GzipCompressor:
    name = "gzip"
    decompress = gzip.decompress
    compress = gzip.compress


class Client:
    def __init__(self, *, pool, url, response_type, compressor=None):
        if pool is None:
            pool = default_connection_pool()

        self.pool = pool
        self.url = url
        self._response_type = response_type
        self._compressor = compressor

    def call_unary(self, req):
        data = req.SerializeToString()

        if self._compressor is not None:
            data = self._compressor.compress(data)

        http_resp = self.pool.request(
            "POST",
            self.url,
            content=data,
            headers={
                "connect-protocol-version": "1",
                "content-encoding": "identity"
                if self._compressor is None
                else self._compressor.name,
                "content-type": "application/proto",
            },
        )

        if http_resp.status != 200:
            raise error_for_response(http_resp)

        resp = self._response_type()
        resp.ParseFromString(http_resp.content)
        return resp

    def call_server_stream(self, req):
        data = req.SerializeToString()
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
            headers={
                "connect-protocol-version": "1",
                "connect-content-encoding": "identity"
                if self._compressor is None
                else self._compressor.name,
                "content-type": "application/connect+proto",
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
                    resp = self._response_type()
                    resp.ParseFromString(buffer)
                    yield resp

                    buffer = buffer[data_len:]
                    needs_header = True
