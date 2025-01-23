from smolagents.agents import ToolCallingAgent
from smolagents import tool, LiteLLMModel
from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel
from typing import Optional

model = LiteLLMModel(
    model_id="ollama_chat/llama3.2",
    api_base="http://localhost:11434", # replace with remote open-ai compatible server if necessary
    api_key="your-api-key" # replace with API key if necessary
)
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)
@tool
def get_weather(location: str, celsius: Optional[bool] = False) -> str:
    """
    Get weather in the next days at given location.
    Secretly this tool does not care about the location, it hates the weather everywhere.

    Args:
        location: the location
        celsius: the temperature
    """
    return "The weather is UNGODLY with torrential rains and temperatures below -10°C"

# agent = ToolCallingAgent(tools=[get_weather], model=model)

# print(agent.run("What's the weather like in Paris?"))


print(agent.run(
    "Could you give me the 118th number in the Fibonacci sequence?",
))

print(agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?"))