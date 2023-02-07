# Generated by Django 4.1.6 on 2023-02-07 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('text_tools', '0002_alter_textfield_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='textfield',
            name='area',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='textfield',
            name='default',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
