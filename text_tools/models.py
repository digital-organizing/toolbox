from django.db import models

# Create your models here.


class TaskTemplate(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    template = models.TextField()
    suffix_template = models.TextField(blank=True)

    model = models.CharField(max_length=200, default='text-davinci-003')
    model_max_tokens = models.IntegerField(default=4096)

    max_tokens = models.IntegerField(default=720)
    temperature = models.FloatField(default=0.9)
    presence_penality = models.FloatField(default=0)
    frequency_penality = models.FloatField(default=0)

    openai_key = models.CharField(max_length=200)
    openai_org = models.CharField(max_length=200, blank=True)

    texts: models.QuerySet['TextField']
    urls: models.QuerySet['UrlField']

    def __str__(self) -> str:
        return self.name


class TextField(models.Model):
    slug = models.SlugField()
    task = models.ForeignKey(TaskTemplate, models.CASCADE, related_name="texts")
    name = models.CharField(max_length=120)
    required = models.BooleanField()

    area = models.BooleanField(default=False)
    default = models.CharField(max_length=500, blank=True)

    def __str__(self) -> str:
        return self.name


class UrlField(models.Model):
    slug = models.SlugField()
    task = models.ForeignKey(TaskTemplate, models.CASCADE, related_name="urls")
    name = models.CharField(max_length=120)

    xpath = models.CharField(max_length=320, default='/html/body//*[self::p | self::h1 | self::h2]')
    min_length = models.IntegerField(default=50)

    required = models.BooleanField()

    def __str__(self) -> str:
        return self.name
