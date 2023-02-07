from django.urls import path

from text_tools.views import list_tasks, task_view

app_name = 'text_tools'

urlpatterns = [
    path('task/', list_tasks, name="task_list"),
    path('task/<slug:slug>/', task_view, name="task_view"),
]

