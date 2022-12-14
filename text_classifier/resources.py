from typing import Dict
from import_export import resources

from text_classifier.models import TextModel, TextSample, TrainingSample


class TextSampleResource(resources.ModelResource):

    class Meta:
        model = TextSample


class TrainingSampleResource(resources.ModelResource):

    class Meta:
        model = TrainingSample
        fields = ('uuid', 'text', 'category__name', 'category__model__uuid', 'id')

    def import_data(self,
                    dataset,
                    dry_run=False,
                    raise_errors=False,
                    use_transactions=None,
                    collect_failed_rows=False,
                    rollback_on_validation_errors=False,
                    **kwargs):
        dataset.remove_duplicates()
        dataset.dict = [row for row in dataset.dict if row['text']]
        return super().import_data(dataset, dry_run, raise_errors, use_transactions,
                                   collect_failed_rows, rollback_on_validation_errors, **kwargs)

    def _get_category(self, model_pk, name):
        model: TextModel = TextModel.objects.get(pk=model_pk)
        category, _ = model.category_set.get_or_create(name=name)

        return category

    def get_or_init_instance(self, instance_loader, row):

        category = self._get_category(row['category__model__uuid'], row['category__name'])
        new = False
        if row.get('id', None):
            instance = super().get_instance(instance_loader, row)
        else:
            instance = super().init_instance(row)
            new = True

        if instance is None:
            return None, False

        instance.category_id = category.pk
        return instance, new
