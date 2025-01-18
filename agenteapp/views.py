# entire file content ...
from django.shortcuts import render,redirect,HttpResponse
from .models import Task,SubTask,PublishedEvent
# Create your views here.
from .og import prompt

def index(request):
    tasks = Task.objects.all().values()
    return render(request,'agentoapp/index.html',context={'tasks':tasks})

def task(request,action,id):
    print(action,id)
    print(request.POST)
    if action == 'create':
        taskName = request.POST.get('taskName','')
        taskDescription = request.POST.get('taskDescription','')
        print(taskName,taskDescription)
        Task.objects.create(name=taskName,description=taskDescription)
    
    task = None
    steps = None
    st_list = []
    if id:
        task = Task.objects.get(id=id)
    # get steps asc
        # subtasks = SubTask.objects.filter(belongs_to=id).order_by('step').values()
        
        for st in SubTask.objects.filter(belongs_to=id).order_by('step'):
            print(st)  
            current_step = st.step
            found = False
            for stl in st_list:
                if stl['step'] == current_step:
                    found = True
                    stl['subtasks'].append(st)
            if not found:
                st_list.append({'step':st.step, 'subtasks':[st]})
                found = False
            
            
    if action == 'run':
        print("RUN")
        answer = ''
        for st in st_list:
            for sb in st['subtasks']:
                p = f"{sb.context} {sb.instruction.replace('previous_result',answer)}  {sb.outputFormatInstruction} "
                answer = prompt(p)
        print(answer)
        return HttpResponse(answer)
    if action == 'publish':
        event = PublishedEvent.objects.create(task=task, message='Task published')
        return HttpResponse(event.id)
    return render(request,'agentoapp/task.html',context={'action':action,'id':id,'task':task,'st_list':st_list})

def subtask(request,taskId,step,action):
    print(action,taskId,step)
   
    if action == 'create':
        subTaskName = request.POST.get('subTaskName','')
        context = request.POST.get('context','')
        instruction = request.POST.get('instruction','')
        outputFormatInstruction = request.POST.get('outputFormatInstruction','')
        print(taskId,step,action)
        print(subTaskName,context,instruction,outputFormatInstruction)
        task = Task.objects.get(id=taskId)
        subTask = SubTask.objects.create(belongs_to=task,name=subTaskName,context=context,instruction=instruction,outputFormatInstruction=outputFormatInstruction,step=step)
        return redirect(f'/task/edit/{taskId}')
    if action == 'publish':
        event = PublishedEvent.objects.create(task=subTask, message='Subtask published')
        return HttpResponse(event.id)
    return render(request,'agentoapp/subtask.html',context={'action':action,'id':id,'task_id':taskId,'step':step})
