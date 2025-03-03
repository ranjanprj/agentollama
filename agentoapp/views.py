from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from .models import SubTaskTool, Task,SubTask,Tool, TaskRun, TaskLog,KnowledgeRep,KnowledgeRepFiles
# Create your views here.
from .og import prompt,prompt_rag
from ollama import chat
from django.http import StreamingHttpResponse,JsonResponse
import json
from django.forms.models import model_to_dict

from ollama import ListResponse, list


from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
import ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
import json_repair


def index(request):
    tasks = Task.objects.all().values()
    return render(request,'agentoapp/index.html',context={'tasks':tasks})

def task(request,action,id):
    print(action,id)
    print(request.POST)

    if action == 'viewlogs':
        # take top running job
        task_run = TaskRun.objects.filter(task=id).order_by('-id').first()
        task_logs = TaskLog.objects.filter(task_run=task_run)
        print(task_run)
        context = {
            'current_task_run_id': task_run.id,
            'current_step': task_run.current_step,
            'status': task_run.current_step_status,
            'task_run':task_run,
            'task_logs': task_logs
        }
        return render(request,'agentoapp/viewlogs.html',context=context)
 
    if action == 'status':       
        # take top running job
        task_run = TaskRun.objects.filter(task=id).order_by('-id').first()
        print(task_run)
        return JsonResponse({
            'current_task_run_id': task_run.id,
            'current_step': task_run.current_step,
            'status': task_run.current_step_status
        })
    if action == 'create' and request.method == 'POST':
        taskName = request.POST.get('taskName','')
        taskDescription = request.POST.get('taskDescription','')
        print(taskName,taskDescription)
        Task.objects.create(name=taskName,description=taskDescription)
    
    task = None
    steps = None
    st_list = []
    subtasks = None
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
        subtasks = SubTask.objects.filter(belongs_to=id).order_by('step')
        print(subtasks)
            
    if action == 'run':
        print("RUN")
        model = request.GET.get('model', 'llama3.1:latest')
        answer = execute_task_run(id=id,model=model)
        return HttpResponse(answer)
    response: ListResponse = list()
    available_models = [model.model for model in response.models]
    print(available_models)
    return render(request,'agentoapp/task.html',context={'action':action,'id':id,'task':task,'st_list':st_list,'available_models':available_models,'subtasks':subtasks})

def subtask(request,taskId,step,action):
    print(action,taskId,'step',step)
   
    if action == 'create':
        subTaskName = request.POST.get('subTaskName','')
        context = request.POST.get('context','')
        instruction = request.POST.get('instruction','')
        outputFormatInstruction = request.POST.get('outputFormatInstruction','')
        type = request.POST.get('type','')
        model = request.POST.get('model','llama3.1')
        
        
        id = int(request.POST.get('knowledgerep',0))
        knowledgerep = None
        if id:            
            knowledgerep = KnowledgeRep.objects.get(id=id)

            
        print(taskId,step,action)
        print(subTaskName,context,instruction,outputFormatInstruction)
        task = Task.objects.get(id=taskId)

        
        subTask = SubTask.objects.create(belongs_to=task,name=subTaskName,context=context,instruction=instruction,outputFormatInstruction=outputFormatInstruction,step=step,type=type,knowledgerep=knowledgerep,model=model)
        return redirect(f'/task/edit/{taskId}')
        # Task.objects.create(name=taskName,description=taskDescription)
    subtask = None
    if action == 'edit':
        # SUBTASK ID HAS BEEN PAASED AS STEP ID !!!
        subtask = SubTask.objects.get(id=step)
    if action == 'edit' and request.method == 'POST':
        print(request.POST)
        subTaskName = request.POST.get('subTaskName','')
        context = request.POST.get('context','')
        instruction = request.POST.get('instruction','')
        outputFormatInstruction = request.POST.get('outputFormatInstruction','')
        selectedTools =  request.POST.get('selectedTools','')
        knowledgerep = request.POST.get('knowledgerep','')
        model = request.POST.get('model','llama3.1')
        # print(type(selectedTools),selectedTools,selectedTools=='')
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
        subtask.model = model
        if knowledgerep:
            subtask.knowledgerep = KnowledgeRep.objects.get(id=knowledgerep) 
        subtask.save()
        print("POST")

    tools = Tool.objects.all()
    knowledgereps = KnowledgeRep.objects.all()
    assigned_tools = None
    if subtask:
        assigned_tools = SubTaskTool.objects.filter(subtask=subtask)
        
    page = None
    if subtask:
        page = f"{subtask.type.lower()}subtask"
    else:
        page = action

    response: ListResponse = list()
    available_models = [model.model for model in response.models]
    return render(request,f'agentoapp/{page}.html',context={'action':action,'taskId':taskId,'step':step,'subtask':subtask,'tools':tools,'assigned_tools':assigned_tools,'knowledgereps':knowledgereps,'available_models':available_models})
    

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

    response: ListResponse = list()
    available_models = [model.model for model in response.models]

    return render(request,'agentoapp/tool.html',context={'action':action,'id':id,'back_url':back_url,'existing_tools':existing_tools,'tool':tool,'available_models':available_models})

