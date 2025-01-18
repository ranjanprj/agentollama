# entire file content ...
from django.urls import path
from . import views

urlpatterns = [
    path('task/',views.index, name='index'),
    path('task/<int:id>/',views.task, name='task'),
    path('subtask/<int:task_id>/<int:step>/',views.subtask, name='subtask'),
]
