import asyncio

import openai
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from text_tools.forms import TaskTemplateForm
from text_tools.models import TaskTemplate
from text_tools.services import count_tokens, extract_url


@login_required
def list_tasks(request: HttpRequest) -> HttpResponse:
    tasks = TaskTemplate.objects.all()

    return render(request, "text_tools/task_list.html", {"tasks": tasks})


def get_form(data=None, task=None):
    return TaskTemplateForm(data, task=task)


def check_access(task: TaskTemplate, user: User):
    if user.is_superuser:
        return
    if user in task.users.all():
        return
    raise PermissionDenied()


# Create your views here.
@sync_to_async
@login_required
@async_to_sync
async def task_view(request: HttpRequest, slug: str) -> HttpResponse:
    task = await TaskTemplate.objects.aget(slug=slug)

    await sync_to_async(check_access)(task, request.user)

    form = await sync_to_async(get_form)(task=task)

    if request.method == "GET":
        return render(
            request,
            "text_tools/task_form.html",
            {
                "form": form,
                "task": task,
            },
        )
    form = await sync_to_async(get_form)(request.POST, task=task)

    if not form.is_valid():
        return render(
            request,
            "text_tools/task_form.html",
            {
                "form": form,
                "task": task,
            },
        )

    data = form.cleaned_data

    url_tasks = []
    url_names = []

    async for url_field in task.urls.all():
        url_tasks.append(extract_url(data.get(url_field.slug, ""), url_field))
        url_names.append(url_field.slug)

    url_contents = await asyncio.gather(*url_tasks)
    url_dict = dict(zip(url_names, url_contents))

    text_dict = {}
    async for text_field in task.texts.all():
        text_dict[text_field.slug] = data.get(text_field.slug)

    format_dict = url_dict | text_dict

    prompt = task.template.format(**format_dict)
    suffix = task.suffix_template.format(**text_dict, **url_dict)

    completion = await openai.Completion.acreate(
        prompt=prompt,
        api_key=task.openai_key,
        model=task.model,
        max_tokens=min(
            task.model_max_tokens - count_tokens(suffix) - count_tokens(prompt),
            task.max_tokens,
        ),
        temperature=task.temperature,
        user=task.slug,
        suffix=suffix,
    )

    return render(
        request,
        "text_tools/task_form.html",
        {
            "completion": completion["choices"][0]["text"],
            "form": form,
            "task": task,
        },
    )
