from django.urls import path

from text_tools.views import task_view

app_name = 'text_tools'

urlpatterns = [
    path('task/<slug:slug>/', task_view, name="task_view"),
]

