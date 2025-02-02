from typing import Dict, Any, Callable
import json
import importlib.util
import types
from ollama import chat
from ollama import ChatResponse



def dynamically_load_tools(tools):
    """
    Dynamically load tools from Tool queryset
    
    Returns:
        tuple: (available_functions, tool_definitions)
    """
    available_functions = {}
    tool_definitions = []
    
    for tool in tools:
        # Create a dynamic module for the tool
        module = types.ModuleType(tool['name'])
        
        try:
            # Execute the codeblock in the module's context
            exec(tool['codeblock'], module.__dict__)
            
            # Get the function with the same name as the tool
            func = getattr(module, tool['name'])
            
            # Add to available functions
            available_functions[tool['name']] = func
            
            # Create tool definition
            tool_definition = tool['codeblock'].metadata
            tool_definitions.append(tool_definition)
        
        except Exception as e:
            print(f"Error loading tool {tool['name']}: {e}")
    
    return available_functions, tool_definitions

def prompt(prompt_text, tools,model):
    log = ''
    final_answer = "NO ANSWER"
    # Dynamically load tools
    tool_definitions = []
    available_functions: Dict[str, Callable] = {}
    for tool in tools:
        # Create a dynamic module for the tool
        
      exec(tool["codeblock"])
      tool_definitions.append(eval(tool['name'] + '_tool'))
      available_functions[tool['name']] = eval(tool['name'])
     
    # available_functions: Dict[str, Callable] = {
    # 'get_order': get_order,
    # 'add_order': add_order,
    # 'delete_order': delete_order,
    # 'get_stock': get_stock
    # } 
    messages = [{'role': 'user', 'content': prompt_text}]
    log += f'<p>{messages}</p>'
    
    # Use dynamically loaded tools in chat
    response = chat(
        model,  # Assuming 'model' is defined globally
        messages=messages,
        tools=tool_definitions,
    )
    
    # Process tool calls
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            if function_to_call := available_functions.get(tool.function.name):
                output = function_to_call(**tool.function.arguments)
                print('Function output:', output)
                log += f'<p>{output}</p>'
            else:
                print('Function', tool.function.name, 'not found')  
                log += f'<p>Function, {tool.function.name}, not found</p>'
                print(output)
  # Only needed to chat with the model using the tool call results
    if response.message.tool_calls:
      # Add the function response to messages for the model to use
      messages.append(response.message)
      messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name})
      print(messages) 
      log += f'<p>Messages, {messages}</p>'
      # Get final response from model with function outputs
      final_response = chat(model, messages=messages)
      print('Final response:', final_response.message.content)
      final_answer = final_response.message.content 
      
    else:
      print('No tool calls returned from model')
      log += f'<p>No tool calls returned from model</p>'
    
    return final_answer,log

if __name__ == '__main__':
  l31 = 'llama3.1'
  l32 = 'llama3.2'
  model = l31
  #  p = '''
  #       You are an Order Management agent that is good at reading carefully the and adding
  #       an order with following details.  Instructions: add an order for Item name ITEM-C, 
  #       with Quantity 40 at price per item as 600  Output : You return the order id and output.
  #       '''
  #  result = prompt(p)
  #  print(result,'\n')

  #  p = '''You are an Order Management AI Agent that is expert at calling the  provided set of tools.
  #          You stick to the tools provide and don't deviate or make up things.
  #          Given the order id previous_result get the order details 
  #          Output the order details in a simple format'''.replace('previous_result',result)
   
  tools = [{
"name":"subtract_two_numbers",
"codeblock":'''
subtract_two_numbers_tool = {
  'type': 'function',
  'function': {
    'name': 'subtract_two_numbers',
    'description': 'Subtract two numbers',
    'parameters': {
      'type': 'object',
      'required': ['a', 'b'],
      'properties': {
        'a': {'type': 'integer', 'description': 'The first number'},
        'b': {'type': 'integer', 'description': 'The second number'},
      },
    },
  },
}
def subtract_two_numbers(a: int, b: int) -> int:
  """
  Subtract two numbers
  """
  return a - b
'''},
{"name":"add_two_numbers",
"codeblock":'''
add_two_numbers_tool = {
  'type': 'function',
  'function': {
    'name': 'add_two_numbers',
    'description': 'Add two numbers',
    'parameters': {
      'type': 'object',
      'required': ['a', 'b'],
      'properties': {
        'a': {'type': 'integer', 'description': 'The first number'},
        'b': {'type': 'integer', 'description': 'The second number'},
      },
    },
  },
}
def add_two_numbers(a: int, b: int) -> int:
  """
  Add two numbers
  """
  return a + b
'''}]
  tool_definitions = []
  available_functions: Dict[str, Callable] = {}
  for tool in tools:
      # Create a dynamic module for the tool
      
    exec(tool["codeblock"])
    tool_definitions.append(eval(tool['name'] + '_tool'))
    available_functions[tool['name']] = eval(tool['name'])
     
  print(add_two_numbers(1,2))
  print(tool_definitions)
  print(available_functions)
  
  p = """you are an expert matheticians and is very accurate and does not hallucinate and make up things, 
      convert the words into numbers and perform the following , add two and three and then subtract five from the result"""
  result = prompt(p,tools,model)
  print(result)