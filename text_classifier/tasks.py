from io import BytesIO

import joblib
from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone

from text_classifier.ml import optimize_model
from text_classifier.models import (
    Classifier,
    TextModel,
    TrainingProcess,
    TrainingSample,
)


@shared_task
def train_model(model_pk, user_id):
    model = TextModel.objects.get(pk=model_pk)
    samples = TrainingSample.objects.filter(category__model_id=model_pk)

    texts = samples.values_list('text', flat=True)
    categories = samples.values_list('category_id', flat=True)

    process_id = TrainingProcess.objects.create(
        model_id=model_pk,
        started_at=timezone.now(),
        user_id=user_id,
    ).pk

    model, sbert, result = optimize_model(
        list(texts),
        list(categories),
        model.sbert_models,
        model.classifiers,
    )

    process = TrainingProcess.objects.get(pk=process_id)

    process.completed_at = timezone.now()
    process.result = result
    process.save()

    Classifier.objects.filter(model_id=model_pk, is_active=True).update(is_active=False)

    classifier = Classifier.objects.create(
        is_active=True,
        model_id=model_pk,
        sentence_model=sbert,
        trained_at=timezone.now(),
        score=result,
        training=process,
    )

    with BytesIO() as io:
        joblib.dump(model, io, compress=True)
        io.seek(0)
        classifier.stored.save('classifier.dump', ContentFile(io.read()))

    return classifier.pk
