import pytest
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_writer
)
from .mock_io import MockIO


@pytest.mark.asyncio
async def test_get_text_plain():
    async def http_request_callback(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')


    app = Application()
    app.http_router.add({'GET'}, '/{path}', http_request_callback)

    instance = app({
        'type': 'http',  # Optional but not empty: 'http' or 'https'.
        'http_version': '1.1',  # One of: '1.0', '1.1', '2'.
        'method': 'GET',  # Always uppercase.
        'scheme': 'http',  # Optional, but not empty.
        'path': '/foo',  # Decoded
        'query_string': b'',
        'root_path': "",
        'headers': [(b'accept', b'text/plain')],  # Headers must be lower cased.
        'client': ('127.0.0.1', 36432),  # Optional, defaults to None.
        'server': ('127.0.0.1', 5000),  # Optional, defaults to None.
    })

    io = MockIO()
    await io.write({
        'type': 'http.request',
        'body': b'',
        'more_body': False,
    })
    await instance(io.receive, io.send)

    start_response = await io.read()
    assert start_response['type'] == 'http.response.start'
    assert start_response['status'] == 200
    assert start_response['headers'] == [(b'content-type', b'text/plain')]

    body_response = await io.read()
    assert body_response['type'] == 'http.response.body'
    assert body_response['body'].decode() == "This is not a test"
    assert body_response['more_body'] == False