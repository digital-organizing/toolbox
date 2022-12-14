from django.urls import path

from text_classifier.views import correct_sample, process_text

app_name = 'text_classifier'

urlpatterns = [
    path('<uuid:model_pk>/', process_text, name="classify-text"),
    path('correct/<uuid:sample_id>/', correct_sample, name="correct-sample"),
]
