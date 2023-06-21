# Generated by Django 4.1.6 on 2023-06-21 09:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('text_tools', '0003_textfield_area_textfield_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasktemplate',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
