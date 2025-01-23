func = [
'''
metadata = {
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
''',
'''
metadata = {
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
''']

for f in func:
    exec(f)

print(add_two_numbers(4,5))
print(metadata['type'])