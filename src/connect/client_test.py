import dataclasses
from typing import List, Tuple

import pytest

from connect.client import split_headers_trailers


@dataclasses.dataclass
class Case:
    input: List[Tuple[bytes, bytes]] | None
    headers: List[Tuple[bytes, bytes]]
    trailers: List[Tuple[bytes, bytes]]


@pytest.mark.parametrize(
    "case",
    [
        Case(
            input=[(b"foo", b"bar")],
            headers=[(b"foo", b"bar")],
            trailers=[],
        ),
        Case(
            input=[(b"trailer-x", b"bar"), (b"foo", b"bar")],
            headers=[(b"foo", b"bar")],
            trailers=[(b"x", b"bar")],
        ),
        Case(
            input=[(b"Trailer-X-Foo", b"foo-trailer"), (b"trailermaybe", b"notreally")],
            headers=[(b"trailermaybe", b"notreally")],
            trailers=[(b"X-Foo", b"foo-trailer")],
        ),
        Case(
            input=None,
            headers=[],
            trailers=[],
        ),
    ],
)
def test_split_headers_trailers(case: Case):
    headers, trailers = split_headers_trailers(case.input)
    assert headers == case.headers, "headers"
    assert trailers == case.trailers, "trailers"
