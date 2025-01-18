# entire file content ...
class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class SubTask(models.Model):
    belongs_to = models.ForeignKey(Task,on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100)
    context = models.CharField(max_length=2048)
    instruction = models.CharField(max_length=2048)
    outputFormatInstruction = models.CharField(max_length=2048)

    step = models.IntegerField()


    def __str__(self):
        return self.name
class PublishedEvent(models.Model):
    task = models.ForeignKey(Task,on_delete=models.DO_NOTHING)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task} - {self.message}"
