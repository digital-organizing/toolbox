from django.contrib import admin

from manager.models import Application

# Register your models here.


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass
