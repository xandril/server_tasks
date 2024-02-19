from aiohttp import web


async def handler(request: web.Request) -> web.Response:
    return web.Response(text="b")


async def init_app() -> web.Application:
    app = web.Application()
    app.add_routes([web.get("/get_char", handler)])
    return app


if __name__ == '__main__':
    web.run_app(init_app(), port=4080, host='127.0.0.1')
