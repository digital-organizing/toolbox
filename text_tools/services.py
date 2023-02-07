from urllib import response

import aiohttp
from bs4 import BeautifulSoup
from parsel import Selector
from transformers import GPT2Tokenizer

from text_tools.models import UrlField

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')


def count_tokens(text: str) -> int:
    """Count tokens in given text."""
    return len(tokenizer(text)['input_ids'])


async def extract_url(url: str, field: UrlField) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            return extract_document(text, field)


def extract_document(text: str, field: UrlField) -> str:

    selector = Selector(text)
    texts = [BeautifulSoup(e.extract(), 'lxml').text for e in selector.xpath(field.xpath)]

    return '\n'.join(filter(lambda text: len(text) > field.min_length, texts))
