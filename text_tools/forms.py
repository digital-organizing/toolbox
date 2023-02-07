from typing import Any

from django import forms

from text_tools.models import TaskTemplate


class TaskTemplateForm(forms.Form):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.task: TaskTemplate = kwargs.pop('task')
        super().__init__(*args, **kwargs)

        for text_field in self.task.texts.all():
            self.fields[text_field.slug] = forms.CharField(
                label=text_field.name,
                required=text_field.required,
            )

        for url_field in self.task.urls.all():
            self.fields[url_field.slug] = forms.URLField(
                label=url_field.name,
                required=url_field.required,
            )
