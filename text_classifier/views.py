import json
from typing import cast

from django.http import HttpRequest
from django.http.response import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from import_export.admin import PermissionDenied
from sentry_sdk.integrations.django import is_authenticated

from ml_api.models.classifier import Classification
from text_classifier.forms import CorrectionForm, PredictForm
from text_classifier.models import Classifier, TextModel, TextSample
from text_classifier.services import check_auth_or_header, get_classification, store_classifications

from asgiref.sync import sync_to_async, async_to_sync
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
async def process_text(request: HttpRequest, model_pk):

    if request.method not in ['POST', 'GET']:
        return HttpResponseNotAllowed(['POST', 'GET'])

    model = await sync_to_async(check_auth_or_header)(request, model_pk)

    if request.method == 'GET':
        return render(request, 'text_classifier/prediction_form.html', {
            'form': PredictForm(),
            'model': model
        })

    classifier: Classifier = await model.classifier_set.filter(is_active=True).aget()

    if request.content_type == 'application/x-www-form-urlencoded' or request.content_type == 'multipart/form-data':
        texts = request.POST.getlist('text')
    else:
        texts = json.loads(request.body)

    classification = cast(Classification, await get_classification(classifier, texts))
    samples = await store_classifications(texts, classification)

    return JsonResponse([await sync_to_async(sample.to_dict)(request) for sample in samples],
                        safe=False)


def correct_sample(request, sample_id):
    sample = TextSample.objects.get(pk=sample_id)
    form = CorrectionForm(sample=sample)

    if request.method == 'POST':
        form = CorrectionForm(request.POST, sample=sample)

        if form.is_valid():
            sample.correction = form.cleaned_data['correction']
            sample.save()

    return render(request, 'text_classifier/correct_sample.html', {'form': form, 'sample': sample})
