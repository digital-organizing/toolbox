from typing import cast

from django import forms


class CorrectionForm(forms.Form):
    correction = forms.ModelChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        self.sample = kwargs.pop('sample')
        super().__init__(*args, **kwargs)
        field = cast(forms.ModelChoiceField, self.fields['correction'])
        field.queryset = self.sample.prediction.model.category_set.all()
        field.initial = self.sample.correction


class PredictForm(forms.Form):
    text = forms.CharField()
