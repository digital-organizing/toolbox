# Generated by Django 4.1.3 on 2023-02-07 10:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TaskTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
                ('template', models.TextField()),
                ('suffix_template', models.TextField(blank=True)),
                ('model', models.CharField(default='text-davinci-003', max_length=200)),
                ('model_max_tokens', models.IntegerField(default=4096)),
                ('max_tokens', models.IntegerField(default=720)),
                ('temperature', models.FloatField(default=0.9)),
                ('presence_penality', models.FloatField(default=0)),
                ('frequency_penality', models.FloatField(default=0)),
                ('openai_key', models.CharField(max_length=200)),
                ('openai_org', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='UrlField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=120)),
                ('xpath', models.CharField(default='/html/body//*[self::p | self::h1 | self::h2]', max_length=320)),
                ('min_length', models.IntegerField(default=50)),
                ('required', models.BooleanField()),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to='text_tools.tasktemplate')),
            ],
        ),
        migrations.CreateModel(
            name='TextField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=120)),
                ('required', models.BooleanField()),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='text_tools.tasktemplate')),
            ],
        ),
    ]
