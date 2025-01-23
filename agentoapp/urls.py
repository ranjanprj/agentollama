
from django.contrib import admin
from django.urls import path, include
from .views import index,task,subtask,tools,generate_code

app_name  = 'agentoapp'

urlpatterns = [    
    path('', name='index',view=index),
    path('task/<str:action>/<int:id>', name='task',view=task),
    path('task/<int:taskId>/step/<int:step>/<str:action>', name='subtask',view=subtask),
    path('task/<int:taskId>/subtask/<int:step>/<str:action>', name='subtask',view=subtask),
    path('tools/<str:action>/<int:id>', name='tools',view=tools),
    path('genai', name='generate_code',view=generate_code),

]
