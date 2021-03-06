"""
Ann example of chaining middleware.
"""

import logging

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    text_writer,
    HttpResponse,
    HttpRequestCallback
)

logging.basicConfig(level=logging.DEBUG)


async def first_middleware(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content,
        handler: HttpRequestCallback
) -> HttpResponse:
    """The first part of a middleware chain"""
    info['message'] = 'This is first the middleware. '
    status, headers, content, pushes = await handler(scope, info, matches, content)
    return status, headers, content, pushes


async def second_middleware(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content,
        handler: HttpRequestCallback
) -> HttpResponse:
    """The second part of a middleware chain"""
    info['message'] += 'This is the second middleware.'
    response = await handler(scope, info, matches, content)
    return response


# pylint: disable=unused-argument
async def http_request_callback(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """The final request handler"""
    return 200, [(b'content-type', b'text/plain')], text_writer(info['message'])


if __name__ == "__main__":
    import uvicorn

    app = Application(middlewares=[first_middleware, second_middleware])
    app.http_router.add({'GET', 'POST', 'PUT', 'DELETE'},
                        '/{path}', http_request_callback)

    uvicorn.run(app, port=9009)
