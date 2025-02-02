from django.contrib import admin
from .models import Task,SubTask,Tool,SubTaskTool,TaskRun,TaskLog
# Register your models here.

admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(Tool)
admin.site.register(SubTaskTool)
admin.site.register(TaskRun)
admin.site.register(TaskLog)