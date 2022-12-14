from contextlib import asynccontextmanager

from django.conf import settings

from ml_api.client import Client


@asynccontextmanager
async def connect():
    host, port, secret = settings.API_HOST, settings.API_PORT, settings.API_SECRET
    """Provides a context manager for a client connection to host and port"""
    client = Client(host, port, secret)
    await client.connect()
    try:
        yield client
    finally:
        await client.quit()
