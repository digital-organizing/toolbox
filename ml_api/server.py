import asyncio
from collections.abc import Coroutine
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import logging
import os
import signal
import socket
from functools import partial
from io import BytesIO
import sys
import traceback

import click
from django.db import connections
import joblib
from cryptography.fernet import InvalidToken
from django.conf import settings

from ml_api.api import HANDLERS, ErrorResult
from ml_api.connection import gen_key, receive_command, send_close, send_result

LOG = logging.getLogger('server')


def shutdown(server, signum):
    """Gracefully shut the server down."""
    LOG.info('%s, shutting down', signal.strsignal(signum))
    server.shutdown()


class Server:
    """TCP Server that allows clients to connect to the database.

    Receives commands, executes them on the database and sends the result back.

    """

    def __init__(self, host: str, port: int, secret):
        """Define the host and port where the server will listen."""
        self.host = host
        self.port = port
        self.server = None
        self.secret = gen_key(secret)
        self.process_pool = ProcessPoolExecutor()
        self.thread_pool = ThreadPoolExecutor()

    async def _next_command(self, reader, writer):
        try:
            return await receive_command(reader, self.secret)
        except InvalidToken:
            LOG.error('Invalid token received, closing connection.')
            await send_close(writer)
            writer.close()
            return None

    async def connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handles a single incoming connection asynchronously"""
        LOG.debug('New connection established.')

        LOG.debug('Waiting for command')
        command = await self._next_command(reader, writer)

        LOG.debug('Command received: %s', command)

        while command is not None:
            try:
                result = HANDLERS[command.name](command, self)

                if isinstance(result, Coroutine):
                    result = await result

                LOG.debug(f'Sending result {result} to')

                await send_result(writer, result, self.secret)
                LOG.debug('Sent result to client.')

            except Exception as e:
                LOG.error(e)
                traceback.print_exc(file=sys.stderr)
                await send_result(writer, ErrorResult(str(e)), self.secret)
            LOG.debug('Waiting for command')
            command = await self._next_command(reader, writer)

        writer.close()
        await writer.wait_closed()

    async def create_server(self):
        """Creates the server socket but doesn't start listening yet."""
        self.server = await asyncio.start_server(self.connection, self.host, self.port)

        for server_socket in self.server.sockets:
            host, port = socket.getnameinfo(server_socket.getsockname(),
                                            socket.NI_NUMERICSERV | socket.NI_NUMERICHOST)
            LOG.info('Serving on %s:%s', host, port)
            self.host = host
            self.port = int(port)

    def shutdown(self):
        """Gracefully terminate the database server."""
        print("Called server close")
        if self.server:
            self.process_pool.shutdown(wait=True)
            self.thread_pool.shutdown(wait=True)
            self.server.close()
        print("Server shtudown")

    async def start(self, callback=None):
        """Start the server and process incoming connections.

        The callback is called shortly before the server starts listening, you can use it to notify
        clients that the server is listening, so they can connect without an error.
        """
        if self.server is None:
            await self.create_server()

        assert self.server is not None

        async with self.server:
            loop = asyncio.get_running_loop()
            if callback is not None:
                loop.call_soon(callback)

            await self.server.start_serving()
            await self.server.wait_closed()

        connections.close_all()
        print("Closed connections")


async def serve(host=None, port=None, secret=None):
    """Main method for the server thread."""

    if host is None:
        host = settings.API_HOST
    if port is None:
        port = settings.API_PORT
    if secret is None:
        secret = settings.API_SECRET

    loop = asyncio.get_running_loop()
    server = Server(host=host, port=port, secret=secret)

    for signum in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(signum, partial(shutdown, server, signum))

    await server.start()


@click.command()
@click.option('--address', default=None)
@click.option('--port', default=None)
@click.option('--loglevel', default="WARN")
def main(address, port, loglevel):

    if address is None:
        address = os.environ.get('API_HOST')
    if port is None:
        port = os.environ.get('API_PORT')

    return asyncio.run(serve(address, port, os.environ.get('API_SECRET')),
                       debug=loglevel.upper() == 'DEBUG')


if __name__ == '__main__':
    main()
