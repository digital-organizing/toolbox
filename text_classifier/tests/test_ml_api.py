import asyncio
from django.test.client import AsyncClient
from unittest import skip
import numpy as np
import csv
import threading
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction, connections

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, TransactionTestCase

from ml_api.django import connect
from ml_api.models.classifier import ClassifierCommand, Classification
from ml_api.models.sbert import SentenceEmbeddingCommand
from ml_api.server import Server, serve
from teams.models import Team
from text_classifier.models import (
    Category,
    Classifier,
    TextModel,
    TrainingSample,
)
from text_classifier.tasks import train_model

CLASSIFIERS = ['SVC']
SBERT_MODELS = ['distiluse-base-multilingual-cased-v1']
# Create your tests here.


def serve_thread(server, loop):
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.start())
    finally:
        connections.close_all()


class TrainTextModelTest(TransactionTestCase):
    test_sentences = [
        "My favourite soccer team won the game.",
        "Lions and tigers are related to house cats.",
    ]

    @classmethod
    def setUpClass(cls):

        import nltk
        nltk.download('punkt')

        super().setUpClass()
        settings.API_PORT = 9124
        settings.API_HOST = 'localhost'
        settings.API_SECRET = 'secret'
        settings.CONN_MAX_AGE = 0
        port = settings.API_PORT
        secret = settings.API_SECRET
        cls.server = Server(host='0.0.0.0', port=port, secret=secret)
        cls.loop = asyncio.new_event_loop()
        cls.thread = threading.Thread(
            target=serve_thread,
            args=(cls.server, cls.loop),
        )

        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.loop.call_soon_threadsafe(cls.server.shutdown)
        cls.thread.join()
        cls.loop.stop()
        cls.loop.close()
        connections.close_all()
        return

    def setUp(self) -> None:
        self.user = get_user_model().objects.create(username="user")
        self.team = Team.objects.create(name="test-team")
        self.team.members.add(self.user)

    def train_model(self):
        self.model: TextModel = TextModel.objects.create(
            name='test',
            team=self.team,
            sbert_models=SBERT_MODELS,
            classifiers=CLASSIFIERS,
        )
        animals = Category.objects.create(name="Animals", model=self.model)
        sports = Category.objects.create(name="Sports", model=self.model)
        with open('text_classifier/tests/data/train_samples.csv') as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row['category'] in ["Animals", "Sports"]
                category = animals if row['category'] == 'Animals' else sports
                TrainingSample.objects.create(
                    text=row['text'],
                    category=category,
                )
        return train_model(self.model.pk, self.user.pk)

    def test_train_model(self):
        pk = self.train_model()
        assert TrainingSample.objects.filter(category__name="Animals").count() > 10
        assert TrainingSample.objects.filter(category__name="Sports").count() > 10
        classifier = Classifier.objects.get(pk=pk)
        model = classifier.load_model()

        assert hasattr(model, 'predict')

    async def test_get_embeddings(self):
        await sync_to_async(self.train_model)()
        classifier = await self.model.classifier_set.afirst()
        assert classifier is not None
        async with connect() as client:
            embeddings = await client.sentence_embeddings(
                classifier.sentence_model,
                self.test_sentences,
            )
            cmd = ClassifierCommand(classifier.pk, embeddings.embeddings)
            labels = await client.send_command(cmd)
        assert isinstance(labels, Classification)
        assert labels.probs.shape == (2, )
        assert (await Category.objects.aget(pk=labels.y[0])).name == 'Sports'
        assert (await Category.objects.aget(pk=labels.y[1])).name == 'Animals'

    def test_get_view(self):
        self.train_model()
        c = Client()
        c.force_login(self.user)
        response = c.post(
            f'/text-classifier/{self.model.uuid}/',
            {"text": self.test_sentences},
        )
        json = response.json()
        assert len(json) == 2
        assert json[0]['category'] == 'Sports'
        assert json[1]['category'] == 'Animals'
