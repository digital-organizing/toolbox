from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from text_classifier.models import (
    Category,
    Classifier,
    TextModel,
    TextSample,
    TrainingSample,
)
from text_classifier.resources import TrainingSampleResource
from text_classifier.tasks import train_model

# Register your models here.


@admin.register(TextModel)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'uuid', 'team']

    fieldsets = (
        (None, {
            'fields': ('name', 'team'),
        }),
        ('Advanced', {
            'fields': ('sbert_models', 'classifiers'),
        }),
    )

    actions = ['start_training']

    list_filter = ['team']

    def start_training(self, request, queryset):
        for model in queryset:
            train_model.delay(model.pk, request.user.pk)


@admin.register(TextSample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'prediction', 'correction', 'created']
    readonly_fields = ['prediction', 'probability', 'text', 'uuid']

    list_filter = ['prediction', 'correction']
    date_hierarchy = 'created'


@admin.register(TrainingSample)
class TrainingSampleAdmin(ImportExportModelAdmin):
    list_display = ['text', 'category', 'sample', 'created']
    resource_classes = [TrainingSampleResource]

    list_filter = ['category']


@admin.register(Classifier)
class ClassifierAdmin(admin.ModelAdmin):
    list_display = ['created', 'model', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'model']
