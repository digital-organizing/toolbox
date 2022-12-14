from itertools import chain
import numpy as np
import logging
from nltk.tokenize import sent_tokenize
from functools import lru_cache
from typing import Any, Dict, List, cast

import sentence_transformers
from ml_api.api import register_handler
from ml_api.base_command import Command
from ml_api.base_result import Result

LOG = logging.getLogger('sbert')


class SentenceEmbeddingCommand(Command):
    name = 'sbert'

    def __init__(self, model, sentences) -> None:
        super().__init__()
        self.model = model
        self.sentences = [s for s in sentences if s]


class SentenceEmbeddingResult(Result):

    def __init__(self, embeddings) -> None:
        super().__init__()
        self.embeddings = embeddings

    def to_dict(self) -> Dict[str, Any]:
        return {
            'embeddings': self.embeddings,
        }


@lru_cache(10)
def load_model(name):
    return sentence_transformers.SentenceTransformer(name)


def split_sentences(documents):
    sentences: List[str] = [sent_tokenize(sentence) for sentence in documents]
    lengths = [len(sentence) for sentence in sentences]
    flat = chain.from_iterable(sentences)

    return list(flat), lengths


@register_handler('sbert')
def sentence_embedding(command: Command, _) -> SentenceEmbeddingResult:
    command = cast(SentenceEmbeddingCommand, command)
    LOG.debug("Loading model")
    model = load_model(command.model)
    LOG.debug("Generating encodings")
    flat, lengths = split_sentences(command.sentences)
    embeddings = model.encode(flat)
    result = []
    i = 0

    for length in lengths:
        result.append(np.mean(embeddings[i:i + length], axis=0))
        i += length

    return SentenceEmbeddingResult(result)