def stream_llm(prompt,model):
    # https://dev.to/epam_india_python/harnessing-the-power-of-django-streaminghttpresponse-for-efficient-web-streaming-56jh
    print("stream_llm(prompt,model):")
    print(prompt)
    print(model)
    stream = chat(
        model=model,
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
        model = data['model']
        prompt = context + " " + instruction + " " + outputFormatInstruction
        print(prompt)
        
        # You are python developer developing tools for Agentic application with 
        response = StreamingHttpResponse(stream_llm(prompt,model))
        response['Content-Type'] = 'text/plain'
        return response
    
def knowledgerep(request,action,id):
    print(request,action,id)
    krep = KnowledgeRep.objects.all()
    krepf = KnowledgeRepFiles.objects.all()
    krepo = None
    tasks = Task.objects.all()
    if action == 'create' and request.method == 'POST':        
        name = request.POST.get('name','')              
        description = request.POST.get('description','')
        associated_task = request.POST.get('associated_task',None)
        if associated_task:
            associated_task = Task.objects.get(id=associated_task)
            KnowledgeRep.objects.create(name=name,description=description,associated_task=associated_task)
        else:
            KnowledgeRep.objects.create(name=name,description=description)
        return redirect('/knowledgerep/create/0')
        
    if action == 'upload' and request.method == 'POST':
        print(request.POST)
        knowledgerep_id = int(request.POST.get('knowledgerep',''))
    
        print(knowledgerep_id)
        krep = KnowledgeRep.objects.get(id=knowledgerep_id)

        instance = KnowledgeRepFiles(Knowledge_rep=krep,file=request.FILES["file"])
        instance.save()
        return redirect('/knowledgerep/create/0')

    if action == 'edit' and request.method == 'GET' and id:
        krepo = KnowledgeRep.objects.get(id=id)        

        krepf = KnowledgeRepFiles.objects.filter(Knowledge_rep=krepo)
    
    if action == 'edit' and request.method == 'POST' and id:
        name = request.POST.get('name','')              
        description = request.POST.get('description','')
        associated_task = request.POST.get('associated_task','')
        krepo = KnowledgeRep.objects.get(id=id) 
        krepo.name = name
        krepo.description = description
        associated_task = Task.objects.get(id=associated_task)
        krepo.associated_task = associated_task
        krepo.save()
        return redirect('/knowledgerep/create/0')
    if action == 'delete' and request.method == 'GET' and id:
        krepof = KnowledgeRepFiles.objects.get(id=id)  
        krepof.delete()
        return redirect('/knowledgerep/create/0')
    if action == 'deletekrep' and request.method == 'GET' and id:
        krepo = KnowledgeRep.objects.get(id=id)  
        krepo.delete()
        return redirect('/knowledgerep/create/0')
    
    if action == 'delete' and request.method == 'GET' and id:
        krepof = KnowledgeRepFiles.objects.get(id=id)  
        krepof.delete()
        return redirect('/knowledgerep/create/0')

    
    if action == 'vectorize' and request.method == 'GET' and id:
        krepo = KnowledgeRep.objects.get(id=id)  
        file_path = f"krep/{krepo.name}"
        file_dir = Path(file_path)
        documents = SimpleDirectoryReader(file_dir).load_data()
        # set up ChromaVectorStore and load in data
        print("============= Setting up ChromaVectorStore and loading data ===========")
        chroma_client = chromadb.PersistentClient(path="db/")
        chroma_collection = chroma_client.get_or_create_collection("news-llmanalyze")
        # bge-base embedding model
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        # ollama
        Settings.llm = Ollama(model='llama3.1', request_timeout=360.0)
        print("=============== Vectorizing =============================")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, embed_model=Settings.embed_model
        )
        
        return redirect('/knowledgerep/create/0')


    return render(request,'agentoapp/knowledgerep.html',context={'krep':krep,'krepf':krepf,'krepo':krepo,'action':action,'id':id, 'tasks':tasks})


