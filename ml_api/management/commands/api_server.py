import asyncio
import logging
from logging import INFO, log
from typing import Any, Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from ml_api.server import serve


class Command(BaseCommand):
    help = 'Start api backend server'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('host', nargs=1, type=str)
        parser.add_argument('port', nargs=1, type=int)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        logging.basicConfig(level=logging.DEBUG)
        host = options.get('host')[0]
        port = options.get('port')[0]

        import nltk
        nltk.download('punkt')

        asyncio.run(serve(host, port, settings.API_SECRET), debug=settings.DEBUG)
