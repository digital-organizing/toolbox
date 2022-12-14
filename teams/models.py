from django.contrib.auth import get_user_model
from django.db import models

from manager.models import Application

# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=120)
    members = models.ManyToManyField(get_user_model(), related_name='teams', blank=True)
    admins = models.ManyToManyField(get_user_model(), related_name='managed_teams', blank=True)
    applications = models.ManyToManyField(Application, blank=True)

    def __str__(self) -> str:
        return self.name
