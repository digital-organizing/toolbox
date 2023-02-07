# Generated by Django 4.1.3 on 2023-02-07 10:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='managed_teams', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='team',
            name='applications',
            field=models.ManyToManyField(blank=True, to='manager.application'),
        ),
        migrations.AlterField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='teams', to=settings.AUTH_USER_MODEL),
        ),
    ]