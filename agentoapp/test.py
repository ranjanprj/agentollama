# func = [
# '''
# metadata = {
#   'type': 'function',
#   'function': {
#     'name': 'subtract_two_numbers',
#     'description': 'Subtract two numbers',
#     'parameters': {
#       'type': 'object',
#       'required': ['a', 'b'],
#       'properties': {
#         'a': {'type': 'integer', 'description': 'The first number'},
#         'b': {'type': 'integer', 'description': 'The second number'},
#       },
#     },
#   },
# }
# def subtract_two_numbers(a: int, b: int) -> int:
#   """
#   Subtract two numbers
#   """
#   return a - b
# ''',
# '''
# metadata = {
#   'type': 'function',
#   'function': {
#     'name': 'add_two_numbers',
#     'description': 'Add two numbers',
#     'parameters': {
#       'type': 'object',
#       'required': ['a', 'b'],
#       'properties': {
#         'a': {'type': 'integer', 'description': 'The first number'},
#         'b': {'type': 'integer', 'description': 'The second number'},
#       },
#     },
#   },
# }
# def add_two_numbers(a: int, b: int) -> int:
#   import requests
#   r = requests.get('https://google.com')
#   print(r.text)
#   """
#   Add two numbers
#   """
#   return a + b
# ''']

# for f in func:
#     exec(f)

# print(add_two_numbers(4,5))
# print(metadata['type'])


# from ollama import ListResponse, list

# response: ListResponse = list()

# for model in response.models:
#   print('Name:', model.model)
#   print('  Size (MB):', f'{(model.size.real / 1024 / 1024):.2f}')
#   if model.details:
#     print('  Format:', model.details.format)
#     print('  Family:', model.details.family)
#     print('  Parameter Size:', model.details.parameter_size)
#     print('  Quantization Level:', model.details.quantization_level)
#   print('\n')


# add_order_tool =  {
# "type": "function",
# "function": 
#   {
#     "name": "add_order",
#     "description": "Add a new order to the database.",
#     "parameters": {
#       "type": "object",
#       "required": ["item_name", "quantity", "price_per_item"],
#       "properties": {
#         "item_name": {"type": "string", "description": "The name of the item."},
#         "quantity": {"type": "integer", "description": "The quantity of the item."},
#         "price_per_item": {"type": "number", "description": "The price per item."}
#       }
#     }
#   }
# }
# def add_order(item_name: str, quantity: int, price_per_item: float) -> int:
#     """Call the REST API to add a new order."""
#     print("XXXXXXXXXXXXXXXXXXXXXXXXXXX")
#     print(item_name,quantity,price_per_item)
#     import requests
#     API_BASE_URL = "http://127.0.0.1:5000/orders/"
#     response = requests.post(API_BASE_URL, json={
#         "item_name": item_name,
#         "quantity": quantity,
#         "price_per_item": price_per_item
#     })

#     if response.status_code == 201:
#         print(response)
#         return response.json().get("order_id")
#     else:
#         raise Exception(f"Failed to add order: {response.json()}")
# import requests
# API_BASE_URL = "http://127.0.0.1:5000/orders"
# response = requests.post(API_BASE_URL, json={
#         "item_name": 'ITEM-A',
#         "quantity": 100,
#         "price_per_item": 100
#     })

# print(response)


from ollama import chat
from pydantic import BaseModel


from typing import Annotated, Literal


allowed_values = ["Positive", "Negative","Neutral"]

class Output(BaseModel):
  symbol: str  
  sentiment: Literal[tuple(allowed_values)]
  explanation: str
print(Output.model_json_schema())


