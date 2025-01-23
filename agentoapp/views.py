from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from .models import SubTaskTool, Task,SubTask,Tool
# Create your views here.
from .og import prompt
from ollama import chat
from django.http import StreamingHttpResponse
import json
from django.forms.models import model_to_dict

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
            tools = []
            for sb in st['subtasks']:
                p = f"{sb.context} {sb.instruction.replace('previous_result',answer)}  {sb.outputFormatInstruction} "
                assigned_tools = SubTaskTool.objects.filter(subtask=sb.id)
                for at in assigned_tools:
                    print(at.tool,'================')
                    # t = Tool.objects.get(id=at.tool)
                    t = model_to_dict(at.tool)
                    tools.append(t)
                print(tools)
                answer = prompt(p,tools)
        print(answer)
        return HttpResponse(answer)
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
        # Task.objects.create(name=taskName,description=taskDescription)
    subtask = None
    if action == 'edit':
        subtask = SubTask.objects.get(id=step)
    if action == 'edit' and request.method == 'POST':
        print(request.POST)
        subTaskName = request.POST.get('subTaskName','')
        context = request.POST.get('context','')
        instruction = request.POST.get('instruction','')
        outputFormatInstruction = request.POST.get('outputFormatInstruction','')
        selectedTools =  request.POST.get('selectedTools','')
        print(type(selectedTools),selectedTools,selectedTools=='')
        if selectedTools != '':
            selectedTools = [int(t) for t in selectedTools.split(',')]
            if len(selectedTools) > 0:
                SubTaskTool.objects.filter(subtask=subtask).delete()
                for t in selectedTools:            
                    tool = Tool.objects.get(id=t)
                    SubTaskTool.objects.create(subtask=subtask,tool=tool)
        elif selectedTools == '':
            SubTaskTool.objects.filter(subtask=subtask).delete()
          
        subtask.name = subTaskName
        subtask.context = context
        subtask.instruction = instruction
        subtask.outputFormatInstruction = outputFormatInstruction
        subtask.save()
        print("POST")
    tools = Tool.objects.all()
    assigned_tools = None
    if subtask:
        assigned_tools = SubTaskTool.objects.filter(subtask=subtask)
        
    return render(request,'agentoapp/subtask.html',context={'action':action,'taskId':taskId,'step':step,'subtask':subtask,'tools':tools,'assigned_tools':assigned_tools})
    
def tools(request,action,id):
    print(action,id)
    print(request.POST)
    back_url = request.META.get('HTTP_REFERER')
    if action == 'create' and request.method == 'POST':        
        toolName = request.POST.get('toolName','')              
        context = request.POST.get('context','')
        instruction = request.POST.get('instruction','')
        outputFormatInstruction = request.POST.get('outputFormatInstruction','')  
        codeblock = request.POST.get('codeblock','')  
        back_url = request.POST.get('back_url','')  

        print(toolName,context,instruction,outputFormatInstruction,codeblock)
        Tool.objects.create(name=toolName,context=context,instruction=instruction,outputFormatInstruction=outputFormatInstruction,codeblock=codeblock)
        return redirect(back_url)
    elif action == 'edit' and request.method == 'POST':
        tool = Tool.objects.get(id=id)
        toolName = request.POST.get('toolName','')              
        context = request.POST.get('context','')
        instruction = request.POST.get('instruction','')
        outputFormatInstruction = request.POST.get('outputFormatInstruction','')  
        codeblock = request.POST.get('codeblock','')  
        back_url = request.POST.get('back_url','')  

        print(toolName,context,instruction,outputFormatInstruction,codeblock)
        tool.name = toolName
        tool.context = context
        tool.instruction = instruction
        tool.outputFormatInstruction = outputFormatInstruction
        tool.codeblock = codeblock
        tool.save()
        return redirect(back_url)

    tool = None
    if action == 'edit' and request.method == 'GET':       
        tool = Tool.objects.get(id=id)
    

    existing_tools = Tool.objects.all()
    return render(request,'agentoapp/tool.html',context={'action':action,'id':id,'back_url':back_url,'existing_tools':existing_tools,'tool':tool})

def stream_llm(prompt):
    # https://dev.to/epam_india_python/harnessing-the-power-of-django-streaminghttpresponse-for-efficient-web-streaming-56jh
    print(prompt)
    stream = chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )

    for chunk in stream:
        yield chunk['message']['content']

def generate_code(request):
    print(request,request.method)
    if request.method == 'POST':
      
        data = request.body
        # data is a bytes-like object, so you might want to convert it to a dictionary or a string
        data = data.decode('utf-8')
        # parse the JSON data
        data = json.loads(data)
        toolName = data['toolName']
        context = data['context']
        instruction = data['instruction']
        outputFormatInstruction = data['outputFormatInstruction']
        prompt = context + " " + instruction + " " + outputFormatInstruction
        print(prompt)
        
        # You are python developer developing tools for Agentic application with 
        response = StreamingHttpResponse(stream_llm(prompt))
        response['Content-Type'] = 'text/plain'
        return response
    