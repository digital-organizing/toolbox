# Generated by Django 4.1.3 on 2023-02-07 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('text_tools', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='textfield',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='texts', to='text_tools.tasktemplate'),
        ),
    ]
