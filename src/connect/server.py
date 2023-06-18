class Handler:
    def __init__(self, routes):
        self.routes = routes

    def __call__(self, environ, start_response):
        try:
            handler = self.routes[environ["PATH_INFO"]]
        except KeyError:
            return not_found_handler(environ, start_response)
        return handler(environ, start_response)


class UnaryHandler:
    def __init__(self, cb, *, request_type):
        self.cb = cb
        self.request_type = request_type

    def __call__(self, environ, start_response):
        print("called unary handler")
        # req = Request(environ)
        # resp = Response(req, start_response)
        content_type = environ["CONTENT_TYPE"]
        content_length = int(environ["CONTENT_LENGTH"])
        print(f"{content_type=}")
        print(f"{content_length=}")
        request_body = environ["wsgi.input"].read(content_length)
        message = self.request_type()
        message.ParseFromString(request_body)
        print(f"{message=}")
        resp = self.cb(message)
        start_response("200", [("content-type", "application/proto")])
        return [resp.SerializeToString()]


class ClientStreamHandler:
    def __init__(self, *args, **kwargs):
        def __call__(self, environ, start_response):
            raise NotImplementedError("not immplemented")


class ServerStreamHandler:
    def __init__(self, *args, **kwargs):
        def __call__(self, environ, start_response):
            raise NotImplementedError("not immplemented")


class BidiStreamHandler:
    def __init__(self, *args, **kwargs):
        def __call__(self, environ, start_response):
            raise NotImplementedError("not immplemented")


# def not_implemented_handler(environ, start_response):
#     start_response("405", [("content-type", "text/plain")])
#     return [b"method not allowed\n"]


def not_found_handler(environ, start_response):
    start_response("404", [("content-type", "text/plain")])
    return [b"not found\n"]


def method_not_allowed_handler(environ, start_response):
    start_response("405", [("content-type", "text/plain")])
    return [b"method not allowed\n"]