def execute_task_run(id=None,agent_name=None,model='llama3.1',repository_name=None):    
    print("====================================================")
    print("---------execute_task_run---------------------------")
    print(id,agent_name,model,repository_name)
    print("====================================================")
    task = None
    steps = None
    st_list = []
    subasks = None
    if id:
        task = Task.objects.get(id=id)
    elif agent_name:
        task = Task.objects.filter(name=agent_name)[0]
    print("Task -> " , task)
    id = task.id
    # gt steps asc
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
    subtasks = SubTask.objects.filter(belongs_to=id).order_by('step')
    print("Subtasks" , subtasks)
    task_run = TaskRun.objects.create(task=task)
  
    answer = ''
    loop_st_found = False
    loop_previous_result = ''
    loop_st = []
    subtasks = SubTask.objects.filter(belongs_to=id).order_by('step')
    for sb in subtasks:            
        task_run.current_step = st.step
        task_run.current_step_status = 'RUNNING'
        task_run.save()
        tools = []
        
        task_log = TaskLog.objects.create(task_run=task_run)
        log = '<p>===========================================================</p>'
        log += f'<p> Running Task {task}</p>'
        
        if loop_st_found:                    
            loop_st.append(sb)
        if sb.type == 'LOOP':
            loop_previous_result = answer
            loop_st_found = True              
        if sb.type == 'RAG' and not loop_st_found:

            p = f"Context:{sb.context} Instruction:{sb.instruction.replace('previous_result',answer)} Output Format: {sb.outputFormatInstruction}"

            if repository_name:
                krep = KnowledgeRep.objects.filter(name=repository_name)[0]
                krep = KnowledgeRep.objects.get(id=krep.id)
                sb.knowledgerep = krep

            if sb.knowledgerep.name != 'Empty':
                answer = run_rag(sb.knowledgerep.id,p,sb.model)                    
                print(answer)
            else:
                output_format = False
                answer,log = prompt_rag(p,output_format,sb.model)                   
                print(answer)
        
        if sb.type == 'TOOL' and not loop_st_found:
            p = f"Context:{sb.context} Instruction:{sb.instruction.replace('previous_result',answer)}   "
            output_format = False
            if sb.outputFormatInstruction != '':
                output_format = json.loads(sb.outputFormatInstruction)  
            print(output_format)
            assigned_tools = SubTaskTool.objects.filter(subtask=sb.id)
            for at in assigned_tools:
                log += f'<p> Assigned tools {at}</p>'
                # t = Tool.objects.get(id=at.tool)
                t = model_to_dict(at.tool)
                log += f'<p> Tool Defininition: {at.tool} </p>'
                tools.append(t)
            print(tools)
            log += f'<p> Prompt {p}</p>'
            log += f'<p> Model  {model}</p>'
            answer,log = prompt(p,tools,output_format,model)
            log += f'<p> Answer {answer}</p>'
            task_log.log = log
            task_log.save()
    # Execute LOOP SUBTASK
    print("====================== LOOP SUBTASKS ====================")
    print(loop_st)
    print(loop_previous_result)
    # loop_previous_result = json.loads(loop_previous_result)
    if loop_st and loop_previous_result and len(loop_previous_result) > 0:
        loop_previous_result = json_repair.loads(loop_previous_result)
        print(loop_previous_result)
        for result in loop_previous_result['previous_result']:
            # Loop over and run all tasks 
            answer = result
            print("====================== LOOP INPUT ANSWER  ====================",answer)
            for sb in loop_st:
                print("====================== LOOP SB ANSWER  ====================",answer)
                if sb.type == 'RAG':
                    p = f"Context:{sb.context} Instruction:{sb.instruction.replace('previous_result',answer)} Output Format: {sb.outputFormatInstruction}"
                    if sb.knowledgerep.name != 'Empty':
                        answer = run_rag(sb.knowledgerep.id,p,sb.model)                    
                        print(answer)
                    else:
                        output_format = False
                        answer,log = prompt_rag(p,output_format,sb.model)
                        print(answer)
                
                if sb.type == 'TOOL':
                    p = f"Context:{sb.context} Instruction:{sb.instruction.replace('previous_result',answer)}   "
                    
                    output_format = False
                    if sb.outputFormatInstruction != '':
                        output_format = json.loads(sb.outputFormatInstruction)  
                    print(output_format)
                    assigned_tools = SubTaskTool.objects.filter(subtask=sb.id)
                    for at in assigned_tools:
                        log += f'<p> Assigned tools {at}</p>'
                        # t = Tool.objects.get(id=at.tool)
                        t = model_to_dict(at.tool)
                        log += f'<p> Tool Defininition: {at.tool} </p>'
                        tools.append(t)
                    print(tools)
                    log += f'<p> Prompt {p}</p>'
                    log += f'<p> Model  {model}</p>'
                    answer,log = prompt(p,tools,output_format,model)
                    log += f'<p> Answer {answer}</p>'
                    task_log.log = log
                    task_log.save()
    print("====================== FINAL ANSWER ====================",answer)
    task_run = TaskRun.objects.get(id=task_run.id)
    print("closing task run",task_run)
    task_run.current_step = -1
    task_run.current_step_status = 'COMPLETED'
    task_run.save()
    print(answer)
    return answer

    

