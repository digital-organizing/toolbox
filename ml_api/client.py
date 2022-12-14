import asyncio
from contextlib import asynccontextmanager
from typing import cast
from ml_api.api import ConnectCommand, ErrorResult

from ml_api.base_command import Command
from ml_api.base_result import Result
from ml_api.connection import gen_key, receive_result, send_close, send_command
from ml_api.models.sbert import (
    SentenceEmbeddingCommand,
    SentenceEmbeddingResult,
)


class Client:

    def __init__(self, host, port, secret) -> None:
        self.host = host
        self.port = port
        self.key = gen_key(secret)

    async def connect(self):
        """Connect to the server"""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        await self.send_command(ConnectCommand())

    async def send_command(self, command: Command) -> Result:
        await send_command(self.writer, command, self.key)
        result = await receive_result(self.reader, self.key)
        if isinstance(result, ErrorResult):
            raise result
        return result

    async def sentence_embeddings(self, model, texts) -> SentenceEmbeddingResult:
        return cast(
            SentenceEmbeddingResult,
            await self.send_command(SentenceEmbeddingCommand(model, texts)),
        )

    async def quit(self):
        await send_close(self.writer)


@asynccontextmanager
async def connect(host, port, secret):
    """Provides a context manager for a client connection to host and port"""
    client = Client(host, port, secret)
    await client.connect()
    try:
        yield client
    finally:
        await client.quit()
