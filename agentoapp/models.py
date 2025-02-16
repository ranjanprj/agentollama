from django.db import models
from django.dispatch import receiver
import os

class KnowledgeRep(models.Model):
    name = models.CharField(max_length=24)
    description = models.CharField(max_length=128)

    def __str__(self):
        return str(self.id)


def user_directory_path(instance,filename):
   # file will be uploaded to MEDIA_ROOT
   return 'krep/{0}/{1}'.format(instance,filename) 

class KnowledgeRepFiles(models.Model):
    Knowledge_rep = models.ForeignKey(KnowledgeRep,on_delete=models.CASCADE)
    file = models.FileField(upload_to =user_directory_path)

    def __str__(self):
        return self.Knowledge_rep.name

@receiver(models.signals.post_delete, sender=KnowledgeRepFiles)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

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
    type = models.CharField(max_length=20,choices=(("TOOL",'Tool'),('RAG','RAG'),('LOOP','Loop')))
    model = models.CharField(max_length=24)
    name = models.CharField(max_length=100)
    context = models.CharField(max_length=2048)
    instruction = models.CharField(max_length=2048)
    outputFormatInstruction = models.CharField(max_length=2048)
    knowledgerep = models.ForeignKey(KnowledgeRep,on_delete=models.DO_NOTHING,null=True,blank=True)

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
    subtask = models.ForeignKey(SubTask,on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subtask} -  {self.tool}"

class TaskRun(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE)
    current_step = models.IntegerField(default=-1)
    current_step_status = models.CharField(max_length=24,choices=(("RUNNING",'Running'),('COMPLETED','Completed'),('FAILED','Failed')))

    
class TaskLog(models.Model):
    task_run = models.ForeignKey(TaskRun,on_delete=models.CASCADE)    
    log = models.TextField()