def run_rag(krepo_id,prompt,model):
    krepo = KnowledgeRep.objects.get(id=krepo_id)  
    file_path = f"krep/{krepo.name}"
    file_dir = Path(file_path)
    documents = SimpleDirectoryReader(file_dir).load_data()
    # set up ChromaVectorStore and load in data
    print("============= Setting up ChromaVectorStore and loading data ===========")
    chroma_client = chromadb.PersistentClient(path="db/")
    chroma_collection = chroma_client.get_or_create_collection(krepo.name)
    # bge-base embedding model
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
    # ollama
    Settings.llm = Ollama(model=model, request_timeout=360.0)
    print("=============== Vectorizing =============================")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=Settings.embed_model
    )
    query_engine = index.as_query_engine()
    print("=============== Prompting LLM =============================")
    # prompt = """
            # [SYSTEM]
            # You are an expert at reading instructions and providing relevant data,
            # you do not hallucinate or make up stuff, you stick to what is given and what
            # is the ask.
            # [USER]               
            # List all the symbols of all companies
            # [OUTPUT]
            # The output format should be in the form of json with strictly following structure
            # There should be no deviation in the output format
            # { output:  ["symbol1","symbol2"] }
            # 
    # """
    response = query_engine.query(prompt)    
    return str(response)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import sqlite3
from datetime import datetime

@csrf_exempt
def post_symbol_sentiment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Get POST data
        print(request.POST)
        data =  json.loads(request.body.decode("utf-8"))
        symbol = data['symbol']
        sentiment = data['sentiment']
        explanation = data['explanation']
        print(symbol, sentiment, explanation)
        # Validate required fields
        if not all([ symbol, sentiment, explanation]):
            return JsonResponse({
                'error-': 'Missing required fields. Need symbol, sentiment, and explanation'
            }, status=400)
        
        # Connect to SQLite database
        conn = sqlite3.connect('stocksentiment.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,                
                symbol TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                explanation TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert data
        cursor.execute('''
            INSERT INTO sentiments (symbol, sentiment, explanation, created_at)
            VALUES (?, ?, ?, ?)
        ''', (symbol, sentiment, explanation, datetime.now().isoformat()))
        
        # Commit and close
        conn.commit()
        conn.close()
        
        return JsonResponse({
            'success': True,
            'message': 'Sentiment data saved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred: {str(e)}'
        }, status=500)
    



from django.views.decorators.csrf import csrf_exempt
import os
from pathlib import Path
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import os
from pathlib import Path
from django.http import JsonResponse
import json
from django.shortcuts import redirect
from django.urls import reverse

@csrf_exempt
def api_upload_document(request):
    """
    API endpoint to receive document uploads from a Flask application
    and add them to a knowledge repository.
    """
    
    if request.method == 'GET':
        return HttpResponse("api_upload_document")

    print(request.method)
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Check if repository ID is provided
        repository_name = request.POST.get('repository_name')
      
        description = request.POST.get('description')
        agent_name = request.POST.get('agent_name')
        if not description:
            description = repository_name
        if not repository_name:
            return JsonResponse({'error': 'Repository nameis required'}, status=400)
        
        # associated_task = request.POST.get('associated_task')
        # associated_task = Task.objects.filter(name=associated_task)
        print(repository_name,description,agent_name)
        
        # Get the knowledge repository
        krep = KnowledgeRep.objects.filter(name=repository_name)

        if len(krep) == 0:
            agent_name = Task.objects.filter(name=agent_name)[0]
            krep = KnowledgeRep.objects.create(name=repository_name,description=description,associated_task=agent_name)
        else:
            krep = krep[0]
            KnowledgeRepFiles.objects.filter(Knowledge_rep=krep).delete()
        
        # Check if file is in the request
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        print("Deleting existing files")
       
        
        

        for file in request.FILES:
            # Save the uploaded file
            uploaded_file = request.FILES['file']
            print(uploaded_file)
            
            # Create instance and save to database
            instance = KnowledgeRepFiles(Knowledge_rep=krep, file=uploaded_file)
            instance.save()
        print("Executing LLM")
        
        llm_answer = execute_task_run(id=None,agent_name=agent_name,model=None,repository_name=repository_name)
        # Response with success message
        print("Sending response back with following answer")
        print(llm_answer)
        return JsonResponse({
            'success': True,
            'message': f'Documents {request.FILES} uploaded successfully to repository {krep.name}',
            'repository_name': repository_name,
            'llm_answer' : llm_answer
          
        })
        
    except Exception as e:
        print(e)
        return JsonResponse({
            'error': f'An error occurred: {str(e)}'
        }, status=500)
