import uuid
from django.utils.safestring import mark_safe
from datetime import datetime
from sklearn.utils import estimator_html_repr

import joblib
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
# from django.contrib.postgres.fields import ArrayField
from django_jsonform.models.fields import ArrayField
from model_utils.models import TimeStampedModel

from teams.models import Team
from text_classifier.ml import CLASSIFIERS


class TextModel(TimeStampedModel):
    name = models.CharField(max_length=120)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    team = models.ForeignKey(Team, models.CASCADE)

    classifier_set: models.QuerySet["Classifier"]
    category_set: models.QuerySet["Category"]

    sbert_models = ArrayField(
        models.CharField(
            max_length=120,
            choices=(
                ('distiluse-base-multilingual-cased-v1', 'distiluse-base-multilingual-cased-v1'),
                ('paraphrase-multilingual-MiniLM-L12-v2', 'paraphrase-multilingual-MiniLM-L12-v2'),
                ('distiluse-base-multilingual-cased-v2', 'distiluse-base-multilingual-cased-v2'),
                ('paraphrase-multilingual-mpnet-base-v2', 'paraphrase-multilingual-mpnet-base-v2'),
            )))

    classifiers = ArrayField(
        models.CharField(max_length=120, choices=((name, name) for name in CLASSIFIERS.keys())))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('text_classifier:classify-text', args=(self.pk, ))


def classifier_path(instance, filename):
    t = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return f'models/{instance.model.uuid}/{t}_{filename}'


class TrainingProcess(TimeStampedModel):
    model = models.ForeignKey(TextModel, models.CASCADE)

    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(get_user_model(), models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        return f'Process: {self.model.name}'


class Classifier(TimeStampedModel):
    model = models.ForeignKey(TextModel, models.CASCADE)
    sentence_model = models.CharField(max_length=250)
    stored = models.FileField(upload_to=classifier_path)
    is_active = models.BooleanField()
    training = models.ForeignKey(TrainingProcess, models.CASCADE)

    trained_at = models.DateTimeField(blank=True)

    score = models.JSONField()

    def classifier_path(self):
        return self.stored

    def load_model(self):
        return joblib.load(self.stored)

    def model_html(self):
        model = self.load_model()
        return mark_safe(estimator_html_repr(model))

    def __str__(self) -> str:
        return f'Classifier: {self.model.name}'


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    model = models.ForeignKey(TextModel, models.CASCADE)

    def __str__(self) -> str:
        return self.name


class TextSample(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    text = models.TextField()
    probability = models.FloatField(default=1)
    prediction = models.ForeignKey(Category, models.CASCADE, related_name='predicted_samples')
    correction = models.ForeignKey(
        Category,
        models.SET_NULL,
        related_name='corrected_samples',
        null=True,
    )

    @property
    def confidence(self):
        return self.probability * 100

    @property
    def html_text(self):
        return self.text.replace('\n', '<br/>')

    def to_dict(self, request):
        return {
            'text':
            self.text,
            'category':
            self.prediction.name,
            'probability':
            self.probability,
            'url':
            request.build_absolute_uri(reverse(
                'text_classifier:correct-sample',
                args=(self.pk, ),
            ))
        }

    def __str__(self):
        return self.text


class TrainingSample(TimeStampedModel):
    text = models.TextField()
    category = models.ForeignKey(Category, models.CASCADE)
    sample = models.OneToOneField(
        TextSample,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='sample',
    )

    def __str__(self) -> str:
        return self.text
