from typing import cast
from django.conf import settings

from django.test import TestCase

from ml_api.api import HANDLERS, ListCommand, ListResult
from ml_api.client import Client
from ml_api.django import connect
from ml_api.models.sbert import (
    SentenceEmbeddingCommand,
    SentenceEmbeddingResult,
    sentence_embedding,
)


class ServiceTest(TestCase):

    async def test_connect_api_server(self):
        command = ListCommand()

        async with connect() as client:
            result = await client.send_command(command)
            assert isinstance(result, ListResult)
            assert isinstance(result.handlers, list)
            assert result.handlers == list(HANDLERS.keys())

    def test_sbert(self):
        embeddings = sentence_embedding(
            SentenceEmbeddingCommand('distiluse-base-multilingual-cased-v1', ['Hello World']))
        embeddings = cast(SentenceEmbeddingResult, embeddings)
        assert len(embeddings.embeddings) == 1

    async def test_many_clients(self):
        clients = []
        for _ in range(100):
            clients.append(Client(settings.API_HOST, settings.API_PORT, settings.API_SECRET))
            await clients[-1].connect()

        for c in clients:
            await c.send_command(ListCommand())
