from django.contrib import admin
from .models import Task,SubTask
# Register your models here.

admin.site.register(Task)
admin.site.register(SubTask)