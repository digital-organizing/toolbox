from django.contrib import admin

from text_tools.models import TaskTemplate, TextField, UrlField

# Register your models here.


class TextFieldInline(admin.TabularInline):
    model = TextField
    extra = 3


class UrlFieldInline(admin.TabularInline):
    model = UrlField
    extra = 1


@admin.register(TaskTemplate)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "model"]

    inlines = [TextFieldInline, UrlFieldInline]

    filter_horizontal = ["users"]
