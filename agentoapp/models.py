from django.db import models


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

SUBTASK_CHOICES = (
    ('AGENT', "Agent"),
    ('TOOL', "Tool"),
    ('CODE', "Code"),
)
 
class SubTask(models.Model):
    belongs_to = models.ForeignKey(Task,on_delete=models.DO_NOTHING)
    
    name = models.CharField(max_length=100)
    context = models.CharField(max_length=2048)
    instruction = models.CharField(max_length=2048)
    outputFormatInstruction = models.CharField(max_length=2048)

    step = models.IntegerField()


    def __str__(self):
        return self.name
    
class Tool(models.Model):    
    name = models.CharField(max_length=100)
    context = models.CharField(max_length=2048)
    instruction = models.CharField(max_length=2048)
    outputFormatInstruction = models.CharField(max_length=2048)
    codeblock = models.TextField(null=True)
    def __str__(self):
        return self.name

class SubTaskTool(models.Model):
    subtask = models.ForeignKey(SubTask,on_delete=models.DO_NOTHING)
    tool = models.ForeignKey(Tool,on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.subtask}  {self.tool}"