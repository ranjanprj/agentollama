
from django.contrib import admin
from django.urls import path, include
from .views import index,task,subtask,tools,generate_code,knowledgerep,post_symbol_sentiment,api_upload_document,api_trigger_agent
app_name  = 'agentoapp'

urlpatterns = [    
    path('', name='index',view=index),
    path('task/<str:action>/<int:id>', name='task',view=task),
    path('task/<int:taskId>/step/<int:step>/<str:action>', name='subtask',view=subtask),
    path('task/<int:taskId>/subtask/<int:step>/<str:action>', name='subtask',view=subtask),
    path('tools/<str:action>/<int:id>', name='tools',view=tools),
    path('genai', name='generate_code',view=generate_code),
    path('knowledgerep/<str:action>/<int:id>', name='knowledgerep',view=knowledgerep),
    path('api_upload_document/upload', name='api_upload_document',view=api_upload_document),
    path('api_trigger_agent', name='api_trigger_agent',view=api_trigger_agent),

    path('post_symbol_sentiment', name='post_symbol_sentiment',view=post_symbol_sentiment),

   


]
