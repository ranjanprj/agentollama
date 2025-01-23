from ollama import chat
from ollama import ChatResponse
from typing import Dict, Any, Callable


import sqlite3
l31 = 'llama3.1'
l32 = 'llama3.2'
model = l32
# Initialize SQLite database

import requests

API_BASE_URL = "http://127.0.0.1:5000/orders"

def get_stock(item_name: str) -> int:
    """Call the REST API to add a new order."""
    response = requests.get(f"{API_BASE_URL}/get_stock/{item_name}")

    if response.status_code == 200:
        return response.json().get('stock_quantity')
    else:
        raise Exception(f"Failed to add order: {response.json()}")

def add_order(item_name: str, quantity: int, price_per_item: float) -> int:
    """Call the REST API to add a new order."""
    response = requests.post(API_BASE_URL, json={
        "item_name": item_name,
        "quantity": quantity,
        "price_per_item": price_per_item
    })

    if response.status_code == 201:
        return response.json().get("order_id")
    else:
        raise Exception(f"Failed to add order: {response.json()}")

def get_order(order_id: int) -> dict:
    """Call the REST API to retrieve an order."""
    response = requests.get(f"{API_BASE_URL}/{order_id}")

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return {}
    else:
        raise Exception(f"Failed to get order: {response.json()}")

def delete_order(order_id: int) -> bool:
    """Call the REST API to delete an order."""
    response = requests.delete(f"{API_BASE_URL}/{order_id}")

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        raise Exception(f"Failed to delete order: {response.json()}")

get_stock_tool =  {
  "type": "function",
  "function": 
    {
      "name": "get_stock",
      "description": "Add a new order to the database.",
      "parameters": {
        "type": "object",
        "required": ["item_name"],
        "properties": {
          "item_name": {"type": "string", "description": "The name of the item."}
        }
      }
    }
  }
add_order_tool =  {
  "type": "function",
  "function": 
    {
      "name": "add_order",
      "description": "Add a new order to the database.",
      "parameters": {
        "type": "object",
        "required": ["item_name", "quantity", "price_per_item"],
        "properties": {
          "item_name": {"type": "string", "description": "The name of the item."},
          "quantity": {"type": "integer", "description": "The quantity of the item."},
          "price_per_item": {"type": "number", "description": "The price per item."}
        }
      }
    }
  }

get_order_tool =  {
    'type':'function',
    'function':
    {
      "name": "get_order",
      "description": "Retrieve an order by ID from the database.",
      "parameters": {
        "type": "object",
        "required": ["order_id"],
        "properties": {
          "order_id": {"type": "integer", "description": "The ID of the order to retrieve."}
        }
      }
    }
  }
delete_order_tool =    {
      "type" : "function",
      "function":{
      "name": "delete_order",
      "description": "Delete an order by ID from the database.",
      "parameters": {
        "type": "object",
        "required": ["order_id"],
        "properties": {
          "order_id": {"type": "integer", "description": "The ID of the order to delete."}
        }
      }
    }
  }


def add_two_numbers(a: int, b: int) -> int:
  """
  Add two numbers

  Args:
    a (int): The first number
    b (int): The second number

  Returns:
    int: The sum of the two numbers
  """
  return a + b


def subtract_two_numbers(a: int, b: int) -> int:
  """
  Subtract two numbers
  """
  return a - b


# Tools can still be manually defined and passed into chat
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

def prompt(prompt):
  final_answer = None
  messages = [{'role': 'user', 'content': prompt}]
  print('Prompt:', messages[0]['content'])  
  available_functions: Dict[str, Callable] = {
    'get_order': get_order,
    'add_order': add_order,
    'delete_order': delete_order,
    'get_stock': get_stock
  } 
  response: ChatResponse = chat(
    model,
    messages=messages,
    tools=[get_order_tool,delete_order_tool,add_order_tool,get_stock_tool],
  )
  print(response)
  if response.message.tool_calls:
    # There may be multiple tool calls in the response
    for tool in response.message.tool_calls:
      # Ensure the function is available, and then call it
      if function_to_call := available_functions.get(tool.function.name):
        print('Calling function:', tool.function.name)
        print('Arguments:', tool.function.arguments)
        output = function_to_call(**tool.function.arguments)
        print('Function output:', output)
      else:
        print('Function', tool.function.name, 'not found')  
  print(output)
  # Only needed to chat with the model using the tool call results
  if response.message.tool_calls:
    # Add the function response to messages for the model to use
    messages.append(response.message)
    messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name})
    print(messages) 
    # Get final response from model with function outputs
    final_response = chat(model, messages=messages)
    print('Final response:', final_response.message.content)
    final_answer = final_response.message.content 
  else:
    print('No tool calls returned from model')
  return final_answer

if __name__ == '__main__':
   p = '''
        You are an Order Management agent that is good at reading carefully the and adding
        an order with following details.  Instructions: add an order for Item name ITEM-C, 
        with Quantity 40 at price per item as 600  Output : You return the order id and output.
        '''
   result = prompt(p)
   print(result,'\n')

   p = '''You are an Order Management AI Agent that is expert at calling the  provided set of tools.
           You stick to the tools provide and don't deviate or make up things.
           Given the order id previous_result get the order details 
           Output the order details in a simple format'''.replace('previous_result',result)
   result = prompt(p)
   print(result)