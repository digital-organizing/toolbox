import asyncio
from django.db import connection, connections
import numpy as np
from functools import lru_cache
from typing import cast
import logging

from sklearn.metrics import classification_report

from ml_api.api import register_handler
from ml_api.base_command import Command
from ml_api.base_result import Result
from ml_api.server import Server
from text_classifier.models import Classifier
from async_lru import alru_cache

LOG = logging.getLogger('classifier')


class ClassifierCommand(Command):
    name = 'classify'

    def __init__(self, pk, X) -> None:
        super().__init__()
        self.X = X
        self.pk = pk


class EvaluateClassifier(Command):
    name = 'evaluate-classifier'

    def __init__(self, pk, X, y, names) -> None:
        super().__init__()
        self.pk = pk
        self.X = X
        self.y = y
        self.names = names


class Classification(Result):

    def __init__(self, y, probs) -> None:
        super().__init__()
        self.y = y
        self.probs = probs

    def to_dict(self):
        return {
            'y': self.y,
            'probabilities': self.probs,
        }


class ClassifierReport(Result):

    def __init__(self, score) -> None:
        super().__init__()
        self.score = score

    def to_dict(self):
        return self.score


@alru_cache(maxsize=100)
async def load_model(pk):
    model = (await Classifier.objects.aget(pk=pk)).load_model()
    return model


@register_handler(ClassifierCommand.name)
async def classify(command: Command, server: Server):
    loop = asyncio.get_running_loop()
    command = cast(ClassifierCommand, command)
    model = await load_model(command.pk)

    result = await loop.run_in_executor(server.process_pool, model.predict_proba, command.X)
    idxs = np.argmax(result, axis=1)
    labels = model.classes_[idxs]
    probabilities = np.max(result, axis=1)
    return Classification(labels, probabilities)


@register_handler(EvaluateClassifier.name)
async def report_classifier(command: Command, server: Server):
    loop = asyncio.get_running_loop()
    command = cast(EvaluateClassifier, command)
    model = await load_model(command.pk)
    y_pred = await loop.run_in_executor(server.process_pool, model.predict, command.X)
    return ClassifierReport(
        classification_report(
            y_true=command.y,
            y_pred=y_pred,
            target_names=command.names,
            output_dict=True,
        ))
