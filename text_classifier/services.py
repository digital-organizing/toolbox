import traceback
from typing import cast
from django.core.exceptions import PermissionDenied

from django.db.models import QuerySet
from rest_framework.authtoken.models import Token

from ml_api.django import connect
from ml_api.models.classifier import Classification, ClassifierCommand
from ml_api.models.sbert import (
    SentenceEmbeddingCommand,
    SentenceEmbeddingResult,
)
from text_classifier.models import TextModel, TextSample, TrainingSample


async def get_classification(classifier, texts):
    async with connect() as client:
        embedding = await client.send_command(
            SentenceEmbeddingCommand(
                classifier.sentence_model,
                texts,
            ))
        embedding = cast(SentenceEmbeddingResult, embedding)
        clasification = await client.send_command(
            ClassifierCommand(
                classifier.id,
                embedding.embeddings,
            ))
    return clasification


async def store_classifications(texts, classification: Classification):
    samples = [
        TextSample(
            text=text,
            prediction_id=category,
            probability=probability,
        ) for text, category, probability in zip(
            texts,
            classification.y,
            classification.probs,
        )
    ]

    await TextSample.objects.abulk_create(samples)

    return samples


async def create_training_samples(samples: QuerySet[TextSample]):
    await TrainingSample.objects.abulk_create([
        TrainingSample(text=sample.text, category=sample.correction, sample=sample)
        async for sample in samples.exclude(correction__isnull=True).exclude(sample__isnull=False)
    ])


def check_auth_or_header(request, model_pk):
    user = request.user
    if not request.user.is_authenticated:
        try:
            print(request.headers)
            key, token = request.headers.get('Authorization').split(' ')
            if key == 'Bearer':
                token = Token.objects.filter(key=token).get()
                user = token.user
        except:
            traceback.print_exc()
            raise PermissionDenied
    model = TextModel.objects.get(pk=model_pk)

    if not model.team.members.filter(pk=user.pk).exists():
        raise PermissionDenied

    return model
