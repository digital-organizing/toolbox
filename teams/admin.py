from django.contrib import admin

from teams.models import Team

# Register your models here.


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['members', 'admins', 'applications']
