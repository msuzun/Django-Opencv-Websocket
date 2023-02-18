# Django Channels Example

This is an example app demonstrating how to use (and deploy) [Django Channels](http://channels.readthedocs.org/en/latest/). It's a simple real-time chat app — like a very, very light-weight Slack. There are a bunch of rooms, and everyone in the same room can chat, in real-time, with each other (using WebSockets).

## Running locally



Then, to run:

- Install requirements: `pip install -r requirements.txt` (you almost certainly want to do this in a virtualenv).
- Migrate: `DATABASE_URL=postgres:///... python manage.py migrate`
- Or, to run locally with multiple proceses by setting the environ, then running the two commands (`daphne` and `runworker`) as shown in the `Procfile`.

What is ``websockets``?
-----------------------

websockets is a library for building WebSocket_ servers and clients in Python
with a focus on correctness, simplicity, robustness, and performance.

WebSocket: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

Built on top of ``asyncio``, Python's standard asynchronous I/O framework, it
provides an elegant coroutine-based API.

`Documentation is available on Read the Docs. <https://websockets.readthedocs.io/>`_

Here's how a client sends and receives messages:



    #!/usr/bin/env python

    import asyncio
    from websockets import connect

    async def hello(uri):
        async with connect(uri) as websocket:
            await websocket.send("Hello world!")
            await websocket.recv()

    asyncio.run(hello("ws://localhost:8765"))

And here's an echo server:



    #!/usr/bin/env python

    import asyncio
    from websockets import serve

    async def echo(websocket):
        async for message in websocket:
            await websocket.send(message)

    async def main():
        async with serve(echo, "localhost", 8765):
            await asyncio.Future()  # run forever

    asyncio.run(main())
